const Scan = require("../mongo_models/Scan");
const Project = require('../mongo_models/Project');
const { DetectionResponse } = require('../mongo_models/DetectionData');
const { RefactoringData } = require('../mongo_models/RefactorData');
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
      const latestScan = await Scan.findOne({ project_id: projectId })
        .populate('detect_id')
        .sort({ started_at: -1 });
      
      if (!latestScan || !latestScan.detect_id || latestScan.detect_id.length === 0) {
        return res.status(200).json({
          magic_numbers: 0,
          duplicated_code: 0,
          unused_variables: 0,
          naming_convention: 0,
          dead_code: 0,
          unreachable_code: 0
        });
      }
      
      // Assuming detect_id is an array of detection responses
      const codeSmellTypes = {
        magic_numbers: 0,
        duplicated_code: 0,
        unused_variables: 0,
        naming_convention: 0,
        dead_code: 0,
        unreachable_code: 0
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
        
        // Initialize code smell types
        const codeSmellTypes = {
          magic_numbers: 0,
          duplicated_code: 0,
          unused_variables: 0,
          naming_convention: 0,
          dead_code: 0,
          unreachable_code: 0
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
  }
};

// Helper function to calculate total issues detected
function calculateTotalIssuesDetected(detectionData) {
  let totalIssues = 0;

  // Helper function to count issues in a specific detection type
  const countIssues = (dataPath) => {
    const pathParts = dataPath.split('.');
    let current = detectionData;
    
    for (const part of pathParts) {
      if (!current || !current[part]) return 0;
      current = current[part];
    }

    return Array.isArray(current) ? current.length : 0;
  };

  // Define paths to different types of code smells
  const issueTypes = [
    'magic_numbers.data.magic_numbers',
    'duplicated_code.data.duplicate_code',
    'unused_variables.data.unused_variables',
    'naming_convention.data.inconsistent_naming',
    'dead_code.data.dead_code',
    'unreachable_code.data.unreachable_code'
  ];

  // Sum up issues from all types
  issueTypes.forEach(type => {
    totalIssues += countIssues(type);
  });

  return totalIssues;
}

module.exports = scanController;