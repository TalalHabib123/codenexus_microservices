const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();
// const GoogleController = require('./controller/google.controller');
// const passport = require('passport');

const authRoutes = require('./routes/auth.route');

// Create Express app
const app = express();

// Middleware
app.use(express.json());


// GoogleController.configureGoogleStrategy();

app.use(cors({
  origin: '*',  // adjust as needed
  credentials: true
}));

// Routes
app.use('/auth', authRoutes);

app.get('/', (req, res) => {
  res.json({ message: 'Hello from Express' });
});

// MongoDB Connection
mongoose.connect('mongodb+srv://admin:K7DPmvaISNvWS1l1@codenexus.d0kap.mongodb.net/?retryWrites=true&w=majority&appName=codenexus')
  .then(() => {
    console.log('Connected to MongoDB');
  })
  .catch((error) => {
    console.error('MongoDB connection error:', error);
  });

// Start server
const PORT = process.env.PORT || 8004;
app.listen(PORT, '0.0.0.0', () => {
  console.log(`Server running on port ${PORT}`);
});