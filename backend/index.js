const express = require('express');
const mongoose = require('mongoose');
const multer = require('multer');
const path = require('path');
const Audio = require('./models/Audio');

const app = express();
const port = process.env.PORT || 3000;

// MongoDB connection
mongoose.connect('mongodb://localhost:27017/studysound', {
  useNewUrlParser: true,
  useUnifiedTopology: true,
});
mongoose.connection.on('connected', () => {
  console.log('Connected to MongoDB');
});
mongoose.connection.on('error', (err) => {
  console.error('MongoDB connection error:', err);
});

app.use(express.json());

// Multer setup for file uploads
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Simple root route
app.get('/', (req, res) => {
  res.send('Welcome to the StudySound backend API!');
});

// Example API route
app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from the backend API!' });
});

// Audio upload route
app.post('/api/upload', upload.single('audio'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No audio file uploaded' });
    }
    const audio = new Audio({
      filename: req.file.originalname,
      mimetype: req.file.mimetype,
      data: req.file.buffer,
    });
    await audio.save();
    res.status(201).json({ message: 'Audio uploaded successfully', id: audio._id });
  } catch (err) {
    res.status(500).json({ error: 'Failed to upload audio' });
  }
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
