const {RulesetModel} = require('../mongo_models/Ruleset.js')
const Project = require('../mongo_models/Project.js')


const rulesetController = {
    addOrUpdateRuleset: async (req, res) => {
        try {
            const {title, ruleset} = req.body;
            const proj = await Project.findOne({title});
            if (!proj) {
                return res.status(404).json({message: 'Project not found'});
            }
            const projectId = proj._id;
            const existingRuleset = await RulesetModel.findOne({projectId});
            if (existingRuleset) {
                // Update existing ruleset
                existingRuleset.ruleset = ruleset;
                await existingRuleset.save();
                return res.status(200).json({message: 'Ruleset updated successfully'});
            }
            // Create new ruleset
            const newRuleset = new RulesetModel({projectId, ruleset});
            await newRuleset.save();
            return res.status(201).json({message: 'Ruleset created successfully'});
        } catch (error) {
            console.error('Error adding/updating ruleset:', error);
            return res.status(500).json({error: 'Internal server error'});
        }
    },

    getRuleset: async (req, res) => {
        try {
            const {projectId} = req.params;
            const ruleset = await RulesetModel.findOne({projectId});
            if (!ruleset) {
                return res.status(404).json({message: 'Ruleset not found'});
            }
            return res.status(200).json(ruleset.ruleset);
        } catch (error) {
            console.error('Error fetching ruleset:', error);
            return res.status(500).json({error: 'Internal server error'});
        }
    }
}

module.exports = rulesetController;