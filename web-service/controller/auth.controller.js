const bcrypt = require('bcrypt');
const User = require('../mongo_models/User');
const authService = require('../services/auth.service');

const authController = {
  hashPassword: async (password) => {
    const saltRounds = 10;
    const salt = await bcrypt.genSalt(saltRounds);
    const hashedPassword = await bcrypt.hash(password, salt);
    return hashedPassword;
  },
  
  verifyPassword: async (plainPassword, hashedPassword) => {
    return bcrypt.compare(plainPassword, hashedPassword);
  },
  
  login: async (req, res) => {
    try {
      const { username, password } = req.body;
      
      // Find the user
      const user = await User.findOne({ username });
      if (!user) {
        return res.status(400).json({ error: "User not found" });
      }
      
      // Verify password
      const isPasswordValid = await authController.verifyPassword(password, user.password);
      if (!isPasswordValid) {
        return res.status(400).json({ error: "Invalid password" });
      }
      
      // Generate JWT token
      const token = authService.generateToken(user);
      console.log("hdfssdfs")
      // Set auth cookies
      authService.setAuthCookies(res, token);
      
      return res.json({
        message: "Login successful",
        success: true,
        user: user.toDict(),
        token // Include token in response for API usage
      });
    } catch (error) {
      console.error("Login error:", error);
      return res.status(400).json({ error: "Failed to login" });
    }
  },
  
  signup: async (req, res) => {
    try {
      const userData = req.body;
      
      // Check if user already exists
      const existingUser = await User.findOne({ username: userData.username });
      if (existingUser) {
        return res.status(400).json({ error: "User already exists" });
      }
      
      // Hash the password
      const hashedPassword = await authController.hashPassword(userData.password);
      
      // Create new user
      const newUser = new User({
        username: userData.username,
        email: userData.email,
        password: hashedPassword,
        first_name: userData.first_name,
        last_name: userData.last_name
      });
      
      await newUser.save();
      
      // Generate JWT token
      const token = authService.generateToken(newUser);
      
      // Set auth cookies
      authService.setAuthCookies(res, token);
      
      return res.json({
        message: "User created",
        success: true,
        user: newUser.toDict(),
        token // Include token in response for API usage
      });
    } catch (error) {
      console.error("Signup error:", error);
      return res.status(400).json({ error: "Failed to create user" });
    }
  },
  
  logout: async (req, res) => {
    try {
      // Clear auth cookies
      authService.clearAuthCookies(res);
      
      return res.json({
        message: "Logout successful",
        success: true
      });
    } catch (error) {
      console.error("Logout error:", error);
      return res.status(500).json({ error: "Failed to logout" });
    }
  },
  
  getCurrentUser: async (req, res) => {
    try {
      // User is attached to request by auth middleware
      if (!req.user) {
        return res.status(401).json({ error: "Not authenticated" });
      }
      
      return res.json({
        success: true,
        user: req.user.toDict()
      });
    } catch (error) {
      console.error("Get current user error:", error);
      return res.status(500).json({ error: "Failed to get current user" });
    }
  }
};

module.exports = authController;