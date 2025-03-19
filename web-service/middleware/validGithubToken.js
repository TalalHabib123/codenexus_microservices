// auth middleware.js
const User = require('../mongo_models/User');
const GithubAuthController = require('../controllers/GithubAuthController');

const ensureValidGithubToken = async (req, res, next) => {
  try {
    if (!req.user || !req.user._id) {
      return res.status(401).json({ error: "Unauthorized, please log in" });
    }
    
    // Get a valid token
    const accessToken = await GithubAuthController.getValidAccessToken(req.user._id);
    
    // Attach the token to the request for use in route handlers
    req.githubToken = accessToken;
    next();
  } catch (error) {
    console.error("Authentication middleware error:", error);
    return res.status(401).json({ error: "Session expired, please log in again" });
  }
};

module.exports = { ensureValidGithubToken };