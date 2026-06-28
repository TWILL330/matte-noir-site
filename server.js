// Local dev server — mirrors what Vercel's serverless function does.
// Usage: HOOKLAYER_API_KEY=hl_xxx node server.js
const express = require('express');
const path = require('path');
const handler = require('./api/index.js');

const app = express();
app.use(express.json());
app.use(express.static(path.join(__dirname)));

// Route all /api requests through the handler
app.all('/api', (req, res) => handler(req, res));
app.all('/api/*', (req, res) => handler(req, res));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Viral Studio running at http://localhost:${PORT}`));
