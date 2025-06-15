// Express Server Implementation with MongoDB

const express = require('express');
const fileDataController = require('../controller/fileData.controller');
const router = express.Router();


// Update file data endpoint
router.post('/update', fileDataController.update);

// Get all file data for a project
router.get('/:projectId', fileDataController.getProjectFileData);

// Get specific file data
router.get('/:projectId/:fileName', fileDataController.getFileData);

// Delete specific file data
router.delete('/:projectId/:fileName', fileDataController.deleteFile);

// // Delete all file data for a project
// app.delete('/file-data/:projectId', async (req, res) => {
//   try {
//     const { projectId } = req.params;
    
//     await ProjectFileData.deleteOne({ projectId });
    
//     res.json({
//       success: true,
//       message: 'All file data deleted successfully for project',
//       projectId
//     });

//   } catch (error) {
//     console.error('Error deleting project file data:', error);
//     res.status(500).json({
//       success: false,
//       error: error.message || 'Internal server error'
//     });
//   }
// });


module.exports = router;