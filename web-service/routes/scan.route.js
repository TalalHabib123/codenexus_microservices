const express = require('express');
const scanController = require('../controller/scan.controller');

const router = express.Router();


router.post('/addDetection', scanController.addDetection);
router.post('/addRefactor', scanController.addRefactor);

// Time-based scan routes
router.get('/daily', scanController.getDailyScans);
router.get('/weekly', scanController.getWeeklyScan);
router.get('/monthly', scanController.getMonthlyScan);

// Code smell type count routes
router.get('/codeSmellTypes/:projectId', scanController.getCodeSmellTypeCount);
router.get('/projectsCodeSmellDistribution', scanController.getProjectsCodeSmellDistribution);


router.get("/", async(req, res) => console.log("tbghtrjskbg"))

module.exports = router;