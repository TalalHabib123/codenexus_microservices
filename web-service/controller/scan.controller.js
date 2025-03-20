const Scan = require("../mongo_models/Scan");
const Project = require('../mongo_models/Project');
const { DetectionResponse } = require('../mongo_models/DetectionData');
const { RefactoringData, Refactor } = require('../mongo_models/RefactorData');
const Log = require('../mongo_models/logs');

const scanController = {
  addDetection: async (req, res) => {
    try {
      const { detectionData, title, scan_type, scan_name } = req.body;
      const detectionResponse = await DetectionResponse.create(detectionData);
      const scan = new Scan({
        scan_type,
        scan_name,
        detect_id: detectionResponse._id
      });

      await scan.save();
      const project = await Project.findOne({ title });
      if (!project) {
        return res.status(404).json({ message: "Project not found" });
      }
      project.scans.push(scan._id);
      await project.save();

      // Create a log entry
      const log = new Log({
        message: `Detection scan added to project ${title}`,
        type: 'detected',
        objectId: scan._id,
        projectId: project._id
      });
      await log.save();

      res.status(201).json({ message: "Detection data added successfully", scan });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: "Internal server error", error: err });
    }
  },

  addRefactor: async (req, res) => {
    try {
      const { filePath, refactorData, title } = req.body;
      const refData = await RefactoringData.create(refactorData);
      await refData.save();
      const refactor = new Refactor({
        filePath,
        refactorData: refData._id
      });
      await refactor.save();
      const project = await Project.findOne({ title });

      const scanId = project.scans[project.scans.length - 1];

      await Scan.updateOne(
        { _id: scanId },
        { $push: { refactor_id: refactor._id } }
      );

      // Create a log entry
      const log = new Log({
        message: `Refactor added to project ${title}`,
        type: 'refactored',
        objectId: refactor._id,
        projectId: project._id
      });
      await log.save();

      res.status(200).json({ message: "Refactor data added successfully" });
    } catch (err) {
      console.error(err);
      res.status(500).json({ message: "Internal server error", error: err });
    }
  }
};

module.exports = scanController;