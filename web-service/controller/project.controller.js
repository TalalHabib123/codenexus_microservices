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

    }
}

module.exports = projectController;