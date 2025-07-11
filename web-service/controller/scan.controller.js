const Scan = require("../mongo_models/Scan");
const Project = require('../mongo_models/Project');
const { DetectionResponse } = require('../mongo_models/DetectionData');
const { RefactoringData } = require('../mongo_models/RefactorData');
const {processFilesFromDetection}= require('../utils/scanUtils.jsx') ;
const Log = require('../mongo_models/logs');

const scanController = {
  // Add a new detection scan
  addDetection: async (req, res) => {
    try {
      const { detectionData, title, scan_type, scan_name } = req.body;
      
      // Find the project
      const project = await Project.findOne({ title });
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }

      // Create detection response
      const detectionResponse = await DetectionResponse.create(detectionData);
      
      // Create scan
      const scan = new Scan({
        project_id: project._id,
        scan_type: scan_type || 'automatic',
        scan_name: scan_name || 'General Detection',
        detect_id: [detectionResponse._id]
      });

      // Calculate total issues detected
      const totalIssuesDetected = calculateTotalIssuesDetected(detectionData);
      scan.total_issues_detected = totalIssuesDetected;

      // Save scan
      await scan.save();

      // Update project's scans
      project.scans.push(scan._id);
      await project.save();

      // Create log entry
      const log = new Log({
        message: `Detection scan added to project ${title}`,
        type: 'detected',
        objectId: scan._id,
        projectId: project._id
      });
      await log.save();

      res.status(201).json({ 
        message: "Detection data added successfully", 
        scan,
        totalIssuesDetected
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: "Internal server error", error: err.message });
    }
  },

  // Add a new refactoring scan
  addRefactor: async (req, res) => {
    try {
      const { filePath, refactorData, title } = req.body;
      
      // Find the project
      const project = await Project.findOne({ title });
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }

      // Create refactoring data
      const refData = await RefactoringData.create(refactorData);
      
      // Find the latest scan for this project
      const latestScan = await Scan.findOne({ project_id: project._id })
        .sort({ started_at: -1 });

      if (!latestScan) {
        return res.status(404).json({ message: "No previous scan found for this project" });
      }

      // Update the latest scan with refactoring data
      latestScan.refactor_id.push(refData._id);
      await latestScan.save();

      // Create log entry
      const log = new Log({
        message: `Refactor added to project ${title}`,
        type: 'refactored',
        objectId: refData._id,
        projectId: project._id
      });
      await log.save();

      res.status(200).json({ 
        message: "Refactor data added successfully",
        refactorData: refData 
      });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: "Internal server error", error: err.message });
    }
  },

  // Get daily scans for all projects
  daily: async (req, res) => {
    try {
      // Get all unique projects
      const projects = await Project.find({});
      
      // Collect last scan for each project per day
      const dailyScans = [];
      
      for (const project of projects) {
        // Find the latest scan for this project today
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        const latestScan = await Scan.findOne({ 
          project_id: project._id,
          started_at: { $gte: today }
        })
        .populate('detect_id')
        .sort({ started_at: -1 })
        .limit(1);
        
        if (latestScan) {
          dailyScans.push(latestScan);
        }
      }
      
      res.status(200).json(dailyScans);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal server error", error: error.message });
    }
  },

  // Get weekly scans for all projects
 Weekly: async (req, res) => {
    try {
      const projects = await Project.find({});
      const weeklyScan = [];
      
      for (const project of projects) {
        // Get scans from the last 7 days
        const oneWeekAgo = new Date();
        oneWeekAgo.setDate(oneWeekAgo.getDate() - 7);
        
        const latestScan = await Scan.findOne({
          project_id: project._id,
          started_at: { $gte: oneWeekAgo }
        })
        .populate('detect_id')
        .sort({ started_at: -1 })
        .limit(1);
        
        if (latestScan) {
          weeklyScan.push(latestScan);
        }
      }
      
      res.status(200).json(weeklyScan);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal server error", error: error.message });
    }
  },

  // Get monthly scans for all projects
  Monthly: async (req, res) => {
    try {
      const projects = await Project.find({});
      const monthlyScan = [];
      
      for (const project of projects) {
        // Get scans from the last 30 days
        const oneMonthAgo = new Date();
        oneMonthAgo.setDate(oneMonthAgo.getDate() - 30);
        
        const latestScan = await Scan.findOne({
          project_id: project._id,
          started_at: { $gte: oneMonthAgo }
        })
        .populate('detect_id')
        .sort({ started_at: -1 })
        .limit(1);
        
        if (latestScan) {
          monthlyScan.push(latestScan);
        }
      }
      
      res.status(200).json(monthlyScan);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal server error", error: error.message });
    }
  },



  // Get code smell type count for a specific project
  getCodeSmellTypeCount: async (req, res) => {
    try {
      const { projectId } = req.params;
    
      // Find the latest scan for the project
       // 1) Load the project and populate exactly one scan (the latest)
      const project = await Project.findById(projectId).populate({
        path: 'scans',
        options: { sort: { started_at: -1 }, limit: 1 },
        populate: { path: 'detect_id', model: 'DetectionResponse' }
      });
           if (!project) {
        return res.status(404).json({ message: 'Project not found' });
      }
      const latestScan = project.scans[0];
      if (!latestScan || !latestScan.detect_id || latestScan.detect_id.length === 0) {
        console.log('No detections found for this project');
        return res.status(200).json({
          magic_numbers: 0,
          duplicated_code: 0,
          unused_variables: 0,
          naming_convention: 0,
          dead_code: 0,
          unreachable_code: 0,
          overly_complex_condition: 0,
          global_conflict: 0,
          long_parameter_list: 0,
          temporary_field: 0,
 
        });
      }
      
      // Initialize all code smell types
      const codeSmellTypes = {
        magic_numbers: 0,
        duplicated_code: 0,
        unused_variables: 0,
        naming_convention: 0,
        dead_code: 0,
        unreachable_code: 0,
        overly_complex_condition: 0,
        global_conflict: 0,
        long_parameter_list: 0,
        temporary_field: 0,
       
      };

      // Iterate through each detection response
      latestScan.detect_id.forEach(detection => {
        // Magic Numbers
        if (detection.magic_numbers?.data?.magic_numbers) {
          codeSmellTypes.magic_numbers += detection.magic_numbers.data.magic_numbers.length;
        }

        // Duplicated Code
        if (detection.duplicated_code?.data?.duplicate_code) {
          codeSmellTypes.duplicated_code += detection.duplicated_code.data.duplicate_code.length;
        }

        // Unused Variables
        if (detection.unused_variables?.data?.unused_variables) {
          codeSmellTypes.unused_variables += detection.unused_variables.data.unused_variables.length;
        }

        // Naming Convention
        if (detection.naming_convention?.data?.inconsistent_naming) {
          detection.naming_convention.data.inconsistent_naming.forEach(namingType => {
            codeSmellTypes.naming_convention += namingType.vars ? namingType.vars.length : 0;
          });
        }

        // Dead Code
        if (detection.dead_code?.data?.dead_code) {
          codeSmellTypes.dead_code += detection.dead_code.data.dead_code.length;
        }

        // Unreachable Code
        if (detection.unreachable_code?.data?.unreachable_code) {
          codeSmellTypes.unreachable_code += detection.unreachable_code.data.unreachable_code.length;
        }

        // Overly Complex Condition
        if (detection.overly_complex_condition?.data?.overly_complex_condition) {
          codeSmellTypes.overly_complex_condition += detection.overly_complex_condition.data.overly_complex_condition.length;
        }

        // Global Conflict
        if (detection.global_conflict?.data?.global_conflict) {
          codeSmellTypes.global_conflict += detection.global_conflict.data.global_conflict.length;
        }

        // Long Parameter List
        if (detection.long_parameter_list?.data?.long_parameter_list) {
          codeSmellTypes.long_parameter_list += detection.long_parameter_list.data.long_parameter_list.length;
        }

        // Temporary Field
        if (detection.temporary_field?.data?.temporary_field) {
          codeSmellTypes.temporary_field += detection.temporary_field.data.temporary_field.length;
        }

      });
      
      res.status(200).json(codeSmellTypes);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal server error", error: error.message });
    }
  },

  // Get code smell distribution across all projects
  getProjectsCodeSmellDistribution: async (req, res) => {
    try {
      // Get all projects
      const projects = await Project.find({});
      
      // Will store code smell distribution for all projects
      const projectsCodeSmellDistribution = [];
      
      // Iterate through each project
      for (const project of projects) {
        // Find the latest scan for this project
        const latestScan = await Scan.findOne({ project_id: project._id })
          .populate('detect_id')
          .sort({ started_at: -1 });
        
        // Initialize all code smell types
        const codeSmellTypes = {
          magic_numbers: 0,
          duplicated_code: 0,
          unused_variables: 0,
          naming_convention: 0,
          dead_code: 0,
          unreachable_code: 0,
          overly_complex_condition: 0,
          global_conflict: 0,
          long_parameter_list: 0,
          temporary_field: 0,
       
        };

        // If latest scan exists and has detection data
        if (latestScan && latestScan.detect_id && latestScan.detect_id.length > 0) {
          // Iterate through each detection response
          latestScan.detect_id.forEach(detection => {
            // Magic Numbers
            if (detection.magic_numbers?.data?.magic_numbers) {
              codeSmellTypes.magic_numbers += detection.magic_numbers.data.magic_numbers.length;
            }

            // Duplicated Code
            if (detection.duplicated_code?.data?.duplicate_code) {
              codeSmellTypes.duplicated_code += detection.duplicated_code.data.duplicate_code.length;
            }

            // Unused Variables
            if (detection.unused_variables?.data?.unused_variables) {
              codeSmellTypes.unused_variables += detection.unused_variables.data.unused_variables.length;
            }

            // Naming Convention
            if (detection.naming_convention?.data?.inconsistent_naming) {
              detection.naming_convention.data.inconsistent_naming.forEach(namingType => {
                codeSmellTypes.naming_convention += namingType.vars ? namingType.vars.length : 0;
              });
            }

            // Dead Code
            if (detection.dead_code?.data?.dead_code) {
              codeSmellTypes.dead_code += detection.dead_code.data.dead_code.length;
            }

            // Unreachable Code
            if (detection.unreachable_code?.data?.unreachable_code) {
              codeSmellTypes.unreachable_code += detection.unreachable_code.data.unreachable_code.length;
            }

            // Overly Complex Condition
            if (detection.overly_complex_condition?.data?.overly_complex_condition) {
              codeSmellTypes.overly_complex_condition += detection.overly_complex_condition.data.overly_complex_condition.length;
            }

            // Global Conflict
            if (detection.global_conflict?.data?.global_conflict) {
              codeSmellTypes.global_conflict += detection.global_conflict.data.global_conflict.length;
            }

            // Long Parameter List
            if (detection.long_parameter_list?.data?.long_parameter_list) {
              codeSmellTypes.long_parameter_list += detection.long_parameter_list.data.long_parameter_list.length;
            }

            // Temporary Field
            if (detection.temporary_field?.data?.temporary_field) {
              codeSmellTypes.temporary_field += detection.temporary_field.data.temporary_field.length;
            }

          
          });
        }

        // Add project's code smell distribution
        projectsCodeSmellDistribution.push({
          projectName: project.title,
          ...codeSmellTypes
        });
      }
      
      res.status(200).json(projectsCodeSmellDistribution);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: "Internal server error", error: error.message });
    }
  },
  // Get files with their code smell counts from latest scan
// Updated route handler with better debugging
getFileCodeSmells: async (req, res) => {
  try {
    const { projectId } = req.params;
    console.log('Processing file code smells for project:', projectId);
    
    // Find the project and get the latest scan
    const project = await Project.findById(projectId).populate({
      path: 'scans',
      options: { sort: { started_at: -1 }, limit: 1 },
      populate: { path: 'detect_id', model: 'DetectionResponse' }
    });

    if (!project) {
      return res.status(404).json({ message: 'Project not found' });
    }

    console.log('Project found:', project.title);

    const latestScan = project.scans[0];
    
    if (!latestScan) {
      console.log('No scans found for this project');
      return res.status(200).json({
        message: 'No scans found for this project',
        files: []
      });
    }

    console.log('Latest scan:', {
      id: latestScan._id,
      date: latestScan.started_at || latestScan.createdAt,
      detectIdCount: latestScan.detect_id ? latestScan.detect_id.length : 0
    });

    if (!latestScan.detect_id || latestScan.detect_id.length === 0) {
      console.log('No detection data found in latest scan');
      return res.status(200).json({
        message: 'No detection data found for this project',
        files: []
      });
    }

    // Log the structure of the first detection to debug
    console.log('First detection structure:', JSON.stringify(latestScan.detect_id[0], null, 2));

    // Process files and count code smells
    const fileCodeSmells = processFilesFromDetection(latestScan.detect_id);

    console.log(`Found ${fileCodeSmells.length} files with code smells`);

    res.status(200).json({
      message: 'Files with code smells retrieved successfully',
      projectId: projectId,
      scanId: latestScan._id,
      scanDate: latestScan.started_at || latestScan.createdAt,
      totalFiles: fileCodeSmells.length,
      files: fileCodeSmells
    });

  } catch (error) {
    console.error('Error getting file code smells:', error);
    res.status(500).json({ 
      message: 'Internal server error', 
      error: error.message 
    });
  }
}
};

function calculateTotalIssuesDetected(detectionData) {
  let totalIssues = 0;

  // Walk a dotted path into detectionData and return length if it's an array
  const countIssues = (dataPath) => {
    const parts = dataPath.split('.');
    let current = detectionData;
    for (const p of parts) {
      if (!current || current[p] == null) return 0;
      current = current[p];
    }
    return Array.isArray(current) ? current.length : 0;
  };

  // All code‐smell paths to count
  const issueTypes = [
    'magic_numbers.data.magic_numbers',
    'duplicated_code.data.duplicate_code',
    'unused_variables.data.unused_variables',
    'naming_convention.data.inconsistent_naming',
    'dead_code.data.dead_code',
    'unreachable_code.data.unreachable_code',
    'overly_complex_condition.data.overly_complex_condition',
    'global_conflict.data.global_conflict',
    'long_parameter_list.data.long_parameter_list',
    'temporary_field.data.temporary_field',
  
  ];

  issueTypes.forEach(path => {
    totalIssues += countIssues(path);
  });

  return totalIssues;
}


module.exports = scanController;