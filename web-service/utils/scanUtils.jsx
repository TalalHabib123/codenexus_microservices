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

module.exports = {
  calculateCodeSmells,
  processProjectsWithCodeSmells
};