/**
 * Utility functions for processing scan data
 */

const Scan = require('../mongo_models/Scan');
const Project = require('../mongo_models/Project');

/**
 * Counts code smells in a detection data object
 * @param {Object} detectData - Detection data object
 * @returns {Number} - Total count of code smells
 */
const countCodeSmellsInDetection = (detectData) => {
  let totalIssues = 0;
  
  // If detection data is null or not an object
  if (!detectData || typeof detectData !== 'object') {
    return 0;
  }
  
  try {
    // The data may have file paths or contain properties like magic_numbers, duplicated_code directly
    // First check if we're dealing with file paths or direct issue types
    
    // Case 1: Check for direct issue types
    const commonIssueTypes = [
      'magic_numbers', 'duplicated_code', 'unused_variables', 'naming_convention',
      'dead_code', 'unreachable_code', 'temporary_field', 'overly_complex_condition'
    ];
    
    const hasDirectIssueTypes = commonIssueTypes.some(type => detectData[type]);
    
    if (hasDirectIssueTypes) {
      // Parse direct issue types
      if (detectData.magic_numbers && 
          detectData.magic_numbers.data && 
          detectData.magic_numbers.data.magic_numbers) {
        totalIssues += detectData.magic_numbers.data.magic_numbers.length;
      }
      
      if (detectData.duplicated_code && 
          detectData.duplicated_code.data && 
          detectData.duplicated_code.data.duplicate_code) {
        totalIssues += detectData.duplicated_code.data.duplicate_code.length;
      }
      
      if (detectData.unused_variables && 
          detectData.unused_variables.data && 
          detectData.unused_variables.data.unused_variables) {
        totalIssues += detectData.unused_variables.data.unused_variables.length;
      }
      
      if (detectData.naming_convention && 
          detectData.naming_convention.data && 
          detectData.naming_convention.data.inconsistent_naming) {
        detectData.naming_convention.data.inconsistent_naming.forEach(namingType => {
          if (namingType.vars) {
            totalIssues += namingType.vars.length;
          }
        });
      }
      
      return totalIssues;
    }
    
    // Case 2: It's structured with file paths
    // Exclude MongoDB _id and special fields
    const excludeFields = ['_id', '__v', 'createdAt', 'updatedAt'];
    
    Object.keys(detectData).forEach(key => {
      if (excludeFields.includes(key)) return;
      
      const fileData = detectData[key];
      
      // Handle the case where file paths contain language-specific data
      if (fileData && typeof fileData === 'object') {
        // Check if this contains language keys like 'py', 'js', etc.
        Object.keys(fileData).forEach(langKey => {
          const langData = fileData[langKey];
          
          if (!langData || typeof langData !== 'object') return;
          
          // Look for issue types in language data
          commonIssueTypes.forEach(issueType => {
            if (langData[issueType] && langData[issueType].data) {
              // Count magic numbers
              if (issueType === 'magic_numbers' && 
                  langData[issueType].data.magic_numbers) {
                totalIssues += langData[issueType].data.magic_numbers.length;
              }
              
              // Count duplicated code instances
              if (issueType === 'duplicated_code' && 
                  langData[issueType].data.duplicate_code) {
                totalIssues += langData[issueType].data.duplicate_code.length;
              }
              
              // Count unused variables
              if (issueType === 'unused_variables' && 
                  langData[issueType].data.unused_variables) {
                totalIssues += langData[issueType].data.unused_variables.length;
              }
              
              // Count naming convention issues
              if (issueType === 'naming_convention' && 
                  langData[issueType].data.inconsistent_naming) {
                langData[issueType].data.inconsistent_naming.forEach(namingType => {
                  if (namingType.vars) {
                    totalIssues += namingType.vars.length;
                  }
                });
              }
            }
          });
        });
      }
    });
  } catch (error) {
    console.error('Error counting code smells:', error);
  }
  
  return totalIssues;
};

/**
 * Calculates the number of code smells in each scan and updates the scan document
 * @param {Array} scans - Array of scan documents
 * @returns {Promise<Array>} - Updated array of scan documents
 */
const calculateCodeSmells = async (scans) => {
  if (!scans || !Array.isArray(scans)) return [];
  
  const updatedScans = [];
  
  for (const scan of scans) {
    try {
      // Skip if no detection data is available
      if (!scan.detect_id || !scan.detect_id.length) continue;
      
      let totalCodeSmells = 0;
      
      // Process all detection reports in the scan
      for (const detectId of scan.detect_id) {
        // Get the full detection data if it's just an ID
        let detectionData = detectId;
        
        // If the detection data is already populated, use it directly
        // Otherwise, we can't count it now and will rely on the existing total_issues_detected
        if (detectId && typeof detectId === 'object' && !Array.isArray(detectId)) {
          const issuesCount = countCodeSmellsInDetection(detectId);
          totalCodeSmells += issuesCount;
        }
      }
      
      // Only update if we found issues and the current count is 0 or different
      if (totalCodeSmells > 0 && scan.total_issues_detected !== totalCodeSmells) {
        await Scan.findByIdAndUpdate(scan._id, { 
          total_issues_detected: totalCodeSmells 
        });
        
        // Add the updated info to the scan object for immediate use
        const updatedScan = {
          ...scan.toObject(),
          total_issues_detected: totalCodeSmells
        };
        
        updatedScans.push(updatedScan);
      } else {
        updatedScans.push(scan);
      }
    } catch (error) {
      console.error(`Error processing scan ${scan._id}:`, error);
      // Still include the original scan in the results
      updatedScans.push(scan);
    }
  }
  
  return updatedScans;
};

/**
 * Updates the getAll projects method to include code smell counts
 * @param {Array} projects - Array of project documents with populated scans
 * @returns {Promise<Array>} - Projects with code smell counts added to scans
 */
const processProjectsWithCodeSmells = async (projects) => {
  if (!projects || !Array.isArray(projects)) return [];
  
  const processedProjects = [];
  let totalLatestScanIssues = 0;
  
  for (const project of projects) {
    try {
      if (project.scans && Array.isArray(project.scans)) {
        // Calculate and update code smells for each scan
        const updatedScans = await calculateCodeSmells(project.scans);
        
        // Find the latest scan for this project
        let latestScan = null;
        if (updatedScans.length > 0) {
          // Sort scans by date, newest first
          const sortedScans = [...updatedScans].sort((a, b) => {
            const dateA = a.started_at || a.createdAt || new Date(0);
            const dateB = b.started_at || b.createdAt || new Date(0);
            return new Date(dateB) - new Date(dateA);
          });
          
          // Get the latest scan
          latestScan = sortedScans[0];
          
          // Add the latest scan's issues to the total
          if (latestScan) {
            totalLatestScanIssues += (latestScan.total_issues_detected || 0);
          }
        }
        
        // Create a new project object with updated scans and project-specific count
        const updatedProject = {
          ...project.toObject(),
          scans: updatedScans,
          projectLatestScanIssues: latestScan ? (latestScan.total_issues_detected || 0) : 0
        };
        
        processedProjects.push(updatedProject);
      } else {
        processedProjects.push({
          ...project.toObject(),
          projectLatestScanIssues: 0
        });
      }
    } catch (error) {
      console.error(`Error processing project ${project._id}:`, error);
      processedProjects.push(project);
    }
  }
  
  // Add the total count of latest scan issues to each project
  const finalProjects = processedProjects.map(project => ({
    ...project,
    totalCodeSmells: totalLatestScanIssues
  }));
  
  return finalProjects;
};
/*
/**
 * Process detection data to extract files and their code smell counts
 * Based on the actual detection data structure where file paths are keys
 * @param {Array} detectData - Array of detection responses  
 * @returns {Array} - Array of files with their code smell counts, sorted by count (highest first)
 */
function processFilesFromDetection(detectData) {
  const fileMap = {};

  console.log('Processing detection data:', detectData);

  detectData.forEach((detection, detectionIndex) => {
    console.log(`Processing detection ${detectionIndex}:`, detection);
    
    // Get the detection object (handle both populated and non-populated cases)
    const detectionObj = detection.toObject ? detection.toObject() : detection;
    
    // Process each key in the detection object
    Object.entries(detectionObj).forEach(([key, value]) => {
      // Skip MongoDB metadata fields
      if (key === '_id' || key === '__v' || key === 'createdAt' || key === 'updatedAt') {
        return;
      }
      
      // Check if this key looks like a file path (contains path separators or file extensions)
      if (isFilePath(key)) {
        console.log(`Processing file path: ${key}`, value);
        
        const fileName = extractFileName(key);
        const fullPath = key;
        
        // Initialize file entry if it doesn't exist
        if (!fileMap[fileName]) {
          fileMap[fileName] = {
            fileName: fileName,
            fullPath: fullPath,
            codeSmellCount: 0,
            smellBreakdown: {}
          };
        }
        
        // Process the file data
        if (value && typeof value === 'object') {
          const smellCount = processFileData(value, fileMap[fileName]);
          console.log(`File ${fileName} has ${smellCount} code smells`);
        }
      }
    });
  });

  // Convert to array and sort by code smell count (highest first)
  const filesArray = Object.values(fileMap)
    .filter(file => file.codeSmellCount > 0) // Only include files with code smells
    .sort((a, b) => b.codeSmellCount - a.codeSmellCount);

  console.log(`Processed ${filesArray.length} files with code smells:`, filesArray);
  console.log('File breakdown:', filesArray.map(file => ({
    fileName: file.fileName,
    codeSmellCount: file.codeSmellCount,
    smellBreakdown: file.smellBreakdown
  })));
  return filesArray;
}

/**
 * Check if a key represents a file path
 * @param {String} key - The key to check
 * @returns {Boolean} - True if it looks like a file path
 */
function isFilePath(key) {
  // Check for common file path indicators
  return (
    key.includes('/') ||           // Unix path
    key.includes('\\') ||          // Windows path  
    key.includes('.py') ||         // Python file
    key.includes('.js') ||         // JavaScript file
    key.includes('.') ||           // Has file extension
    key.match(/^[a-zA-Z]:/) ||     // Windows drive letter
    key.startsWith('./') ||        // Relative path
    key.startsWith('../')          // Parent directory path
  );
}

/**
 * Process file data to count code smells
 * @param {Object} fileData - Data for a specific file
 * @param {Object} fileEntry - File entry in fileMap to update
 * @returns {Number} - Total code smells found in this file
 */
function processFileData(fileData, fileEntry) {
  let totalSmells = 0;
  
  // Code smell types to look for
  const codeSmellTypes = [
    'magic_numbers',
    'duplicated_code', 
    'unused_variables',
    'naming_convention',
    'dead_code',
    'unreachable_code',
    'overly_complex_condition',
    'global_conflict',
    'long_parameter_list',
    'temporary_field'
  ];

  // Process each extension in the file data (e.g., 'py', 'js')
  Object.entries(fileData).forEach(([extension, extensionData]) => {
    console.log(`Processing extension '${extension}' for file ${fileEntry.fileName}:`, extensionData);
    
    if (extensionData && typeof extensionData === 'object') {
      // Process each code smell type within this extension
      codeSmellTypes.forEach(smellType => {
        if (extensionData[smellType]) {
          const smellData = extensionData[smellType];
          console.log(`Found ${smellType} data:`, smellData);
          
          if (smellData && typeof smellData === 'object' && smellData.success === true && smellData.data) {
            const count = countSmellInstances(smellType, smellData.data);
            console.log(`${smellType} count: ${count}`);
            
            if (count > 0) {
              totalSmells += count;
              fileEntry.codeSmellCount += count;
              fileEntry.smellBreakdown[smellType] = 
                (fileEntry.smellBreakdown[smellType] || 0) + count;
            }
          }
        }
      });
    }
  });
  
  return totalSmells;
}

/**
 * Extract filename from file path
 * @param {String} filePath - Full file path
 * @returns {String} - Filename only
 */
function extractFileName(filePath) {
  if (typeof filePath !== 'string') return 'Unknown File';
  
  // Handle Windows and Unix paths
  let fileName = filePath;
  
  // Split by Windows separator
  if (fileName.includes('\\')) {
    fileName = fileName.split('\\').pop();
  }
  
  // Split by Unix separator  
  if (fileName.includes('/')) {
    fileName = fileName.split('/').pop();
  }
  
  return fileName || 'Unknown File';
}

/**
 * Count instances of a specific code smell type
 * @param {String} smellType - Type of code smell
 * @param {Object|Array} data - Code smell data
 * @returns {Number} - Count of smell instances
 */
function countSmellInstances(smellType, data) {
  let count = 0;
  
  try {
    switch (smellType) {
      case 'magic_numbers':
        if (data.magic_numbers && Array.isArray(data.magic_numbers)) {
          count = data.magic_numbers.length;
        }
        break;
        
      case 'duplicated_code':
        if (data.duplicate_code && Array.isArray(data.duplicate_code)) {
          count = data.duplicate_code.length;
        }
        break;
        
      case 'unused_variables':
        if (data.unused_variables && Array.isArray(data.unused_variables)) {
          count = data.unused_variables.length;
        }
        break;
        
      case 'naming_convention':
        if (data.inconsistent_naming && Array.isArray(data.inconsistent_naming)) {
          data.inconsistent_naming.forEach(namingType => {
            if (namingType.vars && Array.isArray(namingType.vars)) {
              count += namingType.vars.length;
            }
          });
        }
        break;
        
      case 'dead_code':
        if (data.dead_code && Array.isArray(data.dead_code)) {
          count = data.dead_code.length;
        }
        break;
        
      case 'unreachable_code':
        if (data.unreachable_code && Array.isArray(data.unreachable_code)) {
          count = data.unreachable_code.length;
        }
        break;
        
      case 'overly_complex_condition':
        if (data.overly_complex_condition && Array.isArray(data.overly_complex_condition)) {
          count = data.overly_complex_condition.length;
        }
        break;
        
      case 'global_conflict':
        if (data.global_conflict && Array.isArray(data.global_conflict)) {
          count = data.global_conflict.length;
        }
        break;
        
      case 'long_parameter_list':
        if (data.long_parameter_list && Array.isArray(data.long_parameter_list)) {
          count = data.long_parameter_list.length;
        }
        break;
        
      case 'temporary_field':
        if (data.temporary_field && Array.isArray(data.temporary_field)) {
          count = data.temporary_field.length;
        }
        break;
        
      default:
        // Fallback: try to find arrays in the data
        if (Array.isArray(data)) {
          count = data.length;
        } else if (typeof data === 'object' && data !== null) {
          const possibleArrays = Object.values(data).filter(value => Array.isArray(value));
          if (possibleArrays.length > 0) {
            count = possibleArrays.reduce((sum, arr) => sum + arr.length, 0);
          }
        }
        break;
    }
  } catch (error) {
    console.error(`Error counting ${smellType}:`, error);
  }
  
  return count;
}

/**
 * Extract filename from file path
 * @param {String} filePath - Full file path
 * @returns {String} - Filename
 */
function extractFileName(filePath) {
  if (typeof filePath !== 'string') return 'Unknown File';
  
  // Handle Windows and Unix paths
  const fileName = filePath.includes('\\') 
    ? filePath.split('\\').pop() 
    : filePath.includes('/') 
      ? filePath.split('/').pop() 
      : filePath;
      
  return fileName || 'Unknown File';
}

/**
 * Count instances of a specific code smell type
 * @param {String} smellType - Type of code smell
 * @param {Object|Array} data - Code smell data
 * @returns {Number} - Count of smell instances
 */
function countSmellInstances(smellType, data) {
  let count = 0;
  
  try {
    switch (smellType) {
      case 'magic_numbers':
        if (data.magic_numbers && Array.isArray(data.magic_numbers)) {
          count = data.magic_numbers.length;
        }
        break;
        
      case 'duplicated_code':
        if (data.duplicate_code && Array.isArray(data.duplicate_code)) {
          count = data.duplicate_code.length;
        }
        break;
        
      case 'unused_variables':
        if (data.unused_variables && Array.isArray(data.unused_variables)) {
          count = data.unused_variables.length;
        }
        break;
        
      case 'naming_convention':
        if (data.inconsistent_naming && Array.isArray(data.inconsistent_naming)) {
          data.inconsistent_naming.forEach(namingType => {
            if (namingType.vars && Array.isArray(namingType.vars)) {
              count += namingType.vars.length;
            }
          });
        }
        break;
        
      case 'dead_code':
        if (data.dead_code && Array.isArray(data.dead_code)) {
          count = data.dead_code.length;
        }
        break;
        
      case 'unreachable_code':
        if (data.unreachable_code && Array.isArray(data.unreachable_code)) {
          count = data.unreachable_code.length;
        }
        break;
        
      case 'overly_complex_condition':
        if (data.overly_complex_condition && Array.isArray(data.overly_complex_condition)) {
          count = data.overly_complex_condition.length;
        }
        break;
        
      case 'global_conflict':
        if (data.global_conflict && Array.isArray(data.global_conflict)) {
          count = data.global_conflict.length;
        }
        break;
        
      case 'long_parameter_list':
        if (data.long_parameter_list && Array.isArray(data.long_parameter_list)) {
          count = data.long_parameter_list.length;
        }
        break;
        
      case 'temporary_field':
        if (data.temporary_field && Array.isArray(data.temporary_field)) {
          count = data.temporary_field.length;
        }
        break;
        
      default:
        // Try to find arrays in the data
        if (Array.isArray(data)) {
          count = data.length;
        } else if (typeof data === 'object' && data !== null) {
          const possibleArrays = Object.values(data).filter(value => Array.isArray(value));
          if (possibleArrays.length > 0) {
            count = possibleArrays.reduce((sum, arr) => sum + arr.length, 0);
          }
        }
        break;
    }
  } catch (error) {
    console.error(`Error counting ${smellType}:`, error);
  }
  
  return count;
}


module.exports = {
  calculateCodeSmells,
  processProjectsWithCodeSmells,
  processFilesFromDetection,
};