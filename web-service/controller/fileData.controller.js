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
                error: 'Project ID is required'
            });
            }
            
            if (!fileData || typeof fileData !== 'object') {
            return res.status(400).json({
                success: false,
                error: 'Invalid fileData format'
            });
            }
            const project = await Project.findOne({title: title})
            // Update file data using the model
            console.log(project, fileData );

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
            const result = await ProjectFileData.getFileData(projectId);
            res.json({
            success: true,
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
            console.log("hello")
            const { projectId } = req.params;
            const { fileName } = req.body;
            const fileData = await ProjectFileData.getSpecificFile(projectId, fileName);
            
            if (!fileData) {
            return res.status(404).json({
                success: false,
                error: 'File not found'
            });
            }
            
            res.json({
            success: true,
            fileName,
            fileData
            });

        } catch (error) {
            console.error('Error getting specific file data:', error);
            res.status(500).json({
            success: false,
            error: error.message || 'Internal server error'
            });
        }
    },

    deleteFile: async (req, res) => {
  try {
    const { projectId, fileName } = req.params;
    
    await ProjectFileData.deleteFile(projectId, fileName);
    
    res.json({
      success: true,
      message: 'File deleted successfully',
      fileName
    });

  } catch (error) {
    console.error('Error deleting file data:', error);
    res.status(500).json({
      success: false,
      error: error.message || 'Internal server error'
    });
  }
},
};


module.exports = fileDataController;