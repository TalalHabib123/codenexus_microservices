const {Graph} = require('../mongo_models/DependencyGraph');
const Project  = require('../mongo_models/Project');

const graphController = {
  // Create or update the dependency graph for a project
  createOrUpdateGraph: async (req, res) => {
    try {
      console.log("jfksdfdfh")
      const { projectTitle, graphData } = req.body;

      if (!projectTitle || !graphData) {
        res.status(400).json({ status: "error", message: 'Project title and graph data are required' });
      }

      // Look for the project by title; if it doesn't exist, create it.
      let project = await Project.findOne({ title: projectTitle });
      if (!project) {
        project = await Project.create({ title: projectTitle });
      }
      console.log('Project found or created:', project._id);
      // Check if a graph already exists for this project.
      let existingGraph = await Graph.findOne({ projectId: project._id });
      if (existingGraph) {
        // Update the existing graph
        console.log(graphData)
        existingGraph.graphData = graphData;
        await existingGraph.save();
        console.log('Graph updated successfully');
        res.status(201).json({ status: "success", message: 'Graph updated successfully'});
      } else {
        // Create a new graph document
        await Graph.create({ graphData: graphData, projectId: project._id });
        console.log('Graph created successfully');
        res.status(201).json({ status: "success", message: 'Graph created successfully'});
      }
    } catch (error) {
      console.log(error);
      return res.status(500).json({ status: "error", message: 'Internal server error', error: error.message });
    }
  },

  // Fetch the dependency graphData for a project using the project title as a parameter
  getGraph: async (req, res) => {
    try {
      const { projectId } = req.params;
      if (!projectId) {
        res.status(400).json({ status: "error", message: 'Project title is required' });
      }

      const graphData = await Graph.findOne({ projectId});
      if (!graphData) {
        res.status(404).json({ status: "error", message: 'Graph not found for the project' });
      }

      res.status(200).json({ status: "success", message: 'Graph fetched successfully', graphData });
    } catch (error) {
      res.status(500).json({ status: "error", message: 'Internal server error', error: error.message });
    }
  },

  // Delete the dependency graph for a project using the project title as a parameter
  deleteGraph: async (req, res) => {
    try {
      const { projectId } = req.params;
      if (!projectId) {
        res.status(400).json({ status: "error", message: 'Project title is required' });
      }

      const graph = await Graph.findOneAndDelete({ projectId});
      if (!graph) {
        res.status(404).json({ status: "error", message: 'Graph not found for the project' });
      }

      res.status(200).json({ status: "success", message: 'Graph deleted successfully' });
    } catch (error) {
      res.status(500).json({ status: "error", message: 'Internal server error', error: error.message });
    }
  }
};

module.exports = graphController;
