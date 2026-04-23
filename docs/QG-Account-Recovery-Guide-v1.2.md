# QuantitativeGenius.com — Account Recovery Guide

| Field | Value |
|---|---|
| **Version** | 1.2 |
| **Last Updated** | April 23, 2026 |
| **Owner email** | jq_007@yahoo.com |
| **Operational inbox** | support@geniusmarketresearch.com |
| **Supersedes** | v1.1 (April 18, 2026) |

**Purpose:** If you lose access to your Perplexity Computer account, follow these steps in a new account to restore full operational capability.

---

## What changed in v1.2

1. **Corrected VPS IP** — the real GCP VPS is `35.233.231.75`. The old IP `136.117.206.145` was Wix's shared Google Cloud infrastructure, NOT a VPS (see QG-Parking-Lot §E4).
2. **Corrected qg-auth ownership** — qg-auth runs under the **support** user's PM2 daemon (id=15), NOT root PM2. v1.1 said root; that was wrong.
3. **HOF email operations migrated to Google Workspace** via `geniusmarketresearch.com`.
   - `support@geniusmarketresearch.com` is the NEW operational inbox (Google Workspace mailbox, billed through Wix).
   - All 12 HOF ImprovMX aliases (6 domains × `*` + `support`) now forward to `support@geniusmarketresearch.com`.
   - **`jq_007@yahoo.com` is retained as the account-recovery owner email for ImprovMX, Resend, NameBright, GitHub, Stripe, Google Cloud.** Do NOT change any of these.
4. **New nginx vhost for `geniusmarketresearch.com`** — pure 301 redirect to `https://quantitativegenius.com/meetings-checkout.html`. SSL issued via Let's Encrypt, expires 2026-07-22, certbot auto-renew configured.
5. **qg-auth magic-link `reply_to` fallback** changed from `support@quantitativegenius.com` to `support@geniusmarketresearch.com` (see `qg-auth/magic-link.js:189`).
6. **POKEMON_EMAIL_WHITELIST** in `qg-auth/auth-middleware.js` includes both `support@quantitativegenius.com` and `support@geniusmarketresearch.com` to keep either address working for Pokemon dashboard admin ops.
7. **Reference doc versions bumped.**

---

## Prerequisites — reference docs to paste in the new thread

| Doc | Latest version |
|---|---|
| QG-Master-Reference | v32.3 |
| QG-Deployment-Guide | v11.1 |
| QG-Security-Reference | v1.6 |
| HOF-Master-Reference | v1.3 |
| HOF-Security-Reference | v1.1 |
| Sports_and_Pokemon_Card_Time_Machine_Methodology | v2.4 |
| Multi-Project-Index | v1.5 |
| QG-Parking-Lot | latest (rolling) |
| QG-Stripe-Promo-Codes | latest |
| QG-Quick-Start-Wake-Up | latest (this is the portable brief) |

**Published methodology PDFs (public):**
- `Bitcoin_Market_Index_Methodology_v2.0.pdf`
- `Oil_Markets_Time_Machine_Methodology_v4.2.pdf`
- `World_Markets_Time_Machine_Methodology_v4.2.pdf`
- `Gold_Time_Machine_Methodology_v1.0.pdf`
- `Cybersecurity_Threat_Index_Methodology_v3.3.pdf`
- `Auto_Market_Index_Methodology_v2.3.2.pdf`
- `Stock_Market_Time_Machine_Methodology_v1.0.pdf`
- `Sports_and_Pokemon_Card_Time_Machine_Methodology_v2.4.pdf`

---

## Step 1 — Paste reference docs

In your first message to the new Perplexity Computer account, paste (or attach) the reference docs above and say:

> "These are my infrastructure reference documents. Read them and use them to guide all future work on QuantitativeGenius.com and the 6 HOF sites. Always GitHub first, then VPS."

The agent now has the full architecture, safety rules, deployment procedures, database schemas, and incident history.

---

## Step 2 — Connect GitHub

### What to do
1. In Perplexity Computer, type: "Connect my GitHub account"
2. The agent will show an OAuth popup — click it and authorize with your GitHub account
3. Verify by asking: "List repos in the CybersecurityAnnouncementDotcom org"

### GitHub details
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
| `bitcoin-market-index-dashboard` | PRIVATE | `main` |
| `gold-time-machine-dashboard` | PRIVATE | `main` |
| `auto-market-index-dashboard` | PRIVATE | `main` |
| `stock-market-time-machine-dashboard` | PRIVATE | `main` |
| `qg-auth` | PRIVATE | `master` |
| `qg-deploy` | PRIVATE | `master` |

### Repositories (HOF — 6 sport-card sites)
| Repo | Visibility | Branch | Notes |
|---|---|---|---|
| `hofcards` | PRIVATE | `master` | Monorepo for all 6 HOF sites + sport dashboards frontends |
| `baseball-card-time-machine-dashboard` | PRIVATE | `master` | Port 5007 |
| `basketball-card-time-machine-dashboard` | PRIVATE | `master` | Port 5008 |
| `football-card-time-machine-dashboard` | PRIVATE | `master` | Port 5009 |
| `hockey-card-time-machine-dashboard` | PRIVATE | `master` | Port 5011 |
| `soccer-card-time-machine-dashboard` | PRIVATE | `master` | Port 5012 |
| `pokemon-card-time-machine-dashboard` | PRIVATE | `master` | Port 5013 |

### Repositories (Scoring Systems)
| Repo | Visibility |
|---|---|
| `rent-history-score` | PRIVATE |
| `employment-history-score` | PRIVATE |
| `performance-review-score` | PRIVATE |
| `scoring-systems-admin` | PRIVATE |

---

## Step 3 — Establish SSH access to the VPS

### What to do
1. Ask the agent: "Generate a new SSH key for VPS access"
2. The agent runs: `ssh-keygen -t ed25519 -f /home/user/.ssh/id_ed25519 -N '' -C 'computer-agent-YYYYMMDD'`
3. The agent displays the public key
4. **You must add this key to the VPS manually** via Google Cloud SSH-in-browser.

### How to add the SSH key (you do this part)
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Navigate to **Compute Engine → VM instances**
3. Find the VM named `quantgenius-server` (IP `35.233.231.75`, type `e2-micro`)
4. Click **SSH** (opens SSH-in-browser as your Google account)
5. In that terminal, run:
   ```bash
   sudo -u support -H bash -c 'echo "THE_PUBLIC_KEY_HERE" >> /home/support/.ssh/authorized_keys'
   ```
6. Back in Perplexity Computer, say: "Test SSH connection"
7. The agent will run: `ssh -o StrictHostKeyChecking=no support@35.233.231.75 'echo connected'`

### VPS details
| Field | Value |
|---|---|
| Hostname | `quantgenius-server` |
| External IP | `35.233.231.75` |
| Old IP (Wix shared infra — NOT the VPS) | ~~`136.117.206.145`~~ |
| SSH user | `support` |
| SSH key path (in Perplexity sandbox) | `/home/user/.ssh/id_ed25519` |
| Key type | `ed25519` |
| SSH command | `ssh -o StrictHostKeyChecking=no support@35.233.231.75` |
| Root access from Perplexity | **Not available** — `support` has no passwordless sudo |
| Root operations | Must be run in Google Cloud SSH-in-browser (pm2 restart, nginx reload, certbot, etc.) |

### Important
- The SSH key is **ephemeral** — it dies when the Perplexity sandbox session ends. You'll need to repeat the key-add step at the start of most new sessions.
- The agent cannot do anything on VPS as `root`. Root operations must be run in Google Cloud SSH-in-browser by you.

### IP confusion — why this matters (from QG-Parking-Lot §E4)
`136.117.206.145` reverse-resolves to `.bc.googleusercontent.com`. During an earlier security audit this looked like a rogue VM. It is actually **Wix's shared Google-Cloud infra** from your pre-GCP hosting. The real QG/HOF VPS is `35.233.231.75`. If any doc, DNS record, or script still says `136.117.206.145`, treat it as stale and fix it.

---

## Step 4 — Connect Google Calendar

### What to do
1. Ask the agent: "Connect my Google Calendar"
2. OAuth popup — authorize with the Google account that owns your calendar.
3. Verify: "Show my upcoming calendar events"

### Account note
- The calendar connector is currently authorized against **`cybersecuritythreatindex@gmail.com`** (your documentation archive account). You chose to swap it in and out of threads as needed rather than permanently switch. If you want the new `support@geniusmarketresearch.com` Workspace account instead, disconnect and reconnect with that Google identity.

---

## Step 5 — Connect Resend (email API)

### What to do
1. Ask the agent: "Connect my Resend account"
2. OAuth popup — authorize
3. Verify: "Send a test email via Resend"

### Resend details
| Field | Value |
|---|---|
| Account owner email | `jq_007@yahoo.com` (break-glass recovery) |
| From address | `service@quantitativegenius.com` |
| Reply-to fallback (v1.2) | **`support@geniusmarketresearch.com`** |
| API key location | `/opt/qg-auth/.env` on VPS (chmod 600) |

Used by `qg-auth` to send magic-link login emails for the paid dashboards and for HOF admin operations.

---

## Step 6 — Connect YouTube Data API

1. Ask the agent: "Connect my YouTube account"
2. OAuth popup — authorize
3. Verify: "List my YouTube channel stats"

Used for QG podcast / video content. Not on the critical path.

---

## Step 7 — Verify everything works

Ask the agent to run this checklist:

> "Run a full health check: clone a QG repo, SSH into VPS and check PM2 status, verify all dashboards return HTTP 200, check database integrity, confirm crontab, and confirm all 6 HOF sites respond."

### Expected results (v1.2 baseline)
| Check | Expected |
|---|---|
| GitHub clone | Success — all repos accessible |
| SSH to VPS | `connected` |
| `pm2 list` (support daemon) | All 13 processes `online` — see process table below |
| HTTP 200 on oil.quantitativegenius.com | `200` |
| HTTP 200 on world.quantitativegenius.com | `200` |
| HTTP 200 on cyber.quantitativegenius.com | `200` |
| HTTP 200 on bitcoin.quantitativegenius.com | `200` |
| HTTP 200 on gold.quantitativegenius.com | `200` |
| HTTP 200 on auto.quantitativegenius.com | `200` |
| HTTP 200 on stock.quantitativegenius.com | `200` |
| HTTP 200 on baseballcardhalloffame.com | `200` |
| HTTP 200 on basketballcardhalloffame.com | `200` |
| HTTP 200 on footballcardhalloffame.com | `200` |
| HTTP 200 on hockeycardhalloffame.com | `200` |
| HTTP 200 on soccercardhalloffame.com | `200` |
| HTTP 200 on pokemoncardhalloffame.com | `200` |
| 301 redirect from geniusmarketresearch.com | `301` → `https://quantitativegenius.com/meetings-checkout.html` |
| `PRAGMA integrity_check` on all sport DBs | `ok` |
| `crontab -l` (support) | `0 4 * * * /home/support/nightly-export.sh` |
| Swap active (`free -h`) | `Swap: 2.0Gi` |
| qg-auth `curl -sI http://localhost:5010/auth/check` | `HTTP/1.1 401 Unauthorized` (401 = alive, correct auth behavior) |

### PM2 process table (support daemon) — v1.2 baseline
| id | name | port | notes |
|---|---|---|---|
| 0 | cyber | 5000 | cybersecurity-threat-index |
| 1 | world | 5001 | world-markets-time-machine |
| 2 | oil | 5002 | oil-markets-time-machine |
| 3 | bitcoin | 5003 | bitcoin-market-index |
| 4 | gold | 5004 | gold-time-machine |
| 5 | auto | 5005 | auto-market-index |
| 6 | stock | 5006 | stock-market-time-machine |
| 7 | baseball | 5007 | baseball-card-time-machine |
| 8 | basketball | 5008 | basketball-card-time-machine |
| 9 | football | 5009 | football-card-time-machine |
| 10 | hockey | 5011 | hockey-card-time-machine |
| 11 | soccer | 5012 | soccer-card-time-machine |
| 12 | pokemon | 5013 | pokemon-card-time-machine |
| **15** | **qg-auth** | **5010** | **Runs as support PM2 (NOT root). v1.1 said root — wrong.** |

> **qg-auth ownership clarification (v1.2 correction):** qg-auth runs under the `support` user's PM2 daemon. Previous docs said "root PM2" — that's incorrect. Restart commands must NOT use sudo:
> ```bash
> # CORRECT (run as support, in Google Cloud SSH-in-browser):
> pm2 restart qg-auth --update-env
> pm2 save
>
> # WRONG — this talks to root's PM2 daemon, which doesn't have qg-auth:
> sudo pm2 restart qg-auth  # ← will error "Process or Namespace qg-auth not found"
> ```

---

## What you don't need to reconnect

These live on the VPS / third-party services and persist through a Perplexity account loss:

| Component | Location | Notes |
|---|---|---|
| Stripe API keys | `/opt/qg-auth/.env` on VPS | Already configured, never changes |
| Stripe webhook secret | Same `.env` | Already configured |
| Stripe promo codes | Stripe dashboard | See `QG-Stripe-Promo-Codes.md` |
| Resend API key | `/opt/qg-auth/.env` on VPS | chmod 600 |
| Domain DNS (QG) | NameBright | quantitativegenius.com |
| Domain DNS (HOF — 6 sport sites) | NameBright | All point to `35.233.231.75` |
| Domain DNS (geniusmarketresearch.com) | NameBright | Nameservers ns1/ns2.namebrightdns.com |
| MX records (geniusmarketresearch.com) | Google Workspace (5 MX records, priorities 1/5/5/10/10) | Billed through Wix |
| SPF | `v=spf1 include:_spf.google.com ~all` | On geniusmarketresearch.com |
| DMARC | `v=DMARC1; p=none; rua=mailto:support@geniusmarketresearch.com` | On geniusmarketresearch.com |
| SSL certs | Let's Encrypt on VPS | All auto-renew via certbot |
| geniusmarketresearch.com SSL | `/etc/letsencrypt/live/geniusmarketresearch.com/` | Expires 2026-07-22, auto-renew |
| nginx config | `/etc/nginx/sites-enabled/*` on VPS | Managed via hofcards/nginx/ + qg-deploy |
| All SQLite databases | Each dashboard's `data/` folder on VPS | Running, accumulating daily |
| PM2 resurrect | `pm2 save` already run as support | Auto-starts on reboot |
| Nightly export cron | `crontab -l` as support | `0 4 * * * /home/support/nightly-export.sh` |
| deploy-guard.sh / deploy-done.sh | `/home/support/` on VPS | Already installed |
| 2 GB swap | `/swapfile` on VPS | Permanent via `/etc/fstab` |
| ImprovMX aliases (HOF) | ImprovMX account (`jq_007@yahoo.com`) | 12 aliases, all forward to `support@geniusmarketresearch.com` |

---

## ImprovMX (HOF email forwarding)

### Account
- **Account owner email:** `jq_007@yahoo.com` (break-glass / recovery — do NOT change)
- **API key:** stored in Perplexity Computer session (cached). If lost, reset at https://improvmx.com/ → Profile → API.
- **Dashboard:** https://improvmx.com/

### 12 aliases (6 HOF domains × `*` + `support`) — all forward to `support@geniusmarketresearch.com`
| Domain | Alias `*` ID | Alias `support` ID |
|---|---|---|
| baseballcardhalloffame.com | 6369591 | 6369596 |
| basketballcardhalloffame.com | 6369592 | 6369597 |
| footballcardhalloffame.com | 6369593 | 6369598 |
| hockeycardhalloffame.com | 6367803 | 6369601 |
| soccercardhalloffame.com | 6369594 | 6369599 |
| pokemoncardhalloffame.com | 6369595 | 6369600 |

### Rollback
Pre-migration snapshot: `/home/user/workspace/improvmx_migration/pre-migration-snapshot-20260423T083123Z.json`
Rollback command:
```bash
bash /home/user/workspace/improvmx_migration/repoint_aliases.sh ROLLBACK
```
This replays every alias to its pre-migration forward target (the old `support@quantitativegenius.com`, etc.).

---

## geniusmarketresearch.com (new, v1.2)

| Item | Value |
|---|---|
| Purpose | Operational inbox for HOF (`support@geniusmarketresearch.com`) + marketing-safe redirect to meetings-checkout |
| DNS registrar | NameBright |
| Nameservers | `ns1.namebrightdns.com`, `ns2.namebrightdns.com` (moved off Wix DNS) |
| A record `@` + `www` | `35.233.231.75` |
| MX | Google Workspace (5 records, priorities 1/5/5/10/10) |
| SPF TXT | `v=spf1 include:_spf.google.com ~all` |
| Google verify TXT | `google-site-verification=OuJsWZPxT7RyPKDy5YPQZ0p9IchipFskm7BnrxMdvK4` |
| DMARC TXT | `v=DMARC1; p=none; rua=mailto:support@geniusmarketresearch.com` |
| nginx vhost | `/etc/nginx/sites-available/geniusmarketresearch.com.conf` |
| nginx source in GitHub | `hofcards/nginx/geniusmarketresearch.com.conf` |
| Deploy script | `hofcards/scripts/deploy-gmr-redirect-root.sh` |
| SSL | Let's Encrypt, `/etc/letsencrypt/live/geniusmarketresearch.com/`, expires 2026-07-22, certbot auto-renew |
| Behavior | HTTPS 301 → `https://quantitativegenius.com/meetings-checkout.html` |
| Workspace mailbox billing | Through Wix |

---

## Stripe dashboard (reference)

- **Dashboard URL:** https://dashboard.stripe.com/
- **Account owner:** `jq_007@yahoo.com` (do NOT change)
- **Active promo code:** `VTMZ99BP` → coupon `TrexuM99Bz` (99% off, forever, case-sensitive). See `QG-Stripe-Promo-Codes.md`.
- **Restricted API key name:** `Perplexity Computer`
- **100% off promo codes:** PERMANENTLY DEPRECATED — never create one.

### Current pricing (Thread 26 · 10x increase, April 11, 2026)
| Tier | Monthly | Yearly |
|---|---|---|
| Individual Basic | $390/mo | $3,900/yr |
| Individual Pro | $590/mo | $5,900/yr |
| All-Access Basic | $790/mo | $7,900/yr |
| All-Access Pro | $990/mo | $9,900/yr |

See QG-Master-Reference for the full Stripe Price ID map + payment links.

---

## Google Cloud Console

- **URL:** https://console.cloud.google.com/
- **Account owner:** `jq_007@yahoo.com` (primary) — also reachable via the Google identity that manages the VM
- **VM location:** Compute Engine → VM instances
- **VM name:** `quantgenius-server`
- **VM type:** `e2-micro` (958 MB RAM + 2 GB swap)
- **VM IP:** `35.233.231.75`
- **SSH-in-browser:** Click the "SSH" button next to the VM in the console — this is the channel for all root operations (pm2, nginx, certbot, etc.).

---

## Domain registrar (NameBright)

- **URL:** https://www.namebright.com/
- **Account owner:** `jq_007@yahoo.com`
- **Domains:**
  - `quantitativegenius.com` — A → `35.233.231.75`
  - `baseballcardhalloffame.com` — A → `35.233.231.75`
  - `basketballcardhalloffame.com` — A → `35.233.231.75`
  - `footballcardhalloffame.com` — A → `35.233.231.75`
  - `hockeycardhalloffame.com` — A → `35.233.231.75`
  - `soccercardhalloffame.com` — A → `35.233.231.75`
  - `pokemoncardhalloffame.com` — A → `35.233.231.75`
  - `geniusmarketresearch.com` — A → `35.233.231.75` (nameservers moved to NameBright in v1.2)

---

## Live URLs

### QG dashboards
- https://oil.quantitativegenius.com
- https://world.quantitativegenius.com
- https://cyber.quantitativegenius.com
- https://bitcoin.quantitativegenius.com
- https://gold.quantitativegenius.com
- https://auto.quantitativegenius.com
- https://stock.quantitativegenius.com
- https://quantitativegenius.com (landing)

### HOF sites (6)
- https://baseballcardhalloffame.com
- https://basketballcardhalloffame.com
- https://footballcardhalloffame.com
- https://hockeycardhalloffame.com
- https://soccercardhalloffame.com
- https://pokemoncardhalloffame.com

### Marketing redirect
- https://geniusmarketresearch.com → 301 → https://quantitativegenius.com/meetings-checkout.html

---

## Key user preferences to tell the new agent

Paste this early so the agent knows your rules:

> **My rules — follow these always:**
> 1. Follow QG-Master, QG-Deploy, QG-Security, HOF-Master reference docs for every action.
> 2. **GitHub first, then VPS. Always.** NEVER edit files directly on VPS.
> 3. On VPS: NEVER `git pull`, NEVER `git reset --hard` while PM2 is running, NEVER `sed -i`, NEVER `python3 -c` inline.
> 4. On VPS: use `git fetch origin master` + `git checkout origin/master -- <file>`.
> 5. Always run `source ~/deploy-guard.sh <dashboard>` BEFORE touching any dashboard file.
> 6. Always run `source ~/deploy-done.sh <dashboard>` AFTER deployment.
> 7. NEVER run `generate_exports.py` while a dashboard is running — stop PM2 first.
> 8. Real data only — no smoothing, no interpolation, no synthesized prices. Gaps are gaps.
> 9. Never abbreviate "HOF" in user-facing UI. Never use CardLadder / CL branding.
> 10. Never use 1/1 cards in any index.
> 11. Only generate PDF methodology docs. Never DOCX.
> 12. Bitcoin dashboard uses a separate right Y-axis in raw mode.
> 13. Always check for and kill stuck processes before restarting PM2.
> 14. qg-auth runs as **support** PM2 (id=15). Never run `sudo pm2 restart qg-auth` — use `pm2 restart qg-auth --update-env` as support in Google Cloud SSH-in-browser.
> 15. The real VPS IP is `35.233.231.75`. If any doc says `136.117.206.145`, that's stale (Wix shared infra) — flag and fix it.
> 16. HOF email forwards to `support@geniusmarketresearch.com`. Yahoo is kept only as account-recovery owner.

---

*End of QG-Account-Recovery-Guide-v1.2.md*
