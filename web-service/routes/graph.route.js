const express = require('express');
const graphController = require('../controller/graph.controller');

const router = express.Router();

router.post('/add-or-update', graphController.createOrUpdateGraph);
router.get('/get/:projectId', graphController.getGraph);
router.delete('/delete/:projectId', graphController.deleteGraph);

module.exports = router;
