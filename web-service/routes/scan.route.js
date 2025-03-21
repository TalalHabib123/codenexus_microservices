const express = require('express');
const scanController = require('../controller/scan.controller');
const {vscodeAuth} = require('../middleware/auth.middleware')
const router = express.Router();


router.post('/addDetection',vscodeAuth, scanController.addDetection);
router.post('/addRefactor', vscodeAuth, scanController.addRefactor);
router.get('/daily', scanController.getDailyScans);
router.get('/weekly', scanController.getWeeklyScans);
router.get('/monthly', scanController.getMonthlyScans);

router.get("/", async(req, res) => console.log("tbghtrjskbg"))

module.exports = router;