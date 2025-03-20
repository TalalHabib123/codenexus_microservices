const express = require('express');
const scanController = require('../controller/scan.controller');

const router = express.Router();


router.post('/addDetection', scanController.addDetection);
router.post('/addRefactor', scanController.addRefactor);
router.get('/daily', scanController.getDailyScans);
router.get('/weekly', scanController.getWeeklyScans);
router.get('/monthly', scanController.getMonthlyScans);

router.get("/", async(req, res) => console.log("tbghtrjskbg"))

module.exports = router;