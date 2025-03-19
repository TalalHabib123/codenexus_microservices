const mongoose = require('mongoose');


const UtilizedEntitySchema = new mongoose.Schema({
    name: { type: String, required: true },
    type: { type: String, required: true },
    alias: { type: String },
    source: { type: String, enum: ['Exporting', 'Importing'], required: true }
});

const DependentNodeSchema = new mongoose.Schema({
    name: { type: String, required: true },
    alias: { type: String },
    valid: { type: Boolean, required: true },
    weight: { type: [UtilizedEntitySchema], default: [] }
});

const FileNodeSchema = new mongoose.Schema({
    name: { type: String, required: true },
    dependencies: { type: [DependentNodeSchema], default: [] }
});

const DependencyGraphSchema = new mongoose.Schema({
    files: { type: Map, of: FileNodeSchema, default: {} }
});


const graphSchema = new mongoose.Schema({
    graphData: DependencyGraphSchema,
    projectId: { type: mongoose.Schema.Types.ObjectId, ref: 'Project' }
}, { timestamps: true });


const FileNode = mongoose.model('FileNode', FileNodeSchema);
const UtilizedEntity = mongoose.model('UtilizedEntity', UtilizedEntitySchema);
const DependentNode = mongoose.model('DependentNode', DependentNodeSchema);
const DependencyGraph = mongoose.model('DependencyGraph', DependencyGraphSchema);
const Graph = mongoose.model('Graph', graphSchema);
module.exports =  { FileNode, UtilizedEntity, DependentNode, DependencyGraph, Graph };