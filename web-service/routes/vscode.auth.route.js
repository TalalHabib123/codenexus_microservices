const express = require('express');
const router = express.Router();

const vscode_authController = require('../controller/vscode.auth.controller');
const GoogleController = require('../controller/google.controller');

router.get('/login-redirect', vscode_authController.loginRedirect);
router.post('/process-login-redirect', vscode_authController.processLoginRedirect);
  
  // Modify GitHub login endpoint (in github.auth.controller.js)
  router.get('/github/login', vscode_authController.processGithubLoginRedirect);
  
  // Update GitHub callback handler
  router.get('/github/callback', vscode_authController.processGithubCallback);
  
router.get("/google/login", vscode_authController.initiateGoogleAuth);


module.exports = router;