const mongoose = require('mongoose');
const User = require('./User');

const ProjectSchema = new mongoose.Schema({
    title: {
        type: String,
        required: true
    },
    description: {
        type: String
    },
    Owner: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        // required: true
    },
    members: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User'
    }],
    startDate: {
        type: Date,
        default: Date.now
    },
    files: [{
        type: String
    }],
    scans: [{
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Scan'
    }]
});

module.exports = mongoose.model('Project', ProjectSchema);