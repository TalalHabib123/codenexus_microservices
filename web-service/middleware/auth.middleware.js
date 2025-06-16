const authService = require('../services/auth.service');

/**
 * Middleware to verify if the user is authenticated
 */
const requireAuth = async (req, res, next) => {
  try {
    // Check for token in cookies
    const token = req.cookies.auth_token;
    
    // If no token, check Authorization header (for API usage)
    const authHeader = req.headers.authorization;
    const bearerToken = authHeader && authHeader.startsWith('Bearer ') 
      ? authHeader.substring(7) 
      : null;
    
    // Use either cookie token or bearer token
    const authToken = token || bearerToken;
    
    if (!authToken) {
      return res.status(401).json({ error: 'Authentication required' });
    }
    
    // Verify token
    const user = await authService.getUserFromToken(authToken);
    if (!user) {
      return res.status(401).json({ error: 'Invalid or expired token' });
    }
    
    // Attach user to request object
    req.user = user;
    next();
  } catch (error) {
    console.error('Auth middleware error:', error);
    res.status(500).json({ error: 'Authentication failed' });
  }
};

const vscodeAuth = async(req, res, next) => {
   const token = req.headers.authorization?.split(' ')[1];
   console.log('Token:', token);
   console.log('Headers:', req.headers);
   if (!token) {
      return res.status(401).json({ error: 'Authentication required' });
   }
    try {
        const user = await authService.getUserFromToken(token);
        if (!user) {
          return res.status(401).json({ error: 'Invalid or expired token' });
        }
        req.user = user;
        console.log('Authenticated user:', user);
        next();
    } catch (error) {
        console.error('Auth middleware error:', error);
        res.status(500).json({ error: 'Authentication failed' });
    }
};

module.exports = { requireAuth, vscodeAuth };