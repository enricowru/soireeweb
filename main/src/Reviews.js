const express = require('express');
const router = express.Router();
const mongoose = require('mongoose');
const { verifyToken } = require('../middlewares/auth'); // adjust this path if needed

// === Review Schema and Model (merged here) ===
const reviewSchema = new mongoose.Schema({
  username: { type: String, required: true },
  feedback: { type: String, required: true },
  rating: { type: Number, required: true, min: 1, max: 5 },
  fpictures: [String], // array of image URLs or filenames
  userpic: String,
  date: { type: Date, default: Date.now },
  userId: { type: mongoose.Schema.Types.ObjectId, ref: 'User', required: true },
});

const Review = mongoose.model('Review', reviewSchema);

// === GET /reviews - fetch all reviews ===
router.get('/', async (req, res) => {
  try {
    const reviews = await Review.find().sort({ date: -1 });
    res.json(reviews);
  } catch (error) {
    res.status(500).json({ message: 'Failed to get reviews' });
  }
});

// === POST /reviews - create a new review ===
router.post('/', verifyToken, async (req, res) => {
  const { feedback, rating, fpictures, userpic } = req.body;
  const userId = req.user.id;
  const username = req.user.username;

  if (!feedback || !rating) {
    return res.status(400).json({ message: 'Feedback and rating are required' });
  }

  try {
    const review = new Review({
      username,
      feedback,
      rating,
      fpictures,
      userpic,
      userId,
    });

    await review.save();
    res.status(201).json({ message: 'Review posted', review });
  } catch (error) {
    res.status(500).json({ message: 'Failed to post review' });
  }
});

module.exports = router;
