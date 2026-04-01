const express = require('express');
const Database = require('better-sqlite3');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 5000;

// Ensure data directory exists
const dataDir = path.join(__dirname, 'data');
if (!fs.existsSync(dataDir)) fs.mkdirSync(dataDir, { recursive: true });

// Initialize SQLite
const dbPath = path.join(dataDir, 'oil_markets.db');
const db = new Database(dbPath);

db.exec(`
  CREATE TABLE IF NOT EXISTS readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    value REAL NOT NULL,
    wti_price REAL,
    brent_price REAL
  )
`);
db.exec('CREATE INDEX IF NOT EXISTS idx_readings_timestamp ON readings(timestamp)');

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// GET /api/current — current index value + WTI + Brent
app.get('/api/current', (req, res) => {
  try {
    const latest = db.prepare(
      'SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1'
    ).get();

    const previous = db.prepare(
      'SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1 OFFSET 1'
    ).get();

    // Get 24h ago reading for threat level
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
    const dayAgoReading = db.prepare(
      'SELECT * FROM readings WHERE timestamp <= ? ORDER BY timestamp DESC LIMIT 1'
    ).get(oneDayAgo);

    if (!latest) {
      return res.json({ error: 'No data available' });
    }

    let change = 0;
    let changePercent = 0;
    if (previous) {
      change = latest.value - previous.value;
      changePercent = ((change / previous.value) * 100);
    }

    let threatLevel = 'stable';
    let threatPercent = 0;
    if (dayAgoReading) {
      threatPercent = ((latest.value - dayAgoReading.value) / dayAgoReading.value) * 100;
      if (threatPercent <= -10) threatLevel = 'critical';
      else if (threatPercent <= -5) threatLevel = 'high';
      else if (threatPercent <= -2) threatLevel = 'elevated';
      else threatLevel = 'stable';
    }

    res.json({
      index_value: latest.value,
      wti_price: latest.wti_price,
      brent_price: latest.brent_price,
      timestamp: latest.timestamp,
      change: Math.round(change * 100) / 100,
      change_percent: Math.round(changePercent * 100) / 100,
      threat_level: threatLevel,
      threat_percent: Math.round(threatPercent * 100) / 100,
      wti_change_percent: 0,
      brent_change_percent: 0
    });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// GET /api/history?range=1H|1D|1W|1Y|MAX
app.get('/api/history', (req, res) => {
  try {
    const range = req.query.range || '1Y';
    let since;
    const now = new Date();

    switch (range) {
      case '1H':
        since = new Date(now - 60 * 60 * 1000).toISOString();
        break;
      case '1D':
        since = new Date(now - 24 * 60 * 60 * 1000).toISOString();
        break;
      case '1W':
        since = new Date(now - 7 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case '1Y':
        since = new Date(now - 365 * 24 * 60 * 60 * 1000).toISOString();
        break;
      case 'MAX':
        since = '1900-01-01T00:00:00.000Z';
        break;
      default:
        since = new Date(now - 365 * 24 * 60 * 60 * 1000).toISOString();
    }

    // For MAX, sample data to avoid sending too many points
    let readings;
    if (range === 'MAX') {
      // Sample ~2000 points evenly
      const total = db.prepare('SELECT COUNT(*) as c FROM readings WHERE timestamp >= ?').get(since).c;
      if (total > 2000) {
        const nth = Math.ceil(total / 2000);
        readings = db.prepare(`
          SELECT timestamp, value, wti_price, brent_price 
          FROM readings 
          WHERE timestamp >= ? AND id % ? = 0
          ORDER BY timestamp ASC
        `).all(since, nth);
      } else {
        readings = db.prepare(
          'SELECT timestamp, value, wti_price, brent_price FROM readings WHERE timestamp >= ? ORDER BY timestamp ASC'
        ).all(since);
      }
    } else if (range === '1Y') {
      // For 1Y, daily data — keep all
      readings = db.prepare(
        'SELECT timestamp, value, wti_price, brent_price FROM readings WHERE timestamp >= ? ORDER BY timestamp ASC'
      ).all(since);
    } else {
      readings = db.prepare(
        'SELECT timestamp, value, wti_price, brent_price FROM readings WHERE timestamp >= ? ORDER BY timestamp ASC'
      ).all(since);
    }

    // Also get previous close for change calculation on price cards
    const firstReading = readings.length > 0 ? readings[0] : null;

    res.json({ readings, firstReading });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// POST /api/readings — store new reading
app.post('/api/readings', (req, res) => {
  try {
    const { value, wti_price, brent_price } = req.body;
    if (value == null) return res.status(400).json({ error: 'value required' });

    // Glitch protection: reject >20% drops
    const last = db.prepare('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1').get();
    if (last && value < last.value * 0.8) {
      return res.status(400).json({ error: 'Rejected: >20% drop (glitch protection)' });
    }

    // Duplicate prevention: only store if value changed by >0.5
    if (last && Math.abs(value - last.value) < 0.5) {
      return res.json({ status: 'skipped', reason: 'value change < 0.5' });
    }

    const timestamp = new Date().toISOString();
    db.prepare(
      'INSERT INTO readings (timestamp, value, wti_price, brent_price) VALUES (?, ?, ?, ?)'
    ).run(timestamp, value, wti_price || null, brent_price || null);

    res.json({ status: 'ok', timestamp, value });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Fetch fresh data from yfinance
function fetchAndStore() {
  try {
    const pythonPath = path.join(__dirname, 'fetch_oil.py');
    const result = execSync(`python3 "${pythonPath}"`, {
      timeout: 30000,
      encoding: 'utf-8'
    });
    const data = JSON.parse(result.trim());
    if (data.error) {
      console.error('Fetch error:', data.error);
      return;
    }

    // Glitch protection
    const last = db.prepare('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1').get();
    if (last && data.index_value < last.value * 0.8) {
      console.warn('Rejected: >20% drop', data.index_value, 'vs', last.value);
      return;
    }

    // Duplicate prevention
    if (last && Math.abs(data.index_value - last.value) < 0.5) {
      return;
    }

    const timestamp = new Date().toISOString();
    db.prepare(
      'INSERT INTO readings (timestamp, value, wti_price, brent_price) VALUES (?, ?, ?, ?)'
    ).run(timestamp, data.index_value, data.wti_price, data.brent_price);

    console.log(`[${new Date().toLocaleTimeString()}] Stored: Index=${data.index_value} WTI=$${data.wti_price} Brent=$${data.brent_price}`);
  } catch (err) {
    console.error('Fetch error:', err.message);
  }
}

// Schedule fetching every 60 seconds
setInterval(fetchAndStore, 60000);

// Initial fetch on startup
setTimeout(fetchAndStore, 5000);

app.listen(PORT, () => {
  console.log(`Oil Markets Index Dashboard running on http://localhost:${PORT}`);
});
