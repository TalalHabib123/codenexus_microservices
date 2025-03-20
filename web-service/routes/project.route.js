const projectController = require('../controller/project.controller');
const express = require('express');

const router = express.Router();

router.post('/create', projectController.create);
router.get('/getAll', projectController.getAll);
router.get('/getAllProjectInfos', projectController.getAllProjectInfos);
router.get('/getProjectById/:projectId', projectController.getProjectById);
// router.get('/getAllMembers/:projectId', projectController.getAllMembers);
// router.get('/getAllScans/:projectId', projectController.getAllScans);
// router.get('/getScanById/:scanId', projectController.getScanById);
// router.put('/update/:projectId', projectController.updateProject);
// router.delete('/delete/:projectId', projectController.deleteProject);
// router.post('/addMember/:projectId', projectController.addMemberToProject);
// router.delete('/removeMember/:projectId', projectController.removeMemberFromProject);
// router.post('/addScan/:projectId', projectController.addScanToProject);
// router.delete('/removeScan/:projectId', projectController.removeScanFromProject);
// router.post('/addFile/:projectId', projectController.addFileToProject);
// router.delete('/removeFile/:projectId', projectController.removeFileFromProject);
// router.put('/updateFile/:projectId', projectController.updateFileInProject);
// router.get('/getFile/:projectId', projectController.getFileFromProject);
// router.delete('/deleteFile/:projectId', projectController.deleteFileFromProject);
// router.post('/addCode/:projectId', projectController.addCodeToProject);
// router.delete('/removeCode/:projectId', projectController.removeCodeFromProject);
// router.get('/getCode/:projectId', projectController.getCodeFromProject);
// router.delete('/deleteCode/:projectId', projectController.deleteCodeFromProject);
// router.post('/addCodeFile/:projectId', projectController.addCodeFileToProject);
// router.delete('/removeCodeFile/:projectId', projectController.removeCodeFileFromProject);
// router.get('/getCodeFile/:projectId', projectController.getCodeFileFromProject);


module.exports = router;