const axios = require("axios");
const crypto = require("crypto");
require("dotenv").config();
const User = require("../mongo_models/User");

// Set up encryption
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
if (!ENCRYPTION_KEY) {
  throw new Error("Missing ENCRYPTION_KEY in environment variables");
}

// Create cipher for encryption
const algorithm = "aes-256-cbc";
const key = crypto.scryptSync(ENCRYPTION_KEY, "salt", 32);
const iv = crypto.randomBytes(16);



// Helper functions for token encryption/decryption
const encryptToken = (token) => {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(token, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    return iv.toString('hex') + ':' + encrypted;
  };
  
const decryptToken = (encryptedToken) => {
    const [ivHex, encryptedHex] = encryptedToken.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    return decrypted;
  };



const GithubAuthController = {
  /**
   * Returns GitHub OAuth URL for frontend to redirect to
   * @returns {string} GitHub OAuth authorization URL
   */
  getGithubOauthUrl: () => {
    const clientId = process.env.CLIENT_ID;
    const redirectUri = process.env.REDIRECT_URI;
    const scope = "user:email,repo, offline_access";

    if (!clientId || !redirectUri) {
      throw new Error(
        "CLIENT_ID or REDIRECT_URI missing from environment variables"
      );
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
          code: code,
          grant_type: "authorization_code",
        },
        {
          headers: { Accept: "application/json" },
        }
      );

      const tokenData = tokenResponse.data;
      const accessToken = tokenData.access_token;
      const refreshToken = tokenData.refresh_token;
      const expiresIn = tokenData.expires_in;
      if (!accessToken) {
        return {
          error: "Failed to obtain access token",
          github_response: tokenData,
        };
      }

      // Fetch user data from GitHub
      const userResponse = await axios.get("https://api.github.com/user", {
        headers: { Authorization: `Bearer ${accessToken}` },
      });

      const userInfo = userResponse.data;
      const githubId = userInfo.id;
      const username = userInfo.login;
      const email = userInfo.email;

      // Split name if available
      const splitName = userInfo.name ? userInfo.name.split(" ") : [];
      const firstName = splitName.length > 0 ? splitName[0] : null;
      const lastName = splitName.length > 1 ? splitName[1] : null;

      // Encrypt the access token
      const cipher = crypto.createCipheriv(algorithm, key, iv);
      const encryptedAccessToken = encryptToken(accessToken);
      const encryptedRefreshToken = encryptToken(refreshToken);
      const expiryDate = new Date();
      expiryDate.setSeconds(expiryDate.getSeconds() + expiresIn);

      // Check if user exists
      let existingUser = await User.findOne({ github_id: githubId });
      let newUser = null;

      if (existingUser) {
        existingUser.encrypted_access_token = encryptedAccessToken;
        existingUser.encrypted_refresh_token = encryptedRefreshToken;
        existingUser.token_expiry = expiryDate;
        await existingUser.save();
      } else {
        newUser = new User({
          username: username,
          email: email,
          github_id: githubId,
          encrypted_access_token: encryptedAccessToken,
          encrypted_refresh_token: encryptedRefreshToken,
          token_expiry: expiryDate,
          first_name: firstName,
          last_name: lastName,
        });
        await newUser.save();
      }

      return {
        msg: "GitHub OAuth success",
        access_token: accessToken,
        user: userInfo,
        new_user: newUser ? newUser.toDict() : existingUser.toDict(),
      };
    } catch (error) {
      console.error(
        "GitHub exchange error:",
        error.response?.data || error.message
      );
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
     return decryptToken(encryptedToken);
    } catch (error) {
      console.error("Decryption error:", error);
      throw new Error("Failed to decrypt token");
    }
  },
  /**
   * Refreshes an access token using the refresh token
   * @param {string} userId - User ID to refresh token for
   * @returns {Promise<Object>} New access token and expiry
   */
  refreshAccessToken: async (userId) => {
    try {
      const user = await User.findById(userId);
      if (!user || !user.encrypted_refresh_token) {
        throw new Error("User not found or missing refresh token");
      }

      // Decrypt refresh token
      const refreshToken = GithubAuthController.decryptAccessToken(
        user.encrypted_refresh_token
      );

      // Request new access token
      const response = await axios.post(
        "https://github.com/login/oauth/access_token",
        {
          client_id: process.env.CLIENT_ID,
          client_secret: process.env.CLIENT_SECRET,
          refresh_token: refreshToken,
          grant_type: "refresh_token",
        },
        {
          headers: { Accept: "application/json" },
        }
      );

      const tokenData = response.data;
      const newAccessToken = tokenData.access_token;
      const newRefreshToken = tokenData.refresh_token || refreshToken;
      const expiresIn = tokenData.expires_in || 28800;

      // Encrypt and store new tokens
      const encryptedAccessToken = encryptToken(newAccessToken);
      const encryptedRefreshToken = encryptToken(newRefreshToken);

      // Update expiration
      const expiryDate = new Date();
      expiryDate.setSeconds(expiryDate.getSeconds() + expiresIn);

      // Update user
      user.encrypted_access_token = encryptedAccessToken;
      user.encrypted_refresh_token = encryptedRefreshToken;
      user.token_expiry = expiryDate;
      await user.save();

      return {
        access_token: newAccessToken,
        expires_at: expiryDate,
      };
    } catch (error) {
      console.error(
        "Token refresh error:",
        error.response?.data || error.message
      );
      throw new Error("Failed to refresh token");
    }
  },

  getValidAccessToken: async (userId) => {
    try {
      const user = await User.findById(userId);
      if (!user) {
        throw new Error("User not found");
      }
      
      // Check if token is expired or about to expire (within 5 minutes)
      const now = new Date();
      const bufferTime = 5 * 60 * 1000; // 5 minutes in milliseconds
      const tokenIsExpired = !user.token_expiry || now.getTime() > (user.token_expiry.getTime() - bufferTime);
      
      if (tokenIsExpired) {
        // Refresh token
        const result = await GithubAuthController.refreshAccessToken(userId);
        return result.access_token;
      } else {
        // Token is still valid
        return GithubAuthController.decryptAccessToken(user.encrypted_access_token);
      }
    } catch (error) {
      console.error("Error getting valid token:", error);
      throw new Error("Failed to get valid access token");
    }
  },


};

module.exports = GithubAuthController;
