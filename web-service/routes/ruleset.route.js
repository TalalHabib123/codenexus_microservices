const express = require('express');
const rulesetController = require('../controller/ruleset.controller.js');
const router = express.Router();



router.post('/add-or-update', rulesetController.addOrUpdateRuleset);
router.get('/get/:projectId', rulesetController.getRuleset);

module.exports = router;