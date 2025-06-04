// models/Review.js
const mongoose = require('mongoose');

const reviewSchema = new mongoose.Schema({
  username: { type: String, required: true },
  feedback: { type: String, required: true },
  rating: { type: Number, required: true, min: 1, max: 5 },
  fpictures: [String], // Array of image URLs or filenames
  userpic: String,
  date: { type: Date, default: Date.now },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true }, // to link review to user
});

module.exports = mongoose.model('Review', reviewSchema);
