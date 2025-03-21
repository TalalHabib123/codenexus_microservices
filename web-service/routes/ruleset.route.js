const express = require('express');
const rulesetController = require('../controller/ruleset.controller.js');
const router = express.Router();
const { vscodeAuth } = require('../middleware/auth.middleware.js');


router.post('/add-or-update', vscodeAuth, rulesetController.addOrUpdateRuleset);
router.get('/get/:projectId', rulesetController.getRuleset);


module.exports = router;