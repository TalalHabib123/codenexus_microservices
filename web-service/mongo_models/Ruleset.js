const mongoose = require('mongoose');

const Schema = mongoose.Schema;

// FileSmell Schema
const FileSmellSchema = new Schema({
    path: { type: String, required: true },
    smells: [{ type: String }]
});

// Ruleset Schema
const RulesetSchema = new Schema({
    refactorSmells: [{ type: String }],
    detectSmells: [{ type: String }],
    includeFiles: [{
        type: Schema.Types.Mixed,
        validate: {
            validator: function(v) {
                return typeof v === 'string' || (v && v.path && Array.isArray(v.smells));
            },
            message: props => `${props.value} is not a valid file inclusion!`
        }
    }],
    excludeFiles: [{
        type: Schema.Types.Mixed,
        validate: {
            validator: function(v) {
                return typeof v === 'string' || (v && v.path && Array.isArray(v.smells));
            },
            message: props => `${props.value} is not a valid file exclusion!`
        }
    }]
});

// InitRulesetRequest Schema
const RulesetModelSchema = new Schema({
    projectId: { type: mongoose.Schema.Types.ObjectId, required: true },
    ruleset: { type: RulesetSchema, required: true }
});

const FileSmell = mongoose.model('FileSmell', FileSmellSchema);
const Ruleset = mongoose.model('Ruleset', RulesetSchema);
const RulesetModel = mongoose.model('RulesetModel', RulesetModelSchema);

module.exports = {
    FileSmell,
    Ruleset,
    RulesetModel
};