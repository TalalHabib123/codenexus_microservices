

const {Graph} = require('../mongo_models/DependencyGraph');
const {DetectionResponse} = require('../mongo_models/DetectionData')
const {Refactor} = require('../mongo_models/RefactorData');
const filesController = {
    getFiles: async (req, res) => {
        try{ 
            const { projectId } = req.params;
            if (!projectId) {
                return res.status(400).json({ message: "Project ID is required" });
            }

            // Fetch the project by ID
            const project = await Graph.findOne({projectId: projectId});
            if (!project) {
                return res.status(404).json({ message: "Project not found" });
            }

            // Return the files associated with the project
            res.status(200).json({ files: Object.keys(project.graphData) || [] });   
        }
        catch (error) {
            console.error("Error fetching files:", error);
            res.status(500).json({ message: "Internal server error", error });
        }
    }
}

module.exports = filesController;