const ProjectFileData = require('../mongo_models/FileData.js'); 
const Project = require('../mongo_models/Project.js'); 

const fileDataController = {
    update: async (req, res) => {
        try {
            const { title, fileData } = req.body;
            console.log('Received file data update request:', title);
            
            if (!title) {
                return res.status(400).json({
                    success: false,
                    error: 'Project title is required'
                });
            }
            
            if (!fileData || typeof fileData !== 'object') {
                return res.status(400).json({
                    success: false,
                    error: 'Invalid fileData format'
                });
            }

            // Find project by title
            const project = await Project.findOne({ title: title });
            if (!project) {
                return res.status(404).json({
                    success: false,
                    error: `Project with title '${title}' not found`
                });
            }

            console.log('Found project:', project._id, 'for fileData:', Object.keys(fileData));

            // Update file data using the model
            const document = await ProjectFileData.updateFileData(project._id, fileData);
               
            // Extract file names from fileData object
            const fileNames = Object.keys(fileData);
            console.log('Files to add to project:', fileNames);
            
            // Update the Project's files array
            if (fileNames.length > 0) {
                // Get current files array (or initialize as empty array if it doesn't exist)
                const currentFiles = project.files || [];
                
                // Create a Set of current files for efficient lookup
                const currentFilesSet = new Set(currentFiles);
                
                // Add only new files (avoid duplicates)
                const newFiles = fileNames.filter(fileName => !currentFilesSet.has(fileName));
                
                if (newFiles.length > 0) {
                    // Add new files to the project's files array
                    project.files = [...currentFiles, ...newFiles];
                    await project.save();
                    console.log('Added new files to project:', newFiles);
                } else {
                    console.log('No new files to add - all files already exist in project');
                }
            }

            res.json({
                status: 200,
                success: true,
                message: 'File data updated successfully',
                projectId: document.projectId,
                updatedFiles: Object.keys(fileData),
                updatedAt: document.updatedAt
            });

        } catch (error) {
            console.error('Error updating file data:', error);
            res.status(500).json({
                success: false,
                error: error.message || 'Internal server error'
            });
        }
    },

    getProjectFileData: async (req, res) => {
        try {
            const { projectId } = req.params;
            
            if (!projectId) {
                return res.status(400).json({
                    success: false,
                    error: 'Project ID is required'
                });
            }

            // Verify project exists
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({
                    success: false,
                    error: `Project with ID '${projectId}' not found`
                });
            }

            const result = await ProjectFileData.getFileData(projectId);
            res.json({
                success: true,
                projectTitle: project.title,
                ...result
            });

        } catch (error) {
            console.error('Error getting file data:', error);
            res.status(500).json({
                success: false,
                error: error.message || 'Internal server error'
            });
        }
    },

    getFileData: async (req, res) => {
        try {
            console.log("Getting specific file data...");
            const { projectId } = req.params;
            const { fileName } = req.body;
            
            if (!projectId) {
                return res.status(400).json({
                    success: false,
                    error: 'Project ID is required'
                });
            }

            if (!fileName) {
                return res.status(400).json({
                    success: false,
                    error: 'File name is required'
                });
            }

            // Verify project exists
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({
                    success: false,
                    error: `Project with ID '${projectId}' not found. This feature is not available for this project.`
                });
            }

            console.log(`Looking for file '${fileName}' in project '${project.title}' (${projectId})`);

            // Check if file exists in project's files array
            const projectFiles = project.files || [];
            if (!projectFiles.includes(fileName)) {
                return res.status(404).json({
                    success: false,
                    error: `File '${fileName}' not found in project '${project.title}'. Available files: ${projectFiles.join(', ') || 'none'}`
                });
            }

            const fileData = await ProjectFileData.getSpecificFile(projectId, fileName);
            
            if (!fileData) {
                return res.status(404).json({
                    success: false,
                    error: `File '${fileName}' data not found in project '${project.title}'. This feature is not available for this project.`
                });
            }

            // Ensure we have code data
            if (!fileData.code) {
                return res.status(404).json({
                    success: false,
                    error: `File '${fileName}' exists but contains no code data. This feature is not available for this file.`
                });
            }
            
            console.log(`Successfully retrieved file data for '${fileName}'`);
            res.json({
                success: true,
                fileName,
                projectTitle: project.title,
                fileData: {
                    code: fileData.code,
                    ast: fileData.ast || null
                }
            });

        } catch (error) {
            console.error('Error getting specific file data:', error);
            
            // Provide user-friendly error messages
            let errorMessage = 'This feature is not available for this project';
            if (error.message.includes('Cast to ObjectId failed')) {
                errorMessage = 'Invalid project ID provided';
            } else if (error.message.includes('not found')) {
                errorMessage = error.message;
            }

            res.status(500).json({
                success: false,
                error: errorMessage
            });
        }
    },

    deleteFile: async (req, res) => {
        try {
            const { projectId, fileName } = req.params;
            
            if (!projectId) {
                return res.status(400).json({
                    success: false,
                    error: 'Project ID is required'
                });
            }

            if (!fileName) {
                return res.status(400).json({
                    success: false,
                    error: 'File name is required'
                });
            }

            // Verify project exists
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({
                    success: false,
                    error: `Project with ID '${projectId}' not found`
                });
            }

            // Check if file exists in project's files array
            const projectFiles = project.files || [];
            if (!projectFiles.includes(fileName)) {
                return res.status(404).json({
                    success: false,
                    error: `File '${fileName}' not found in project '${project.title}'`
                });
            }

            await ProjectFileData.deleteFile(projectId, fileName);
            
            // Remove file from project's files array
            project.files = projectFiles.filter(file => file !== fileName);
            await project.save();
            
            console.log(`Successfully deleted file '${fileName}' from project '${project.title}'`);
            res.json({
                success: true,
                message: `File '${fileName}' deleted successfully from project '${project.title}'`,
                fileName,
                projectTitle: project.title
            });

        } catch (error) {
            console.error('Error deleting file data:', error);
            res.status(500).json({
                success: false,
                error: error.message || 'Internal server error'
            });
        }
    },

    // New method to check if AST visualization is available for a project
    checkASTAvailability: async (req, res) => {
        try {
            const { projectId } = req.params;
            
            if (!projectId) {
                return res.status(400).json({
                    success: false,
                    error: 'Project ID is required'
                });
            }

            // Verify project exists
            const project = await Project.findById(projectId);
            if (!project) {
                return res.status(404).json({
                    success: false,
                    available: false,
                    error: `Project with ID '${projectId}' not found`
                });
            }

            // Check if project has any Python files
            const projectFiles = project.files || [];
            const pythonFiles = projectFiles.filter(file => 
                file.endsWith('.py') || file.endsWith('.python')
            );

            // Get file data to check which files have code
            const fileDataResult = await ProjectFileData.getFileData(projectId);
            const filesWithCode = [];
            
            if (fileDataResult.fileData) {
                for (const [fileName, data] of Object.entries(fileDataResult.fileData)) {
                    if (data.code && data.code.trim()) {
                        filesWithCode.push(fileName);
                    }
                }
            }

            res.json({
                success: true,
                available: filesWithCode.length > 0,
                projectTitle: project.title,
                totalFiles: projectFiles.length,
                pythonFiles: pythonFiles,
                filesWithCode: filesWithCode,
                message: filesWithCode.length > 0 
                    ? 'AST visualization is available for this project'
                    : 'No files with code found. AST visualization is not available for this project.'
            });

        } catch (error) {
            console.error('Error checking AST availability:', error);
            res.status(500).json({
                success: false,
                available: false,
                error: 'Unable to check AST availability for this project'
            });
        }
    }
};

module.exports = fileDataController;