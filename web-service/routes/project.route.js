const projectController = require('../controller/project.controller');
const express = require('express');
const { vscodeAuth, requireAuth } = require('../middleware/auth.middleware');
const router = express.Router();

router.post('/create', vscodeAuth, projectController.create);
router.get('/getAll', projectController.getAll);
router.get('/getAllProjectInfos', projectController.getAllProjectInfos);
router.get('/getProjectById/:projectId', projectController.getProjectById);
router.get('/latest-scan/:projectId', projectController.getLatestScan);
// Updated member management routes
router.post('/invite/:projectId', requireAuth, projectController.inviteMember);
router.delete('/removeMember/:projectId', projectController.removeMember);

// New invitation management routes
router.get('/accept-invitation/:token', projectController.acceptInvitation);
router.get('/invitations/:projectId', projectController.getPendingInvitations);
router.delete('/cancel-invitation/:projectId', projectController.cancelInvitation);

module.exports = router;