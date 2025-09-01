const mongoose = require('mongoose');

const audioSchema = new mongoose.Schema({
  filename: String,
  mimetype: String,
  data: Buffer,
  uploadedAt: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Audio', audioSchema);
