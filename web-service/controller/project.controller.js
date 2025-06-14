const Scan = require('../mongo_models/Scan');
const Project = require('../mongo_models/Project');
const User = require('../mongo_models/User');
const { processProjectsWithCodeSmells } = require('../utils/scanUtils.jsx');
const { get } = require('mongoose');

const projectController = {
    create: async (req, res) => {
        try {
            const {title, description} = req.body
            const project = new Project({
                title,
                description,
                Owner: req.user._id,
                members: [req.user._id],
            });
            await project.save();
            console.log("Project created successfully", project);
            res.status(201).json({message: "Project created successfully", project});
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },
    getAll: async (req, res) => {
        try {
            const projects = await Project.find().populate('Owner').populate('members').populate('scans').populate({
                path: 'scans',
                populate: [
                    { path: 'detect_id' },
                    { path: 'refactor_id' }
                ]
            });
            
            // Process projects to calculate and update code smell counts
            const processedProjects = await processProjectsWithCodeSmells(projects);
            
            res.status(200).json(processedProjects);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

getAllProjectInfos: async (req, res) => {
    try {
        const projects = await Project.find()
            .populate('Owner')
            .populate('members')
            .populate('scans')
            .populate({
                path: 'scans',
                populate: [
                    { path: 'detect_id' },
                    { path: 'refactor_id' }
                ]
            });

        // Process projects to calculate and update code smell counts
        const processedProjects = await processProjectsWithCodeSmells(projects);

        // Map processed projects to only return needed fields
        const result = processedProjects.map(proj => {
            const { _id, title, description, scans } = proj;
            const totalScans = scans?.length || 0;

            // Sort scans by date (newest first) to find the latest
            const sortedScans = [...scans].sort((a, b) =>
                new Date(b.started_at || b.createdAt) - new Date(a.started_at || a.createdAt)
            );

            // Get the latest scan and its code smells
            const latestScan = sortedScans[0] || {};
            const codeSmellsInLatestScan = latestScan.total_issues_detected || 0;

            // Count total refactors across all scans
            let totalRefactors = 0;
            scans.forEach(scan => {
                if (scan.refactor_id && Array.isArray(scan.refactor_id)) {
                    totalRefactors += scan.refactor_id.length;
                }
            });

            return {
                _id,
                title,
                description,
                totalScans,
                codeSmellsInLatestScan,
                totalRefactors
            };
        });

        res.status(200).json(result);
    } catch (error) {
        console.error(error);
        res.status(500).json({ message: "Internal server error", error });
    }
},


    getAllScans: async (req, res) => {
        try {
            const projectId = req.params.projectId;
            const scans = await Scan.find({project_id: projectId}).populate('project_id');
            res.status(200).json(scans);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getScanById: async (req, res) => {
        try {
            const scanId = req.params.scanId;
            const scan = await Scan.findById(scanId).populate('project_id');
            if (!scan) {
                return res.status(404).json({message: "Scan not found"});
            }
            res.status(200).json(scan);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    },

    getProjectById: async (req, res) => {
        try {
            const projectId = req.params.projectId;
            const project = await Project
            .findById(projectId).populate('Owner').populate('members')
                .populate({
                path: 'scans',
                populate: [
                    {
                        path: 'detect_id'
                    },
                    {
                        path: 'refactor_id',
                        populate: {
                            path: 'refactorData'
                        }
                    }
                ]
            });
            if (!project) {
                return res.status(404).json({message: "Project not found"});
            }
            res.status(200).json(project);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "error occurred"});
        }
    },

   getLatestScan: async (req, res) => {
        try {
               const { projectId } = req.params;

      // 1) Load the project and populate only the most recent scan
      const project = await Project.findById(projectId).populate({
        path: 'scans',
        options: { sort: { started_at: -1 }, limit: 1 },
        populate: [
          { path: 'detect_id' },
        ]
      });

      if (!project) {
        return res.status(404).json({ message: 'Project not found' });
      }
      if (!project.scans.length) {
        return res.status(404).json({ message: 'No scans for this project' });
      }

      // 2) The first (and only) element is the latest
      const latestScan = project.scans[0];
      res.status(200).json(latestScan);
    } catch (error) {
      console.error(error);
      res.status(500).json({ message: 'Internal server error', error });
    }
  },

  addMember: async (req, res) => {
    try {
        const projectId = req.params.projectId;
        const userEmail = req.body.email;

        //create user with given email if it doesn't exist 
        let user = await User.findOne({ email:
            userEmail
        });
        if (!user) {
            user = new User({ email: userEmail });
            await user.save();
        }
        const userId = user._id;

        // Check if the user is already a member
        const project = await Project.findById(projectId);
        if (!project) {
            return res.status(404).json({message: "Project not found"});
        }
        if (project.members.includes(userId)) {
            return res.status(400).json({message: "User is already a member of this project"});
        }

        // Add the user to the project's members
        project.members.push(userId);
        await project.save();

        res.status(200).json({message: "Member added successfully", project});
    } catch (error) {
        console.error(error);
        res.status(500).json({message: "Internal server error", error});
    }
  },
  removeMember: async (req, res) => {
    try {
        const projectId = req.params.projectId;
        const userId = req.body;

        // Check if the project exists
        const project = await Project.findById(projectId);
        if (!project) {
            return res.status(404).json({message: "Project not found"});
        }

        // Check if the user is a member
        if (!project.members.includes(userId)) {
            return res.status(400).json({message: "User is not a member of this project"});
        }

        // Remove the user from the project's members
        project.members = project.members.filter(member => member.toString() !== userId.toString());
        await project.save();

        res.status(200).json({message: "Member removed successfully", project});
    } catch (error) {
        console.error(error);
        res.status(500).json({message: "Internal server error", error});
    }
  },
  
}

module.exports = projectController;