

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
    required: false
  },
  ast: {
    type: String,
    required: false
  }
}, { _id: false }); // Disable _id for subdocuments

// Main schema for storing project file data
const projectFileDataSchema = new mongoose.Schema({
  projectId: {
    type: String,
    required: true,
    index: true
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

// Static method to upsert file data
projectFileDataSchema.statics.updateFileData = async function(projectId, fileData) {
  try {
    // Prepare the update object with encoded file data
    const updateObj = { projectId };
    
    // Process each file in fileData
    Object.keys(fileData).forEach(fileName => {
      const file = fileData[fileName];
      const filteredFile = {};
      
      if (file.code !== undefined) {
        filteredFile.code = file.code;
      }
      
      if (file.ast !== undefined) {
        filteredFile.ast = file.ast;
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
        setDefaultsOnInsert: true       // Apply schema defaults on insert
      }
    );
    
    return document;
    
  } catch (error) {
    throw new Error(`Failed to update file data: ${error.message}`);
  }
};


// Static method to get file data for a project
projectFileDataSchema.statics.getFileData = async function(projectId) {
  try {
    const document = await this.findOne({ projectId }).lean();
    
    if (!document) {
      return { fileData: {} };
    }
    
    // Convert Map to Object and decode keys for easier JSON serialization
    const fileDataObj = {};
    if (document.fileData) {
      for (const [encodedFileName, fileInfo] of Object.entries(document.fileData)) {
        const decodedFileName = decodeKey(encodedFileName);
        fileDataObj[decodedFileName] = fileInfo;
      }
    }
    
    return {
      projectId: document.projectId,
      fileData: fileDataObj,
      updatedAt: document.updatedAt,
      createdAt: document.createdAt
    };
    
  } catch (error) {
    throw new Error(`Failed to get file data: ${error.message}`);
  }
};

// Static method to get specific file data
projectFileDataSchema.statics.getSpecificFile = async function(projectId, fileName) {
  try {
    const document = await this.findOne({ projectId });
    if (!document) {
      return null;
    }
    
    // Try to find the file using encoded key first
    const encodedFileName = encodeKey(fileName);
    let fileData = document.fileData.get(encodedFileName);
    
    // If not found with encoded key, try original key (for backwards compatibility)
    if (!fileData) {
      fileData = document.fileData.get(fileName);
    }
    
    return fileData || null;
    
  } catch (error) {
    throw new Error(`Failed to get file data: ${error.message}`);
  }
};

// Static method to delete file data
projectFileDataSchema.statics.deleteFile = async function(projectId, fileName) {
  try {
    const document = await this.findOne({ projectId });
    
    if (!document) {
      throw new Error('Project not found');
    }
    
    const encodedFileName = encodeKey(fileName);
    
    // Try to delete both encoded and original key versions (for backwards compatibility)
    let deleted = document.fileData.delete(encodedFileName);
    if (!deleted) {
      deleted = document.fileData.delete(fileName);
    }
    
    if (deleted) {
      await document.save();
    }
    
    return true;
    
  } catch (error) {
    throw new Error(`Failed to delete file: ${error.message}`);
  }
};

// Create and export the model
const ProjectFileData = mongoose.model('ProjectFileData', projectFileDataSchema);

module.exports = ProjectFileData;