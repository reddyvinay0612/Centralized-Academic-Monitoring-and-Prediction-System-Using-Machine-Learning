/**
 * Centralized Academic Monitoring and Prediction System (CAMPS-ML)
 * Express REST API Server Entry Point
 * VTU Capstone Project - PES Institute of Technology and Management, Shivamogga
 */

import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';

// Load environment variables
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
dotenv.config({ path: path.resolve(__dirname, '../.env') });

const app = express();
const PORT = process.env.PORT || 5000;
const CLIENT_URL = process.env.CLIENT_URL || 'http://localhost:5173';

// Security & Parsing Middleware
app.use(helmet());
app.use(
  cors({
    origin: CLIENT_URL,
    credentials: true,
    methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  })
);
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Health Check & Diagnostic Endpoint
app.get('/api/health', (req, res) => {
  res.status(200).json({
    status: 'healthy',
    project: 'CAMPS-ML Backend API',
    institution: 'PESITM Shivamogga (VTU)',
    nodeVersion: process.version,
    environment: process.env.NODE_ENV || 'development',
    mlServiceUrl: process.env.ML_SERVICE_URL || 'http://127.0.0.1:5001',
    timestamp: new Date().toISOString(),
  });
});

// Root API Welcome Route
app.get('/api', (req, res) => {
  res.status(200).json({
    message: 'Welcome to CAMPS-ML REST API. Refer to API documentation for endpoints.',
    institution: 'PES Institute of Technology & Management, Shivamogga',
  });
});

// Start Server if not imported by test suite
if (process.env.NODE_ENV !== 'test') {
  app.listen(PORT, () => {
    console.log('='.repeat(65));
    console.log(`[+] CAMPS-ML Express Server running on http://localhost:${PORT}`);
    console.log(`[+] Connected to Client URL: ${CLIENT_URL}`);
    console.log(`[+] ML Service Target:      ${process.env.ML_SERVICE_URL || 'http://127.0.0.1:5001'}`);
    console.log('='.repeat(65));
  });
}

export default app;
