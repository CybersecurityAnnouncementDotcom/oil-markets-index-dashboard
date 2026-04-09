const express = require('express');
const Database = require('better-sqlite3');
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');
const { rateLimiter } = require('./rate-limiter');

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
// ---------------------------------------------------------------------------
// Rate limiting — defense in depth (also rate-limited at nginx level)
// ---------------------------------------------------------------------------
const apiLimiter = rateLimiter({ windowMs: 60000, max: 60, message: 'Too many API requests. Please wait a moment.' });
const exportLimiter = rateLimiter({ windowMs: 60000, max: 5, message: 'Export rate limit exceeded. Please wait before exporting again.' });
const authLimiter = rateLimiter({ windowMs: 60000, max: 10, message: 'Too many auth attempts. Please wait.' });


// ---------------------------------------------------------------------------
// Auth helpers — nginx sets X-Auth-* headers from the auth_request subrequest
// ---------------------------------------------------------------------------

// API key validation helper — calls auth server at localhost:5010
// Passes this dashboard's Stripe product ID so the auth server verifies
// the user actually has a subscription covering this specific dashboard.
const DASHBOARD_PRODUCT_ID = 'prod_UGE7bG3qM4Bz2I'; // Oil Markets Index

function validateApiKeyRemote(apiKey) {
  return new Promise((resolve) => {
    const url = `http://localhost:5010/auth/validate-key?key=${encodeURIComponent(apiKey)}&product=${encodeURIComponent(DASHBOARD_PRODUCT_ID)}`;
    require('http').get(url, (resp) => {
      let data = '';
      resp.on('data', chunk => data += chunk);
      resp.on('end', () => {
        try { resolve(JSON.parse(data)); } catch(e) { resolve({ valid: false }); }
      });
    }).on('error', () => resolve({ valid: false }));
  });
}

// API key cache: key -> { tier, email, expires }
const apiKeyCache = new Map();

/**
 * Middleware: require any authenticated user (Basic or Pro).
 * Method 1: nginx sets X-Auth-Plan-Tier (cookie-based flow — unchanged).
 * Method 2: X-API-Key header (direct programmatic access, validated via auth server).
 */
async function requireAuth(req, res, next) {
  // Method 1: nginx auth (existing cookie-based flow)
  const tier = req.headers['x-auth-plan-tier'];
  if (tier) {
    req.planTier = tier;
    return next();
  }

  // Method 2: API key (direct programmatic access)
  const apiKey = req.headers['x-api-key'];
  if (apiKey) {
    // Check cache first
    const cached = apiKeyCache.get(apiKey);
    if (cached && cached.expires > Date.now()) {
      req.planTier = cached.tier;
      return next();
    }

    try {
      const data = await validateApiKeyRemote(apiKey);
      if (data.valid) {
        // Cache for 60 seconds
        apiKeyCache.set(apiKey, { tier: data.tier, email: data.email, expires: Date.now() + 60000 });
        req.planTier = data.tier;
        return next();
      }
    } catch(e) { /* auth server unreachable */ }

    return res.status(401).json({ error: 'Invalid API key' });
  }

  return res.status(401).json({ error: 'Authentication required. Access this dashboard through the website.' });
}

/**
 * Middleware: require Pro tier subscription.
 */
function requirePro(req, res, next) {
  if (!req.planTier) {
    return res.status(401).json({ error: 'Authentication required.' });
  }
  if (req.planTier !== 'pro') {
    return res.status(403).json({ error: 'Pro subscription required for API access. Upgrade at https://quantitativegenius.com' });
  }
  next();
}

// GET /api/user-tier — returns the user's plan tier (used by frontend to show/hide Pro features)
app.get('/api/user-tier', apiLimiter, requireAuth, (req, res) => {
  res.json({ tier: req.planTier });
});

// GET /api/current — current index value + WTI + Brent
app.get('/api/current', apiLimiter, requireAuth, (req, res) => {
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
app.get('/api/history', apiLimiter, requireAuth, (req, res) => {
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

    // For MAX/1Y, aggregate to weekly averages for smooth chart lines
    let readings;
    if (range === 'MAX' || range === '1Y') {
      readings = db.prepare(`
        SELECT 
          MIN(timestamp) as timestamp,
          ROUND(AVG(value), 2) as value,
          ROUND(AVG(wti_price), 2) as wti_price,
          ROUND(AVG(brent_price), 2) as brent_price
        FROM readings 
        WHERE timestamp >= ?
        GROUP BY strftime('%Y-%W', timestamp)
        ORDER BY timestamp ASC
      `).all(since);
      // Append the very latest reading so the chart extends to today
      const latestReading = db.prepare('SELECT timestamp, value, wti_price, brent_price FROM readings ORDER BY timestamp DESC LIMIT 1').get();
      if (latestReading && (readings.length === 0 || readings[readings.length - 1].timestamp !== latestReading.timestamp)) {
        readings.push(latestReading);
      }
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

// S&P 500 data from world markets DB for overlay
const worldDbPath = path.join(__dirname, '..', 'world-markets-index-dashboard', 'data', 'world_markets.db');
app.get('/api/sp500-history', apiLimiter, requireAuth, (req, res) => {
  try {
    const worldDb = require('better-sqlite3')(worldDbPath, { readonly: true });
    const range = req.query.range || 'MAX';
    const now = new Date();
    let rows;
    switch(range) {
      case '1H': {
        const since = new Date(now - 3600000).toISOString();
        rows = worldDb.prepare('SELECT timestamp, price as value FROM country_data WHERE ticker = ? AND timestamp >= ? ORDER BY timestamp ASC').all('^GSPC', since);
        break;
      }
      case '1D': {
        const since = new Date(now - 86400000).toISOString();
        rows = worldDb.prepare('SELECT timestamp, price as value FROM country_data WHERE ticker = ? AND timestamp >= ? ORDER BY timestamp ASC').all('^GSPC', since);
        break;
      }
      case '1W': {
        const since = new Date(now - 7 * 86400000).toISOString();
        rows = worldDb.prepare('SELECT timestamp, price as value FROM country_data WHERE ticker = ? AND timestamp >= ? ORDER BY timestamp ASC').all('^GSPC', since);
        break;
      }
      default: {
        // 1Y and MAX: use date-only comparison for daily backfill data
        let since;
        if (range === '1Y') since = new Date(now - 365 * 86400000).toISOString().split('T')[0];
        else since = '1986-01-01';
        rows = worldDb.prepare('SELECT timestamp, price as value FROM country_data WHERE ticker = ? AND timestamp >= ? ORDER BY timestamp ASC').all('^GSPC', since);
      }
    }
    worldDb.close();
    res.json({ readings: rows });
  } catch(err) {
    res.json({ readings: [] });
  }
});

// POST /api/readings — store new reading (internal only — called by fetch script on localhost)
app.post('/api/readings', (req, res) => {
  // Only allow from localhost (server's own fetch script)
  const ip = req.ip || req.connection.remoteAddress;
  if (ip !== '127.0.0.1' && ip !== '::1' && ip !== '::ffff:127.0.0.1') {
    return res.status(403).json({ error: 'Internal endpoint' });
  }
  try {
    const { value, wti_price, brent_price } = req.body;
    if (value == null) return res.status(400).json({ error: 'value required' });

    // Glitch protection: reject >20% drops
    const last = db.prepare('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 1').get();
    if (last && value < last.value * 0.8) {
      return res.status(400).json({ error: 'Rejected: >20% drop (glitch protection)' });
    }

    // Duplicate prevention: only store if value changed by >0.01
    if (last && Math.abs(value - last.value) < 0.01) {
      return res.json({ status: 'skipped', reason: 'value change < 0.01' });
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

// ---------------------------------------------------------------------------
// Pro-only: CSV/JSON export endpoints
// Serve pre-generated files from data/exports/ when available,
// fall back to live DB queries if files don't exist yet.
// ---------------------------------------------------------------------------

const EXPORT_DIR = path.join(__dirname, 'data', 'exports');
const DAILY_DIR = path.join(EXPORT_DIR, 'daily');

// Helper: try to serve a pre-generated file, return false if not found
function tryServeFile(filePath, contentType, downloadName, res) {
  if (fs.existsSync(filePath)) {
    res.setHeader('Content-Type', contentType);
    res.setHeader('Content-Disposition', `attachment; filename="${downloadName}"`);
    res.setHeader('X-Export-Source', 'pre-generated');
    return res.sendFile(filePath);
  }
  return false;
}

// --- JSON export ---
app.get('/api/export/json', exportLimiter, requireAuth, requirePro, (req, res) => {
  try {
    const range = req.query.range || 'MAX';

    // Try pre-generated files first
    if (range === 'MAX') {
      const file = path.join(EXPORT_DIR, 'oil-markets-history.json');
      if (fs.existsSync(file)) return tryServeFile(file, 'application/json', 'oil-markets-index-MAX.json', res);
    }

    // Check for today's daily snapshot
    const today = new Date().toISOString().split('T')[0];
    if (range === '1D' || range === 'latest') {
      const file = path.join(DAILY_DIR, `${today}.json`);
      if (fs.existsSync(file)) return tryServeFile(file, 'application/json', `oil-markets-index-${today}.json`, res);
    }

    // Latest snapshot
    const latestFile = path.join(EXPORT_DIR, 'oil-markets-latest.json');
    if (range === 'latest' && fs.existsSync(latestFile)) {
      return tryServeFile(latestFile, 'application/json', 'oil-markets-latest.json', res);
    }

    // Fallback: live DB query — consolidated to 1 row per day
    const now = new Date();
    let since = '1900-01-01T00:00:00.000Z';
    switch (range) {
      case '1W': since = new Date(now - 7 * 86400000).toISOString(); break;
      case '1M': since = new Date(now - 30 * 86400000).toISOString(); break;
      case '1Y': since = new Date(now - 365 * 86400000).toISOString(); break;
      case 'MAX': default: since = '1900-01-01T00:00:00.000Z';
    }

    const readings = db.prepare(`
      SELECT date(timestamp) as date, MAX(timestamp) as timestamp,
             value as index_value, wti_price, brent_price
      FROM readings WHERE timestamp >= ?
      GROUP BY date(timestamp) ORDER BY date ASC
    `).all(since);

    res.setHeader('Content-Disposition', `attachment; filename="oil-markets-index-${range}.json"`);
    res.setHeader('X-Export-Source', 'live-query');
    res.json({ export_date: new Date().toISOString(), range, record_count: readings.length, data: readings });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// --- CSV export ---
app.get('/api/export/csv', exportLimiter, requireAuth, requirePro, (req, res) => {
  try {
    const range = req.query.range || 'MAX';

    // Try pre-generated files first
    if (range === 'MAX') {
      const file = path.join(EXPORT_DIR, 'oil-markets-history.csv');
      if (fs.existsSync(file)) return tryServeFile(file, 'text/csv', 'oil-markets-index-MAX.csv', res);
    }

    const today = new Date().toISOString().split('T')[0];
    if (range === '1D' || range === 'latest') {
      const file = path.join(DAILY_DIR, `${today}.csv`);
      if (fs.existsSync(file)) return tryServeFile(file, 'text/csv', `oil-markets-index-${today}.csv`, res);
    }

    const latestFile = path.join(EXPORT_DIR, 'oil-markets-latest.csv');
    if (range === 'latest' && fs.existsSync(latestFile)) {
      return tryServeFile(latestFile, 'text/csv', 'oil-markets-latest.csv', res);
    }

    // Fallback: live DB query — consolidated to 1 row per day
    const now = new Date();
    let since = '1900-01-01T00:00:00.000Z';
    switch (range) {
      case '1W': since = new Date(now - 7 * 86400000).toISOString(); break;
      case '1M': since = new Date(now - 30 * 86400000).toISOString(); break;
      case '1Y': since = new Date(now - 365 * 86400000).toISOString(); break;
      case 'MAX': default: since = '1900-01-01T00:00:00.000Z';
    }

    const readings = db.prepare(`
      SELECT date(timestamp) as date, MAX(timestamp) as timestamp,
             value as index_value, wti_price, brent_price
      FROM readings WHERE timestamp >= ?
      GROUP BY date(timestamp) ORDER BY date ASC
    `).all(since);

    let csv = 'date,index_value,wti_price,brent_price\n';
    for (const r of readings) {
      csv += `${r.date},${r.index_value},${r.wti_price || ''},${r.brent_price || ''}\n`;
    }

    res.setHeader('Content-Type', 'text/csv');
    res.setHeader('Content-Disposition', `attachment; filename="oil-markets-index-${range}.csv"`);
    res.setHeader('X-Export-Source', 'live-query');
    res.send(csv);
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
    if (last && Math.abs(data.index_value - last.value) < 0.01) {
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

// ---------------------------------------------------------------------------
// Auth proxy: forward /api/auth/* to auth server at localhost:5010
// Avoids cross-origin issues when dashboard fetches API key endpoints
// ---------------------------------------------------------------------------

function proxyToAuth(method) {
  return (req, res) => {
    const authPath = req.path.replace('/api/auth', '/auth');
    const options = {
      hostname: 'localhost',
      port: 5010,
      path: authPath,
      method: method,
      headers: { cookie: req.headers.cookie || '' },
    };
    const proxyReq = require('http').request(options, (proxyRes) => {
      let data = '';
      proxyRes.on('data', chunk => data += chunk);
      proxyRes.on('end', () => {
        res.status(proxyRes.statusCode);
        if (proxyRes.headers['set-cookie']) {
          res.setHeader('set-cookie', proxyRes.headers['set-cookie']);
        }
        res.setHeader('Content-Type', 'application/json');
        res.send(data);
      });
    });
    proxyReq.on('error', () => {
      res.status(502).json({ error: 'Auth server unreachable' });
    });
    proxyReq.end();
  };
}

app.get('/api/auth/api-key-status', authLimiter, proxyToAuth('GET'));
app.post('/api/auth/api-key', authLimiter, proxyToAuth('POST'));
app.delete('/api/auth/api-key', authLimiter, proxyToAuth('DELETE'));

app.listen(PORT, () => {
  console.log(`Oil Markets Index Dashboard running on http://localhost:${PORT}`);
});
