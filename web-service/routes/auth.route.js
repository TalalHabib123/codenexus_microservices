const express = require('express');
const router = express.Router();
const GithubAuthController = require('../controller/github.auth.controller');
const AuthController = require('../controller/auth.controller');
const GoogleController = require('../controller/google.controller');
const { requireAuth } = require('../middleware/auth.middleware');

// Initialize Google authentication strategy
GoogleController.configureGoogleStrategy();

// Traditional authentication routes
router.post('/signup', AuthController.signup);
router.post('/login', AuthController.login);
router.post('/logout', AuthController.logout);
router.get('/me', requireAuth, AuthController.getCurrentUser);

// GitHub OAuth routes
router.get('/github/login', (req, res) => {
  try {
    const authUrl = GithubAuthController.getGithubOauthUrl();
    res.json({ authorization_url: authUrl });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

router.post('/github/exchange', async (req, res) => {
  try {
    const { code } = req.body;
    if (!code) {
      return res.status(400).json({ error: 'Code is required' });
    }
    
    // Pass res object to allow setting cookies
    const response = await GithubAuthController.exchangeGithubCode(code, res);
    if (response.error) {
      return res.status(400).json({ error: response.error });
    }
    
    res.json(response);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

// Google OAuth routes
router.get('/google/login', GoogleController.initiateGoogleAuth);
router.get('/google/callback', GoogleController.handleCallBack);

// Protected route to get GitHub access token
router.get('/github/token', requireAuth, async (req, res) => {
  try {
    // Only allow if the user has a GitHub ID
    if (!req.user.github_id) {
      return res.status(403).json({ error: 'User not linked with GitHub' });
    }
    
    const accessToken = await GithubAuthController.getValidAccessToken(req.user._id);
    res.json({ access_token: accessToken });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Protected route to get Google access token
router.get('/google/token', requireAuth, async (req, res) => {
  try {
    // Only allow if the user has a Google ID
    if (!req.user.google_id) {
      return res.status(403).json({ error: 'User not linked with Google' });
    }
    
    const accessToken = await GoogleController.getValidGoogleToken(req.user._id);
    res.json({ access_token: accessToken });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;