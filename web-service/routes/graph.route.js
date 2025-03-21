const express = require('express');
const graphController = require('../controller/graph.controller');
const { vscodeAuth } = require('../middleware/auth.middleware');
const router = express.Router();

router.post('/add-or-update', vscodeAuth, graphController.createOrUpdateGraph);
router.get('/get/:projectId', graphController.getGraph);
router.delete('/delete/:projectId', graphController.deleteGraph);

module.exports = router;
