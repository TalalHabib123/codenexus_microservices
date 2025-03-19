const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const User = require('../mongo_models/User');

// Make sure to add JWT_SECRET to your .env file
const JWT_SECRET = process.env.JWT_SECRET || 'your-jwt-secret-key';
const TOKEN_EXPIRY = '7d'; // 7 days

// Set up encryption
const ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
if (!ENCRYPTION_KEY) {
  throw new Error("Missing ENCRYPTION_KEY in environment variables");
}

// Create cipher for encryption
const algorithm = "aes-256-cbc";
const key = crypto.scryptSync(ENCRYPTION_KEY, "salt", 32);

// Token encryption/decryption
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

const authService = {
  /**
   * Generate a JWT token for a user
   * @param {Object} user - User object to generate token for
   * @returns {string} JWT token
   */
  generateToken: (user) => {
    return jwt.sign(
      { 
        id: user._id, 
        username: user.username,
        email: user.email 
      },
      JWT_SECRET,
      { expiresIn: TOKEN_EXPIRY }
    );
  },

  /**
   * Verify a JWT token
   * @param {string} token - JWT token to verify
   * @returns {Object|null} Decoded token payload or null if invalid
   */
  verifyToken: (token) => {
    try {
      return jwt.verify(token, JWT_SECRET);
    } catch (error) {
      return null;
    }
  },

  /**
   * Encrypt an OAuth access token for storage
   * @param {string} token - Token to encrypt
   * @returns {string} Encrypted token
   */
  encryptToken,

  /**
   * Decrypt an OAuth access token
   * @param {string} encryptedToken - Encrypted token
   * @returns {string} Decrypted token
   */
  decryptToken,

  /**
   * Set authentication cookies
   * @param {Object} res - Express response object
   * @param {string} token - JWT token
   */
  setAuthCookies: (res, token) => {
    // Set HTTP-only cookie with the JWT token
    res.cookie('auth_token', token, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      sameSite: 'lax'
    });

    // Set a non-HTTP-only cookie to signal authentication state to frontend
    res.cookie('is_authenticated', 'true', {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      maxAge: 7 * 24 * 60 * 60 * 1000, // 7 days
      sameSite: 'lax'
    });
  },

  /**
   * Clear authentication cookies
   * @param {Object} res - Express response object
   */
  clearAuthCookies: (res) => {
    res.clearCookie('auth_token');
    res.clearCookie('is_authenticated');
  },

  /**
   * Get user from token
   * @param {string} token - JWT token
   * @returns {Promise<Object|null>} User document or null
   */
  getUserFromToken: async (token) => {
    const decoded = authService.verifyToken(token);
    if (!decoded) return null;
    
    try {
      return await User.findById(decoded.id);
    } catch (error) {
      return null;
    }
  }
};

module.exports = authService;