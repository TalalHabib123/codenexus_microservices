const Scan = require("../mongo_models/Scan");
const Project = require('../mongo_models/Project');
const User = require('../mongo_models/User');
const {DetectionResponse} = require ('../mongo_models/DetectionData');
const {RefactoringData} = require ('../mongo_models/RefactorData');



const scanController = {
    addDetection: async (req, res) => {
        try {
            const { detectionData, title, scan_type, scan_name} = req.body;
            const detectionResponse = await DetectionResponse.create(detectionData);
            console.log("efjeifeif")
            const scan = new Scan({
                scan_type,
                scan_name,
                detect_id: detectionResponse._id
            });
            
            await scan.save();
            const project = await Project.findOne({title});
            if (!project) {
                console.log("dfjei")
                return res.status(404).json({ message: "Project not found" });
            }
            project.scans.push(scan._id);
            await project.save();
            res.status(201).json({ message: "Detection data added successfully", scan });
            } catch(err)
            {
                console.error(err);
                res.status(500).json({ message: "Internal server error", error: err });
            }
        }, 

    addRefactor: async (req, res) => {
        try {
            const { refactorData, title} = req.body;
            const refData = await RefactoringData.create(refactorData)
            await refData.save()

            const project = await Project.findOne(title);
            const scanId = project.scans.pop();
            const scan = Scan.findbyOne({_id: scanId});
            scan.refactor_id.push(refData._id);
            await scan.save();
            project.scans.push(scan._id);
            await project.save();

            res.status(200).json({message: "refactor data added successfully"})
        }
        catch(Err){

        }
    }
};


module.exports = scanController;