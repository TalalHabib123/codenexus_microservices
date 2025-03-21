const bcrypt = require('bcrypt');
const User = require('../mongo_models/User.js');
const Project = require('../mongo_models/Project.js');
const Log = require('../mongo_models/logs.js');

const profileController = {
  // Get user profile information
  getProfile: async (req, res) => {
    try {
      const userId = req.user._id;
      const user = await User.findById(userId);
      
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      // Return user data without sensitive information
      const userData = {
        _id: user._id,
        username: user.username,
        email: user.email,
        first_name: user.first_name,
        last_name: user.last_name,
        github_id: user.github_id ? true : false,
        google_id: user.google_id ? true : false,
        register_date: user.register_date
      };
      
      return res.status(200).json(userData);
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  },
  
  // Update user profile information
  updateProfile: async (req, res) => {
    try {
      const userId = req.user._id;
      const { username, email, first_name, last_name } = req.body;
      
      // Check if username or email is already in use by another user
      if (username) {
        const existingUsername = await User.findOne({ username, _id: { $ne: userId } });
        if (existingUsername) {
          return res.status(400).json({ message: 'Username is already taken' });
        }
      }
      
      if (email) {
        const existingEmail = await User.findOne({ email, _id: { $ne: userId } });
        if (existingEmail) {
          return res.status(400).json({ message: 'Email is already in use' });
        }
      }
      
      // Update user profile
      const updatedUser = await User.findByIdAndUpdate(
        userId,
        { 
          $set: {
            ...(username && { username }),
            ...(email && { email }),
            ...(first_name && { first_name }),
            ...(last_name && { last_name })
          }
        },
        { new: true }
      );
      
      if (!updatedUser) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      // Return updated user data without sensitive information
      const userData = {
        _id: updatedUser._id,
        username: updatedUser.username,
        email: updatedUser.email,
        first_name: updatedUser.first_name,
        last_name: updatedUser.last_name,
        github_id: updatedUser.github_id ? true : false,
        google_id: updatedUser.google_id ? true : false,
        register_date: updatedUser.register_date
      };
      
      return res.status(200).json({ message: 'Profile updated successfully', user: userData });
    } catch (error) {
      console.error('Error updating user profile:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  },
  
  // Change user password
  changePassword: async (req, res) => {
    try {
      const userId = req.user._id;
      const { currentPassword, newPassword } = req.body;
      
      // Make sure new password is provided
      if (!newPassword || newPassword.length < 6) {
        return res.status(400).json({ message: 'New password must be at least 6 characters long' });
      }
      
      const user = await User.findById(userId);
      
      if (!user) {
        return res.status(404).json({ message: 'User not found' });
      }
      
      // If user has a password (not OAuth-only), verify current password
      if (user.password) {
        const isMatch = await bcrypt.compare(currentPassword, user.password);
        if (!isMatch) {
          return res.status(400).json({ message: 'Current password is incorrect' });
        }
      }
      
      // Hash the new password
      const salt = await bcrypt.genSalt(10);
      const hashedPassword = await bcrypt.hash(newPassword, salt);
      
      // Update user password
      user.password = hashedPassword;
      await user.save();
      
      return res.status(200).json({ message: 'Password updated successfully' });
    } catch (error) {
      console.error('Error changing password:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  },
  
  // Get user's projects
  getUserProjects: async (req, res) => {
    try {
      const userId = req.user._id;
      
      const projects = await Project.find({ user: userId });
      
      return res.status(200).json(projects);
    } catch (error) {
      console.error('Error fetching user projects:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  },
  
  // Get user's recent activity
  getUserActivity: async (req, res) => {
    try {
      const userId = req.user._id;
      const limit = parseInt(req.query.limit) || 10;
      
      const projects = await Project.find({ user: userId });
      const projectIds = projects.map(project => project._id);
      
      const logs = await Log.find({ projectId: { $in: projectIds } })
        .sort({ timestamp: -1 })
        .limit(limit);
      
      return res.status(200).json(logs);
    } catch (error) {
      console.error('Error fetching user activity:', error);
      return res.status(500).json({ error: 'Internal server error' });
    }
  }
};

module.exports = profileController;