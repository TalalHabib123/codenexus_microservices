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
            });
            await project.save();
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
            .findById(projectId).populate('Owner').populate('members').populate('scans');
            if (!project) {
                return res.status(404).json({message: "Project not found"});
            }
            res.status(200).json(project);
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "error occurred"});
        }
    },

    getDailyScanByProjectId: async (req, res) => {
        // endpoint to return the last scan of each day. 
        // this is used to show the daily scan in the dashboard
        try {
            const projectId = req.params.projectId;
            const scans = await Scan.find({project_id: projectId}).populate('project_id');
            const dailyScans = {};

            scans.forEach(scan => {
                const date = new Date(scan.started_at).toISOString().split('T')[0]; // Get the date part
                if (!dailyScans[date] || new Date(scan.started_at) > new Date(dailyScans[date].started_at)) {
                    dailyScans[date] = scan;
                }
            });

            res.status(200).json(Object.values(dailyScans));
        } catch (error) {
            console.error(error);
            res.status(500).json({message: "Internal server error", error});
        }
    }
}

module.exports = projectController;