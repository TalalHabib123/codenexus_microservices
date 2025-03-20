const Log = require('../mongo_models/logs');
const Project = require('../mongo_models/Project');

const logController = {
  // Create a new log and attach it to a project
  createLog: async (req, res) => {
    try {
      const { projectId } = req.params;
      const { message, type, objectId } = req.body;

      // Create a new log entry
      const log = new Log({
        message,
        type,
        objectId,
        projectId
      });
      await log.save();

      res.status(201).json({ message: 'Log added to project successfully', log });
    } catch (error) {
      console.error('Error adding log to project:', error);
      res.status(500).json({ message: 'Internal server error', error });
    }
  },

  // Get all logs for a project
  getLogsforProj: async (req, res) => {
    try {
      const { projectId } = req.params;

      // Find logs by projectId
      const logs = await Log.find({ projectId });
      if (!logs) {
        return res.status(404).json({ message: 'Logs not found' });
      }

      res.status(200).json(logs);
    } catch (error) {
      console.error('Error fetching logs for project:', error);
      res.status(500).json({ message: 'Internal server error', error });
    }
  },

  // Get all logs for all projects
  getAllLogs: async (req, res) => {
    try {
      // Find all logs
      const logs = await Log.find();
      if (!logs) {
        return res.status(404).json({ message: 'Logs not found' });
      }

      res.status(200).json(logs);
    } catch (error) {
      console.error('Error fetching all logs:', error);
      res.status(500).json({ message: 'Internal server error', error });
    }
  },

  // Delete a log by ID
  deleteLog: async (req, res) => {
    try {
      const { logId } = req.params;

      // Find and delete the log entry
      const log = await Log.findByIdAndDelete(logId);
      if (!log) {
        return res.status(404).json({ message: 'Log not found' });
      }

      res.status(200).json({ message: 'Log deleted successfully' });
    } catch (error) {
      console.error('Error deleting log:', error);
      res.status(500).json({ message: 'Internal server error', error });
    }
  }
};

module.exports = logController;