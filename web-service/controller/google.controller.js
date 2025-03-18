const passport = require('passport');
const GoogleStrategy = require('passport-google-oauth20').Strategy;
const fs = require('fs');
const User = require('../mongo_models/User');

const GoogleController = {
    configureGoogleStrategy: () => {
        const googleCredentials = JSON.parse(fs.readFileSync('client.json', 'utf8'));
        passport.use(new GoogleStrategy({
            clientID: googleCredentials.web.client_id,
            clientSecret: googleCredentials.web.client_secret,
            callbackURL: "/auth/google/callback",
            passReqToCallback: true
        },
        async (req, accessToken, refreshToken, profile, done) => {
            try {
                // Check if user already exists in the database
                let user = await User.findOne({ google_id: profile.id });
                if (!user) {
                    // If not, create a new user
                    user = new User({
                        username: profile.displayName,
                        email: profile.emails[0].value,
                        googleId: profile.id,
                        password: null // Password is not needed for Google login
                    });
                }
                user.accessToken = accessToken; // Store the access token
                await user.save(); // Save the user to the database
                done(null, user);
            } catch (error) {
                done(error, null);
            }
        }));        
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

    initiateGoogleAuth: passport.authenticate('google', { 
        scope: ['profile', 'email'] 
      }),

    handleCallBack: (req, res, next) => {
        passport.authenticate('google', { session: false }, (err, user) => {
            if (err) {
              return res.status(500).json({ error: 'Authentication failed' });
            }
            
            if (!user) {
              return res.status(401).json({ error: 'Authentication failed' });
            }
            
            // Generate JWT token
            const token = jwt.sign(
              { id: user._id, email: user.email },
              process.env.JWT_SECRET,
              { expiresIn: '7d' }
            );
            res.redirect(`${process.env.FRONTEND_URL}/auth/callback?token=${token}`);
        })(req, res, next);
    },

    getCurrentUser: (req, res) => {
        if (!req.user) {
            return res.status(401).json({ error: 'Unauthorized' });
        }
        res.json({
            message: 'User retrieved successfully',
            user: req.user.toDict()
        });
    },

    logout: (req, res) => {
        req.logout((err) => {
          if (err) {
            return res.status(500).json({ error: 'Logout failed' });
          }
          res.json({ message: 'Logged out successfully' });
        });
      }
}


module.exports = GoogleController;