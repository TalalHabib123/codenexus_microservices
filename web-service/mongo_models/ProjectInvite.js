const mongoose = require('mongoose');

const ProjectInviteSchema = new mongoose.Schema({
    email: {
        type: String,
        required: true,
        lowercase: true,
        trim: true
    },
    projectId: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'Project',
        required: true
    },
    invitedBy: {
        type: mongoose.Schema.Types.ObjectId,
        ref: 'User',
        required: true
    },
    inviteToken: {
        type: String,
        required: true,
        unique: true
    },
    status: {
        type: String,
        enum: ['pending', 'accepted', 'cancelled', 'expired'],
        default: 'pending'
    },
    createdAt: {
        type: Date,
        default: Date.now
    },
    expiresAt: {
        type: Date,
        required: true,
        index: { expireAfterSeconds: 0 } // MongoDB TTL index
    },
    acceptedAt: {
        type: Date
    },
    cancelledAt: {
        type: Date
    }
});

// Compound index to ensure one pending invitation per email per project
ProjectInviteSchema.index({ email: 1, projectId: 1, status: 1 }, { 
    unique: true,
    partialFilterExpression: { status: 'pending' }
});

// Index for token lookups
ProjectInviteSchema.index({ inviteToken: 1 });

// Method to check if invitation is expired
ProjectInviteSchema.methods.isExpired = function() {
    return new Date() > this.expiresAt;
};

// Static method to cleanup expired invitations
ProjectInviteSchema.statics.cleanupExpired = async function() {
    return this.updateMany(
        { 
            status: 'pending',
            expiresAt: { $lt: new Date() }
        },
        { 
            status: 'expired'
        }
    );
};

module.exports = mongoose.model('ProjectInvite', ProjectInviteSchema);