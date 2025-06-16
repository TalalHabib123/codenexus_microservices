const express = require('express');
const router = express.Router();
const fileDataController = require('../controller/fileData.controller');

// Route to update file data for a project
// PUT /api/file-data/update
router.put('/update', fileDataController.update);

// Route to get all file data for a project
// GET /api/file-data/:projectId
router.get('/:projectId', fileDataController.getProjectFileData);

// Route to get specific file data
// POST /api/file-data/:projectId/file
router.post('/:projectId/file', fileDataController.getFileData);

// Route to delete a specific file
// DELETE /api/file-data/:projectId/file/:fileName
router.delete('/:projectId/file/:fileName', fileDataController.deleteFile);

// Route to check AST visualization availability for a project
// GET /api/file-data/:projectId/ast-availability
router.get('/:projectId/ast-availability', fileDataController.checkASTAvailability);

// Example usage routes that might be helpful for debugging

// Route to get project statistics
// GET /api/file-data/:projectId/stats
router.get('/:projectId/stats', async (req, res) => {
    try {
        const { projectId } = req.params;
        const ProjectFileData = require('../mongo_models/FileData.js');
        
        const stats = await ProjectFileData.getProjectStats(projectId);
        
        res.json({
            success: true,
            projectId,
            stats
        });
    } catch (error) {
        console.error('Error getting project stats:', error);
        res.status(500).json({
            success: false,
            error: error.message || 'Failed to get project statistics'
        });
    }
});

// Route to check if a specific file exists
// GET /api/file-data/:projectId/exists/:fileName
router.get('/:projectId/exists/:fileName', async (req, res) => {
    try {
        const { projectId, fileName } = req.params;
        const ProjectFileData = require('../mongo_models/FileData.js');
        
        const exists = await ProjectFileData.fileExists(projectId, fileName);
        
        res.json({
            success: true,
            projectId,
            fileName,
            exists
        });
    } catch (error) {
        console.error('Error checking file existence:', error);
        res.status(500).json({
            success: false,
            error: error.message || 'Failed to check file existence'
        });
    }
});

// Route to validate project and file for AST visualization
// POST /api/file-data/validate-ast-request
router.post('/validate-ast-request', async (req, res) => {
    try {
        const { projectId, fileName } = req.body;
        
        if (!projectId || !fileName) {
            return res.status(400).json({
                success: false,
                valid: false,
                error: 'Project ID and file name are required'
            });
        }

        const Project = require('../mongo_models/Project.js');
        const ProjectFileData = require('../mongo_models/FileData.js');
        
        // Check if project exists
        const project = await Project.findById(projectId);
        if (!project) {
            return res.status(404).json({
                success: false,
                valid: false,
                error: 'Project not found. This feature is not available for this project.'
            });
        }

        // Check if file exists in project
        const projectFiles = project.files || [];
        if (!projectFiles.includes(fileName)) {
            return res.status(404).json({
                success: false,
                valid: false,
                error: `File '${fileName}' not found in project. Available files: ${projectFiles.join(', ') || 'none'}`
            });
        }

        // Check if file has code data
        const fileData = await ProjectFileData.getSpecificFile(projectId, fileName);
        if (!fileData || !fileData.code || !fileData.code.trim()) {
            return res.status(404).json({
                success: false,
                valid: false,
                error: `File '${fileName}' exists but contains no code. This feature is not available for this file.`
            });
        }

        res.json({
            success: true,
            valid: true,
            projectTitle: project.title,
            fileName,
            hasCode: !!fileData.code,
            hasAST: !!fileData.ast,
            message: 'File is ready for AST visualization'
        });

    } catch (error) {
        console.error('Error validating AST request:', error);
        res.status(500).json({
            success: false,
            valid: false,
            error: 'This feature is not available for this project'
        });
    }
});

module.exports = router;