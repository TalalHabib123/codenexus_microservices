const bcrypt = require('bcrypt');
const User = require('../models/User');

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
      
      return res.json({
        message: "Login successful",
        success: true,
        user: user.toDict()
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
        encrypted_access_token: userData.encrypted_access_token,
        first_name: userData.first_name,
        last_name: userData.last_name
      });
      
      await newUser.save();
      
      return res.json({
        message: "User created",
        success: true,
        user: newUser.toDict()
      });
    } catch (error) {
      console.error("Signup error:", error);
      return res.status(400).json({ error: "Failed to create user" });
    }
  }
};

module.exports = authController;