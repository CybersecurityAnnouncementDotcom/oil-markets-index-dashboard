<!-- MANDATORY: This filename MUST include the version number (e.g., QG-Master-Reference-v22.0.md). -->
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- SAFETY: Always use `git fetch origin main` + `git checkout origin/main -- <file>` on VPS. NEVER use `git pull` or `git checkout main`. -->
<!-- SAFETY: Pre-generated export files in data/exports/ are served BEFORE live DB queries. Update generate_exports.py AND regenerate when changing export logic. -->

# QuantitativeGenius.com · Master Reference Guide

| Field | Value |
|---|---|
| **Last Updated** | April 2026 |
| **Version** | 28.0 (Thread 30 · Gold Time Machine dashboard, BMI composite weights, oil export perf fix, 100x scale documentation) |
| **Owner** | jq_007@yahoo.com |
| **Brand** | QuantitativeGenius.com |

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
2. Google Cloud VM
3. Dashboards
4. Data Sources & Provenance
5. GitHub Repositories
6. Podcast Projects
7. Cron Jobs & Automation
8. Domain & DNS
9. How to Restore Everything from Scratch
10. How to SSH into the VM
11. Key Technical Details
12. Accounts & Credentials
13. Thread History
14. Known Issues & Deployment Lessons
15. Database Protection & Recovery
16. API Key System
17. Master Calculations Reference
18. Bitcoin Overlay (Thread 24)
19. OOM Crash Fix (Thread 24)
20. CSV Export Date Filter Fix (Thread 24)
21. Nightly Export Cron (Thread 25)
22. WAL Mode Fix (Thread 25)
23. Dual Y-Axis % Mode (Thread 29)

---

## Infrastructure Overview

```
···················································
·                                                 ·
·           QuantitativeGenius.com                ·
·                                                 ·
·               (Wix website)                     ·
·                                                 ·
···················································
···················································
·                                                 ·
·         Google Cloud VM (e2-micro)              ·
·                                                 ·
·         IP: 136.117.206.145                     ·
·         Ubuntu 22.04 LTS, 30GB disk             ·
·         2GB swap file (/swapfile)               ·
·                                                 ·
·  ·············· ··············· ··············  ·
·  · Oil Markets· · World Markets· · Cybersec  ·  ·
·  · Port 5000  · · Port 5001   · · Port 5002 ·  ·
·  ·············· ··············· ··············  ·
·  ·············· ················                ·
·  · Bitcoin    · · Gold       ·                  ·
·  · Port 5003  · · Port 5004  ·                  ·
·  ·············· ················                ·
·                                                 ·
·  Nginx (port 80/443) · subdomain routing        ·
·  SSL via Let's Encrypt (auto-renew)             ·
·  PM2 process manager (auto-restart on reboot)   ·
·                                                 ·
···················································
···················································
·                                                 ·
·           GitHub (Public Repos)                 ·
·                                                 ·
·   User: CybersecurityAnnouncementDotcom         ·
·                                                 ·
·   Dashboards:                                   ·
·   · oil-markets-time-machine-dashboard                 ·
·   · world-markets-time-machine-dashboard               ·
·   · cybersecurity-threat-index-dashboard        ·
·   · qg-deploy (Bitcoin + Gold + shared pages)   ·
·                                                 ·
·   Podcasts (GitHub Pages):                      ·
·   · oil-market-index-podcast                    ·
·   · world-market-index-podcast                  ·
·   · cybersecurity-bulletin-podcast              ·
·                                                 ·
···················································
···················································
·                                                 ·
·       Perplexity Computer (Cron Jobs)           ·
·                                                 ·
·   · Cybersecurity Threat Index · PAUSED (deleted) ·
·   · Oil Markets Index Bulletin · multiple daily   ·
·   · World Market Index · PAUSED                   ·
·                                                 ·
···················································
```

---

## Google Cloud VM

| Setting | Value |
|---|---|
| Project | quantitativegenius |
| Project ID | tonal-affinity-492010-j5 |
| Instance Name | quantgenius-server |
| Zone | us-west1-b |
| Machine Type | e2-micro (free tier eligible) |
| OS | Ubuntu 22.04 LTS |
| Disk | 30GB standard |
| External IP | 136.117.206.145 |
| SSH User | support |
| Internal IP | 10.138.0.2 |
| Swap | 2GB at /swapfile (permanent via /etc/fstab — added April 8, 2026) |

### Firewall Rules

- `allow-dashboards` · TCP ports 5000, 5001, 5002
- `default-allow-http` · TCP port 80
- `default-allow-https` · TCP port 443

### What's Running on the VM

- PM2 manages 3 Node.js dashboard processes (auto-restarts on crash/reboot)
- Nginx reverse proxy with SSL (subdomain routing)
- Let's Encrypt SSL certificates (auto-renew via certbot timer)
- Auto-update cron: **REMOVED** (April 6, 2026) · The hourly auto-update.sh cron was killing SQLite databases mid-write via `pm2 restart all`. Removed with `crontab -r`. All updates now require manual deployment scripts only.

### PM2 Processes

| ID | Name | Port | Status |
|---|---|---|---|
| 0 | cyber-dashboard | 5002 | online |
| 1 | world-dashboard | 5001 | online |
| 2 | oil-dashboard | 5000 | online |
| 3 | bitcoin | 5003 | online |
| 4 | gold | 5004 | online |

> **Note:** PM2 IDs can change after a full VM reboot or if processes are deleted and recreated. Always verify with `pm2 list` and reference by name when possible. IDs above reflect state after Thread 25 cleanup (April 10, 2026). The old `oil-export-cron` and `world-export-cron` PM2 processes were removed and replaced by a system cron (see Section 21).

---

## Dashboards

### Oil Markets Time Machine

- **URL:** https://oil.quantitativegenius.com
- **Direct:** http://136.117.206.145:5000
- **Data sources:** Yahoo Finance live (CL=F for WTI, BZ=F for Brent) + FRED historical backfill (DCOILWTICO for WTI, DCOILBRENTEU for Brent) + Yahoo Finance ^GSPC for S&P 500 overlay. See Data Sources & Provenance for full details.
- **Fetch interval:** Every 60 seconds
- **Index scale:** Scaled to S&P 500 range
- **Formula:** `(composite / 147.0) * 5000`
- **Composite weighting:** `(Brent × 0.7) + (WTI × 0.3)` (70% Brent, 30% WTI) · consistent across fetch_oil.py and backfill.py
- **Color scheme:** Brown background, yellow/gold lettering
- **Big number color:** Yellow (#f5c542)
- **Chart overlays:** Oil Composite in gold (#d4af37), S&P 500 in blue (#4488ff) · no separate WTI/Brent lines. Both share a single left Y-axis (no separate right axis).
- **S&P 500 overlay:** Available on ALL time ranges (1H, 1D, 1W, 1Y, MAX). Intra-day data from live fetches; historical from backfill. Starts from January 1987 on MAX view (10,464 records from world DB). Thread 20 fix: removed hardcoded `['1W','1Y','MAX']` filter in frontend that excluded S&P from 1H/1D. Intraday matching uses minute-level keys (`slice(0,16)`) not date-level.
- **API endpoints:** `GET /api/current`, `/api/history`, `/api/sp500-history` (all requireAuth), `GET /api/bitcoin-history` (requireAuth — Thread 24), `GET /api/export/csv`, `/api/export/json` (requirePro), `GET /api/user-tier` (requireAuth), `POST /api/readings` (localhost-only)
- **Pro export UI:** Export button visible only to Pro users in chart header
- **CSV export format:** 5 columns · `date`, `index_value`, `wti_price`, `brent_price`, `bitcoin_price` (Thread 24: bitcoin_price column added; 1 row per trading day, consolidated by generate_exports.py)
- **Daily export cron:** System cron runs `nightly-export.sh` at 4:00 AM UTC (9:00 PM PDT) daily — stops PM2, runs generate_exports.py, restarts PM2 (see Section 21)
- **Export files:** `data/exports/daily/YYYY-MM-DD.{csv,json}`, `data/exports/oil-markets-latest.{csv,json}`, `data/exports/oil-markets-history.{csv,json}`
- **Export serving:** `tryServeFile()` serves pre-generated files first; live DB fallback uses `GROUP BY date(timestamp)` for 1 row/day
- **No market open/closed indicator at top**
- **ATH normalization:** WTI/145.29 × 5000, Brent/146.08 × 5000
- **Historical data:** 9,918 records from May 20, 1987 to present (aligned with Brent FRED start date). WTI: 10,141 rows, Brent: 9,789 rows.
- **Weekly averaging:** MAX and 1Y views use `GROUP BY strftime('%Y-%W')`
- **1Y/MAX latest reading:** Appends current day's most recent reading to prevent being a day behind
- **Deduplication threshold:** 0.01 (lowered from 0.5 to prevent flat lines on 1H/1D/1M)
- **% Change Toggle (Thread 22, updated Thread 29):** A % button next to the 1H/1D/1W/1Y/MAX time range selectors. Default loads as raw price view. Both Oil Composite and S&P 500 share a single left Y-axis in all modes (no separate right axis · removed in Thread 22 per user request). When toggled to % mode, both lines are normalized to percentage change from their first visible data point. Tooltips show both raw value and % change in both modes. Y-axis shows +0.05% format in % mode. CSS class `.pct-toggle` with `.active` state (green glow). `toPctChange()` function normalizes arrays. **Dual Y-axis % mode (Thread 29):** When BTC overlay is active and BTC % change is >5x the Oil/S&P % change, chart auto-splits to dual axes (left: Oil/S&P %, right: BTC %). See Section 23.
- **Bitcoin overlay (Thread 24):** BTC price fetched from Yahoo Finance BTC-USD every 60 seconds via native Node.js `https.get` in server.js. Stored in `bitcoin_data` table in `oil_markets.db`. Toggle: ₿ button, orange #f7931a, glow when active. Separate right Y-axis in raw mode; shared left Y-axis in % mode (unless dual-axis triggers — see Section 23). Key commit: 815d02a (nearest-match BTC alignment).
- **BTC independent charting (Thread 27):** BTC continues charting on 1H/1D when oil/S&P markets are closed. Appends real BTC timestamps beyond last main index reading. Index and S&P lines show as gaps (null) during closed hours. Key commit: 3e0108c.
- **Markets-closed fix (Thread 29):** When oil/S&P readings are empty for 1H/1D (weekend/holiday) but BTC has data: shows "Markets Closed" banner, renders clean BTC-only chart on left Y-axis with proper $ formatting. Oil tooltip handles null oil data gracefully.

### World Markets Time Machine

- **URL:** https://world.quantitativegenius.com
- **Direct:** http://136.117.206.145:5001
- **Data source:** yfinance (20 country tickers)
- **Index scale:** All three main section scales (World, S&P 500, SSE) scaled in the range of the S&P 500
- **Header text:** Blue "WORLD MARKETS INDEX"
- **Big number font:** DM Sans 700 (bolder/softer)
- **Hero sub-text font:** DM Sans (changed from DM Mono to match bottom time font)
- **Chart overlays:** S&P 500 in blue (#4488ff), SSE in red (#ef4444), World in green (#22c55e)
- **ATH normalization:** S&P: price/7002 × 5000, SSE: price/6124 × 5000
- **Historical data:** 5,669 records from January 4, 2006 to present (trimmed: removed 1/2 and 1/3 entries)
- **CSV export format:** 23 columns · `date`, `composite_value`, then all 20 country prices as individual columns, `bitcoin_price` (Thread 24: bitcoin_price column added; pivoted by generate_exports.py)
- **Weekly averaging:** MAX and 1Y views use `GROUP BY strftime('%Y-%W')`
- **1Y/MAX latest reading:** Appends current day's most recent reading to prevent being a day behind
- **Deduplication threshold:** 0.01 (lowered from 0.5 to prevent flat lines on 1H/1D/1M)
- **Timestamp format:** fetch_data.py uses `datetime.utcnow().isoformat() + 'Z'` (Thread 20 fix: appended Z suffix so Chart.js converts UTC→local time). Frontend also appends Z to labels from the API for consistency.
- **API endpoints:** `GET /api/composite`, `/api/history`, `/api/country-history`, `/api/countries` (all requireAuth), `GET /api/bitcoin-history` (requireAuth — Thread 24), `GET /api/export/csv`, `/api/export/json` (requirePro), `GET /api/user-tier` (requireAuth), `POST /api/readings` (localhost-only)
- **Pro API endpoints:** `GET /api/pro/latest`, `/api/pro/history`, `/api/pro/daily/:date`, `/api/pro/dates` (all requirePro) · serve pre-generated files from `data/exports/` with live DB fallback
- **Daily export cron:** System cron runs `nightly-export.sh` at 4:00 AM UTC (9:00 PM PDT) daily — stops PM2, runs generate_exports.py, restarts PM2 (see Section 21)
- **Export files:** `data/exports/daily/YYYY-MM-DD.{csv,json}`, `data/exports/world-markets-latest.{csv,json}`, `data/exports/world-markets-history.{csv,json}`, `data/exports/world-markets-history-detailed.csv`
- **Pro export UI:** Export button visible only to Pro users in chart header
- **Other Markets section:** Shows "Country · Index Name" on flag hover (not just ticker symbols)
- **Countries (20):** Russia/MOEX removed
- **% Change Toggle (Thread 22, updated Thread 29):** Same pattern as Oil. A % button next to the time range selectors. Default loads as raw price view showing World (green), S&P 500 (blue), and SSE (red) on the same Y-axis. When toggled to % mode, all three lines are normalized to percentage change from their first visible data point. **Dual Y-axis % mode (Thread 29):** When BTC overlay is active and BTC % change is >5x the World/S&P/SSE % change, chart auto-splits to dual axes (left: World/S&P/SSE %, right: BTC %). See Section 23.
- **Bitcoin overlay (Thread 24):** BTC price fetched from Yahoo Finance BTC-USD every 60 seconds via native Node.js `https.get` in server.js. Stored in `bitcoin_data` table in `world_markets.db`. Toggle: ₿ button, orange #f7931a, glow when active. Separate right Y-axis in raw mode; shared left Y-axis in % mode (unless dual-axis triggers — see Section 23). Key commit: 62d3201 (nearest-match BTC alignment).
- **BTC independent charting (Thread 27):** BTC continues charting on 1H/1D when world markets are closed. Appends real BTC timestamps beyond last main index reading. World, S&P, and SSE lines show as gaps (null) during closed hours. Key commit: 9d94c68.

| Country | Weight | Ticker |
|---|---|---|
| USA | 24.6% | ^GSPC |
| China | 14.3% | 000001.SS |
| Japan | 8.2% | ^N225 |
| Germany | 6.1% | ^GDAXI |
| India | 6.1% | ^BSESN |
| UK | 5.1% | ^FTSE |
| France | 4.1% | ^FCHI |
| Canada | 3.1% | ^GSPTSE |
| South Korea | 3.1% | ^KS11 |
| Australia | 3.1% | ^AXJO |
| Brazil | 3.1% | ^BVSP |
| Italy | 3.1% | FTSEMIB.MI |
| Mexico | 2.0% | ^MXX |
| Spain | 2.0% | ^IBEX |
| Indonesia | 2.0% | ^JKSE |
| Saudi Arabia | 2.0% | ^TASI.SR |
| Netherlands | 2.0% | ^AEX |
| Turkey | 2.0% | XU100.IS |
| Taiwan | 2.0% | ^TWII |
| Switzerland | 2.0% | ^SSMI |

### Cybersecurity Threat Index

- **URL:** https://cyber.quantitativegenius.com
- **Direct:** http://136.117.206.145:5002
- **Data source:** Perplexity Computer cron (daily research + scoring)
- **Score range:** 0–100%
- **Historical data:** 125 monthly scores from Jan 2016 to present
- **DB columns:** year, month, score, level, events (note: `level` and `events`, NOT `assessment`)
- **Gauge:** Horseshoe opening at bottom, dynamically colored arc (green/yellow/orange/red by score), gray remainder, gray knob at boundary
- **Gauge center text:** Dynamically colored by threat level
- **Rating big number:** Dynamically colored by threat level
- **Chart line:** Color-coded by threat level using Chart.js `segment.borderColor` · each segment colored based on the score at that point (green ≤30%, yellow 31-60%, orange 61-80%, red 81-100%)
- **Threat color thresholds:** 0-30% green (#22c55e), 31-60% yellow (#facc15), 61-80% orange (#f0861e), 81-100% red (#ef4444)
- **Yellow shade:** #facc15 (lighter, for contrast vs orange · changed from #f59e0b)
- **Card layout:** Three equal-width cards (1fr 1fr 1fr) · Gauge Card (with Key Indicators below gauge), Chart Card, Distribution Card
- **Key Indicators:** Moved from rating card to gauge card (below the gauge dial)
- **Section title:** "CYBERSECURITY BULLETIN" (changed from "TODAY'S BRIEFING")
- **Threat categories:** 15 types (Ransomware, Phishing, etc.)
- **Distribution colors:** Blue/purple/cyan (no green/yellow/orange/red)
- **1M tab:** Hidden until 30+ daily data points accumulated
- **API endpoints:** `GET /api/scores` (requireAuth), `GET /api/current` (requireAuth), `GET /api/export/csv` (requirePro), `GET /api/export/json` (requirePro), `GET /api/user-tier` (requireAuth)
- **Data write:** `POST /api/readings` (localhost-only), `POST /api/threat-types`

### Bitcoin Market Index (Thread 28 · April 11, 2026)

- **URL:** https://bitcoin.quantitativegenius.com
- **Direct:** http://136.117.206.145:5003
- **Data sources:** Yahoo Finance BTC-USD (every 60s), Yahoo Finance ^GSPC via World Markets DB (read-only), Yahoo Finance ^IXIC and ^DJI (every 5 min)
- **Fetch intervals:** BTC every 60 seconds (constant, 24/7). NASDAQ/DJI every 5 minutes during market hours, every 30 minutes otherwise.
- **Default state:** Opens with BTC + all three stock overlays ON, time range MAX, % mode OFF
- **Color scheme:** Dark background, orange (#f7931a) BTC branding
- **Big number color:** Orange (#f7931a)
- **Chart lines:** BTC in orange (#f7931a), S&P 500 in blue (#4488ff), NASDAQ in green (#22c55e), DJI in purple (#a855f7)
- **Stock overlay toggles:** S&P 500 (blue), NASDAQ (green), DJI (purple) — all ON by default, can be toggled OFF individually. This is opposite of Oil/World where BTC is toggled ON.
- **Y-axis (raw mode):** BTC on left Y-axis ($), stock overlays on right Y-axis ($). Dual axes always active in raw mode since BTC (~$70k+) and stocks (~5k–48k) are on different scales.
- **Y-axis (% mode):** See Section 23 — Dual Y-Axis % Mode.
- **API endpoints:** `GET /api/current` (requireAuth), `GET /api/bitcoin-history` (requireAuth), `GET /api/sp500-history` (requireAuth), `GET /api/nasdaq-history` (requireAuth), `GET /api/dji-history` (requireAuth), `GET /api/export/csv` (requirePro), `GET /api/export/json` (requirePro), `GET /api/user-tier` (requireAuth)
- **Pro export UI:** Export button visible only to Pro users in chart header
- **CSV export format:** 5 columns · `date`, `bitcoin_price`, `sp500_price`, `nasdaq_price`, `dji_price` · 1 row per day via `GROUP BY date(timestamp)`. S&P 500 joined from World Markets DB. No pre-generated files — always live DB query.
- **API key endpoints:** `GET /api/auth/api-key-status`, `POST /api/auth/api-key`, `DELETE /api/auth/api-key` (proxied to auth server at port 5010)
- **Database:** `/home/support/bitcoin-market-index-dashboard/data/bitcoin_markets.db`
- **DB tables:** `bitcoin_data` (timestamp TEXT, price REAL), `nasdaq_data` (timestamp TEXT, price REAL), `dji_data` (timestamp TEXT, price REAL)
- **Record counts (as of April 12, 2026):** bitcoin_data: 4,251 (from 2014-09-17), nasdaq_data: 10,071 (from 1986-04-22), dji_data: 8,630 (from 1992-01-02)
- **S&P 500 source:** Read-only from World Markets DB at `../world-markets-time-machine-dashboard/data/world_markets.db` (table `country_data`, ticker `^GSPC`)
- **Backfill:** On server startup, automatically backfills BTC-USD (max), ^IXIC (max), ^DJI (max) from Yahoo Finance daily history if data is missing
- **Weekly averaging:** MAX and 1Y views use `GROUP BY strftime('%Y-%W')`
- **Deduplication threshold:** 0.01% (same as Oil/World BTC dedup)
- **PM2 process:** bitcoin (ID 5) on port 5003
- **GitHub repo:** `qg-deploy` → `bitcoin-market-index-dashboard/` subdirectory
- **Key commits:** `c8af10d` (dual Y-axis % mode), `0c81927` (temporal dead zone fix)

### Gold Time Machine (Thread 30 · April 13, 2026)

- **URL:** https://gold.quantitativegenius.com
- **Direct:** http://136.117.206.145:5004
- **Data sources:** Yahoo Finance GC=F (Gold Futures), ^HUI (Gold BUGS Index), GDX (Gold Miners ETF), SI=F (Silver Futures for gold/silver ratio), ^XAU (Gold/Silver Sector Index), BTC-USD (Bitcoin overlay)
- **Fetch intervals:** All gold/silver/mining tickers every 60 seconds via yfinance. BTC every 60 seconds via Node.js https.
- **Default state:** Opens with GTM composite, time range MAX
- **Color scheme:** Dark background, gold (#FFD700) branding
- **Big number color:** Gold (#FFD700)
- **GTM Composite weights:** GC=F 30%, ^HUI 25%, GDX 20%, GC=F/SI=F ratio 15%, ^XAU 10%
- **GTM May 2006 gap:** Composite is empty for first ~1,424 rows (Aug 2000 – May 2006) because GDX ETF didn't exist until May 22, 2006. Individual components available from Aug 2000. This is correct — never fabricate data.
- **100x scale discrepancy:** Chart frontend uses (component/base)*100 (values ~100-1400). CSV export uses (component/base)*10000 (values ~10000-120000). Same relative shape, different anchor. Document both, never modify real data to reconcile.
- **API endpoints:** Same pattern as Bitcoin dashboard (requireAuth on GET, requirePro on exports)
- **CSV export format:** Columns: date, gtm_composite, gc_price, hui_price, gdx_price, silver_price, xau_price, gold_silver_ratio, bitcoin_price. 1 row per day.
- **Database:** /home/support/gold-time-machine-dashboard/data/gold_markets.db
- **PM2 process:** gold (ID 4) on port 5004
- **GitHub repo:** qg-deploy → gold-time-machine-dashboard/ subdirectory
- **Stripe products:** Gold Time Machine Product: prod_UKDSgK35wz6GFu. Basic Monthly: price_1TLZ1fKXRVV7arrHGls7yfy6, Pro Monthly: price_1TLZ1eKXRVV7arrHDAypUc6A, Basic Yearly: price_1TLZ1fKXRVV7arrHLdFdLWSs, Pro Yearly: price_1TLZ1fKXRVV7arrH8GzM0FEh
- **Forward-fill:** On weekends/holidays, stock components (^HUI, GDX, ^XAU) use last known closing price. Gold and silver futures report actual prices. Standard mixed-frequency approach.

### Common Dashboard Settings

- **Footer:** "Sponsored by QuantitativeGenius.com"
- **Disclaimer:** "This research publication is not intended to be investment advice and is not from a Registered Investment Advisor."
- **Time format:** UTC / PDT / Stanford University Time
- **No "Live" label** · never use the word "Live" anywhere

---

## Data Sources & Provenance

> **CRITICAL · Locked Down April 7, 2026 (Thread 19).** The data below represents the verified build. All record counts, date ranges, and sources were confirmed against the live VPS databases. Any future changes to data sources must be documented here with date, reason, and new record counts.

### Oil Markets Time Machine · Data Sources

**WTI Crude Oil:**

| Priority | Source | Ticker/ID | Date Range | Notes |
|---|---|---|---|---|
| Primary (live + recent) | Yahoo Finance | CL=F (NYMEX WTI Crude Futures) | ~August 23, 2000 to present | More accurate futures price; fetched every 60s |
| Secondary (historical) | FRED | DCOILWTICO (Cushing, OK WTI Spot Price FOB) | January 2, 1986 to present | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO |

**Brent Crude Oil:**

| Priority | Source | Ticker/ID | Date Range | Notes |
|---|---|---|---|---|
| Primary (live + recent) | Yahoo Finance | BZ=F (ICE Brent Crude Futures) | July 30, 2007 to present | More accurate futures price; fetched every 60s |
| Secondary (historical) | FRED | DCOILBRENTEU (Europe Brent Spot Price FOB) | May 20, 1987 to present | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILBRENTEU |

**Merge Logic:** Use Yahoo Finance ticker where available (more accurate futures price). Use FRED for dates before Yahoo data begins. Where both exist for the same date, Yahoo takes precedence.

**S&P 500 Overlay (for Oil chart):**
- Source: Yahoo Finance ^GSPC · stored in world DB `country_data` table (cross-database dependency)
- Range: January 2, 1987 to present (10,464 records)
- server.js MAX query starts from 1986-01-01 (changed from 2000-01-01 in Thread 19)
- Path: `../world-markets-time-machine-dashboard/data/world_markets.db`

**Verified Record Counts (April 7, 2026):**
- Composite readings: 9,918 (from May 20, 1987)
- WTI price rows: 10,141
- Brent price rows: 9,789
- S&P 500 overlay: 10,464 records (from world DB)

### World Markets Time Machine · Data Sources

- Source: Yahoo Finance via yfinance library · 20 country tickers (see ticker table above)
- Live fetch interval: 60 seconds
- Backfill start: DB trimmed to start January 4, 2006 (removed 1/2 and 1/3 entries)
- S&P 500 data: Also backfilled to January 2, 1987 (4,795 additional records from Yahoo ^GSPC) for cross-database use by Oil dashboard

**Verified Record Counts (April 7, 2026):**
- Composite readings: 5,669 (from January 4, 2006)
- Country data rows: includes all 20 countries
- S&P 500 in country_data: 10,464 records (from 1987-01-02)
- CSV export: 23 columns (date, composite_value, 20 country price columns, bitcoin_price — Thread 24)

### Cybersecurity Threat Index · Data Sources

- Source: Perplexity Computer daily research + scoring
- Seed data: seed_data.py (deterministic random seed 42) for historical months
- Events column: Populated by add_events.py
- DB columns: year, month, score, level, events

**Verified Record Counts (April 7, 2026):**
- Monthly scores: 125 (from January 2016)
- CSV columns: year, month, score, level, events
- JSON includes: threat_distribution array

### Bitcoin Data Source (Thread 24)

- Source: Yahoo Finance BTC-USD via native Node.js `https.get` (NOT yfinance Python)
- Fetch interval: Every 60 seconds in server.js
- Database: `bitcoin_data` table (`timestamp TEXT`, `price REAL`) in both `oil_markets.db` and `world_markets.db`
- Dedup: Only stores if price changes ≥ 0.01%
- API: `GET /api/bitcoin-history?range=1H|1D|1W|1Y|MAX`
- Data accumulates from first deploy forward (no backfill)

### Data Source Change Log

| Date | Dashboard | Change | Reason |
|---|---|---|---|
| April 7, 2026 | Oil | Added FRED DCOILWTICO as secondary WTI source | Pre-2000 rows had Brent but empty WTI column |
| April 7, 2026 | Oil | Added FRED DCOILBRENTEU as secondary Brent source | Extended Brent data back to May 1987 |
| April 7, 2026 | Oil | S&P 500 overlay MAX query start changed from 2000-01-01 to 1986-01-01 | Match expanded FRED data range |
| April 7, 2026 | Oil | Trimmed 346 pre-Brent rows (before May 20, 1987) | Align composite start with earliest Brent data |
| April 7, 2026 | World | Trimmed 2 rows (1/2 and 1/3 2006) | Start on first full trading day 1/4/06 |
| April 7, 2026 | World | S&P 500 backfilled to January 2, 1987 (4,795 extra records) | Support Oil overlay going back to 1987 |
| April 7, 2026 | World | generate_exports.py updated to pivot country prices as columns | Pre-generated CSV had only 3 columns; now 22 |
| April 9, 2026 | Oil | Added generate_exports.py (matching World pattern) | Oil CSV was dumping every intraday row (~850/day); now 1 row/day |
| April 9, 2026 | Oil | Updated server.js export endpoints with tryServeFile() + GROUP BY date | Pre-generated file serving with daily-consolidated DB fallback |
| Thread 24 | Oil + World | Added bitcoin_data table; BTC price fetched via Node.js https.get | Bitcoin overlay on both dashboards |
| Thread 24 | Oil + World | Added bitcoin_price column to CSV exports | Pro export includes BTC price per trading day |
| Thread 30 | Gold | Gold Time Machine dashboard created with 5-component GTM composite | Predictive gold market composite |
| Thread 30 | Bitcoin | BMI composite weights documented (BTC 40%, NDX 25%, SPX 20%, DJI 15%) | Prediction weights rationale |
| Thread 30 | Oil | generate_exports.py rewritten to dictionary-based lookups | Fixed O(N*M) correlated subquery zombie/OOM |

---

## GitHub Repositories

**GitHub User:** CybersecurityAnnouncementDotcom

### Dashboard Repos (All Public)

| Repo | Last Commit | URL |
|---|---|---|
| oil-markets-time-machine-dashboard | 3e0108c (BTC independent charting) | https://github.com/CybersecurityAnnouncementDotcom/oil-markets-time-machine-dashboard |
| world-markets-time-machine-dashboard | 9d94c68 (BTC independent charting) | https://github.com/CybersecurityAnnouncementDotcom/world-markets-time-machine-dashboard |
| cybersecurity-threat-index-dashboard | e92ddbd (pricing table update) | https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard |
| qg-deploy (PRIVATE) | ec5df73 (Thread 30: oil export dict-based lookup, gold dashboard) | https://github.com/CybersecurityAnnouncementDotcom/qg-deploy |

### Podcast Repos (All Public, GitHub Pages enabled)

| Repo | RSS Feed | URL |
|---|---|---|
| cybersecurity-bulletin-podcast | https://cybersecurityannouncementdotcom.github.io/cybersecurity-bulletin-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-bulletin-podcast |
| world-market-index-podcast | https://cybersecurityannouncementdotcom.github.io/world-market-index-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/world-market-index-podcast |
| oil-market-index-podcast | https://cybersecurityannouncementdotcom.github.io/oil-market-index-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/oil-market-index-podcast |

### Each Dashboard Repo Contains

- `server.js` · Express backend with SQLite, yfinance fetching, API endpoints, API key validation, Bitcoin fetch (Thread 24)
- `public/index.html` · Frontend dashboard (single-page) with Pro features (export, API key UI, BTC toggle)
- `data/*.db` · SQLite database (in .gitignore, not pushed)
- `backfill.py` · Historical data backfill script (uses yfinance + FRED for oil WTI/Brent)
- `fetch_*.py` · Real-time price fetch script (called by server.js)
- `generate_exports.py` · Daily export generator (consolidates DB readings to 1 row/day, writes CSV/JSON to `data/exports/`). Present in world and oil repos.
- `package.json` · Node.js dependencies
- `deploy/gcloud-setup/` · VM setup scripts (oil repo only)

### Git Configuration

```bash
git config user.name "Quantitative Genius"
git config user.email "jq_007@yahoo.com"
```

---

## Podcast Projects

### Cybersecurity Threat Index Podcast

- **Title:** Cybersecurity Threat Index
- **Brand:** QuantitativeGenius.com
- **Schedule:** PAUSED (cron deleted April 1, 2026; old cron IDs: 286060d1, de608a39)
- **Voice:** kore (TTS)
- **YouTube:** Unlisted, notifySubscribers = false
- **Email recipients:** jq_007@yahoo.com, jq_007@icloud.com
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/cybersecurity-bulletin-podcast/feed.xml
- **Platforms:** Spotify, Apple Podcasts, Amazon Music

### Oil Markets Index Bulletin

- **Title:** Daily Oil Markets Index Bulletin
- **Brand:** QuantitativeGenius.com
- **Email recipients:** jq_007@yahoo.com, jq_007@icloud.com, oilmarketsindex@gmail.com
- **YouTube channel:** OilMarketIndexDotcom
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/oil-market-index-podcast/feed.xml
- **Schedule:** Multiple times daily · 1AM, 5AM, 6AM (podcast), 7AM, 8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 5PM, 8PM PDT

### World Market Index Podcast

- **Title:** World Market Index
- **Brand:** QuantitativeGenius.com
- **Status:** PAUSED (as of April 1, 2026)
- **Previous schedule:** Daily at 1:00 AM PDT
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/world-market-index-podcast/feed.xml
- **Platforms:** Spotify, Apple Podcasts, Amazon Music
- **Sources:** CNBC, CNN, WSJ, Reuters, Bloomberg, MarketWatch, Yahoo Finance, IBD

---

## Cron Jobs & Automation

### On the Google Cloud VM

- Hourly auto-update: **REMOVED** (April 6, 2026) · Was `~/auto-update.sh` running `pm2 restart all` hourly. This caused recurring SQLite database corruption by killing processes mid-write. Disabled with `crontab -r`.
- **Nightly export cron (Thread 25):** System crontab runs `/home/support/nightly-export.sh` at `0 4 * * *` (4:00 AM UTC / 9:00 PM PDT). Stops Oil + World PM2 processes, runs both `generate_exports.py` scripts sequentially, restarts dashboards, health checks. Logs to `/home/support/nightly-export.log`. Replaces the old PM2-based `oil-export-cron` and `world-export-cron` processes (which were unreliable — PM2 `cron_restart` doesn't fire for stopped processes).

### On Perplexity Computer

- Cybersecurity Threat Index · PAUSED/DELETED (old cron ID: de608a39, deleted April 1, 2026; prior cron ID 286060d1 also deleted)
- Oil Markets Index Bulletin · Multiple daily (schedules set in prior threads)
- World Market Index · PAUSED

---

## Domain & DNS

| Domain | Registrar | Nameservers | Website |
|---|---|---|---|
| quantitativegenius.com | Namebright | Wix DNS | Wix website |

### DNS Records (managed on Wix)

| Host | Type | Value | TTL |
|---|---|---|---|
| quantitativegenius.com | A | 185.230.63.171 | 1 Hour |
| quantitativegenius.com | A | 185.230.63.186 | 1 Hour |
| quantitativegenius.com | A | 185.230.63.107 | 1 Hour |
| oil.quantitativegenius.com | A | 136.117.206.145 | 1 Hour |
| world.quantitativegenius.com | A | 136.117.206.145 | 1 Hour |
| cyber.quantitativegenius.com | A | 136.117.206.145 | 1 Hour |
| en.quantitativegenius.com | CNAME | cdn1.wixdns.net | 1 Hour |

### SSL / TLS

| Property | Value |
|---|---|
| Provider | Let's Encrypt |
| Renewal | Auto-renew via certbot |
| Current expiry | July 1, 2026 |
| Protocol | TLS 1.2 / 1.3 |

---

## How to Restore Everything from Scratch

### Step 1: Create a new VM

```bash
# Google Cloud Console > Compute Engine > Create Instance
# Name: quantgenius-server
# Zone: us-west1-b
# Machine: e2-micro
# OS: Ubuntu 22.04 LTS
# Disk: 30GB standard
# Allow HTTP + HTTPS traffic
```

### Step 2: Add firewall rule

```bash
# VPC Network > Firewall > Create Rule
# Name: allow-dashboards
# Targets: All instances
# Source: 0.0.0.0/0
# Protocols: TCP 5000,5001,5002
```

### Step 3: SSH in and run setup

```bash
# Install Node.js, PM2, Python, Nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash
sudo apt install -y nodejs nginx python3-pip
sudo npm install -g pm2
pip3 install yfinance pandas

# Clone all 3 repos
cd ~
git clone https://github.com/CybersecurityAnnouncementDotcom/oil-markets-time-machine-dashboard.git
git clone https://github.com/CybersecurityAnnouncementDotcom/world-markets-time-machine-dashboard.git
git clone https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard.git

# Install dependencies
cd ~/oil-markets-time-machine-dashboard && npm install
cd ~/world-markets-time-machine-dashboard && npm install
cd ~/cybersecurity-threat-index-dashboard && npm install

# Backfill databases
cd ~/cybersecurity-threat-index-dashboard && python3 seed_data.py
cd ~/oil-markets-time-machine-dashboard && python3 backfill.py
cd ~/world-markets-time-machine-dashboard && python3 backfill.py

# Start all dashboards with PM2
cd ~/oil-markets-time-machine-dashboard && pm2 start server.js --name oil-dashboard -- --port 5000
cd ~/world-markets-time-machine-dashboard && pm2 start server.js --name world-dashboard -- --port 5001
cd ~/cybersecurity-threat-index-dashboard && pm2 start server.js --name cyber-dashboard -- --port 5002

# Set PM2 to auto-start on reboot
pm2 save
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u support --hp /home/support
pm2 save
```

### Step 3b: Create swap file (MANDATORY for e2-micro)

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
# Verify
free -h  # Should show Swap: 2.0Gi
```

### Step 4: Set up Nginx + SSL

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d oil.quantitativegenius.com -d world.quantitativegenius.com -d cyber.quantitativegenius.com --non-interactive --agree-tos -m jq_007@yahoo.com
```

### Step 5: Backfill S&P 500 pre-2006 data

The world backfill only covers 2006+ (when all 20 tickers have data). Oil's S&P overlay needs data back to 2000:

```python
python3 -c "
import yfinance as yf, sqlite3
db = sqlite3.connect('/home/support/world-markets-time-machine-dashboard/data/world_markets.db')
earliest = db.execute(\"SELECT MIN(timestamp) FROM country_data WHERE ticker='^GSPC'\").fetchone()[0]
hist = yf.Ticker('^GSPC').history(start='2000-01-01', end=earliest[:10], interval='1d')
for date, row in hist.iterrows():
    ts = date.strftime('%Y-%m-%d')
    price = round(row['Close'], 2)  # RAW price, NOT normalized
    db.execute('INSERT OR IGNORE INTO country_data (timestamp, country, ticker, price, weight, contribution) VALUES (?, ?, ?, ?, ?, ?)',
               (ts, 'USA', '^GSPC', price, 0.246, 0.0))
db.commit()
db.close()
"
```

> **WARNING:** Do NOT set up an auto-update cron. All updates must use manual deployment scripts.

### Step 6: Update DNS (if IP changed)

- Go to Wix Studio > Domains > quantitativegenius.com > DNS Records
- Update the A records for oil, world, cyber subdomains to the new IP

---

## How to SSH into the VM

1. Go to https://console.cloud.google.com
2. Select project quantitativegenius (ID: tonal-affinity-492010-j5)
3. Navigate to Compute Engine > VM Instances
4. Click SSH next to quantgenius-server

### Useful SSH Commands

```bash
pm2 list                      # Check dashboard status
pm2 logs                      # View real-time logs
crontab -l                    # Should show ONLY: 0 4 * * * /home/support/nightly-export.sh
sudo nginx -t                 # Test Nginx config
sudo systemctl restart nginx  # Restart Nginx
sudo certbot renew --dry-run  # Test SSL renewal
free -h                       # Verify swap is active (should show Swap: 2.0Gi)
```

---

## Key Technical Details

### Data Sources

- Oil & World Dashboards: yfinance (free, no API key needed) + native Node.js https.get for Bitcoin (Thread 24)
- Cybersecurity Dashboard: Perplexity Computer daily research + seed_data.py
- Podcasts: Web research via Perplexity Computer cron jobs

### Important Tickers

- Saudi Arabia: ^TASI.SR (NOT ^TASI)
- China SSE: 000001.SS
- Turkey: XU100.IS
- Italy: FTSEMIB.MI
- Bitcoin: BTC-USD (Yahoo Finance, fetched via Node.js https.get — NOT yfinance)

### Known Issues & Fixes

- `pandas_datareader` has compatibility issues with Python 3.12 · use yfinance directly
- Sawtooth noise on MAX/1Y charts · fixed with weekly averaging (`GROUP BY strftime('%Y-%W')`)
- Glitch protection · servers reject any reading that drops >20% from previous value
- YouTube API uploads require publicly accessible URL for filePath (local paths fail silently)
- 1Y/MAX stale data fix: Both oil and world servers now append the latest reading from today when serving 1Y/MAX data
- Deduplication threshold: Lowered from 0.5 to 0.01 on oil and world to prevent 1H/1D/1M from showing flat lines
- SQLite WAL files: If DB shows stale cached data, delete .db-wal and .db-shm files, then restart PM2
- Oil backfill.py weighting fix (April 3, 2026): backfill.py previously used 60/40 (WTI/Brent) instead of 70/30 (Brent/WTI). Fixed to match fetch_oil.py.
- World backfill.py SCALE_FACTOR fix (April 3, 2026): backfill.py was missing the `SCALE_FACTOR = 0.194715` multiplier that fetch_data.py uses.
- Cross-dashboard dependency (April 6, 2026): Oil's `/api/sp500-history` reads from the WORLD database (`country_data` table, `^GSPC`). If the world DB is corrupt or missing, both dashboards lose their S&P 500 overlay lines.
- NEVER use `git reset --hard` on VPS · Known Issue #12 (April 8, 2026)
- deploy-guard.sh is MANDATORY before any VPS file modification · Known Issue #14 (April 8, 2026)
- After world DB restore, must re-backfill S&P 500 pre-2006 data · Known Issue #15 (April 8, 2026)
- Always deploy code to VPS after pushing to GitHub · Known Issue #16 (April 8, 2026)
- World MAX CSV date filter fix (Thread 24): Pre-generated export file in data/exports/ was stale, showing rows starting 2006-01-02 instead of correct 2006-01-04. Fix: re-ran `python3 generate_exports.py` on VPS.
- NEVER run `generate_exports.py` while PM2 dashboards are running · Known Issue #17 (Thread 25, April 10, 2026): Python export scripts consume enough memory to OOM-crash the 1GB VPS. The nightly export cron (`nightly-export.sh`) stops PM2 first. If running manually, use `deploy-guard` first.
- Oil WAL mode fix · Known Issue #18 (Thread 25, April 10, 2026): Oil’s SQLite was in `delete` journal mode while World used `wal`. This caused ~18% of Oil fetch attempts to fail with "database is locked" when reads/writes collided. Fixed: `PRAGMA journal_mode=WAL`. All databases now use WAL.
- PM2 `cron_restart` doesn’t fire for stopped processes · Known Issue #19 (Thread 25, April 10, 2026): The old `oil-export-cron` and `world-export-cron` PM2 processes were in "stopped" state, meaning PM2 never triggered them at 23:55 UTC. Replaced with system crontab.
- VPS rebooted 3 times in 10 days (Apr 1, Apr 8, Apr 10) · Known Issue #20 (Thread 25): Apr 10 reboot caused by running `generate_exports.py` via screen while all dashboards were active. Load spiked to 52, OOM killed processes.
- 100x Scale Discrepancy · Known Issue #21 (Thread 30, April 13, 2026): Chart frontend computes composites as (component/base)*100 while CSV export uses (component/base)*10000. Same relative movements, different anchor. Both are valid for their contexts. Never modify real data to reconcile scales.
- GTM May 2006 Gap · Known Issue #22 (Thread 30, April 13, 2026): GTM composite is empty for first ~1,424 rows (Aug 2000 – May 2006) because GDX ETF started trading May 22, 2006. Individual components (GC=F, ^HUI, SI=F, ^XAU) have data from Aug 2000.
- Oil export correlated subquery repeat · Known Issue #23 (Thread 30, April 13, 2026): generate_exports.py for Oil hung at 90% CPU — same O(N*M) correlated subquery pattern from Known Issue #17. Rewritten to dictionary-based lookups. Rule: NEVER use correlated subqueries on e2-micro. Always use dictionary-based or hash-join patterns.

> **CRITICAL DATA INTEGRITY NOTE:** NEVER remove or modify real data to improve visual appearance. Real data must be preserved even if it creates visual anomalies in charts. This principle applies to all dashboards and all data — if real data "looks weird," the correct approach is to document the anomaly, not delete or smooth the data.

---

## Accounts & Credentials

| Service | Account/Username |
|---|---|
| Email | jq_007@yahoo.com |
| Email (Apple) | jq_007@icloud.com |
| Email (Oil) | oilmarketsindex@gmail.com |
| GitHub | CybersecurityAnnouncementDotcom |
| Google Cloud | (same Google account used for Perplexity) |
| Domain Registrar | Namebright (quantitativegenius.com) |
| Website Host | Wix Studio (jq0077 account) |
| Spotify Podcasts | Submit RSS feeds at podcasters.spotify.com |
| Apple Podcasts | Submit RSS feeds at podcastsconnect.apple.com |
| Amazon Music | Submit RSS feeds at podcasters.amazon.com |
| YouTube (Cyber) | CybersecurityAnnouncementDotcom channel |
| YouTube (Oil) | OilMarketIndexDotcom channel |
| Stripe | Restricted API key "Perplexity Computer" |

### Stripe Pricing (Thread 26 · 10x Increase — April 11, 2026)

**Current pricing tiers:**

| Tier | Monthly | Yearly |
|---|---|---|
| Individual Basic | $390/mo | $3,900/yr |
| Individual Pro | $590/mo | $5,900/yr |
| All-Access Basic | $790/mo | $7,900/yr |
| All-Access Pro | $990/mo | $9,900/yr |

**New Stripe Price IDs (Thread 26):**

| Product | Basic Monthly | Basic Yearly | Pro Monthly | Pro Yearly |
|---|---|---|---|---|
| Oil (prod_UGE7bG3qM4Bz2I) | price_1TKyPLKXRVV7arrHcOMlcCij | price_1TKyPLKXRVV7arrHkNeCyQwE | price_1TKyPLKXRVV7arrH7o3En3WM | price_1TKyPLKXRVV7arrHY8g355WV |
| World (prod_UGE7tfjecutQJD) | price_1TKyPTKXRVV7arrHeDL1JE9n | price_1TKyPUKXRVV7arrHynLLmXUY | price_1TKyPTKXRVV7arrHiXqbaog2 | price_1TKyPTKXRVV7arrHSlbTE4Ga |
| Cyber (prod_UGE7O0dI68hTVj) | price_1TKyPdKXRVV7arrH0ipBqF5C | price_1TKyPdKXRVV7arrHFQOpCcPT | price_1TKyPdKXRVV7arrHzT5O1iag | price_1TKyPdKXRVV7arrHCR0c3S6V |
| Bundle (prod_UGE78JOODDPF33) | price_1TKyPmKXRVV7arrH2bOt20kF | price_1TKyPmKXRVV7arrHT3Yyqf0x | price_1TKyPnKXRVV7arrHDNWXg0Br | price_1TKyPmKXRVV7arrHHSEshvKW |

**Hidden Pricing Pages (Thread 26):**
- https://quantitativegenius.com/pricing-H-kOciugfY024DZguSarypN6fodcEbVKAH4QNBiruyk.html
- https://quantitativegenius.com/pricing-hMNOUJ-4d98B5alVffeZo0BVka6brb5pkESLjlnOm0g.html

**Legacy Pro Price IDs (kept for existing subscribers):**

| Product | Monthly ($59 legacy) | Yearly ($590 legacy) |
|---|---|---|
| Oil Pro | price_1THhsnKXRVV7arrHEqtwMM7L | price_1THhsnKXRVV7arrHy4W5CdKb |
| World Pro | price_1THhsoKXRVV7arrHW1dndy6D | price_1THhsoKXRVV7arrHYYV23gR5 |
| Cyber Pro | price_1THhspKXRVV7arrHunUc5LjR | price_1THhspKXRVV7arrHudiK0fRG |
| Bundle Pro | price_1THhspKXRVV7arrHdcBM4qz2 ($99/mo legacy) | price_1THhsqKXRVV7arrHi6qlZUW5 ($990/yr legacy) |

> **TODO:** Add the new Thread 26 price IDs to `PRO_PRICE_IDS` in `stripe-webhook.js` on the auth server. Update hidden pricing page payment links to use the new Stripe payment links.

---

## Thread History

### Thread 1 · Original Dashboard Build + Oil Bulletins

- Built Oil Markets Time Machine dashboard
- Built World Markets Time Machine dashboard
- Set up Oil Markets Index bulletins (multiple daily)
- Branding updates from old brands to QuantitativeGenius.com
- Fixed chart scaling, tooltip colors, sawtooth noise

### Thread 2 · Cybersecurity Threat Index Dashboard + Podcast

- Rebranded from "Daily Cybersecurity Threat Bulletin" to "Cybersecurity Threat Index"
- Built Cybersecurity Threat Index dashboard (gauge, chart, distribution)
- Set up daily 6:00 AM cron for podcast + dashboard updates
- Recalculated threat scores from 2016 (including WannaCry, etc.)

### Thread 3 · World Market Index Podcast

- Built World Market Index podcast (same workflow as Cybersecurity)
- Set up daily 1:00 AM cron (currently PAUSED)
- Japanese reporter intro video (silent, 2 seconds)

### Thread 4 · GitHub Push + Google Cloud Deployment

- Pushed all 3 dashboard repos to GitHub (public)
- Created Google Cloud VM (e2-micro, Ubuntu 22.04)
- Deployed all 3 dashboards with PM2
- Backfilled all databases on the VM
- Set up Nginx reverse proxy with subdomain routing
- Set up SSL via Let's Encrypt
- Set up hourly auto-update cron (later removed)
- Configured DNS on Wix (oil/world/cyber subdomains)

### Thread 5 · Bug Fixes Round 1 (March 31–April 1, 2026)

- Fixed world dashboard scale to S&P 500 range
- Fixed oil S&P 500 overlay to start from 2001
- Fixed cyber dashboard missing blurbs, April data point, wrong indicator
- Paused/deleted cybersecurity 6AM cron job
- Added April 2026 entry to cyber dashboard (78% HIGH)

### Thread 6 · Bug Fixes Round 2 (April 2, 2026)

- World: Country names show "Country · Index Name" on flag hover
- World: Changed hero-sub font from DM Mono to DM Sans
- Oil + World: 1Y/MAX now append latest reading so they always show current day data
- Oil + World: Lowered deduplication threshold 0.5 → 0.01

### Thread 7 · Code & Documentation Audit Fixes (April 3, 2026)

- Oil: backfill.py weighting corrected from 60/40 to 70/30 (Brent/WTI)
- World: backfill.py now includes SCALE_FACTOR = 0.194715
- World: USA weight adjusted 0.245 → 0.246 so all 20 weights sum to exactly 1.000
- All changes pushed to GitHub

### Thread 8 · Data Regression Fix & Chart Corrections (April 3, 2026)

- Discovered NO auto-pull cron exists on VPS · all updates require manual `git pull` + `pm2 restart`
- Oil: backfill.py now requires `--force` flag to clear and re-insert (commit 3768d10)
- Oil: Removed 1H/1D stale data fallback (commit 49ae753)
- Oil: S&P 500 intra-day fix · full ISO timestamps for 1H/1D/1W queries (commit 7e5eaac)
- World: Fixed 1H/1D to use time-window filtering instead of LIMIT N (commit ca079ab)

### Thread 9 · Pro Features Build (April 3, 2026)

- Built and deployed Pro features across all 3 dashboards
- `requireAuth` middleware on all GET API endpoints
- `requirePro` middleware on new export endpoints (returns 403 for non-pro)
- POST /api/readings locked to localhost only
- CSV/JSON export endpoints: `/api/export/csv`, `/api/export/json`
- Commits: oil f0b31c1, world 6c328db, cyber e94d080

### Thread 10 · Auth System Pro Tier + Nginx Tier Forwarding + Site Outage & Recovery (April 3, 2026)

- Auth system Pro Tier support implemented
- Site-wide outage (~2:50 PM PDT) due to deployment order violation · nginx before auth
- Emergency rollback and correct deployment completed ~4:00 PM PDT

### Thread 11 · Pro Export System Build (April 3, 2026)

- Built daily CSV/JSON export generation system for World Markets Time Machine Pro subscribers
- `generate_exports.py` · reads SQLite DB, writes daily snapshots
- New `/api/pro/*` endpoints for programmatic API access
- `ecosystem.config.js` · PM2 cron at 23:55 UTC

### Thread 12 · Promo Code System (April 3, 2026)

- Created 8 Stripe coupons for discount tiers (10%–100%)
- Enabled `allow_promotion_codes: true` on all 16 QG Stripe Payment Links
- 100% off promo codes later deprecated (Thread 21)

### Thread 13 · Auth Login Fix + DNS Migration + Promo Code (April 6, 2026)

- Auth login broken: `auth_request` applying to /auth/login · fixed with `auth_request off;`
- Homepage missing Sign In link · added to landing page nav
- DNS MX migration fixed for support@quantitativegenius.com

### Thread 14 · Stripe Webhook Fix + Dashboard Picker + DB Corruption Fix (April 6, 2026)

- Stripe webhook fixed (wrong signing secret · 99% error rate)
- Dashboard picker route added (`/auth/dashboards`)
- Database corruption root cause identified: hourly auto-update cron
- Removed cron, re-backfilled world DB (5,285 readings)
- Created QG-Database-Protection-Checklist.md

### Thread 15 · API Key System + Cyber Export Fix (April 7, 2026)

- Complete API key infrastructure for Pro subscribers
- `api_keys` table with SHA-256 hash storage
- 4 auth endpoints for key management
- Cyber export fix: `.chart-header` → `.chart-top` selector
- Key format: `qg_` + 32 hex chars

### Thread 16 · CORS Fix for API Key UI (April 7, 2026)

- API key management UI stuck on "Loading..." · CORS issue
- Added `proxyToAuth()` function to all 3 dashboard server.js files
- Changed all 3 index.html files to fetch from local `/api/auth/api-key-status`

### Thread 17 · API Key Per-Product Access Control (April 7, 2026)

- Bug: API key validated against ALL subscriptions; fixed to per-product scope
- `/auth/validate-key` now accepts `?product=<stripe_product_id>` param

### Thread 18 · Export Endpoint Auth Fix (April 7, 2026)

- Bug: All export endpoints returned 401 for all users
- Root cause: `requirePro` used without `requireAuth` first
- Fixed: chained `requireAuth, requirePro` on all 10 affected routes

### Thread 19 · FRED Historical Backfill + Data Source Lockdown + Deployment Fix (April 7, 2026)

- SSH access established: ed25519 key added to VPS authorized_keys
- CRITICAL FIX: Changed all `git checkout main --` to `git checkout origin/main --`
- Added FRED DCOILWTICO as secondary WTI source
- Added FRED DCOILBRENTEU as secondary Brent source
- Backfilled 4,795 S&P 500 records to January 2, 1987
- Data lockdown: record counts, date ranges, and sources documented

### Thread 20 · World Timezone Fix + Oil S&P 500 1H/1D Fix + Doc Cleanup (April 7, 2026)

- Oil S&P 500 missing on 1H/1D: removed hardcoded `['1W','1Y','MAX']` filter
- World timezone display: fetch_data.py now appends 'Z' to all timestamps
- Methodology doc versioning: renamed all 6 files to include version numbers

### Thread 21 · Rate Limiting, Swap, Stripe Hardening, deploy-guard, World DB Recovery (April 8, 2026)

- Express rate limiting: `rate-limiter.js` added to all 3 dashboards
- Nginx rate limiting: `/etc/nginx/snippets/rate-limit.conf`
- GCP VM OOM crash: all 3 sites down ~7 hours (e2-micro with no swap)
- 2GB swap file created at /swapfile (permanent via /etc/fstab)
- Stripe restricted API key created
- World DB corruption incident: `git reset --hard` ran while PM2 active
- deploy-guard.sh / deploy-done.sh system created

### Thread 22 · % Change Toggle on World + Oil Dashboards (April 8, 2026)

- Added % toggle button (CSS class `.pct-toggle`) next to time range selectors on both dashboards
- `toPctChange()` function normalizes price arrays
- Oil: single shared left Y-axis in ALL modes (removed dual axis per user request)
- S&P 500 data gap discovered and fixed after Thread 21 DB restore (re-backfilled 3,286 rows from 1987–2000)
- Known Issue #15 added: After any world DB restore, verify S&P 500 pre-2006 data
- Known Issue #16 added: Pushing to GitHub does NOT deploy to VPS
- GitHub commits: world dae358a (% toggle), oil 68b0529 (single shared Y-axis)

### Thread 23 · Oil Export Consolidation (April 9, 2026)

- Added generate_exports.py to Oil dashboard (matching World pattern)
- Oil CSV was dumping every intraday row (~850/day); now 1 row/day
- Updated server.js export endpoints with `tryServeFile()` + `GROUP BY date`
- ecosystem.config.js updated with `oil-export-cron` PM2 cron at 23:55 UTC
- GitHub commits: oil 30685e3

### Thread 24 · Bitcoin Overlay + OOM Crash Fix + CSV Date Filter Fix

- **Bitcoin overlay** added to both Oil and World dashboards (see Section 18)
- **OOM Crash Fix**: 2GB swap file documented and verified (see Section 19)
- **CSV Date Filter Fix**: World MAX CSV stale export repaired (see Section 20)
- GitHub commits: World 62d3201 (nearest-match BTC), Oil 815d02a (nearest-match BTC)

### Thread 25 · WAL Mode, Nightly Export Cron, PM2 Cleanup, Bitcoin Backfill (April 10, 2026)

- **Oil Bitcoin backfill**: Ran `backfill_bitcoin.py` on Oil — populated 4,649 BTC records from 2014-09-17 to present. Oil previously only had ~424 real-time BTC rows.
- **OOM crash (Apr 10)**: Running `generate_exports.py` via screen while all 3 dashboards were active spiked load to 52 and OOM-killed processes. Killed runaway Python, restarted Oil dashboard.
- **WAL mode on Oil**: Oil’s SQLite was using `delete` journal mode (causing ~18% fetch failures from lock conflicts). Switched to `wal` to match World. All databases now use WAL.
- **Nightly export cron**: Created `/home/support/nightly-export.sh` — stops Oil + World PM2, runs both `generate_exports.py` sequentially, restarts, health checks. System cron at `0 4 * * *` (4:00 AM UTC / 9:00 PM PDT). Logs to `/home/support/nightly-export.log`.
- **PM2 cleanup**: Removed old `oil-export-cron` (PM2 ID 4) and `world-export-cron` (PM2 ID 3). PM2 now has 3 processes only: cyber(0), world(1), oil(2).
- **Methodology PDFs updated**: Oil v4.0, World v4.0, Cyber v3.2 — pushed to all 3 repos + VPS.
- **QG reference docs updated**: Master v25.0, Deploy v7.0, Security v1.2.
- **Documentation Deployment section** (Section 17) added to QG-Deployment-Guide.

### Thread 26 · 10x Pricing Increase, New Stripe Prices & Payment Links (April 11, 2026)

- **10x pricing increase**: All subscription prices increased 10x. New 4-tier structure: Individual Basic $390/mo, Individual Pro $590/mo, All-Access Basic $790/mo, All-Access Pro $990/mo.
- **New Stripe prices**: Created new Stripe price objects for all 4 products (Oil, World, Cyber, Bundle) × 4 tiers (Basic Monthly, Basic Yearly, Pro Monthly, Pro Yearly) = 16 new price IDs. Saved to `new-stripe-prices.json`.
- **New Stripe payment links**: Created corresponding payment links for all 16 new prices. Saved to `new-payment-links.json`.
- **Hidden pricing pages**: Two hidden pricing HTML pages deployed to VPS at obfuscated URLs (not linked from main site). These contain the new payment links.
- **Legacy prices preserved**: Old $59/$590 price IDs kept active for any existing subscribers.
- **QG-Deployment-Guide updated**: Section 13 now shows new pricing table with legacy IDs below.
- GitHub commits: Oil 80f2888, World 1587371, Cyber e92ddbd (docs: pricing table update)

### Thread 27 · BTC Independent Charting Fix (April 11, 2026)

- **BTC independent charting**: BTC trades 24/7 but was previously mapped only onto main index timestamps. When oil/S&P/world markets closed, BTC flatlined or disappeared. Fix appends real BTC timestamps beyond the last main reading so the BTC line continues live during off-hours. Index/S&P lines show as gaps (null) during closed hours — accurate behavior.
- **Oil commit:** 3e0108c — `public/index.html` (24 lines added)
- **World commit:** 9d94c68 — `public/index.html` (26 lines added)
- **QG reference docs updated**: Master v26.0, Deploy v8.0, Security v1.3, Account Recovery updated.
- **Methodology PDFs updated**: Oil v4.1, World v4.1, Cyber v3.3.

### Thread 28 · Bitcoin Market Index + Meetings Page + Stock Market Time Machine (April 11, 2026)

- **Bitcoin Market Index dashboard** created at `bitcoin.quantitativegenius.com` (port 5003, PM2 ID 5). BTC primary with S&P 500, NASDAQ, DJI as toggleable overlays (all ON by default). Based on Oil dashboard architecture but BTC-centric. Data: BTC-USD every 60s, NASDAQ/DJI every 5 min, S&P from World DB.
- **Meetings/checkout page** at `/meetings` with Stripe payment links for 5/10/15/30-min phone/video meetings ($35/$65/$95/$150). Collects name, phone, email via Stripe checkout. All homepage mailto links redirected to meetings page.
- **Stock Market Time Machine** clone site at randomized URL (`smtm-x7k9q2.html`) — mirrors homepage content with all four indices, links to meetings page.
- **Homepage updated** from "three indices" to "four indices" across all pages.
- **Hidden pricing pages** updated with Bitcoin Market Index card.
- **Stripe products:** Bitcoin Basic (`prod_UJxoNlMTbSpuFF`) with Basic/Pro price tiers.
- **Key commits (qg-deploy):** `6958558` (initial), `37ad7a1` (text cleanup), `f086124` (3→4 indices), `23cc7fe` (Bitcoin dashboard), `6756f3d` (pricing cards), `5177756` (webhook fix), `f31d988` (export/backfill).

### Thread 29 · Dual Y-Axis % Mode Fix + Oil Markets-Closed Fix (April 12, 2026)

- **Problem 1 — S&P 500 flat line in % mode (Bitcoin dashboard):** When % toggle was ON, S&P 500 appeared as a flat line because BTC % change (~1000%+ on MAX) compressed the stock % change (~200%) to near-zero on a shared axis.
- **Solution — Dual Y-axis % mode:** When BTC % change range is >5x the stock % change range, chart auto-splits to dual Y-axes (left: BTC %, right: Stock %). Below 5x threshold, all lines share a single left Y-axis as before. Applied to all three dashboards: Bitcoin, Oil, World.
- **Problem 2 — Oil 1H/1D blank when markets closed:** When oil/S&P markets are closed (weekends/holidays) and only BTC has data, the Oil 1H/1D chart showed only the BTC line with no context.
- **Solution — Markets-closed banner:** Oil dashboard now detects empty oil readings on 1H/1D, shows a "Markets Closed" banner, and renders a clean BTC-only chart on the left Y-axis with proper $ formatting. Tooltip handles null oil data gracefully.
- **Bug encountered:** First Bitcoin deploy broke ALL charts due to `let` temporal dead zone — `pctDualAxis` was used at line 1168 but defined at line 1222. Fixed by moving the calculation block before the dataset definitions.
- **Bitcoin commits (qg-deploy):** `c8af10d` (dual Y-axis), `0c81927` (temporal dead zone fix)
- **Oil fix:** Applied via SCP to VPS (not in git repo). Includes dual-axis % mode + markets-closed banner.
- **World fix:** Applied via SCP to VPS (not in git repo). Includes dual-axis % mode.
- **CSV export verified:** BTC CSV export confirmed working — 4,226 days of data from 2014-09-17 through today, always live DB query (no pre-generated files).
- **QG reference docs updated**: Master v27.0, Deploy v9.0.

### Thread 30 · Gold Time Machine + Documentation Round 5 (April 13, 2026)

- **Gold Time Machine dashboard** deployed at gold.quantitativegenius.com (port 5004, PM2 ID 4). GTM composite with 5 components: GC=F (30%), ^HUI (25%), GDX (20%), GC=F/SI=F ratio (15%), ^XAU (10%). Based on Bitcoin dashboard architecture.
- **Oil export zombie/OOM incident (April 13):** Oil generate_exports.py hung at 90% CPU for 8+ minutes. Root cause: correlated subquery O(N*M) in get_daily_close_readings() — same pattern as Known Issue #17 (April 10). Killed zombie PID 485163. Rewrote to dictionary-based lookups (fast mode) matching Bitcoin/Gold approach.
- **Oil export fix pushed:** qg-deploy commit ec5df73, oil-markets commit 9f9b203. Dictionary-based lookup eliminates O(N*M) correlated subquery.
- **100x scale discrepancy documented:** Chart frontend computes composites as (component/base)*100. CSV export computes as (component/base)*10000. Both produce same relative shape. Documented in Gold and Bitcoin methodology PDFs.
- **GTM May 2006 gap flagged:** GTM composite empty for rows before May 22, 2006 (GDX inception date). Individual components available from Aug 2000.
- **Bitcoin methodology updated to v2.0:** Added BMI composite weights (BTC 40%, NASDAQ 25%, S&P 20%, DJI 15%) and rationale section.
- **Gold methodology v1.0 created:** New document covering GTM composite design, component rationale, forward-fill methodology.
- **Nightly export updated:** nightly-export.sh now includes Bitcoin and Gold exports with timeout 120.
- **Documentation round 5:** All reference docs updated (Master v28.0, Deploy v10.0, Security v1.4, Account Recovery updated). All methodology PDFs current.
- **Branding rebrand (April 13):** Oil Markets Index → Oil Markets Time Machine. World Markets Index → World Markets Time Machine. Full rename including repos, VPS folders, PM2 names, methodology PDFs, and all documentation references. Bitcoin Market Index and Cybersecurity Threat Index names unchanged. Podcast names unchanged. See Branding History section for complete mapping.

---

## Branding History

This section records all brand name changes for reference during troubleshooting. Old names may still appear in Git commit messages, log files, and historical thread descriptions.

### Thread 30 Rebrand (April 13, 2026)

| Component | Old Name | New Name | Notes |
|---|---|---|---|
| Oil dashboard display name | Oil Markets Index | Oil Markets Time Machine | All user-facing references |
| Oil GitHub repo | oil-markets-index-dashboard | oil-markets-time-machine-dashboard | Repo rename required |
| Oil VPS folder | /home/support/oil-markets-index-dashboard/ | /home/support/oil-markets-time-machine-dashboard/ | Folder rename + PM2 update |
| Oil methodology PDF | Oil_Market_Index_Methodology_v4.1.pdf | Oil_Markets_Time_Machine_Methodology_v4.2.pdf | New version with rebrand |
| Oil subdomain | oil.quantitativegenius.com | oil.quantitativegenius.com | URL unchanged |
| World dashboard display name | World Markets Index | World Markets Time Machine | All user-facing references |
| World GitHub repo | world-markets-index-dashboard | world-markets-time-machine-dashboard | Repo rename required |
| World VPS folder | /home/support/world-markets-index-dashboard/ | /home/support/world-markets-time-machine-dashboard/ | Folder rename + PM2 update |
| World methodology PDF | World_Markets_Index_Methodology_v4.1.pdf | World_Markets_Time_Machine_Methodology_v4.2.pdf | New version with rebrand |
| World subdomain | world.quantitativegenius.com | world.quantitativegenius.com | URL unchanged |

### Names NOT Changed (Thread 30)

| Component | Current Name | Why Not Changed |
|---|---|---|
| Bitcoin dashboard | Bitcoin Market Index | Per user decision — no rebrand |
| Cybersecurity dashboard | Cybersecurity Threat Index | Per user decision — no rebrand |
| Gold dashboard | Gold Time Machine | Already uses Time Machine naming (created Thread 30) |
| Oil podcast | Daily Oil Markets Index Bulletin | Podcast names kept separate from dashboard rebrand |
| World podcast | World Market Index Podcast | Podcast names kept separate from dashboard rebrand |
| Cyber podcast | Cybersecurity Threat Index Podcast | No dashboard rebrand, no podcast rebrand |
| Parent brand | QuantitativeGenius.com | Unchanged |

### Cross-Reference: Where Old Names May Still Appear

- **Git commit messages** before Thread 30: All commits reference the old names. Do not rewrite Git history.
- **PM2 log files** on VPS: Old PM2 names will appear in historical logs.
- **Thread History entries** (Threads 1-29): Historical descriptions use old names intentionally — they record what happened at the time.
- **Nginx config**: Subdomain URLs did not change, but `proxy_pass` targets may reference old folder paths until the VPS folder rename is completed.
- **nightly-export.sh**: References old folder paths until updated on VPS.
- **deploy-guard.sh / deploy-done.sh**: May reference old PM2 names until updated.
- **Cross-DB dependency path**: Oil's S&P 500 overlay reads from `../world-markets-index-dashboard/data/world_markets.db` → must be updated to `../world-markets-time-machine-dashboard/data/world_markets.db` during VPS rename.

### Rebrand Deployment Checklist

When executing the repo/VPS rename:

- [ ] Rename GitHub repos (oil-markets-index-dashboard → oil-markets-time-machine-dashboard, world-markets-index-dashboard → world-markets-time-machine-dashboard)
- [ ] On VPS: Stop PM2 for oil and world (deploy-guard)
- [ ] Rename VPS folders: `mv /home/support/oil-markets-index-dashboard /home/support/oil-markets-time-machine-dashboard`
- [ ] Rename VPS folders: `mv /home/support/world-markets-index-dashboard /home/support/world-markets-time-machine-dashboard`
- [ ] Update `server.js` cross-DB path in Oil (../world-markets-time-machine-dashboard/data/world_markets.db)
- [ ] Update `server.js` cross-DB path in Bitcoin (../world-markets-time-machine-dashboard/data/world_markets.db)
- [ ] Update PM2 process names if needed
- [ ] Update nightly-export.sh paths
- [ ] Update deploy-guard.sh / deploy-done.sh if they reference folder names
- [ ] Update Nginx config if it references folder paths
- [ ] Update git remote URLs in VPS repos after GitHub rename
- [ ] Restart PM2, verify all 5 dashboards HTTP 200
- [ ] Verify nightly export still runs correctly

---

## Database Protection & Recovery

### Purpose

The deploy-guard system prevents the three most common causes of SQLite database corruption:

| Incident | Date | Cause |
|---|---|---|
| DB corruption #1 | April 6, 2026 | Auto-update cron ran `git pull` mid-write |
| DB corruption #2 | April 7, 2026 | Stale branch checkout overwrote DB file |
| DB corruption #3 | April 8, 2026 | `git reset --hard` executed while PM2 process was running |

### deploy-guard.sh — MANDATORY BEFORE ANY VPS FILE MODIFICATION

Location: `/home/support/deploy-guard.sh`

```bash
source ~/deploy-guard.sh <world|oil|cyber>
```

Steps performed:
1. **Stop PM2 process** for the relevant dashboard — ensures no active writes to the database.
2. **Back up the database** with a timestamp suffix (e.g., `readings.db.2026-04-08T14-32-00.bak`).
3. **Run `PRAGMA integrity_check`** on the database.
4. **Abort with error** if the integrity check does not return `ok`.

### deploy-done.sh — MANDATORY AFTER DEPLOYMENT

Location: `/home/support/deploy-done.sh`

```bash
source ~/deploy-done.sh <world|oil|cyber>
```

Steps performed:
1. **Restart the PM2 process** for the relevant dashboard.
2. **HTTP health check** — sends a request to the dashboard and confirms HTTP 200.
3. **DB integrity check** — runs `PRAGMA integrity_check` post-restart.

### Recovery Procedure

After any world DB restore from backup:

1. Check: `SELECT MIN(timestamp), COUNT(*) FROM country_data WHERE ticker='^GSPC'` — must start at 1987-01-02 with ~10,400+ records
2. If starting at 2000 or later, run the S&P 500 pre-2006 backfill script
3. Verify the Oil MAX chart shows S&P line starting at 1987

### WAL Mode

All QG SQLite databases run in Write-Ahead Logging (WAL) mode:

```sql
PRAGMA journal_mode=WAL;
```

---

## API Key System

### Key Format

```
qg_<32 random hex characters>
```

### Storage Model

| Data | How Stored |
|---|---|
| Full plaintext key | **Never stored** — shown to user once at generation, then discarded |
| Key hash | SHA-256 of the full key, stored in `api_keys` table |
| Display prefix | First 8 characters stored as `key_prefix` for UI display only |

### Key Lifecycle

- Each user may have **one active key** at a time.
- Generating a new key **immediately revokes** the previous key (old hash deleted from table).
- Keys can be explicitly deleted via `DELETE /auth/api-key`.

### Per-Product Access Control

API key validation is product-scoped. Each dashboard passes its own Stripe product ID when validating:

```
GET /auth/validate-key?key=qg_...&product=prod_XXXXXXXXXXXX
```

### Auth Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/api-key` | Generate new key (revokes old) |
| `DELETE` | `/auth/api-key` | Revoke current key |
| `GET` | `/auth/api-key-status` | Return key prefix and active status |
| `GET` | `/auth/validate-key?key=...&product=...` | Validate key + subscription for a product |

---

## Master Calculations Reference

### Oil Markets Time Machine Formula

```
composite = (brent_price × 0.7) + (wti_price × 0.3)
index_value = (composite / 147.0) × 5000
```

- WTI ATH normalization: WTI/145.29 × 5000
- Brent ATH normalization: Brent/146.08 × 5000
- Composite weighting: 70% Brent, 30% WTI (consistent across fetch_oil.py and backfill.py)

### World Markets Time Machine Formula

```
contribution = price × weight × SCALE_FACTOR
SCALE_FACTOR = 0.194715
```

- All 20 country weights sum to exactly 1.000
- USA weight: 0.246 (not 0.245)
- S&P ATH: price/7002 × 5000
- SSE ATH: price/6124 × 5000

### Glitch Protection

Incoming readings are validated before insertion. A reading is **rejected** if it represents a drop of more than **20%** from the most recent stored value.

### Duplicate Prevention

A reading is **silently skipped** if the change from the previous value is less than **0.01 points** (index) or **0.01%** (Bitcoin).

---

## Bitcoin Overlay (Thread 24)

### Overview

The Oil Markets Time Machine, World Markets Time Machine, and Bitcoin Market Index dashboards all include Bitcoin (BTC) price data. On Oil and World, BTC is an optional overlay toggle (Thread 24). On the Bitcoin Market Index (Thread 28), BTC is the primary asset with S&P 500, NASDAQ, and DJI as toggleable overlays.

### Data Source

- **Source:** Yahoo Finance BTC-USD ticker
- **Method:** Native Node.js `https.get` — NOT yfinance Python
- **Fetch interval:** Every 60 seconds in `server.js`
- **Why Node.js, not yfinance:** Bitcoin price is fetched on the server-side in the same process as the dashboard, avoiding an additional Python subprocess. This is consistent with the existing architecture where server.js manages the data collection loop.

### Database

| Field | Detail |
|---|---|
| Table name | `bitcoin_data` |
| Schema | `timestamp TEXT, price REAL` |
| Database (Oil) | `oil_markets.db` |
| Database (World) | `world_markets.db` |
| Dedup rule | Only stores a new row if price has changed ≥ 0.01% from the last stored reading |
| Backfill (Oil) | 4,649 historical records from 2014-09-17 to present via `backfill_bitcoin.py` (Thread 25) |
| Backfill (World) | None — BTC data accumulates from first deploy forward |

### API Endpoint

```
GET /api/bitcoin-history?range=1H|1D|1W|1Y|MAX
```

Protected by `requireAuth` middleware. Available on both Oil and World dashboards.

### Frontend Matching Algorithm

**For 1H and 1D ranges — Nearest-match within ±2 minutes:**

BTC readings are matched to index readings using binary search on a sorted array of BTC timestamps.

```javascript
// Constants
const BTC_MAX_GAP = 2 * 60 * 1000; // 2 minutes in milliseconds

// BTC data sorted ascending by timestamp
const btcSorted = [...btcData].sort((a, b) => new Date(a.t) - new Date(b.t));

// Binary search for nearest BTC reading
function findNearestBtc(targetTime, btcSorted) {
    // Binary search implementation
    // Returns nearest BTC price if within BTC_MAX_GAP, otherwise null
}
```

Remaining gaps after the ±2 minute window are legitimate — caused by the BTC dedup filter (price unchanged ≥ 0.01%).

**For 1W, 1Y, and MAX ranges — Date-level matching:**

```javascript
// BTC data keyed by YYYY-MM-DD date string
const btcDateMap = {};
btcData.forEach(b => {
    const dateKey = b.t.slice(0, 10); // YYYY-MM-DD
    btcDateMap[dateKey] = b.price;
});
```

### Algorithm Evolution

| Attempt | Method | Result |
|---|---|---|
| First attempt | Minute-only matching (exact minute key) | ~38% gaps — too many misses |
| Final | Nearest-match ±2 min via binary search | Remaining gaps are legitimate (BTC dedup filter) |

### UI/UX

| Property | Value |
|---|---|
| Toggle button | ₿ symbol |
| Button color | Orange #f7931a |
| Glow when active | Yes |
| Y-axis (raw mode) | Separate right Y-axis (BTC ~$80k vs index ~1–7k) |
| Y-axis (% mode) | Shared left Y-axis when ratio ≤5x; dual axes when ratio >5x (Thread 29 — see Section 23) |

### CSV Exports

The `bitcoin_price` column is added to both Oil and World export CSVs:

- **Oil CSV:** `date, index_value, wti_price, brent_price, bitcoin_price`
- **World CSV:** `date, composite_value, [20 country columns], bitcoin_price`

### BTC Independent Charting (Thread 27 · April 11, 2026)

BTC trades 24/7 but the chart previously mapped BTC data points onto main index timestamps only. When oil/S&P/world markets closed, BTC would flatline or disappear from the chart. The fix appends real BTC timestamps beyond the last main index reading, so the BTC line continues showing live price movement during off-hours. Index and S&P lines render as gaps (null) during closed hours — this is accurate since those markets are not trading.

- **Oil commit:** 3e0108c — `public/index.html` (24 lines added)
- **World commit:** 9d94c68 — `public/index.html` (26 lines added)

### Key Commits

| Dashboard | Commit | Description |
|---|---|---|
| World | 62d3201 | BTC overlay with nearest-match algorithm |
| World | 9d94c68 | BTC independent charting (continues when markets closed) |
| Oil | 815d02a | BTC overlay with nearest-match algorithm |
| Oil | 3e0108c | BTC independent charting (continues when markets closed) |
| Bitcoin | c8af10d | Dual Y-axis % mode (Thread 29) |
| Bitcoin | 0c81927 | Temporal dead zone fix for pctDualAxis (Thread 29) |

---

## OOM Crash Fix (Thread 24 / April 8, 2026)

### Incident Summary

All three PM2 processes were killed by the Linux kernel OOM (Out of Memory) killer. The e2-micro VPS had only 1GB RAM and no swap file configured. Running 3 Node.js servers, 2 Python fetchers, Google Ops Agent, nginx, and snapd simultaneously exhausted all physical memory. The kernel OOM killer cascaded into a full system freeze. GCP auto-rebooted the VM; all three sites were down for approximately 7 hours.

### Root Cause

- e2-micro VM: 958MB RAM
- No swap file
- Memory consumers: 3 Node.js dashboard processes + 2 Python fetchers + Google Ops Agent + nginx + snapd
- yfinance can spike memory during bulk historical data fetches

### Fix

Created a 2GB swap file at `/swapfile`, made persistent via `/etc/fstab`.

```bash
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile
echo '/swapfile none swap sw 0 0' >> /etc/fstab
```

### Verification

```bash
# Verify swap is active
free -h
# Expected output includes: Swap:  2.0Gi

# Verify swap survives reboots
grep swap /etc/fstab
# Expected: /swapfile none swap sw 0 0
```

### Status

Swap file is permanent (persists across reboots via /etc/fstab). This fix is also documented in the Security Reference (Section 9) and is part of the monthly monitoring checklist.

---

## CSV Export Date Filter Fix (Thread 24)

### Problem

The World dashboard MAX CSV export was showing rows starting `2006-01-02` instead of the correct first trading day `2006-01-04`. The database was correctly trimmed to start at 2006-01-04 (done in Thread 19), but the pre-generated export file in `data/exports/` was stale and had not been regenerated after the trim.

### Root Cause

Pre-generated export files in `data/exports/` are served before live DB queries (via `tryServeFile()`). After the Thread 19 database trim removed the 1/2 and 1/3 rows, the pre-generated CSV was not regenerated — it continued to serve the old file with the incorrect start date.

### Fix

Re-ran `generate_exports.py` directly on the VPS:

```bash
source ~/deploy-guard.sh world
cd /home/support/world-markets-time-machine-dashboard
python3 generate_exports.py
source ~/deploy-done.sh world
```

### Prevention

The nightly export cron (`nightly-export.sh`) runs `generate_exports.py` automatically at 4:00 AM UTC (9:00 PM PDT) daily. However, after any manual database modification (trim, restore, backfill), the export files must be regenerated immediately rather than waiting for the nightly cron.

**Rule:** After any database trim, restore, or schema change affecting the export output, immediately run `python3 generate_exports.py` on the VPS (after stopping PM2 via deploy-guard).

---

## Nightly Export Cron (Thread 25)

### Overview

The nightly export cron replaces the old PM2-based `oil-export-cron` and `world-export-cron` processes. Those PM2 crons were unreliable — PM2’s `cron_restart` only fires for processes in "online" state, and both had drifted to "stopped" status, meaning exports never ran.

### How It Works

A system crontab entry runs `/home/support/nightly-export.sh` at 4:00 AM UTC (9:00 PM PDT) daily:

1. **Stop** Oil and World PM2 dashboards (prevents OOM — Python exports + Node.js dashboards exceed 1GB RAM)
2. **Run** Oil `generate_exports.py` (with 120s timeout)
3. **Run** World `generate_exports.py` (with 120s timeout)
4. **Run** Bitcoin `generate_exports.py` (with 120s timeout) — added Thread 30
5. **Run** Gold `generate_exports.py` (with 120s timeout) — added Thread 30
6. **Restart** Oil and World PM2 dashboards
7. **Health check** — verifies HTTP 200 from both dashboards
8. **Save PM2 state** — `pm2 save`

Cyber dashboard stays running throughout (it has no exports). Bitcoin and Gold exports added in Thread 30.

### Downtime Window

Oil and World dashboards are offline for approximately 30 seconds each night at 9:00 PM PDT during the export run.

### Files

| File | Location |
|---|---|
| Export script | `/home/support/nightly-export.sh` |
| Log file | `/home/support/nightly-export.log` |
| System crontab | `crontab -l` as `support` user |
| Cron expression | `0 4 * * *` (4:00 AM UTC / 9:00 PM PDT) |

### Verification

```bash
# Verify cron is installed
crontab -l
# Expected: 0 4 * * * /home/support/nightly-export.sh

# Check last export run
tail -20 /home/support/nightly-export.log
```

### Why Not PM2 Cron?

PM2’s `cron_restart` feature has a critical limitation: it only triggers for processes in "online" state. The export scripts are designed to run once and exit (not stay running), so PM2 marks them as "stopped" after completion. Once stopped, PM2 never re-triggers them. A system crontab doesn’t have this limitation.

Additionally, PM2 `cron_restart` cannot stop other PM2 processes before running — the export scripts must run with dashboards stopped to avoid OOM on the memory-constrained VPS.

---

## WAL Mode Fix (Thread 25)

### Problem

Oil’s SQLite database was using `delete` journal mode (the legacy default), while World’s was using `wal` (Write-Ahead Logging). In `delete` mode, a write operation locks the entire database file. Since Oil’s server writes a new reading every 60 seconds AND serves API requests (reads) concurrently, ~18% of fetch attempts were failing with "database is locked" errors.

### Fix

Switched Oil’s database to WAL mode:

```sql
sqlite3 /home/support/oil-markets-time-machine-dashboard/data/oil_markets.db 'PRAGMA journal_mode=WAL;'
```

This is a one-time, non-destructive change. WAL mode persists across database opens — it only needs to be set once.

### Current State

All QG SQLite databases now use WAL mode:

| Database | Journal Mode |
|---|---|
| oil_markets.db | WAL |
| world_markets.db | WAL |
| cybersecurity.db | WAL (verify) |
| bitcoin_markets.db | WAL (set on creation via server.js) |

### Verification

```bash
sqlite3 /home/support/oil-markets-time-machine-dashboard/data/oil_markets.db 'PRAGMA journal_mode;'
# Expected: wal
```

---

## Dual Y-Axis % Mode (Thread 29)

### Problem

When the % Change toggle is active and BTC is enabled alongside stock overlays, BTC's percentage change over long periods (e.g., ~1000%+ on MAX) dwarfs the stock percentage change (~200%). On a shared single Y-axis, the stock lines are compressed to near-flat, making them unreadable.

### Solution — Adaptive Dual Y-Axes

A dynamic threshold-based system detects when dual axes are needed:

```javascript
let pctDualAxis = false;
const maxBtcPct = Math.max(...btcPctData.filter(v => v !== null).map(Math.abs));
const maxStockPct = Math.max(...stockPctData.filter(v => v !== null).map(Math.abs));
// If BTC % range is > 5x the stock % range, use dual axes
if (maxStockPct > 0 && maxBtcPct / maxStockPct > 5) {
  pctDualAxis = true;
}
```

### Behavior

| Condition | Y-Axis Layout |
|---|---|
| % mode OFF (raw prices) | Left: primary asset ($), Right: overlays ($) — always dual |
| % mode ON, BTC/stock ratio ≤ 5x | Single shared left Y-axis (all lines as % change) |
| % mode ON, BTC/stock ratio > 5x | Left: BTC % change, Right: Stock % change — dual axes |
| % mode ON, only one line visible | Single left Y-axis |

### Axis Labels

- **Bitcoin dashboard:** Left = "BTC % Change", Right = "Stock % Change" (when dual). Left = "% Change" (when shared).
- **Oil dashboard:** Left = "Bitcoin (USD)" or "Oil / S&P % Change" (when dual in % mode). Right = "BTC % Change" (when dual).
- **World dashboard:** Left = "BTC % Change" or "% Change", Right = "Stock % Change" (when dual).

### Threshold

The 5x ratio was chosen empirically:
- On MAX view, BTC since 2014 shows ~1000%+ change while S&P shows ~200% — ratio ~5x+, dual axes activate.
- On 1W/1M views, BTC and stocks often move within similar %, so they share a single axis.
- The threshold adapts automatically to the visible time range.

### Dashboards Affected

| Dashboard | Commit | Method |
|---|---|---|
| Bitcoin | `c8af10d`, `0c81927` (fix) | Git push → VPS pull |
| Oil | SCP to VPS (not in git) | Direct file deploy |
| World | SCP to VPS (not in git) | Direct file deploy |

### Markets-Closed Banner (Oil Only)

When oil/S&P readings are empty for 1H/1D (weekends/holidays) but BTC has data:

1. A "Markets Closed" banner appears above the chart
2. Chart renders BTC-only on the left Y-axis with proper `$` formatting
3. Tooltip gracefully handles null oil data using `indexData[idx]` check
4. Right Y-axis is hidden (no stock data to display)

### Known Edge Cases

- **S&P 500 line stops before BTC on weekends:** Expected behavior — S&P doesn't trade weekends, so the blue line ends at Friday's close while BTC continues through Saturday/Sunday.
- **NASDAQ/DJI weekend data:** Yahoo Finance returns Friday's closing price when queried on weekends. These appear in the DB with weekend timestamps but represent the last real close.

---

*End of QG-Master-Reference-v27.0.md*
