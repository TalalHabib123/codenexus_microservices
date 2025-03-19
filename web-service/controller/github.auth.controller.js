const axios = require("axios");
require("dotenv").config();
const User = require("../mongo_models/User");
const authService = require('../services/auth.service');

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
   * @param {Object} res - Express response object for cookie setting
   * @returns {Promise<Object>} Response with token and user info
   */
  exchangeGithubCode: async (code, res) => {
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
      const lastName = splitName.length > 1 ? splitName.slice(1).join(" ") : null;

      // Encrypt the OAuth tokens
      const encryptedAccessToken = authService.encryptToken(accessToken);
      const encryptedRefreshToken = refreshToken ? authService.encryptToken(refreshToken) : null;
      
      // Set token expiry date
      const expiryDate = new Date();
      expiryDate.setSeconds(expiryDate.getSeconds() + (expiresIn || 28800)); // Default to 8 hours

      // Check if user exists
      let user = await User.findOne({ github_id: githubId });

      if (user) {
        // Update existing user
        user.encrypted_access_token = encryptedAccessToken;
        user.encrypted_refresh_token = encryptedRefreshToken;
        user.token_expiry = expiryDate;
        // Update other fields that might have changed
        if (email) user.email = email;
        if (firstName) user.first_name = firstName;
        if (lastName) user.last_name = lastName;
        
        await user.save();
      } else {
        // Create new user
        user = new User({
          username: username,
          email: email,
          github_id: githubId,
          encrypted_access_token: encryptedAccessToken,
          encrypted_refresh_token: encryptedRefreshToken,
          token_expiry: expiryDate,
          first_name: firstName,
          last_name: lastName,
        });
        
        await user.save();
      }

      // Generate JWT for our application
      const jwtToken = authService.generateToken(user);
      
      // Set authentication cookies if response object is provided
      if (res) {
        authService.setAuthCookies(res, jwtToken);
      }

      return {
        message: "GitHub authentication successful",
        success: true,
        user: user.toDict(),
        token: jwtToken
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
      const refreshToken = authService.decryptToken(user.encrypted_refresh_token);

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
      const encryptedAccessToken = authService.encryptToken(newAccessToken);
      const encryptedRefreshToken = authService.encryptToken(newRefreshToken);

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

  /**
   * Get a valid GitHub access token for a user
   * @param {string} userId - User ID to get token for
   * @returns {Promise<string>} Valid access token
   */
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
        return authService.decryptToken(user.encrypted_access_token);
      }
    } catch (error) {
      console.error("Error getting valid token:", error);
      throw new Error("Failed to get valid access token");
    }
  }
};

module.exports = GithubAuthController;