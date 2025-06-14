const projectController = require('../controller/project.controller');
const express = require('express');
const { vscodeAuth } = require('../middleware/auth.middleware');
const router = express.Router();

router.post('/create', vscodeAuth, projectController.create);
router.get('/getAll', projectController.getAll);
router.get('/getAllProjectInfos', projectController.getAllProjectInfos);
router.get('/getProjectById/:projectId', projectController.getProjectById);
router.get('/latest-scan/:projectId', projectController.getLatestScan);
module.exports = router;