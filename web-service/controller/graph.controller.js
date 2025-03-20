const {Graph} = require('../mongo_models/DependencyGraph');
const Project  = require('../mongo_models/Project');

const graphController = {
  // Create or update the dependency graph for a project
  createOrUpdateGraph: async (req, res) => {
    try {
      const { projectTitle, graphData } = req.body;
      if (!projectTitle || !graphData) {
        return res.status(400).json({ message: 'Project title and graph data are required' });
      }

      // Look for the project by title; if it doesn't exist, create it.
      let project = await Project.findOne({ title: projectTitle });
      if (!project) {
        project = await Project.create({ title: projectTitle });
      }

      // Check if a graph already exists for this project.
      let existingGraph = await Graph.findOne({ projectId: project._id });
      if (existingGraph) {
        // Update the existing graph
        existingGraph.graphData = graphData;
        await existingGraph.save();
        return res.status(200).json({ message: 'Graph updated successfully'});
      } else {
        // Create a new graph document
        await Graph.create({ graphData: graphData, projectId: project._id });
        return res.status(201).json({ message: 'Graph created successfully'});
      }
    } catch (error) {
      console.log(error);
      return res.status(500).json({ message: 'Internal server error', error: error.message });
    }
  },

  // Fetch the dependency graphData for a project using the project title as a parameter
  getGraph: async (req, res) => {
    try {
      const { projectTitle } = req.params;
      if (!projectTitle) {
        return res.status(400).json({ message: 'Project title is required' });
      }

      const project = await Project.findOne({ title: projectTitle });
      if (!project) {
        return res.status(404).json({ message: 'Project not found' });
      }

      const graphData = await Graph.findOne({ projectId: project._id });
      if (!graphData) {
        return res.status(404).json({ message: 'Graph not found for the project' });
      }

      return res.status(200).json({ message: 'Graph fetched successfully', graphData });
    } catch (error) {
      return res.status(500).json({ message: 'Internal server error', error: error.message });
    }
  },

  // Delete the dependency graph for a project using the project title as a parameter
  deleteGraph: async (req, res) => {
    try {
      const { projectTitle } = req.params;
      if (!projectTitle) {
        return res.status(400).json({ message: 'Project title is required' });
      }

      const project = await Project.findOne({ title: projectTitle });
      if (!project) {
        return res.status(404).json({ message: 'Project not found' });
      }

      const graph = await Graph.findOneAndDelete({ projectId: project._id });
      if (!graph) {
        return res.status(404).json({ message: 'Graph not found for the project' });
      }

      return res.status(200).json({ message: 'Graph deleted successfully' });
    } catch (error) {
      return res.status(500).json({ message: 'Internal server error', error: error.message });
    }
  }
};

module.exports = graphController;
