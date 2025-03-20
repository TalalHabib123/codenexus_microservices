const express = require('express');
const logController = require('../controller/log.controller');

const router = express.Router();

// Create a new log and attach it to a project
router.post('/:projectId/logs', logController.createLog);

// Get all logs for a project
router.get('/:projectId/logs', logController.getLogsforProj);

// Get all logs for all projects
router.get('/', logController.getAllLogs);

// Delete a log by ID
router.delete('/logs/:logId', logController.deleteLog);

module.exports = router;