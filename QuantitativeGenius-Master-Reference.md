# QuantitativeGenius.com — Master Reference Guide

**Last Updated:** April 1, 2026
**Owner:** jq_007@yahoo.com
**Brand:** QuantitativeGenius.com

---

## Table of Contents

1. [Infrastructure Overview](#infrastructure-overview)
2. [Google Cloud VM](#google-cloud-vm)
3. [Dashboards](#dashboards)
4. [GitHub Repositories](#github-repositories)
5. [Podcast Projects](#podcast-projects)
6. [Cron Jobs & Automation](#cron-jobs--automation)
7. [Domain & DNS](#domain--dns)
8. [How to Restore Everything from Scratch](#how-to-restore-everything-from-scratch)
9. [How to SSH into the VM](#how-to-ssh-into-the-vm)
10. [Key Technical Details](#key-technical-details)
11. [Accounts & Credentials](#accounts--credentials)
12. [Thread History](#thread-history)

---

## Infrastructure Overview

```
┌─────────────────────────────────────────────────┐
│              QuantitativeGenius.com              │
│                  (Wix website)                   │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│         Google Cloud VM (e2-micro)               │
│         IP: 136.117.206.145                      │
│         Ubuntu 22.04 LTS, 30GB disk              │
│                                                  │
│  ┌─────────────┐ ┌──────────────┐ ┌───────────┐ │
│  │ Oil Markets  │ │ World Markets│ │ Cybersec  │ │
│  │ Port 5000    │ │ Port 5001    │ │ Port 5002 │ │
│  └─────────────┘ └──────────────┘ └───────────┘ │
│                                                  │
│  Nginx (port 80/443) → subdomain routing         │
│  SSL via Let's Encrypt (auto-renew)              │
│  PM2 process manager (auto-restart on reboot)    │
│  Hourly cron: git pull + pm2 restart             │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│              GitHub (Public Repos)                │
│         User: CybersecurityAnnouncementDotcom    │
│                                                  │
│  Dashboards:                                     │
│  • oil-markets-index-dashboard                   │
│  • world-markets-index-dashboard                 │
│  • cybersecurity-threat-index-dashboard           │
│                                                  │
│  Podcasts (GitHub Pages):                        │
│  • oil-market-index-podcast                      │
│  • world-market-index-podcast                    │
│  • cybersecurity-bulletin-podcast                │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│           Perplexity Computer (Cron Jobs)         │
│                                                  │
│  • Cybersecurity Threat Index — 6:00 AM PDT daily│
│  • Oil Markets Index Bulletin — multiple daily    │
│  • World Market Index — PAUSED                   │
└─────────────────────────────────────────────────┘
```

---

## Google Cloud VM

| Setting | Value |
|---|---|
| Project | `quantitativegenius` |
| Project ID | `tonal-affinity-492010-j5` |
| Instance Name | `quantgenius-server` |
| Zone | `us-west1-b` |
| Machine Type | e2-micro (free tier eligible) |
| OS | Ubuntu 22.04 LTS |
| Disk | 30GB standard |
| External IP | `136.117.206.145` |
| SSH User | `support` |
| Internal IP | `10.138.0.2` |

### Firewall Rules
- `allow-dashboards` — TCP ports 5000, 5001, 5002
- `default-allow-http` — TCP port 80
- `default-allow-https` — TCP port 443

### What's Running on the VM
- **PM2** manages 3 Node.js processes (auto-restarts on crash/reboot)
- **Nginx** reverse proxy with SSL (subdomain routing)
- **Let's Encrypt** SSL certificates (auto-renew via certbot timer)
- **Hourly cron** — `~/auto-update.sh` runs `git pull` on all 3 repos + `pm2 restart all`

### PM2 Processes

| ID | Name | Port | Status |
|---|---|---|---|
| 0 | oil-dashboard | 5000 | online |
| 1 | world-dashboard | 5001 | online |
| 2 | cyber-dashboard | 5002 | online |

---

## Dashboards

### Oil Markets Index
- **URL:** https://oil.quantitativegenius.com
- **Direct:** http://136.117.206.145:5000
- **Data source:** yfinance (CL=F for WTI, BZ=F for Brent)
- **Fetch interval:** Every 60 seconds
- **Index scale:** 0–5,000
- **Formula:** `(composite / 147.0) * 5000`
- **Composite:** `(WTI × 0.4) + (Brent × 0.6)`
- **Color scheme:** Brown background, yellow/gold lettering
- **Big number color:** Yellow (`#f5c542`)
- **Chart overlays:** WTI in blue (#3b82f6), Brent in orange (#e07a3a)
- **ATH normalization:** WTI/145.29 × 5000, Brent/146.08 × 5000
- **Tooltip:** Composite in gold (#d4af37), WTI in blue with $ price, Brent in orange with $ price
- **Historical data:** 6,650+ records from 2000 to present
- **Weekly averaging:** MAX and 1Y views use `GROUP BY strftime('%Y-%W')`

### World Markets Index
- **URL:** https://world.quantitativegenius.com
- **Direct:** http://136.117.206.145:5001
- **Data source:** yfinance (20 country tickers)
- **Index scale:** 0–5,000 base (grows over time)
- **Header text:** Blue "WORLD MARKETS INDEX"
- **Big number font:** DM Sans 700 (bolder/softer)
- **Chart overlays:** S&P 500 in blue (#4488ff), SSE in red (#ef4444), World in green (#22c55e)
- **ATH normalization:** S&P: price/7002 × 5000, SSE: price/6124 × 5000
- **Historical data:** 5,281 records from 2006 to present
- **Weekly averaging:** MAX and 1Y views use `GROUP BY strftime('%Y-%W')`
- **Countries (20):** Russia/MOEX removed

| Country | Weight | Ticker |
|---|---|---|
| USA | 24.5% | ^GSPC |
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
- **Historical data:** 123 monthly scores from Jan 2016 to Mar 2026
- **Gauge:** Horseshoe opening at bottom, orange arc to score mark, gray remainder, gray knob at boundary
- **75% text and rating card:** Orange
- **Change indicator:** Green when threat goes DOWN (good), red when UP (bad)
- **No decimals:** Show "-5%" not "-5.0%"
- **Threat categories:** 15 types (Ransomware, Phishing, etc.)
- **Distribution colors:** Blue/purple/cyan (no green/yellow/orange/red)
- **1M tab:** Hidden until 30+ daily data points accumulated
- **API endpoints:** POST /api/readings, POST /api/threat-types

### Common Dashboard Settings
- **Footer:** "Sponsored by QuantitativeGenius.com"
- **Disclaimer:** "This research publication is not intended to be investment advice and is not from a Registered Investment Advisor."
- **Time format:** UTC / PDT / Stanford University Time
- **No "Live" label** — never use the word "Live" anywhere

---

## GitHub Repositories

**GitHub User:** [CybersecurityAnnouncementDotcom](https://github.com/CybersecurityAnnouncementDotcom)

### Dashboard Repos (All Public)

| Repo | Last Commit | URL |
|---|---|---|
| oil-markets-index-dashboard | `4bb138c` | https://github.com/CybersecurityAnnouncementDotcom/oil-markets-index-dashboard |
| world-markets-index-dashboard | `134170e` | https://github.com/CybersecurityAnnouncementDotcom/world-markets-index-dashboard |
| cybersecurity-threat-index-dashboard | `136a784` | https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard |

### Podcast Repos (All Public, GitHub Pages enabled)

| Repo | RSS Feed | URL |
|---|---|---|
| cybersecurity-bulletin-podcast | https://cybersecurityannouncementdotcom.github.io/cybersecurity-bulletin-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-bulletin-podcast |
| world-market-index-podcast | https://cybersecurityannouncementdotcom.github.io/world-market-index-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/world-market-index-podcast |
| oil-market-index-podcast | https://cybersecurityannouncementdotcom.github.io/oil-market-index-podcast/feed.xml | https://github.com/CybersecurityAnnouncementDotcom/oil-market-index-podcast |

### Each Dashboard Repo Contains
- `server.js` — Express backend with SQLite, yfinance fetching, API endpoints
- `public/index.html` — Frontend dashboard (single-page)
- `data/*.db` — SQLite database (in .gitignore, not pushed)
- `backfill.py` — Historical data backfill script (uses yfinance)
- `fetch_*.py` — Real-time price fetch script (called by server.js)
- `package.json` — Node.js dependencies
- `deploy/gcloud-setup/` — VM setup scripts (oil repo only)

### Git Configuration
```
git config user.name "CybersecurityAnnouncementDotcom"
git config user.email "jq_007@yahoo.com"
```

---

## Podcast Projects

### Cybersecurity Threat Index Podcast
- **Title:** Cybersecurity Threat Index
- **Brand:** QuantitativeGenius.com
- **Schedule:** Daily at 6:00 AM PDT (cron ID: 286060d1)
- **Voice:** kore (TTS)
- **YouTube:** Unlisted, notifySubscribers = false
- **Email recipients:** jq_007@yahoo.com, jq_007@icloud.com
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/cybersecurity-bulletin-podcast/feed.xml
- **Platforms:** Spotify, Apple Podcasts, Amazon Music

**Daily Workflow:**
1. Research latest cybersecurity threats
2. Calculate Threat Level Estimate (0-100%)
3. Estimate threat type distribution percentages
4. Write bulletin email
5. Generate TTS audio narration (kore voice)
6. Create scrolling text video (1920x1080, dark theme, header/footer bars)
7. Upload to YouTube (unlisted, no subscriber notification)
8. Push podcast episode to GitHub feed
9. Send emails to jq_007@yahoo.com and jq_007@icloud.com
10. Update the Cybersecurity dashboard with new data point
11. Send notification with summary

### Oil Markets Index Bulletin
- **Title:** Daily Oil Markets Index Bulletin
- **Brand:** QuantitativeGenius.com
- **Email recipients:** jq_007@yahoo.com, jq_007@icloud.com, oilmarketsindex@gmail.com
- **YouTube channel:** OilMarketIndexDotcom
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/oil-market-index-podcast/feed.xml
- **Schedule:** Multiple times daily — 1AM, 5AM, 6AM (podcast), 7AM, 8AM, 9AM, 10AM, 11AM, 12PM, 1PM, 5PM, 8PM PDT

### World Market Index Podcast
- **Title:** World Market Index
- **Brand:** QuantitativeGenius.com
- **Status:** PAUSED (as of April 1, 2026)
- **Previous schedule:** Daily at 1:00 AM PDT
- **RSS Feed:** https://cybersecurityannouncementdotcom.github.io/world-market-index-podcast/feed.xml
- **Platforms:** Spotify, Apple Podcasts, Amazon Music
- **Sources:** CNBC, CNN, WSJ, Reuters, Bloomberg, MarketWatch, Yahoo Finance, IBD
- **Intro:** Japanese reporter video (silent mode, 2 seconds)
- **To resume:** Ask Perplexity Computer to recreate the cron job

---

## Cron Jobs & Automation

### On the Google Cloud VM
- **Hourly auto-update:** `~/auto-update.sh` runs at minute 0 every hour
  - `git pull` on all 3 dashboard repos
  - `pm2 restart all`
  - Logs to `~/auto-update.log`

### On Perplexity Computer
- **Cybersecurity Threat Index** — Daily 6:00 AM PDT (cron ID: 286060d1, UTC: `0 13 * * *`)
- **Oil Markets Index Bulletin** — Multiple daily (schedules set in prior threads)
- **World Market Index** — PAUSED

### SSL Certificate Renewal
- **Certbot timer** runs automatically on the VM
- Current certificate expires June 30, 2026
- Auto-renews before expiration — no action needed

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

---

## How to Restore Everything from Scratch

### If the VM dies or needs to be rebuilt:

**Step 1: Create a new VM**
```bash
# Google Cloud Console > Compute Engine > Create Instance
# Name: quantgenius-server
# Zone: us-west1-b
# Machine: e2-micro
# OS: Ubuntu 22.04 LTS
# Disk: 30GB standard
# Allow HTTP + HTTPS traffic
```

**Step 2: Add firewall rule**
```bash
# VPC Network > Firewall > Create Rule
# Name: allow-dashboards
# Targets: All instances
# Source: 0.0.0.0/0
# Protocols: TCP 5000,5001,5002
```

**Step 3: SSH in and run setup**
```bash
# Install Node.js, PM2, Python, Nginx
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs nginx python3-pip
sudo npm install -g pm2
pip3 install yfinance pandas

# Clone all 3 repos
cd ~
git clone https://github.com/CybersecurityAnnouncementDotcom/oil-markets-index-dashboard.git
git clone https://github.com/CybersecurityAnnouncementDotcom/world-markets-index-dashboard.git
git clone https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard.git

# Install dependencies
cd ~/oil-markets-index-dashboard && npm install
cd ~/world-markets-index-dashboard && npm install
cd ~/cybersecurity-threat-index-dashboard && npm install

# Backfill databases
cd ~/cybersecurity-threat-index-dashboard && python3 seed_data.py
cd ~/oil-markets-index-dashboard && python3 backfill.py
cd ~/world-markets-index-dashboard && python3 backfill.py

# Start all dashboards with PM2
cd ~/oil-markets-index-dashboard && pm2 start server.js --name oil-dashboard -- --port 5000
cd ~/world-markets-index-dashboard && pm2 start server.js --name world-dashboard -- --port 5001
cd ~/cybersecurity-threat-index-dashboard && pm2 start server.js --name cyber-dashboard -- --port 5002

# Set PM2 to auto-start on reboot
pm2 save
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u support --hp /home/support
pm2 save
```

**Step 4: Set up Nginx + SSL**
```bash
# Create Nginx config (use subdomain-based routing)
# See Nginx config in this document below
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d oil.quantitativegenius.com -d world.quantitativegenius.com -d cyber.quantitativegenius.com --non-interactive --agree-tos -m jq_007@yahoo.com
```

**Step 5: Set up auto-update cron**
```bash
cat > ~/auto-update.sh << 'SCRIPT'
#!/bin/bash
cd /home/support/oil-markets-index-dashboard && git pull origin main
cd /home/support/world-markets-index-dashboard && git pull origin main
cd /home/support/cybersecurity-threat-index-dashboard && git pull origin main
pm2 restart all
SCRIPT
chmod +x ~/auto-update.sh
(crontab -l 2>/dev/null; echo "0 * * * * /home/support/auto-update.sh >> /home/support/auto-update.log 2>&1") | sort -u | crontab -
```

**Step 6: Update DNS (if IP changed)**
- Go to Wix Studio > Domains > quantitativegenius.com > DNS Records
- Update the A records for oil, world, cyber subdomains to the new IP

---

## How to SSH into the VM

1. Go to https://console.cloud.google.com
2. Select project `quantitativegenius` (ID: `tonal-affinity-492010-j5`)
3. Navigate to Compute Engine > VM Instances
4. Click **SSH** next to `quantgenius-server`

### Useful SSH Commands
```bash
pm2 list                    # Check dashboard status
pm2 logs                    # View real-time logs
pm2 restart all             # Restart all dashboards
pm2 stop all                # Stop all dashboards
pm2 start all               # Start all dashboards

tail -f ~/auto-update.log   # Check auto-update cron logs

sudo nginx -t               # Test Nginx config
sudo systemctl restart nginx # Restart Nginx
sudo certbot renew --dry-run # Test SSL renewal

cd ~/oil-markets-index-dashboard && git pull    # Manual update from GitHub
cd ~/world-markets-index-dashboard && git pull
cd ~/cybersecurity-threat-index-dashboard && git pull
```

---

## Key Technical Details

### Data Sources
- **Oil & World Dashboards:** yfinance (free, no API key needed)
- **Cybersecurity Dashboard:** Perplexity Computer daily research + seed_data.py
- **Podcasts:** Web research via Perplexity Computer cron jobs

### Important Tickers
- Saudi Arabia: `^TASI.SR` (NOT `^TASI`)
- China SSE: `000001.SS`
- Turkey: `XU100.IS`
- Italy: `FTSEMIB.MI`

### Known Issues & Fixes
- `pandas_datareader` has compatibility issues with Python 3.12 — use yfinance directly
- Sawtooth noise on MAX/1Y charts — fixed with weekly averaging (`GROUP BY strftime('%Y-%W')`)
- Glitch protection — servers reject any reading that drops >20% from previous value
- YouTube API uploads require publicly accessible URL for filePath (local paths fail silently)

### Branding
- **Current brand:** QuantitativeGenius.com
- **Replaces:** UnhackableComputers.com, CybersecurityAnnouncement.com, GeniusMarketIntelligence.com, GeniusMarketResearch.com
- **Footer on all dashboards:** "Sponsored by QuantitativeGenius.com"
- **Disclaimer on all dashboards:** "This research publication is not intended to be investment advice and is not from a Registered Investment Advisor."

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

---

## Thread History

These are the Perplexity Computer threads where the projects were built:

### Thread 1 — Original Dashboard Build + Oil Bulletins
- Built Oil Markets Index dashboard
- Built World Markets Index dashboard
- Set up Oil Markets Index bulletins (multiple daily)
- Branding updates from old brands to QuantitativeGenius.com
- Fixed chart scaling, tooltip colors, sawtooth noise

### Thread 2 — Cybersecurity Threat Index Dashboard + Podcast
- Rebranded from "Daily Cybersecurity Threat Bulletin" to "Cybersecurity Threat Index"
- Built Cybersecurity Threat Index dashboard (gauge, chart, distribution)
- Set up daily 6:00 AM cron for podcast + dashboard updates
- Cleared old podcast episodes from GitHub
- Recalculated threat scores from 2016 (including WannaCry, etc.)

### Thread 3 — World Market Index Podcast
- Built World Market Index podcast (same workflow as Cybersecurity)
- Set up daily 1:00 AM cron (currently PAUSED)
- Japanese reporter intro video (silent, 2 seconds)

### Thread 4 — GitHub Push + Google Cloud Deployment (THIS THREAD)
- Pushed all 3 dashboard repos to GitHub (public)
- Created Google Cloud VM (e2-micro, Ubuntu 22.04)
- Deployed all 3 dashboards with PM2
- Backfilled all databases on the VM
- Set up Nginx reverse proxy with subdomain routing
- Set up SSL via Let's Encrypt
- Set up hourly auto-update cron
- Configured DNS on Wix (oil/world/cyber subdomains)

---

## Quick Reference URLs

| What | URL |
|---|---|
| Oil Dashboard | https://oil.quantitativegenius.com |
| World Dashboard | https://world.quantitativegenius.com |
| Cyber Dashboard | https://cyber.quantitativegenius.com |
| Oil (direct IP) | http://136.117.206.145:5000 |
| World (direct IP) | http://136.117.206.145:5001 |
| Cyber (direct IP) | http://136.117.206.145:5002 |
| Google Cloud Console | https://console.cloud.google.com |
| GitHub Profile | https://github.com/CybersecurityAnnouncementDotcom |
| Wix DNS Management | https://manage.wix.com/studio/domains |
| Cyber Podcast Feed | https://cybersecurityannouncementdotcom.github.io/cybersecurity-bulletin-podcast/feed.xml |
| World Podcast Feed | https://cybersecurityannouncementdotcom.github.io/world-market-index-podcast/feed.xml |
| Oil Podcast Feed | https://cybersecurityannouncementdotcom.github.io/oil-market-index-podcast/feed.xml |

---

*This document serves as the master reference for all QuantitativeGenius.com projects. To restore anything, start a new Perplexity Computer thread and reference this guide.*
