<!-- MANDATORY: This filename MUST include the version number (e.g., QG-Deployment-Guide-v4.9.md). -->
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- SAFETY: Always use `git fetch origin main` + `git checkout origin/main -- <file>` on VPS. NEVER use `git pull` or `git checkout main`. -->
<!-- SAFETY: Pre-generated export files in data/exports/ are served BEFORE live DB queries. Update generate_exports.py AND regenerate when changing export logic. -->

# QuantitativeGenius.com · Deployment Guide

| Field | Value |
|---|---|
| **Last Updated** | April 2026 |
| **Version** | 7.0 (v6.0 + Thread 25: Nightly export cron, WAL mode fix, PM2 cleanup) |
| **Author** | QuantitativeGenius / Perplexity Computer |

---

## ·· STOP · READ BEFORE ANY VPS WORK ··

1. Run `source ~/deploy-guard.sh <world|oil|cyber>` **BEFORE** touching any file on VPS. No exceptions.
2. **NEVER** `git reset --hard` while PM2 is running. It corrupts SQLite databases.
3. **NEVER** `sed`, `python3 -c`, or direct-patch files on VPS. Push to GitHub first, then `git fetch` + `git checkout origin/main -- <file>`.
4. **NEVER** `git pull`. Use `git fetch origin main` + `git checkout origin/main -- <file>`.
5. Run `source ~/deploy-done.sh <world|oil|cyber>` **AFTER** deployment. It restarts PM2 and verifies integrity.
6. If you skip these steps, you will corrupt a database. It has happened on April 6, April 7, and April 8, 2026.

---

## Table of Contents

1. Infrastructure Overview
2. GitHub Repositories
3. VPS Directory Structure
4. Regular Deployment Process
5. Deploying Individual Dashboards
6. Deploying the Landing Page
7. Deploying the Auth System
8. Deploying Paywall Pages
9. PM2 Process Management
10. Nginx Configuration
11. SSL Certificate Renewal
12. Troubleshooting
13. API Key System Deployment (April 7, 2026)
14. Bitcoin Overlay Deployment (Thread 24)
15. Swap File Deployment (Thread 24)
16. Deploy Guard Reminder
17. Documentation Deployment

---

## 1. Infrastructure Overview

| Component | Detail |
|---|---|
| VPS IP | 136.117.206.145 |
| Domain | quantitativegenius.com (DNS via NameBright) |
| SSL | Let's Encrypt wildcard, expires July 1, 2026 |
| OS | Linux (Google Cloud VPS, e2-micro) |
| RAM | ~958MB physical + 2GB swap (added April 8, 2026) |
| Web Server | Nginx |
| Process Manager | PM2 |
| Runtime | Node.js |
| Email | service@quantitativegenius.com via Resend API (replies forward to support@quantitativegenius.com) |

### Subdomains & Port Mapping

| Subdomain | Service | Port | PM2 User |
|---|---|---|---|
| quantitativegenius.com | Landing Page (static) | N/A (Nginx serves directly) | N/A |
| oil.quantitativegenius.com | Oil Markets Index Dashboard | 5000 | support |
| world.quantitativegenius.com | World Markets Index Dashboard | 5001 | support |
| cyber.quantitativegenius.com | Cybersecurity Threat Index Dashboard | 5002 | support |
| quantitativegenius.com/paywall-gate/ | Paywall pages (static) | N/A | N/A |
| Auth API (internal) | Authentication & Stripe | 5010 | root |

---

## 2. GitHub Repositories

| Repository | Visibility | Branch | Description |
|---|---|---|---|
| CybersecurityAnnouncementDotcom/qg-auth | PRIVATE | master | Auth system (magic links, Stripe webhooks, session management) |
| CybersecurityAnnouncementDotcom/qg-deploy | PRIVATE | master | Landing page, paywall HTMLs, Nginx config |
| CybersecurityAnnouncementDotcom/oil-markets-index-dashboard | PUBLIC | main | Oil Markets Index Dashboard |
| CybersecurityAnnouncementDotcom/world-markets-index-dashboard | PUBLIC | main | World Markets Index Dashboard |
| CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard | PUBLIC | main | Cybersecurity Threat Index Dashboard |

### Git Config

```bash
git config user.email "jq_007@yahoo.com"
git config user.name "QuantitativeGenius"
```

---

## 3. VPS Directory Structure

```
/var/www/quantitativegenius.com/
    index.html                          · Landing page (from qg-deploy)

/var/www/paywall-gate/
    index.html                          · Cyber paywall (default)
    oil.html                            · Oil paywall
    world.html                          · World paywall

/home/support/
    oil-markets-index-dashboard/        · Oil dashboard app
        server.js
        fetch_oil.py
        public/
        data/oil_markets.db
        data/exports/                   · Pre-generated export files (VPS only)

    world-markets-index-dashboard/      · World dashboard app
        server.js
        fetch_data.py
        public/
        data/world_markets.db
        data/exports/                   · Pre-generated export files (VPS only)

    cybersecurity-threat-index-dashboard/   · Cyber dashboard app
        server.js
        seed_data.py
        public/
        data/cybersecurity.db

    deploy-guard.sh                     · MANDATORY before any VPS file change
    deploy-done.sh                      · MANDATORY after any deployment

/opt/qg-auth/                           · Auth server
    auth-server.js
    auth-routes.js
    auth-middleware.js
    magic-link.js
    stripe-webhook.js
    setup-db.js
    migrate-add-tier.js
    ecosystem.config.js                 · Contains API keys (Stripe, Resend)

/etc/nginx/sites-enabled/dashboards    · Nginx config for all subdomains
/etc/nginx/snippets/rate-limit.conf    · Nginx rate limiting zones
/swapfile                              · 2GB swap file (permanent via /etc/fstab)
```

---

## 4. Regular Deployment Process

### Method A: Git Fetch + Checkout on VPS (Preferred)

> **CRITICAL (Thread 19 Fix):** NEVER use `git pull`. NEVER use `git checkout main --`. Always use `git fetch origin main` + `git checkout origin/main -- <file>`.

Complete deployment sequence (v4.8+, deploy-guard MANDATORY):

```bash
# 1. Make code changes locally · push to GitHub

# 2. SSH to VPS:
ssh -o StrictHostKeyChecking=no support@136.117.206.145

# 3. MANDATORY: Run deploy-guard FIRST (stops PM2, backs up DB, integrity check)
source ~/deploy-guard.sh <world|oil|cyber>

# 4. Set git config (required every session)
git config --global user.email "jq_007@yahoo.com"
git config --global user.name "QuantitativeGenius"

# 5. Pull from GitHub
cd /home/support/<dashboard-repo>
git fetch origin main
git checkout origin/main -- <files>

# 6. Validate (always grep before restart)
grep -c DASHBOARD_PRODUCT_ID server.js

# 7. MANDATORY: Run deploy-done (restarts PM2, health check, integrity check)
source ~/deploy-done.sh <world|oil|cyber>
```

> **CRITICAL (v4.8):** NEVER skip deploy-guard.sh. NEVER run `git reset --hard` while PM2 is running.

### Method B: Transfer Site (When Git Pull Is Not Available)

When the VPS doesn't have Git credentials set up, or a file needs to be transferred directly:

1. In Perplexity Computer workspace: Create/update the file, then deploy a temporary transfer site.
2. On the VPS: Use `curl` or `wget` to download from the transfer URL.

```bash
cd /home/support/oil-markets-index-dashboard && \
curl -sL "TRANSFER_URL/server.js" -o server.js && \
pm2 delete oil-dashboard && pm2 start server.js --name oil-dashboard
```

### Method C: Base64-Embedded Deploy Script (Preferred for Multi-File Updates)

For deploying multiple files at once when VPS has no git access to the repos:

1. In Perplexity Computer: Make changes across repos, commit & push to GitHub
2. Generate a `.sh` script that base64-encodes all changed files inline
3. User uploads the script to VPS via Google Cloud SSH-in-browser "Upload File" button
4. User runs the script on VPS

**Important deployment script conventions:**
- Script filename must be unique and descriptive (e.g., `deploy-cors-fix.sh`, not `deploy.sh`)
- Uploaded files land in the SSH user's home directory (e.g., `/home/support/`)
- Dashboard scripts must run as support user: `sudo -u support bash /home/support/deploy-xyz.sh`
- Auth scripts must run as root: `sudo bash /home/support/deploy-xyz.sh`
- Scripts should back up existing files before overwriting
- Scripts should restart PM2 by ID (cyber=0, world=1, oil=2, auth=varies), not by name
- Scripts should verify all processes are online at the end

### Method D: Direct SSH from Perplexity Computer (Preferred · April 7, 2026+)

Perplexity Computer can SSH directly into the VPS from its sandbox.

**Setup for new session:**

```bash
# In Perplexity Computer sandbox:
ssh-keygen -t ed25519 -f /home/user/.ssh/id_ed25519 -N '' -C 'computer-agent'
# Then add the public key to VPS authorized_keys (requires user assistance for first session)
```

**Key details:**
- SSH key is ephemeral per sandbox session · a new key must be generated and added at the start of each new Perplexity Computer session
- Key comment: `computer-agent`
- Key type: ed25519, located at `/home/user/.ssh/id_ed25519` in the sandbox
- Connection: `ssh -o StrictHostKeyChecking=no support@136.117.206.145`
- Root operations (auth system, nginx): not available directly — support user has no passwordless sudo

---

## 5. Deploying Individual Dashboards

### Oil Markets Index Dashboard

```bash
# STEP 1: MANDATORY deploy-guard
source ~/deploy-guard.sh oil

# STEP 2: Set git config
git config --global user.email "jq_007@yahoo.com" && git config --global user.name "QuantitativeGenius"

# STEP 3: Pull from GitHub
cd /home/support/oil-markets-index-dashboard
git fetch origin main
git checkout origin/main -- server.js public/index.html

# STEP 4: Validate
grep -c 'DASHBOARD_PRODUCT_ID' server.js
# Also validate BTC endpoint if deploying Thread 24 changes:
grep -c 'bitcoin' server.js

# STEP 5: MANDATORY deploy-done
source ~/deploy-done.sh oil
```

**Key files:**
- `server.js` · Express server, SQLite, yfinance + BTC fetch every 60s, auth middleware, export endpoints
- `fetch_oil.py` · Python script to get WTI/Brent prices
- `public/index.html` · Frontend dashboard + Pro export UI + BTC toggle (Thread 24)
- `data/oil_markets.db` · SQLite database (DO NOT delete)
- `data/exports/` · Pre-generated export files (VPS only, not in GitHub)

If pm2 process doesn't exist, start fresh:

```bash
pm2 start server.js --name oil-dashboard
pm2 save
```

### World Markets Index Dashboard

```bash
# STEP 1: MANDATORY deploy-guard
source ~/deploy-guard.sh world

# STEP 2: Set git config
git config --global user.email "jq_007@yahoo.com" && git config --global user.name "QuantitativeGenius"

# STEP 3: Pull from GitHub
cd /home/support/world-markets-index-dashboard
git fetch origin main
git checkout origin/main -- server.js public/index.html generate_exports.py

# STEP 4: Validate (also regenerate exports if export logic changed)
grep -c 'DASHBOARD_PRODUCT_ID' server.js
# If generate_exports.py changed or after any DB modification:
python3 generate_exports.py

# STEP 5: MANDATORY deploy-done
source ~/deploy-done.sh world
```

**Key files:**
- `server.js` · Express server, 20-ticker composite, yfinance + BTC fetch every 60s, auth middleware, export endpoints, Pro API endpoints
- `fetch_data.py` · Python script for all 20 tickers
- `generate_exports.py` · Daily CSV/JSON export generator (run by PM2 cron)
- `ecosystem.config.js` · PM2 config for dashboard + daily export cron
- `public/index.html` · Frontend with 3-line chart + BTC toggle (Thread 24) + Pro export UI
- `data/world_markets.db` · SQLite database (DO NOT delete)
- `data/exports/` · Pre-generated export files (VPS only, not in GitHub)

### Cybersecurity Threat Index Dashboard

```bash
# STEP 1: MANDATORY deploy-guard
source ~/deploy-guard.sh cyber

# STEP 2: Set git config
git config --global user.email "jq_007@yahoo.com" && git config --global user.name "QuantitativeGenius"

# STEP 3: Pull from GitHub
cd /home/support/cybersecurity-threat-index-dashboard
git fetch origin main
git checkout origin/main -- server.js public/index.html

# STEP 4: Validate
grep -c 'DASHBOARD_PRODUCT_ID' server.js

# STEP 5: MANDATORY deploy-done
source ~/deploy-done.sh cyber
```

**Key files:**
- `server.js` · Express server, reads from seeded database, auth middleware, export endpoints
- `seed_data.py` · Seeds 123 months of data (Jan 2016 - Mar 2026)
- `add_events.py` · Adds recent events/commentary
- `public/index.html` · Frontend with threat gauge + distribution + Pro export UI
- `data/cybersecurity.db` · SQLite database (DO NOT delete)

Note: Daily 6AM cron for cyber data refresh is currently PAUSED.

---

## 6. Deploying the Landing Page

```bash
# SSH as root (need write access to /var/www/)
ssh root@136.117.206.145
cd /tmp
git clone https://github.com/CybersecurityAnnouncementDotcom/qg-deploy.git
cp /tmp/qg-deploy/landing-index.html /var/www/quantitativegenius.com/index.html
rm -rf /tmp/qg-deploy
```

Or via transfer site:

```bash
curl -sL "TRANSFER_URL/landing-index.html" -o /var/www/quantitativegenius.com/index.html
```

---

## 7. Deploying the Auth System

Auth files must be embedded inline in deploy scripts — VPS has no GitHub credentials for private repos.

```bash
# SSH as root
ssh root@136.117.206.145
# Auth files must be embedded inline in deploy scripts · VPS has no GitHub credentials for private repos
pm2 restart 0  # qg-auth (verify ID with pm2 list first)
```

**Auth server location:** `/opt/qg-auth/`

---

## 8. Deploying Paywall Pages

```bash
# SSH as root
ssh root@136.117.206.145
cd /tmp
git clone https://github.com/CybersecurityAnnouncementDotcom/qg-deploy.git
cp /tmp/qg-deploy/cyber-paywall.html /var/www/paywall-gate/index.html
cp /tmp/qg-deploy/oil-paywall.html /var/www/paywall-gate/oil.html
cp /tmp/qg-deploy/world-paywall.html /var/www/paywall-gate/world.html
rm -rf /tmp/qg-deploy
```

---

## 9. PM2 Process Management

### View All Processes

```bash
# As support user (dashboards)
su - support
pm2 list

# As root (auth server)
pm2 list
```

### Common PM2 Commands

```bash
pm2 restart <name>       # Restart a process
pm2 stop <name>          # Stop a process
pm2 delete <name>        # Remove from PM2
pm2 logs <name>          # View logs
pm2 logs <name> --lines 50  # Last 50 log lines
pm2 save                 # Save current process list
pm2 startup              # Set PM2 to start on boot
```

### Current PM2 Process Names & IDs (as of April 8, 2026 reboot)

| PM2 Name | PM2 ID | Port | User |
|---|---|---|---|
| cyber-dashboard | 0 | 5002 | support |
| world-dashboard | 1 | 5001 | support |
| oil-dashboard | 2 | 5000 | support |
| (export crons removed) | — | — | See Section 18 |
| qg-auth | varies | 5010 | root |

> **Note:** PM2 IDs change after a full VM reboot or when processes are deleted and recreated. Always verify with `pm2 list` before using IDs. Reference by name when possible. The old `oil-export-cron` and `world-export-cron` PM2 processes were removed in Thread 25 (April 10, 2026) and replaced by a system crontab (see Section 18).

### CRITICAL: Never Auto-Restart PM2 Processes

Do NOT create any cron job, systemd timer, or script that runs `pm2 restart all` or `pm2 restart <name>` automatically. SQLite databases are corrupted when Node.js processes are killed mid-write. All restarts must be manual, through deployment scripts reviewed by a human.

Before any deployment, verify: `crontab -l` (as support user) should show only the nightly export cron (`0 4 * * * /home/support/nightly-export.sh`). No other entries should exist.

### deploy-guard.sh and deploy-done.sh (MANDATORY · April 8, 2026+)

Two scripts at `/home/support/` on VPS are MANDATORY for all deployments:

**deploy-guard.sh · Run BEFORE any VPS file modification:**

```bash
source ~/deploy-guard.sh <world|oil|cyber>
```

Does: stops PM2 process, backs up SQLite DB, runs integrity check. If integrity fails, aborts and does NOT proceed.

**deploy-done.sh · Run AFTER deployment:**

```bash
source ~/deploy-done.sh <world|oil|cyber>
```

Does: restarts PM2, runs HTTP health check, runs DB integrity check.

**Why this is mandatory:** Running `git reset --hard`, `git checkout`, `sed`, or any file write while PM2 is running can corrupt the SQLite database (Node.js holds write locks). The April 8 world DB corruption incident was caused by skipping this step.

**NEVER skip deploy-guard.sh, even for "small" changes.**

---

## 10. Nginx Configuration

Config file: `/etc/nginx/sites-enabled/dashboards`
Rate limit config: `/etc/nginx/snippets/rate-limit.conf`

After editing Nginx config:

```bash
nginx -t                  # Test configuration
systemctl reload nginx    # Apply changes
```

---

## 11. SSL Certificate Renewal

The SSL certificate covers all subdomains and expires July 1, 2026. Auto-renewal should be set up via Certbot cron. To check:

```bash
certbot certificates
```

To manually renew:

```bash
certbot renew
systemctl reload nginx
```

---

## 12. Troubleshooting

### Database Corruption Prevention (CRITICAL · April 6, 2026)

**Root Cause Identified:** An hourly cron job ran `pm2 restart all` every hour. This killed Node.js processes mid-SQLite-write, corrupting databases.

**Fix Applied:**
- Removed the auto-update cron: `crontab -r` (as support user)
- Re-backfilled world database (5,285 readings, 2006–present)
- Backfilled S&P 500 pre-2006 data (1,508 records, 2000–2006) with RAW prices into world's `country_data` table
- Restarted all dashboards

**Prevention Rules:**
1. NEVER create a cron that runs `pm2 restart all` or any automated PM2 restart
2. NEVER run backfill scripts while dashboards are running · stop PM2 first
3. ALWAYS verify `crontab -l` returns `"no crontab for support"` after any deployment
4. ALWAYS run `PRAGMA integrity_check` on all databases after any deployment
5. NEVER use `git checkout main --` · always `git checkout origin/main --` (Thread 19 fix)
6. When updating World export logic, also update `generate_exports.py` AND regenerate pre-generated files

**Cross-Dashboard Dependency:** Oil's S&P 500 overlay reads from the WORLD database (`country_data` table, ticker `^GSPC`). If the world DB is corrupted or missing, BOTH dashboards lose overlay lines. Always fix world DB first.

### Dashboard Shows No Data

1. Check PM2 logs: `pm2 logs <name> --lines 100`
2. Verify Python/yfinance is working: `cd /home/support/<dashboard> && python3 fetch_oil.py`
3. Check database: `sqlite3 data/<db>.db "SELECT COUNT(*) FROM readings;"`

### Dashboard Not Accessible

1. Check PM2 status: `pm2 list`
2. Check Nginx: `systemctl status nginx`
3. Test port directly: `curl http://localhost:5000`

### 502 Bad Gateway

PM2 process is likely down. Check and restart:

```bash
pm2 list
pm2 restart <name>
```

### Database Locked

WAL file issue. Stop process, checkpoint, restart:

```bash
pm2 stop <name>
sqlite3 data/<db>.db "PRAGMA wal_checkpoint(TRUNCATE);"
pm2 start <name>
```

### 1H/1D Charts Show No Line, Few Points, or Stale Timestamps

The 1H and 1D views only display data from the actual requested time window. If the dashboard was recently restarted or backfilled, these views may be empty or sparse until enough live readings accumulate (one reading per 60 seconds). This is expected.

### Historical Data Shows Wrong Values (Data Regression)

Root cause: Pulling updated code and restarting PM2 only fixes new data points going forward. Historical data must be recalculated by re-running backfill scripts.

```bash
# 1. Fetch latest code (NEVER use git pull)
cd /home/support/oil-markets-index-dashboard && git fetch origin main && git checkout origin/main -- backfill.py server.js
cd /home/support/world-markets-index-dashboard && git fetch origin main && git checkout origin/main -- backfill.py server.js

# 2. Stop dashboards so backfill has exclusive DB access
pm2 stop oil-dashboard
pm2 stop world-dashboard

# 3. Re-run backfills (oil requires --force flag, world auto-clears)
cd /home/support/oil-markets-index-dashboard && python3 backfill.py --force
cd /home/support/world-markets-index-dashboard && python3 backfill.py

# 4. Restart dashboards
pm2 restart oil-dashboard
pm2 restart world-dashboard
pm2 save
pm2 list
```

### Pre-Generated Export File Is Stale

If CSV/JSON exports show wrong data (e.g., wrong date ranges, missing columns):

1. Verify the `data/exports/` files are not stale
2. Stop the dashboard process via deploy-guard
3. Regenerate: `python3 generate_exports.py`
4. Restart via deploy-done

This was the root cause of the Thread 24 CSV date filter issue (World MAX CSV showed 2006-01-02 instead of 2006-01-04).

### Bitcoin Overlay Shows No Data

1. Check if `bitcoin_data` table exists: `sqlite3 data/oil_markets.db ".tables"`
2. Check table is populated: `sqlite3 data/oil_markets.db "SELECT COUNT(*) FROM bitcoin_data;"`
3. The table is created automatically by server.js on first run — no manual setup needed
4. BTC data accumulates from first deploy forward. On a fresh deploy, 1H/1D will show sparse data until readings accumulate.
5. Check PM2 logs for BTC fetch errors: `pm2 logs oil-dashboard --lines 50`

---

## 13. API Key System Deployment (April 7, 2026)

### What Was Built

- Complete API key infrastructure for Pro subscribers
- `api_keys` table with SHA-256 hash storage
- 4 auth endpoints for key management
- Key format: `qg_` + 32 hex chars (stored as SHA-256 hash, prefix shown in UI)
- One active key per user (generating new key revokes old one)
- API key access is per-product: each dashboard passes its Stripe product ID

### Deployment

The API key system is deployed as part of the auth server. Files are embedded inline in deploy scripts (no git pull needed for private repo).

**Key commits:** qg-deploy 1a66d06, cyber a3ce45a, oil bb1455a, world 4620269

### Stripe Pro Price IDs

**Current pricing (10x increase — April 11, 2026, Thread 26):**

| Tier | Monthly | Yearly |
|---|---|---|
| Individual Basic | $390/mo | $3,900/yr |
| Individual Pro | $590/mo | $5,900/yr |
| All-Access Basic | $790/mo | $7,900/yr |
| All-Access Pro | $990/mo | $9,900/yr |

**Legacy Pro Price IDs (kept for existing subscribers):**

| Product | Monthly ($59 legacy) | Yearly ($590 legacy) |
|---|---|---|
| Oil Pro | price_1THhsnKXRVV7arrHEqtwMM7L | price_1THhsnKXRVV7arrHy4W5CdKb |
| World Pro | price_1THhsoKXRVV7arrHW1dndy6D | price_1THhsoKXRVV7arrHYYV23gR5 |
| Cyber Pro | price_1THhspKXRVV7arrHunUc5LjR | price_1THhspKXRVV7arrHudiK0fRG |
| Bundle Pro | price_1THhspKXRVV7arrHdcBM4qz2 ($99/mo legacy) | price_1THhsqKXRVV7arrHi6qlZUW5 ($990/yr legacy) |

> **TODO:** After creating new Stripe prices at the 10x amounts, add the new price IDs to `PRO_PRICE_IDS` in `stripe-webhook.js` and create new Payment Links in the Stripe Dashboard. Update this table with the new IDs.

---

## 14. Bitcoin Overlay Deployment (Thread 24)

### Overview

The Bitcoin price overlay was added to both Oil and World dashboards in Thread 24. It uses native Node.js `https.get` to fetch BTC-USD from Yahoo Finance — no Python changes are needed.

### Files Modified

| Dashboard | File | Change |
|---|---|---|
| Oil | `server.js` | Added BTC fetch loop (https.get every 60s), `bitcoin_data` table creation, `/api/bitcoin-history` endpoint |
| Oil | `public/index.html` | Added ₿ toggle button, BTC chart overlay, nearest-match algorithm, right Y-axis in raw mode |
| World | `server.js` | Added BTC fetch loop (https.get every 60s), `bitcoin_data` table creation, `/api/bitcoin-history` endpoint |
| World | `public/index.html` | Added ₿ toggle button, BTC chart overlay, nearest-match algorithm, right Y-axis in raw mode |

### No Python Changes Needed

BTC fetching is implemented entirely in Node.js (native `https` module in server.js). No changes to `fetch_oil.py`, `fetch_data.py`, `backfill.py`, or `generate_exports.py` are required for the BTC fetch itself.

**Note:** `generate_exports.py` does need updating to include the `bitcoin_price` column in CSV exports — query the `bitcoin_data` table by date and join to the main readings.

### Database Setup

The `bitcoin_data` table is created **automatically by server.js on first run**. No manual migration is required.

```sql
CREATE TABLE IF NOT EXISTS bitcoin_data (
    timestamp TEXT,
    price REAL
);
```

### No Backfill Needed

BTC data accumulates from the first deploy forward. There is no historical backfill. On a fresh deploy, 1H/1D views will start empty and populate over time.

### Deployment Steps

```bash
# STEP 1: Push updated server.js and public/index.html to GitHub for both dashboards

# STEP 2: Deploy World dashboard
source ~/deploy-guard.sh world
cd /home/support/world-markets-index-dashboard
git fetch origin main
git checkout origin/main -- server.js public/index.html
# Validate BTC endpoint present:
grep -c 'bitcoin' server.js
grep -c 'bitcoin' public/index.html
source ~/deploy-done.sh world

# STEP 3: Deploy Oil dashboard
source ~/deploy-guard.sh oil
cd /home/support/oil-markets-index-dashboard
git fetch origin main
git checkout origin/main -- server.js public/index.html
# Validate BTC endpoint present:
grep -c 'bitcoin' server.js
grep -c 'bitcoin' public/index.html
source ~/deploy-done.sh oil

# STEP 4: Verify bitcoin_data table exists after restart
sqlite3 /home/support/world-markets-index-dashboard/data/world_markets.db ".tables"
sqlite3 /home/support/oil-markets-index-dashboard/data/oil_markets.db ".tables"
# Expected: bitcoin_data should appear in both
```

### Post-Deployment Verification

```bash
# Test BTC history API endpoint (requires valid session/API key)
curl -s http://localhost:5001/api/bitcoin-history?range=1H | head -c 200
curl -s http://localhost:5000/api/bitcoin-history?range=1H | head -c 200

# Check BTC data is accumulating (wait 60+ seconds after deploy)
sqlite3 /home/support/world-markets-index-dashboard/data/world_markets.db \
  "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM bitcoin_data;"
sqlite3 /home/support/oil-markets-index-dashboard/data/oil_markets.db \
  "SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM bitcoin_data;"
```

### Key Commits

| Dashboard | Commit | Description |
|---|---|---|
| World | 62d3201 | Bitcoin overlay with nearest-match algorithm |
| Oil | 815d02a | Bitcoin overlay with nearest-match algorithm |

---

## 15. Swap File Deployment (Thread 24 / April 8, 2026)

### Background

The e2-micro VPS (958MB RAM) experienced a full OOM (Out of Memory) crash on April 8, 2026, taking all three dashboards offline for ~7 hours. The root cause was no swap file configured. A 2GB swap file was created immediately after the incident as a permanent fix.

### One-Time Setup (Already Applied — Included Here for Disaster Recovery)

If rebuilding the VPS from scratch, create the swap file before starting the dashboards:

```bash
# Create swap file (requires root)
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# Make permanent across reboots
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Verification

```bash
# Verify swap is currently active
free -h
# Expected output (Swap line):
# Swap:          2.0Gi       XXXMi       XXXGi

# Verify swap persists across reboots
grep swap /etc/fstab
# Expected:
# /swapfile none swap sw 0 0
```

### Monitoring

Swap usage is part of the monthly monitoring checklist. Run `free -h` to confirm swap is still active after any VM reboot or maintenance window.

---

## 16. Deploy Guard Reminder

This section is a standalone reminder of the mandatory deployment workflow. All rules exist because of real database corruption incidents.

### ALWAYS: Pre-Deployment

```bash
# Run deploy-guard BEFORE touching any file on VPS
source ~/deploy-guard.sh <world|oil|cyber>
```

This script:
1. **Stops** the PM2 process (prevents mid-write corruption)
2. **Backs up** the SQLite database with timestamp
3. **Runs integrity check** — aborts if not `ok`

### ALWAYS: Post-Deployment

```bash
# Run deploy-done AFTER deployment is complete
source ~/deploy-done.sh <world|oil|cyber>
```

This script:
1. **Restarts** the PM2 process
2. **HTTP health check** — verifies dashboard responds HTTP 200
3. **Post-deploy integrity check** — confirms DB is intact

### NEVER: Forbidden Operations

| What | Why |
|---|---|
| `git pull` | Merges can run mid-write if PM2 is running; caused DB corruption April 6 |
| `git reset --hard` while PM2 running | Wipes working tree including live DB file; caused DB corruption April 8 |
| `sed` on VPS | Regex errors can silently corrupt config or source files |
| `python3 -c` inline patches | Unreliable; hard to audit; has caused partial writes |
| Automated PM2 restart crons | Restart during write = DB corruption; all restarts must be manual |
| Skipping deploy-guard for "small" changes | No exceptions — even a one-line change can corrupt the DB if PM2 is writing |

### Git Operations (Correct Pattern)

```bash
# CORRECT: Fetch specific file without running merge logic
git fetch origin main
git checkout origin/main -- server.js public/index.html

# WRONG: Never do this
# git pull
# git checkout main -- server.js   (uses local branch, may be stale)
# git reset --hard origin/main
```

### Version Control Discipline

- **Push to GitHub first**, then deploy to VPS.
- GitHub is the source of truth. The VPS is a deployment target, not a development environment.
- Never make edits directly on the VPS that are not first committed to the repository.
- After any `git push`, you MUST also deploy to VPS — pushing to GitHub does NOT deploy automatically.

### Deployment Order (When Deploying Multiple Components)

```
1. Auth server (qg-auth) → deploy first
2. Dashboard(s) → deploy second
3. Nginx config → deploy LAST
```

Deploying nginx last ensures the auth server and dashboards are running and healthy before traffic is routed to them.

---

## 17. Documentation Deployment

### Source of Truth

GitHub is the single source of truth for all documentation. The VPS always pulls docs from GitHub — never edit docs directly on the VPS.

Each dashboard repo has a `docs/` directory containing:
- The dashboard's methodology PDF (e.g., `Oil_Market_Index_Methodology_v4.0.pdf`)
- `QG-Master-Reference-v25.0.md`
- `QG-Deployment-Guide-v7.0.md` (this document)
- `QG-Security-Reference-v1.2.md`

The three QG reference docs are duplicated across all three repos so each project is self-contained.

### Updating Documentation

```bash
# 1. Update docs in the workspace, push to GitHub
# Example: updated Oil methodology
cd oil-markets-index-dashboard
cp updated_doc.pdf docs/
git add docs/
git commit -m "docs: update Oil methodology to v4.1"
git push origin main

# 2. If a QG reference doc changed, push to ALL THREE repos
# (Master, Deploy, and Security are shared across all dashboards)
```

### Deploying Docs to VPS

Use the same deploy-guard/deploy-done workflow as code:

```bash
# For EACH dashboard that has updated docs:
source ~/deploy-guard.sh <dashboard>
git fetch origin main
git checkout origin/main -- docs/
source ~/deploy-done.sh <dashboard>
```

When a shared QG reference doc changes, deploy to all three dashboards:

```bash
for dash in oil world cyber; do
  cd /home/support/$(case $dash in
    oil) echo oil-markets-index-dashboard;;
    world) echo world-markets-index-dashboard;;
    cyber) echo cybersecurity-threat-index-dashboard;;
  esac)
  source ~/deploy-guard.sh $dash
  git fetch origin main
  git checkout origin/main -- docs/
  source ~/deploy-done.sh $dash
done
```

### Rules

- **NEVER** create or edit docs directly on the VPS
- **NEVER** SCP/rsync docs to the VPS — always push to GitHub first, then pull
- When updating a shared QG reference doc, update and push to ALL THREE repos, then deploy all three
- When updating a dashboard-specific methodology PDF, only that repo needs updating

---

## Appendix: % Change Toggle Deployment (Thread 22 · April 8, 2026)

### Files Changed

- **Oil Dashboard:** `public/index.html` · Added `.pct-toggle` button, `toPctChange()` function, single shared Y-axis (removed dual axis per user request)
- **World Dashboard:** `public/index.html` · Added `.pct-toggle` button, `toPctChange()` function, all three lines normalize to % change

### Key Commits

| Repo | Commit | Description |
|---|---|---|
| world-markets-index-dashboard | dae358a | % Change toggle on World dashboard |
| oil-markets-index-dashboard | 68b0529 | Single shared Y-axis (removed dual axis) + % Change toggle |

---

## Appendix: Oil Export Consolidation Deployment (Thread 23 · April 9, 2026)

### What Was Deployed

Added `generate_exports.py` to Oil dashboard, matching the World pattern. Oil CSV was dumping every intraday row (~850/day); now consolidated to 1 row/day.

### Files Changed

- **Oil Dashboard:** `server.js` · Updated export endpoints with `tryServeFile()` + `GROUP BY date`
- **Oil Dashboard:** `generate_exports.py` · New file (copied and adapted from World)
- **Oil Dashboard:** `ecosystem.config.js` · Added `oil-export-cron` PM2 cron at 23:55 UTC

### Key Commits

| Repo | Commit | Description |
|---|---|---|
| oil-markets-index-dashboard | 30685e3 | generate_exports.py + export consolidation |

---

## 18. Nightly Export Cron Deployment (Thread 25 · April 10, 2026)

### What Was Deployed

Replaced the unreliable PM2-based export crons with a system crontab that safely stops dashboards before running exports.

### Problem

The old `oil-export-cron` and `world-export-cron` PM2 processes had two fatal flaws:
1. **PM2 `cron_restart` doesn’t fire for stopped processes.** Both had drifted to "stopped" state after their one-time run, so PM2 never re-triggered them.
2. **Running `generate_exports.py` while dashboards are active causes OOM.** On April 10, running exports via screen while all 3 dashboards were active spiked load to 52 and crashed the server.

### Solution

1. Created `/home/support/nightly-export.sh` — stops Oil + World PM2, runs both exports, restarts, health checks
2. Installed system crontab: `0 4 * * *` (4:00 AM UTC / 9:00 PM PDT)
3. Removed old PM2 export crons: `pm2 delete oil-export-cron` and `pm2 delete world-export-cron`
4. Saved PM2 state: `pm2 save`

### Also Deployed: WAL Mode on Oil

Oil’s SQLite was using `delete` journal mode (the legacy default), causing ~18% of fetch attempts to fail with "database is locked". Fixed with:

```sql
sqlite3 /home/support/oil-markets-index-dashboard/data/oil_markets.db 'PRAGMA journal_mode=WAL;'
```

### Verification

```bash
# Cron installed
crontab -l
# Expected: 0 4 * * * /home/support/nightly-export.sh

# PM2 clean (3 processes only)
pm2 list
# Expected: cyber(0), world(1), oil(2) — no export crons

# WAL mode confirmed
sqlite3 /home/support/oil-markets-index-dashboard/data/oil_markets.db 'PRAGMA journal_mode;'
# Expected: wal

# Check export log after first run
tail -20 /home/support/nightly-export.log
```

---

*End of QG-Deployment-Guide-v7.0.md*
