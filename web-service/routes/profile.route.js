const express = require('express');
const profileController = require('../controller/profile.controller.js');
const router = express.Router();
const { requireAuth } = require('../middleware/auth.middleware.js');

// Get user profile information
router.get('/', requireAuth, profileController.getProfile);

// Update user profile information
router.put('/update', requireAuth, profileController.updateProfile);

// Change user password
router.put('/change-password', requireAuth, profileController.changePassword);

// Get user's projects
router.get('/projects', requireAuth, profileController.getUserProjects);

// Get user's recent activity
router.get('/activity', requireAuth, profileController.getUserActivity);

module.exports = router;