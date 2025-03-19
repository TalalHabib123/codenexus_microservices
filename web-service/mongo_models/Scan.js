const mongoose = require('mongoose');



const ScanSchema = new mongoose.Schema({
    scan_type: {
        type: String, 
        enum: ['automatic', 'manual'],
        required: true 
    },
    scan_name: {
        type: String,
        required: true,
        default: "General"
    },
    started_at: { 
        type: Date, 
        default: Date.now 
      },
    completed_at: { 
        type: Date 
    },
    total_issues_detected: {
        type: Number,
        default: 0
    },
    detect_id: [
        {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'DetectionResponse'
        }
    ],
    refactor_id: [
        {
            type: mongoose.Schema.Types.ObjectId,
            ref: 'Refactor'
        }
    ]
});

module.exports = mongoose.model('Scan', ScanSchema);



