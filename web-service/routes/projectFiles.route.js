const filesController = require('../controller/projectFiles.controller');
const express = require('express');
const { vscodeAuth } = require('../middleware/auth.middleware');
const router = express.Router();

router.get('/getFiles/:projectId', filesController.getFiles);
module.exports = router;