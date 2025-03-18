const mongoose = require('mongoose');
const { Schema } = mongoose;

const UserSchema = new Schema({
  username: {
    type: String,
    required: true
  },
  email: String,
  password: String,
  github_id: Number,
  google_id: String,
  encrypted_access_token: String,
  first_name: String,
  last_name: String,
  register_date: {
    type: Date,
    default: Date.now
  }
});

// Method to convert the user document to a plain JavaScript object
UserSchema.methods.toDict = function() {
  const userObj = this.toObject();
  userObj._id = userObj._id.toString(); // Convert ObjectId to string
  return userObj;
};

const User = mongoose.model('User', UserSchema);

module.exports = User;