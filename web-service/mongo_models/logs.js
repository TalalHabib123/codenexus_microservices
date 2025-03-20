const mongoose = require('mongoose');
const { Schema } = mongoose;

const LogSchema = new Schema({
  message: {
    type: String,
    required: true
  },
  type: {
    type: String,
    enum: ['detected', 'refactored'],
    required: true
  },
  objectId: {
    type: Schema.Types.ObjectId,
    required: true,
    refPath: 'type'
  },
  projectId: {
    type: Schema.Types.ObjectId,
    required: true,
    ref: 'Project'
  }
}, { timestamps: true });

const Log = mongoose.model('Log', LogSchema);

module.exports = Log;