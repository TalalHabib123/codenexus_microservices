const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const cookieParser = require('cookie-parser');
const session = require('express-session');
require('dotenv').config();


const authRoutes = require('./routes/auth.route');
const projectRoutes = require('./routes/project.route');
const scanRoutes = require('./routes/scan.route');
const graphRoutes = require('./routes/graph.route'); 
const logRoutes = require('./routes/log.route');
// Create Express app
const app = express();

// Middleware


app.use(cors({
  origin: process.env.FRONTEND_URL || 'http://localhost:5173',
  credentials: true // Important for cookies
}));

app.use(cookieParser());
app.use(express.json({ limit: '500mb' }));
app.use(session({
  secret: process.env.SESSION_SECRET || 'your-secret-key',
  resave: false,
  saveUninitialized: false,
  cookie: {
    secure: process.env.NODE_ENV === 'production', // Use secure cookies in production
    httpOnly: true,
    maxAge: 7 * 24 * 60 * 60 * 1000 // 7 days
  }
}));


// Routes
app.use('/auth', authRoutes);
app.use('/project', projectRoutes);
app.use('/scan', scanRoutes);
app.use('/graph', graphRoutes);
app.use('/logs', logRoutes);
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