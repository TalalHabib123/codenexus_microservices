const axios = require('axios');
const crypto = require('crypto');
require('dotenv').config();
const User = require('../mongo_models/User');

// Set up encryption
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
if (!ENCRYPTION_KEY) {
  throw new Error("Missing ENCRYPTION_KEY in environment variables");
}

// Create cipher for encryption
const algorithm = 'aes-256-cbc';
const key = crypto.scryptSync(ENCRYPTION_KEY, 'salt', 32);
const iv = crypto.randomBytes(16);

const GithubAuthController = {
  /**
   * Returns GitHub OAuth URL for frontend to redirect to
   * @returns {string} GitHub OAuth authorization URL
   */
  getGithubOauthUrl: () => {
    const clientId = process.env.CLIENT_ID;
    const redirectUri = process.env.REDIRECT_URI;
    const scope = "user:email,repo";

    if (!clientId || !redirectUri) {
      throw new Error("CLIENT_ID or REDIRECT_URI missing from environment variables");
    }

    return `https://github.com/login/oauth/authorize?client_id=${clientId}&redirect_uri=${redirectUri}&scope=${scope}`;
  },

  /**
   * Exchanges GitHub code for an access token and manages user data
   * @param {string} code - The authorization code from GitHub
   * @returns {Promise<Object>} Response with token and user info
   */
  exchangeGithubCode: async (code) => {
    try {
      // Exchange code for access token
      const tokenResponse = await axios.post(
        "https://github.com/login/oauth/access_token",
        {
          client_id: process.env.CLIENT_ID,
          client_secret: process.env.CLIENT_SECRET,
          code: code
        },
        {
          headers: { "Accept": "application/json" }
        }
      );

      const tokenData = tokenResponse.data;
      const accessToken = tokenData.access_token;

      if (!accessToken) {
        return { error: "Failed to obtain access token", github_response: tokenData };
      }

      // Fetch user data from GitHub
      const userResponse = await axios.get(
        "https://api.github.com/user",
        {
          headers: { "Authorization": `Bearer ${accessToken}` }
        }
      );

      const userInfo = userResponse.data;
      const githubId = userInfo.id;
      const username = userInfo.login;
      const email = userInfo.email;
      
      // Split name if available
      const splitName = userInfo.name ? userInfo.name.split(' ') : [];
      const firstName = splitName.length > 0 ? splitName[0] : null;
      const lastName = splitName.length > 1 ? splitName[1] : null;
      
      // Encrypt the access token
      const cipher = crypto.createCipheriv(algorithm, key, iv);
      let encryptedToken = cipher.update(accessToken, 'utf8', 'hex');
      encryptedToken += cipher.final('hex');
      
      // Store the IV with the token for decryption later
      const encryptedAccessToken = iv.toString('hex') + ':' + encryptedToken;

      // Check if user exists
      let existingUser = await User.findOne({ github_id: githubId });
      let newUser = null;

      if (existingUser) {
        existingUser.encrypted_access_token = encryptedAccessToken;
        await existingUser.save();
      } else {
        newUser = new User({
          username: username,
          email: email,
          github_id: githubId,
          encrypted_access_token: encryptedAccessToken,
          first_name: firstName,
          last_name: lastName
        });
        await newUser.save();
      }

      return {
        msg: "GitHub OAuth success",
        access_token: accessToken,
        user: userInfo,
        new_user: newUser ? newUser.toDict() : existingUser.toDict()
      };
    } catch (error) {
      console.error("GitHub exchange error:", error.response?.data || error.message);
      return { error: "Failed to exchange GitHub code" };
    }
  },

  /**
   * Decrypt an access token
   * @param {string} encryptedToken - The encrypted token
   * @returns {string} Decrypted access token
   */
  decryptAccessToken: (encryptedToken) => {
    try {
      const [ivHex, encryptedHex] = encryptedToken.split(':');
      const iv = Buffer.from(ivHex, 'hex');
      const decipher = crypto.createDecipheriv(algorithm, key, iv);
      let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
      decrypted += decipher.final('utf8');
      return decrypted;
    } catch (error) {
      console.error("Decryption error:", error);
      throw new Error("Failed to decrypt token");
    }
  }
};

module.exports = GithubAuthController;