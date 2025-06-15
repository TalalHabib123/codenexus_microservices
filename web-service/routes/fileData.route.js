// Express Server Implementation with MongoDB

const express = require('express');
const fileDataController = require('../controller/fileData.controller');
const router = express.Router();


// Update file data endpoint
router.post('/update', fileDataController.update);
router.post('/:projectId/file', fileDataController.getFileData);

// Get all file data for a project
router.get('/:projectId', fileDataController.getProjectFileData);


module.exports = router;