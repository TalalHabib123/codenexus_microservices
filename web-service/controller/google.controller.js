const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const fs = require('fs');
const User = require('../mongo_models/User');
const authService = require('../services/auth.service');

const GoogleController = {
    configureGoogleStrategy: () => {
        // Load Google OAuth credentials from file or environment variables
        let googleCredentials;
        
        try {
            // Try to load from file
            googleCredentials = JSON.parse(fs.readFileSync('client.json', 'utf8'));
        } catch (error) {
            // Fallback to environment variables
            googleCredentials = {
                web: {
                    client_id: process.env.GOOGLE_CLIENT_ID,
                    client_secret: process.env.GOOGLE_CLIENT_SECRET
                }
            };
        }
        
        // Verify credentials are available
        if (!googleCredentials.web.client_id || !googleCredentials.web.client_secret) {
            throw new Error('Google client credentials are missing');
        }
        
        // Configure Passport strategy
        passport.use(new GoogleStrategy({
            clientID: googleCredentials.web.client_id,
            clientSecret: googleCredentials.web.client_secret,
            callbackURL: "/auth/google/callback",
            passReqToCallback: true
        },
        async (req, accessToken, refreshToken, profile, done) => {
            try {
                // Encrypt tokens
                const encryptedAccessToken = authService.encryptToken(accessToken);
                const encryptedRefreshToken = refreshToken ? authService.encryptToken(refreshToken) : null;
                
                // Set token expiry (Google tokens typically last 1 hour)
                const expiryDate = new Date();
                expiryDate.setHours(expiryDate.getHours() + 1);
                
                // Check if user already exists in the database
                let user = await User.findOne({ google_id: profile.id });
                
                if (!user) {
                    // If not, create a new user
                    user = new User({
                        username: profile.displayName || `user_${profile.id}`,
                        email: profile.emails && profile.emails.length > 0 ? profile.emails[0].value : null,
                        google_id: profile.id,
                        first_name: profile.name?.givenName,
                        last_name: profile.name?.familyName,
                        encrypted_access_token: encryptedAccessToken,
                        encrypted_refresh_token: encryptedRefreshToken,
                        token_expiry: expiryDate
                    });
                } else {
                    // Update existing user with new tokens
                    user.encrypted_access_token = encryptedAccessToken;
                    user.encrypted_refresh_token = encryptedRefreshToken;
                    user.token_expiry = expiryDate;
                    
                    // Update profile information if available
                    if (profile.emails && profile.emails.length > 0) {
                        user.email = profile.emails[0].value;
                    }
                    if (profile.name?.givenName) {
                        user.first_name = profile.name.givenName;
                    }
                    if (profile.name?.familyName) {
                        user.last_name = profile.name.familyName;
                    }
                }
                
                await user.save();
                done(null, user);
            } catch (error) {
                console.error('Google auth error:', error);
                done(error, null);
            }
        }));
        
        // Configure Passport serialization
        passport.serializeUser((user, done) => {
            done(null, user.id);
        });
          
        passport.deserializeUser(async (id, done) => {
            try {
                const user = await User.findById(id);
                done(null, user);
            } catch (err) {
                done(err, null);
            }
        });
    },

    // Initialize Google authentication
    initiateGoogleAuth: passport.authenticate('google', { 
        scope: ['profile', 'email'],
        accessType: 'offline', // Request a refresh token
        prompt: 'consent' // Force consent screen to ensure we get a refresh token
    }),

    // Handle Google callback
    handleCallBack: (req, res, next) => {
        passport.authenticate('google', { session: false }, async (err, user) => {
            if (err) {
                console.error('Google authentication error:', err);
                return res.redirect(`${process.env.FRONTEND_URL}/login?error=auth_failed`);
            }
            
            if (!user) {
                return res.redirect(`${process.env.FRONTEND_URL}/login?error=auth_failed`);
            }
            
            try {
                // Generate JWT token
                const token = authService.generateToken(user);
                
                // Set auth cookies
                authService.setAuthCookies(res, token);
                
                if (req.session.googleCallback) {
                  const { callback, state } = req.session.googleCallback;
                  
                  // Clear the session data
                  delete req.session.googleCallback;
                  
                  // Redirect to the VS Code callback with token
                  return res.redirect(`${callback}?token=${encodeURIComponent(token)}&state=${encodeURIComponent(state)}`);
                }
                
                // Redirect to frontend with success
                return res.redirect(`${process.env.FRONTEND_URL}/auth/callback?success=true&token=${encodeURIComponent(token)}`);
            } catch (error) {
                console.error('Error during Google auth callback:', error);
                return res.redirect(`${process.env.FRONTEND_URL}/login?error=server_error`);
            }
        })(req, res, next);
    },

    // Get the current authenticated user
    getCurrentUser: (req, res) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Unauthorized' });
        }
        
        res.json({
            success: true,
            user: req.user.toDict()
        });
    },

    // Log out the user
    logout: (req, res) => {
        // Clear passport session
        req.logout((err) => {
            if (err) {
                console.error('Passport logout error:', err);
                return res.status(500).json({ error: 'Logout failed' });
            }
            
            // Clear auth cookies
            authService.clearAuthCookies(res);
            
            res.json({ 
                success: true,
                message: 'Logged out successfully' 
            });
        });
    },
    
    // Refresh Google access token
    refreshGoogleToken: async (userId) => {
        try {
            const user = await User.findById(userId);
            if (!user || !user.encrypted_refresh_token) {
                throw new Error("User not found or missing refresh token");
            }
            
            // Decrypt refresh token
            const refreshToken = authService.decryptToken(user.encrypted_refresh_token);
            
            // Load Google OAuth credentials
            let googleCredentials;
            try {
                googleCredentials = JSON.parse(fs.readFileSync('client.json', 'utf8'));
            } catch (error) {
                googleCredentials = {
                    web: {
                        client_id: process.env.GOOGLE_CLIENT_ID,
                        client_secret: process.env.GOOGLE_CLIENT_SECRET
                    }
                };
            }
            
            // Exchange refresh token for a new access token
            const response = await axios.post('https://oauth2.googleapis.com/token', {
                client_id: googleCredentials.web.client_id,
                client_secret: googleCredentials.web.client_secret,
                refresh_token: refreshToken,
                grant_type: 'refresh_token'
            });
            
            const tokenData = response.data;
            const newAccessToken = tokenData.access_token;
            const expiresIn = tokenData.expires_in || 3600; // Default to 1 hour
            
            // Encrypt the new access token
            const encryptedAccessToken = authService.encryptToken(newAccessToken);
            
            // Update token expiry
            const expiryDate = new Date();
            expiryDate.setSeconds(expiryDate.getSeconds() + expiresIn);
            
            // Update user record
            user.encrypted_access_token = encryptedAccessToken;
            user.token_expiry = expiryDate;
            await user.save();
            
            return {
                access_token: newAccessToken,
                expires_at: expiryDate
            };
        } catch (error) {
            console.error('Google token refresh error:', error.response?.data || error.message);
            throw new Error('Failed to refresh Google token');
        }
    },
    
    // Get a valid Google access token
    getValidGoogleToken: async (userId) => {
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
                const result = await GoogleController.refreshGoogleToken(userId);
                return result.access_token;
            } else {
                // Token is still valid
                return authService.decryptToken(user.encrypted_access_token);
            }
        } catch (error) {
            console.error("Error getting valid Google token:", error);
            throw new Error("Failed to get valid Google access token");
        }
    }
};

module.exports = GoogleController;