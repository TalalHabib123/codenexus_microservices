const express = require('express');
const router = express.Router();
const GithubAuthController = require('../controller/github.auth.controller');
const AuthController = require('../controller/auth.controller');

// GitHub OAuth routes
router.get('/github/login', (req, res) => {
  try {
    const authUrl = GithubAuthController.getGithubOauthUrl();
    res.json({ authorization_url: authUrl });
  } catch (error) {
    res.status(400).json({ detail: error.message });
  }
});

router.post('/github/exchange', async (req, res) => {
  try {
    const { code } = req.body;
    if (!code) {
      return res.status(400).json({ detail: 'Code is required' });
    }
    
    const response = await GithubAuthController.exchangeGithubCode(code);
    if (response.error) {
      return res.status(400).json({ detail: response.error });
    }
    
    res.json(response);
  } catch (error) {
    res.status(400).json({ detail: error.message });
  }
});

// User authentication routes
router.post('/signup', async (req, res) => {
  try {
    await AuthController.signup(req, res);
  } catch (error) {
    res.status(400).json({ detail: error.message });
  }
});

router.post('/login', async (req, res) => {
  try {
    await AuthController.login(req, res);
  } catch (error) {
    res.status(400).json({ detail: error.message });
  }
});

module.exports = router;