# QuantitativeGenius.com — Account Recovery Guide

**Purpose:** If you lose access to your Perplexity Computer account, follow these steps in a new account to restore full operational capability.

**Prerequisites:** You must have copies of these three documents:
- `QG-Master-Reference-v28.0.md`
- `QG-Deployment-Guide-v10.0.md`
- `QG-Security-Reference-v1.4.md`

---

## Step 1: Paste Reference Docs

In your first message to the new Perplexity Computer account, paste all three reference docs (or attach them as files) and say:

> "These are my infrastructure reference documents. Read them and use them to guide all future work on QuantitativeGenius.com."

This gives the agent the full architecture, safety rules, deployment procedures, database schemas, and incident history.

---

## Step 2: Connect GitHub

### What to do
1. In Perplexity Computer, type: "Connect my GitHub account"
2. The agent will show an OAuth popup — click it and authorize with your GitHub account
3. After connecting, verify by asking: "List repos in the CybersecurityAnnouncementDotcom org"

### What this restores
- Push/pull access to all 5 QG repos and 4 Scoring Systems repos
- Ability to commit and push code changes before deploying to VPS

### Your GitHub details
| Field | Value |
|---|---|
| Organization | `CybersecurityAnnouncementDotcom` |
| Git user.name | `QuantitativeGenius` |
| Git user.email | `jq_007@yahoo.com` |

### Repositories (QG)
| Repo | Visibility | Branch |
|---|---|---|
| `oil-markets-time-machine-dashboard` | PUBLIC | `main` |
| `world-markets-time-machine-dashboard` | PUBLIC | `main` |
| `cybersecurity-threat-index-dashboard` | PUBLIC | `main` |
| `qg-auth` | PRIVATE | `master` |
| `qg-deploy` | PRIVATE | `master` |

### Repositories (Scoring Systems)
| Repo | Visibility |
|---|---|
| `rent-history-score` | PRIVATE |
| `employment-history-score` | PRIVATE |
| `performance-review-score` | PRIVATE |
| `scoring-systems-admin` | PRIVATE |

### Direct links
- https://github.com/CybersecurityAnnouncementDotcom/oil-markets-time-machine-dashboard
- https://github.com/CybersecurityAnnouncementDotcom/world-markets-time-machine-dashboard
- https://github.com/CybersecurityAnnouncementDotcom/cybersecurity-threat-index-dashboard
- https://github.com/CybersecurityAnnouncementDotcom/qg-auth (private)
- https://github.com/CybersecurityAnnouncementDotcom/qg-deploy (private)
- https://github.com/CybersecurityAnnouncementDotcom/rent-history-score (private)
- https://github.com/CybersecurityAnnouncementDotcom/employment-history-score (private)
- https://github.com/CybersecurityAnnouncementDotcom/performance-review-score (private)
- https://github.com/CybersecurityAnnouncementDotcom/scoring-systems-admin (private)

---

## Step 3: Establish SSH Access to VPS

### What to do
1. Ask the agent: "Generate a new SSH key for VPS access"
2. The agent will run: `ssh-keygen -t ed25519 -f /home/user/.ssh/id_ed25519 -N '' -C 'computer-agent'`
3. The agent will display the public key
4. **You must add this key to the VPS manually:**

### How to add the SSH key (you do this part)
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Navigate to: **Compute Engine → VM instances**
3. Find your VM (IP: `136.117.206.145`, type: `e2-micro`)
4. Click **SSH** (opens SSH-in-browser as your Google account)
5. In that terminal, run:
   ```bash
   # Switch to support user
   sudo su - support
   
   # Add the public key (paste the key the agent gave you)
   echo "THE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
   ```
6. Go back to Perplexity Computer and say: "Test SSH connection"
7. The agent will run: `ssh -o StrictHostKeyChecking=no support@136.117.206.145 'echo connected'`

### VPS details
| Field | Value |
|---|---|
| IP Address | `136.117.206.145` |
| SSH User | `support` |
| SSH Key Path (in sandbox) | `/home/user/.ssh/id_ed25519` |
| Key Type | `ed25519` |
| Key Comment | `computer-agent` |
| SSH Command | `ssh -o StrictHostKeyChecking=no support@136.117.206.145` |
| Root Access | Not available via SSH from Perplexity (no passwordless sudo for `support`) |
| Root Operations | Must be done via Google Cloud SSH-in-browser |

### Important
- The SSH key is **ephemeral** — it dies when the Perplexity sandbox session ends
- You'll need to repeat this key-adding process at the start of each new session (this is normal, same as current account)
- The agent cannot do anything on VPS as `root` — nginx changes, auth server restarts, etc. require Google Cloud SSH-in-browser

---

## Step 4: Connect Google Calendar

### What to do
1. Ask the agent: "Connect my Google Calendar"
2. OAuth popup will appear — authorize with your Google account
3. Verify: "Show my upcoming calendar events"

### What this restores
- Calendar event reading/creation
- Email search and sending via Gmail

### Your email
- **Account email:** `jq_007@yahoo.com`
- **Service email (Resend):** `service@quantitativegenius.com`
- **Support email:** `support@quantitativegenius.com`

---

## Step 5: Connect Resend (Email API)

### What to do
1. Ask the agent: "Connect my Resend account"
2. OAuth popup — authorize
3. Verify: "Send a test email via Resend"

### What this restores
- Ability to send emails from `service@quantitativegenius.com` via the Resend API
- Used by the auth system for magic link login emails

### Resend details
- **From address:** `service@quantitativegenius.com`
- **Replies forward to:** `support@quantitativegenius.com`
- **API key location on VPS:** `/opt/qg-auth/ecosystem.config.js` (already configured — this connector is for Perplexity-side email ops only)

---

## Step 6: Connect YouTube Data API

### What to do
1. Ask the agent: "Connect my YouTube account"
2. OAuth popup — authorize
3. Verify: "List my YouTube channel stats"

### What this restores
- Video uploads, thumbnail uploads, playlist management
- Used for QG podcast/video content

---

## Step 7: Verify Everything Works

Ask the agent to run this checklist:

> "Run a full health check: clone a QG repo, SSH into VPS and check PM2 status, verify all 5 dashboards return HTTP 200, check database integrity, and confirm crontab."

### Expected results
| Check | Expected |
|---|---|
| GitHub clone | Success — all repos accessible |
| SSH to VPS | `connected` |
| `pm2 list` | cyber(0), world(1), oil(2), bitcoin(3), gold(4) — all `online` |
| HTTP 200 on oil.quantitativegenius.com | `200` |
| HTTP 200 on world.quantitativegenius.com | `200` |
| HTTP 200 on cyber.quantitativegenius.com | `200` |
| HTTP 200 on bitcoin.quantitativegenius.com | `200` |
| HTTP 200 on gold.quantitativegenius.com | `200` |
| `PRAGMA integrity_check` on all 5 DBs | `ok` |
| `crontab -l` | `0 4 * * * /home/support/nightly-export.sh` |
| `PRAGMA journal_mode` on oil DB | `wal` |
| Swap active (`free -h`) | Swap: 2.0Gi |

---

## What You Don't Need to Reconnect

These live on your VPS/services independently and are already configured:

| Component | Location | Notes |
|---|---|---|
| Stripe API keys | `/opt/qg-auth/ecosystem.config.js` on VPS | Already configured, never changes |
| Stripe webhook secret | Same file | Already configured |
| Domain DNS | NameBright (quantitativegenius.com) | Managed at https://www.namebright.com/ |
| SSL certificate | Let's Encrypt on VPS, expires July 1, 2026 | Auto-renews via certbot |
| Nginx config | `/etc/nginx/sites-enabled/dashboards` on VPS | Already configured |
| All SQLite databases | On VPS in each dashboard's `data/` folder | Already running, accumulating data |
| PM2 process list | On VPS | Auto-resurrects on reboot |
| Nightly export cron | `crontab` on VPS as `support` user | Already installed |
| Auth server | `/opt/qg-auth/` on VPS (runs as root PM2) | Already running on port 5010 |
| 2GB swap file | `/swapfile` on VPS | Permanent via `/etc/fstab` |
| deploy-guard.sh | `/home/support/deploy-guard.sh` on VPS | Already installed |
| deploy-done.sh | `/home/support/deploy-done.sh` on VPS | Already installed |
| nightly-export.sh | `/home/support/nightly-export.sh` on VPS | Already installed |
| Bitcoin Market Index dashboard | `/home/support/bitcoin-market-index-dashboard/` on VPS | Already running on port 5003 |
| Gold Time Machine dashboard | `/home/support/gold-time-machine-dashboard/` on VPS | Already running on port 5004 |

---

## Stripe Dashboard (for reference)

- **Dashboard URL:** https://dashboard.stripe.com/
- **Active promo code:** `WBSEGWt90w` (90% off, forever)
- **Restricted API key name:** `Perplexity Computer`
- **100% off promo codes:** PERMANENTLY DEPRECATED — never create one

### Current Pricing (Thread 26 · 10x Increase — April 11, 2026)

| Tier | Monthly | Yearly |
|---|---|---|
| Individual Basic | $390/mo | $3,900/yr |
| Individual Pro | $590/mo | $5,900/yr |
| All-Access Basic | $790/mo | $7,900/yr |
| All-Access Pro | $990/mo | $9,900/yr |

See QG-Master-Reference for full new Stripe Price IDs (16 new prices) and payment links.

### Legacy Stripe Pro Price IDs (kept for existing subscribers)
| Product | Monthly ($59 legacy) | Yearly ($590 legacy) |
|---|---|---|
| Oil Pro | `price_1THhsnKXRVV7arrHEqtwMM7L` | `price_1THhsnKXRVV7arrHy4W5CdKb` |
| World Pro | `price_1THhsoKXRVV7arrHW1dndy6D` | `price_1THhsoKXRVV7arrHYYV23gR5` |
| Cyber Pro | `price_1THhspKXRVV7arrHunUc5LjR` | `price_1THhspKXRVV7arrHudiK0fRG` |
| Bundle Pro | `price_1THhspKXRVV7arrHdcBM4qz2` ($99/mo legacy) | `price_1THhsqKXRVV7arrHi6qlZUW5` ($990/yr legacy) |

### Gold Time Machine Stripe Product & Prices

| Item | ID |
|---|---|
| Gold Time Machine Product | `prod_UKDSgK35wz6GFu` |
| Basic Monthly | `price_1TLZ1fKXRVV7arrHGls7yfy6` |
| Pro Monthly | `price_1TLZ1eKXRVV7arrHDAypUc6A` |
| Basic Yearly | `price_1TLZ1fKXRVV7arrHLdFdLWSs` |
| Pro Yearly | `price_1TLZ1fKXRVV7arrH8GzM0FEh` |

---

## Google Cloud Console

- **URL:** https://console.cloud.google.com/
- **VM Location:** Compute Engine → VM instances
- **VM Type:** e2-micro (958MB RAM + 2GB swap)
- **VM IP:** 136.117.206.145
- **SSH-in-browser:** Click "SSH" button next to the VM in the console (for root operations)

---

## Domain Registrar

- **Registrar:** NameBright
- **URL:** https://www.namebright.com/
- **Domain:** quantitativegenius.com
- **DNS:** Points to 136.117.206.145

---

## Live Dashboard URLs

- https://oil.quantitativegenius.com
- https://world.quantitativegenius.com
- https://cyber.quantitativegenius.com
- https://bitcoin.quantitativegenius.com
- https://gold.quantitativegenius.com
- https://quantitativegenius.com (landing page)

---

## Key User Preferences to Tell the New Agent

Paste this in an early message so the agent knows your rules:

> **My rules — follow these always:**
> 1. Follow QG-Master, QG-Deploy, and QG-Security reference docs for every action
> 2. NEVER `git pull` on VPS — use `git fetch origin main` + `git checkout origin/main -- <file>`
> 3. NEVER `git reset --hard` while PM2 is running
> 4. NEVER `sed`, `python3 -c`, or direct-patch files on VPS
> 5. Always run `source ~/deploy-guard.sh <dashboard>` BEFORE touching any file on VPS
> 6. Always run `source ~/deploy-done.sh <dashboard>` AFTER deployment
> 7. NEVER run `generate_exports.py` while dashboard is running — must stop PM2 first
> 8. No smoothing, no fake data, no interpolation — real data only
> 9. Only generate PDF methodology docs, never DOCX
> 10. Bitcoin uses a separate right Y-axis in raw mode
> 11. Push to GitHub first, then deploy to VPS — GitHub is source of truth
> 12. We don't need zombie processes — always check for and kill stuck processes before restarting

---

*End of QG-Account-Recovery-Guide.md*
