
const User = require('../mongo_models/user.model');
const GoogleController = require('./google.controller');
const authController = require('./auth.controller');
const GithubAuthController = require('./github.auth.controller');
const authService = require('../services/auth.service');


const vscode_authController = {
    loginRedirect: (req, res) => {
        // Get the callback URL and state from query parameters
        const { callback, state } = req.query;
        
        if (!callback || !state) {
          return res.status(400).json({ error: 'Missing required parameters' });
        }
        
        // Store the callback URL and state in the session for use after login
        req.session.authCallback = {
          callback: callback,
          state: state,
          expiresAt: Date.now() + (10 * 60 * 1000) // 10 minute expiration
        };
        
        // Show the login form
        res.render('login', { 
          title: 'Login to CodeNexus', 
          isVSCode: true, 
          redirectForm: true,
          actionUrl: '/api/auth/process-login-redirect'
        });
      },

      processLoginRedirect:async (req, res) => {
        try {
          const { username, password } = req.body;
          
          // Check if we have callback information in the session
          if (!req.session.authCallback) {
            return res.status(400).json({ error: 'No active authentication session' });
          }
          
          // Check if the callback session has expired
          if (Date.now() > req.session.authCallback.expiresAt) {
            delete req.session.authCallback;
            return res.status(400).json({ error: 'Authentication session expired' });
          }
          
          // Get the callback URL and state from the session
          const { callback, state } = req.session.authCallback;
          
          // Clear the callback data from the session
          delete req.session.authCallback;
          
          // Find the user
          const user = await User.findOne({ username });
          if (!user) {
            return res.status(400).json({ error: 'User not found' });
          }
          
          // Verify password
          const isPasswordValid = await authController.verifyPassword(password, user.password);
          if (!isPasswordValid) {
            return res.status(400).json({ error: 'Invalid password' });
          }
          
          // Generate JWT token
          const token = authService.generateToken(user);
          
          // Redirect to the callback URL with the token and state
          res.redirect(`${callback}?token=${encodeURIComponent(token)}&state=${encodeURIComponent(state)}`);
        } catch (error) {
          console.error('Login redirect processing error:', error);
          res.status(500).json({ error: 'Failed to process login' });
        }
      },

      processGithubLoginRedirect: (req, res) => {
        try {
          // Get callback and state parameters
          const { callback, state } = req.query;
          
          // Store callback info in session if provided
          if (callback && state) {
            req.session.githubCallback = {
              callback,
              state,
              expiresAt: Date.now() + (10 * 60 * 1000) // 10 minute expiration
            };
          }
          
          // Get GitHub authorization URL
          const authUrl = GithubAuthController.getGithubOauthUrl();
          
          // Redirect to GitHub login
          res.redirect(authUrl);
        } catch (error) {
          res.status(400).json({ error: error.message });
        }
      },

      processGithubCallback: async (req, res) => {
        try {
          const { code } = req.query;
          
          // Exchange code for tokens
          const response = await GithubAuthController.exchangeGithubCode(code);
          
          if (response.error) {
            return res.status(400).json({ error: response.error });
          }
          
          // Generate JWT token
          const token = authService.generateToken(response.new_user);
          
          // Set auth cookies for browsers
          authService.setAuthCookies(res, token);
          
          // Check if this is a VS Code authentication
          if (req.session.githubCallback) {
            const { callback, state } = req.session.githubCallback;
            delete req.session.githubCallback;
            return res.redirect(`${callback}?token=${encodeURIComponent(token)}&state=${encodeURIComponent(state)}`);
          }
          
          // Regular web flow - redirect to frontend
          return res.redirect(`${process.env.FRONTEND_URL}/auth/github/callback?success=true`);
        } catch (error) {
          console.error('GitHub callback error:', error);
          return res.status(500).json({ error: 'GitHub authentication failed' });
        }
      },

      initiateGoogleAuth:  (req, res, next) => {
        // Get callback and state parameters (for VS Code authentication)
        const { callback, state } = req.query;
        
        // Store callback info in session if provided
        if (callback && state) {
          req.session.googleCallback = {
            callback,
            state,
            expiresAt: Date.now() + (10 * 60 * 1000) // 10 minute expiration
          };
        }
        
        // Continue with standard Google OAuth flow
        GoogleController.initiateGoogleAuth(req, res, next);
      },

      handleGoogleCallback: async (req, res, next) => {
        GoogleController.handleCallBack(req, res, next);
      }
    
}

module.exports = vscode_authController;
