const express = require('express');
const scanController = require('../controller/scan.controller');
const {vscodeAuth} = require('../middleware/auth.middleware')
const router = express.Router();


router.post('/addDetection', scanController.addDetection);
router.post('/addRefactor', scanController.addRefactor);


router.get('/daily', scanController.daily);
router.get('/weekly', scanController.Weekly);
router.get('/monthly', scanController.Monthly);

// Code smell type count routes
router.get('/codeSmellTypes/:projectId', scanController.getCodeSmellTypeCount);
router.get('/projectsCodeSmellDistribution', scanController.getProjectsCodeSmellDistribution);


router.get("/", async(req, res) => console.log("tbghtrjskbg"))

module.exports = router;