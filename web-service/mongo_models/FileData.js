const mongoose = require('mongoose');

// Helper functions to encode/decode keys
const encodeKey = (key) => key.replace(/\./g, '___DOT___');
const decodeKey = (key) => key.replace(/___DOT___/g, '.');

const encodeFileData = (fileData) => {
  const encoded = {};
  for (const [key, value] of Object.entries(fileData)) {
    encoded[encodeKey(key)] = value;
  }
  return encoded;
};

const decodeFileData = (encodedData) => {
  const decoded = {};
  for (const [key, value] of Object.entries(encodedData)) {
    decoded[decodeKey(key)] = value;
  }
  return decoded;
};

// Schema for individual file data
const fileDataSchema = new mongoose.Schema({
  code: {
    type: String,
    required: false,
    default: null
  },
  ast: {
    type: String,
    required: false,
    default: null
  },
  language: {
    type: String,
    required: false,
    default: 'python'
  },
  lastModified: {
    type: Date,
    default: Date.now
  }
}, { _id: false }); // Disable _id for subdocuments

// Main schema for storing project file data
const projectFileDataSchema = new mongoose.Schema({
  projectId: {
    type: String,
    required: true,
    index: true,
    validate: {
      validator: function(v) {
        return mongoose.Types.ObjectId.isValid(v);
      },
      message: 'Invalid project ID format'
    }
  },
  fileData: {
    type: Map,
    of: fileDataSchema,
    default: new Map()
  },
  updatedAt: {
    type: Date,
    default: Date.now
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

// Update the updatedAt field on save
projectFileDataSchema.pre('save', function(next) {
  this.updatedAt = new Date();
  next();
});

// Create indexes for better performance
projectFileDataSchema.index({ projectId: 1 });
projectFileDataSchema.index({ updatedAt: -1 });

// Static method to upsert file data with enhanced error handling
projectFileDataSchema.statics.updateFileData = async function(projectId, fileData) {
  try {
    // Validate inputs
    if (!projectId) {
      throw new Error('Project ID is required');
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      throw new Error('Invalid project ID format');
    }

    if (!fileData || typeof fileData !== 'object') {
      throw new Error('Invalid file data format');
    }

    if (Object.keys(fileData).length === 0) {
      throw new Error('No file data provided');
    }

    console.log(`Updating file data for project ${projectId}:`, Object.keys(fileData));

    // Prepare the update object with encoded file data
    const updateObj = { projectId };
    
    // Process each file in fileData
    Object.keys(fileData).forEach(fileName => {
      if (!fileName || typeof fileName !== 'string') {
        throw new Error('Invalid file name provided');
      }

      const file = fileData[fileName];
      if (!file || typeof file !== 'object') {
        throw new Error(`Invalid data for file: ${fileName}`);
      }

      const filteredFile = {
        lastModified: new Date()
      };
      
      if (file.code !== undefined) {
        if (typeof file.code !== 'string') {
          throw new Error(`Invalid code format for file: ${fileName}`);
        }
        filteredFile.code = file.code;
      }
      
      if (file.ast !== undefined) {
        if (typeof file.ast !== 'string') {
          throw new Error(`Invalid AST format for file: ${fileName}`);
        }
        
        // Validate AST is valid JSON if provided
        if (file.ast.trim()) {
          try {
            JSON.parse(file.ast);
          } catch (astError) {
            console.warn(`Invalid AST JSON for file ${fileName}, storing as-is:`, astError.message);
          }
        }
        filteredFile.ast = file.ast;
      }

      if (file.language !== undefined) {
        if (typeof file.language !== 'string') {
          throw new Error(`Invalid language format for file: ${fileName}`);
        }
        filteredFile.language = file.language;
      }
      
      // Use encoded key for storage and set in the update object
      const encodedFileName = encodeKey(fileName);
      updateObj[`fileData.${encodedFileName}`] = filteredFile;
    });
    
    // Use findOneAndUpdate with upsert
    const document = await this.findOneAndUpdate(
      { projectId },                    // Query to find the document
      { $set: updateObj },              // Fields to set/overwrite
      { 
        upsert: true,                   // Create if not exists
        new: true,                      // Return updated document
        setDefaultsOnInsert: true,      // Apply schema defaults on insert
        runValidators: true             // Run schema validators
      }
    );
    
    console.log(`Successfully updated file data for project ${projectId}`);
    return document;
    
  } catch (error) {
    console.error('Failed to update file data:', error);
    throw new Error(`Failed to update file data: ${error.message}`);
  }
};

// Static method to get file data for a project with enhanced error handling
projectFileDataSchema.statics.getFileData = async function(projectId) {
  try {
    if (!projectId) {
      throw new Error('Project ID is required');
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      throw new Error('Invalid project ID format');
    }

    console.log(`Retrieving file data for project: ${projectId}`);

    const document = await this.findOne({ projectId }).lean();
    
    if (!document) {
      console.log(`No file data found for project: ${projectId}`);
      return { fileData: {} };
    }
    
    // Convert Map to Object and decode keys for easier JSON serialization
    const fileDataObj = {};
    if (document.fileData) {
      for (const [encodedFileName, fileInfo] of Object.entries(document.fileData)) {
        const decodedFileName = decodeKey(encodedFileName);
        
        // Ensure file info has expected structure
        const sanitizedFileInfo = {
          code: fileInfo.code || null,
          ast: fileInfo.ast || null,
          language: fileInfo.language || 'python',
          lastModified: fileInfo.lastModified || new Date()
        };
        
        fileDataObj[decodedFileName] = sanitizedFileInfo;
      }
    }
    
    console.log(`Found ${Object.keys(fileDataObj).length} files for project ${projectId}`);
    
    return {
      projectId: document.projectId,
      fileData: fileDataObj,
      updatedAt: document.updatedAt,
      createdAt: document.createdAt
    };
    
  } catch (error) {
    console.error('Failed to get file data:', error);
    throw new Error(`Failed to get file data: ${error.message}`);
  }
};

// Static method to get specific file data with enhanced error handling
projectFileDataSchema.statics.getSpecificFile = async function(projectId, fileName) {
  try {
    if (!projectId) {
      throw new Error('Project ID is required');
    }

    if (!fileName) {
      throw new Error('File name is required');
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      throw new Error('Invalid project ID format');
    }

    if (typeof fileName !== 'string') {
      throw new Error('File name must be a string');
    }

    console.log(`Retrieving specific file '${fileName}' for project: ${projectId}`);

    const document = await this.findOne({ projectId });
    if (!document) {
      console.log(`No file data document found for project: ${projectId}`);
      return null;
    }
    
    // Try to find the file using encoded key first
    const encodedFileName = encodeKey(fileName);
    let fileData = document.fileData.get(encodedFileName);
    
    // If not found with encoded key, try original key (for backwards compatibility)
    if (!fileData) {
      fileData = document.fileData.get(fileName);
      console.log(`File '${fileName}' not found with encoded key, tried original key:`, !!fileData);
    }

    if (!fileData) {
      console.log(`File '${fileName}' not found in project ${projectId}`);
      return null;
    }

    // Ensure file data has expected structure
    const sanitizedFileData = {
      code: fileData.code || null,
      ast: fileData.ast || null,
      language: fileData.language || 'python',
      lastModified: fileData.lastModified || new Date()
    };

    console.log(`Successfully retrieved file '${fileName}' from project ${projectId}`);
    return sanitizedFileData;
    
  } catch (error) {
    console.error('Failed to get specific file data:', error);
    throw new Error(`Failed to get file data: ${error.message}`);
  }
};

// Static method to delete file data with enhanced error handling
projectFileDataSchema.statics.deleteFile = async function(projectId, fileName) {
  try {
    if (!projectId) {
      throw new Error('Project ID is required');
    }

    if (!fileName) {
      throw new Error('File name is required');
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      throw new Error('Invalid project ID format');
    }

    if (typeof fileName !== 'string') {
      throw new Error('File name must be a string');
    }

    console.log(`Deleting file '${fileName}' from project: ${projectId}`);

    const document = await this.findOne({ projectId });
    
    if (!document) {
      throw new Error(`Project with ID '${projectId}' not found`);
    }
    
    const encodedFileName = encodeKey(fileName);
    
    // Try to delete both encoded and original key versions (for backwards compatibility)
    let deleted = document.fileData.delete(encodedFileName);
    if (!deleted) {
      deleted = document.fileData.delete(fileName);
    }
    
    if (deleted) {
      await document.save();
      console.log(`Successfully deleted file '${fileName}' from project ${projectId}`);
    } else {
      console.log(`File '${fileName}' not found in project ${projectId}, nothing to delete`);
    }
    
    return deleted;
    
  } catch (error) {
    console.error('Failed to delete file:', error);
    throw new Error(`Failed to delete file: ${error.message}`);
  }
};

// Static method to check if a file exists in a project
projectFileDataSchema.statics.fileExists = async function(projectId, fileName) {
  try {
    if (!projectId || !fileName) {
      return false;
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      return false;
    }

    const document = await this.findOne({ projectId }).lean();
    if (!document || !document.fileData) {
      return false;
    }

    const encodedFileName = encodeKey(fileName);
    return document.fileData.hasOwnProperty(encodedFileName) || 
           document.fileData.hasOwnProperty(fileName);
    
  } catch (error) {
    console.error('Error checking if file exists:', error);
    return false;
  }
};

// Static method to get file statistics for a project
projectFileDataSchema.statics.getProjectStats = async function(projectId) {
  try {
    if (!projectId) {
      throw new Error('Project ID is required');
    }

    if (!mongoose.Types.ObjectId.isValid(projectId)) {
      throw new Error('Invalid project ID format');
    }

    const document = await this.findOne({ projectId }).lean();
    if (!document || !document.fileData) {
      return {
        totalFiles: 0,
        filesWithCode: 0,
        filesWithAST: 0,
        lastUpdated: null
      };
    }

    let filesWithCode = 0;
    let filesWithAST = 0;
    const totalFiles = Object.keys(document.fileData).length;

    for (const fileInfo of Object.values(document.fileData)) {
      if (fileInfo.code && fileInfo.code.trim()) {
        filesWithCode++;
      }
      if (fileInfo.ast && fileInfo.ast.trim()) {
        filesWithAST++;
      }
    }

    return {
      totalFiles,
      filesWithCode,
      filesWithAST,
      lastUpdated: document.updatedAt
    };

  } catch (error) {
    console.error('Failed to get project stats:', error);
    throw new Error(`Failed to get project stats: ${error.message}`);
  }
};

// Create and export the model
const ProjectFileData = mongoose.model('ProjectFileData', projectFileDataSchema);

module.exports = ProjectFileData;