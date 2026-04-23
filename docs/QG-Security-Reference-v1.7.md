<!-- MANDATORY: This filename MUST include the version number (e.g., QG-Security-Reference-v1.0.md). -->

## v1.7 — 2026-04-23 (changelog)

**Phase 2 email migration — new surfaces:**
- **Corrected VPS IP:** `136.117.206.145` → **`35.233.231.75`** (old IP was Wix shared infra; see QG-Parking-Lot §E4).
- **HOF ImprovMX aliases repointed** to `support@geniusmarketresearch.com`. 12 aliases (6 domains × `support` + `*`). Owner email on ImprovMX account remains `jq_007@yahoo.com` (break-glass).
- **New Google Workspace inbox:** `support@geniusmarketresearch.com`, billed through Wix. Add to operational comms scope. DMARC on GMR: `v=DMARC1; p=none; rua=mailto:support@geniusmarketresearch.com`. SPF: `v=spf1 include:_spf.google.com ~all`.
- **Resend reply_to fallback** changed from `support@quantitativegenius.com` → `support@geniusmarketresearch.com`.
- **Pre-migration snapshot:** `/home/user/workspace/improvmx_migration/pre-migration-snapshot-20260423T083123Z.json`. Rollback: `bash /home/user/workspace/improvmx_migration/repoint_aliases.sh ROLLBACK`.
- **Break-glass / ownership invariants (do NOT change):** `jq_007@yahoo.com` owns ImprovMX, Resend, NameBright, GitHub, Stripe, Google Cloud.

**Older versions preserved:** v1.6, v1.5, v1.4, v1.3 remain in `docs/` as historical record.

---
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- INTERNAL ONLY: This document contains security implementation details. NEVER include in public methodology PDFs or share externally. -->

# QuantitativeGenius.com — Security Reference Guide

| Field | Value |
|---|---|
| **Version** | 1.7 (v1.5 + Thread 32: Resend Pro upgrade $20/mo, 6 HOF .com domains added with verified domain IDs, ImprovMX Premium retained at $9/mo, NameBright DNS instructions tracked) |
| **Last Updated** | April 18, 2026 (Thread 31) |
| **Owner** | jq_007@yahoo.com |
| **Classification** | INTERNAL ONLY |
| **Scope** | All QG infrastructure, VPS, dashboards, auth, and deployment |

---

## 1. Security Overview

### Purpose

This document consolidates every security measure protecting the QuantitativeGenius.com infrastructure. It is the definitive internal reference covering rate limiting, authentication, API protection, database integrity, deployment safety rules, and monitoring procedures. It reflects all measures implemented through Thread 30 and all prior threads.

### Classification

**INTERNAL ONLY.** This document contains implementation details — endpoint names, middleware patterns, key formats, database procedures, and infrastructure topology — that must never be shared publicly. It must never appear in public-facing methodology PDFs, help articles, or any externally distributed material.

### Threat Model Summary

| Threat | Mitigation Layer |
|---|---|
| Brute-force login | Magic link auth (no password to brute-force) |
| Credential theft | No passwords stored in any database |
| API scraping / DDoS | Nginx rate limiting + Express rate limiting (layered) |
| Unauthorized API access | `requireAuth` middleware on all GET endpoints |
| Export abuse | `requirePro` middleware on all export endpoints |
| External data injection | POST /api/readings locked to localhost only |
| API key theft | SHA-256 hash storage only; plaintext never persisted |
| Free access circumvention | 100% off promo codes deprecated; per-product key validation |
| DB corruption on deploy | deploy-guard.sh / deploy-done.sh mandatory workflow |
| OOM-induced corruption | 2 GB swap file; auto-update cron removed; nightly export stops PM2 first (Thread 25) |
| Privilege escalation | `support` user has no passwordless sudo |
| Supply chain / credential leak | No GitHub credentials stored on VPS; private repos not cloned |
| Bitcoin data injection | BTC fetch uses HTTPS to Yahoo Finance; read-only external call (Thread 24) |
| Zombie process on export | Dictionary-based rewrite; timeout 120 on nightly exports; kill zombie before restart |

---

## 2. Express Rate Limiting

### Implementation

A zero-dependency `rate-limiter.js` module is present in **all three dashboard repositories**. It uses an in-process sliding-window store with no external Redis or database dependency.

### Rate Limit Zones

| Zone | Limit | Applied To |
|---|---|---|
| `api` | 60 req/min | All `/api/*` endpoints |
| `export` | 5 req/min | All `/api/export*` and download endpoints |
| `auth` | 10 req/min | All `/auth/*` endpoints |
| `pro` (world only) | 30 req/min | Pro-tier endpoints on World dashboard |

### Response Headers

Every rate-limited response includes the following headers so clients can self-throttle:

```
X-RateLimit-Limit: <zone_limit>
X-RateLimit-Remaining: <requests_remaining>
X-RateLimit-Reset: <unix_timestamp_reset>
```

When a limit is exceeded, the server responds with **HTTP 429 Too Many Requests**.

### Implementation History

Implemented in Thread 21, April 8, 2026. All three dashboards were updated in the same deployment session to ensure consistent coverage.

### Key Files

- `<dashboard-repo>/middleware/rate-limiter.js` — shared module (copied to each repo)
- Applied via `app.use()` in each dashboard's `server.js` before route handlers

---

## 3. Nginx Rate Limiting

### Configuration File

```
/etc/nginx/snippets/rate-limit.conf
```

This file requires **root/sudo access** to modify. It is included into the nginx dashboard virtual host config via the `include` directive.

### Rate Limit Zones

```nginx
# /etc/nginx/snippets/rate-limit.conf
limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=api:10m    rate=5r/s;
limit_req_zone $binary_remote_addr zone=auth:10m   rate=3r/s;
limit_req_zone $binary_remote_addr zone=export:10m rate=1r/s;
```

| Zone | Rate | Applied To |
|---|---|---|
| `general` | 10 req/s | Default — all unspecified locations |
| `api` | 5 req/s | `/api/*` location blocks |
| `auth` | 3 req/s | `/auth/*` location blocks |
| `export` | 1 req/s | `/api/export*` location blocks |

### Inclusion in Dashboard Config

The snippet is included in each dashboard's nginx server block:

```nginx
include /etc/nginx/snippets/rate-limit.conf;
```

Individual location blocks then apply zones:

```nginx
location /api/ {
    limit_req zone=api burst=10 nodelay;
    ...
}
location /auth/ {
    limit_req zone=auth burst=5 nodelay;
    auth_request off;
    ...
}
```

### Layered Defense Model

Nginx rate limiting fires **first** (at the reverse proxy layer) before any request reaches the Node.js process. Express rate limiting fires **second** (inside the application). An attacker must bypass both independent layers. This defense-in-depth approach ensures that even if one layer is misconfigured or temporarily unavailable, the other continues to provide protection.

---

## 4. Authentication System

### Design Principle

QG uses **magic link authentication** — no passwords are stored anywhere in the system. There is nothing to brute-force and nothing to steal via credential exposure.

### Auth Server

| Property | Value |
|---|---|
| Location on VPS | `/opt/qg-auth/` |
| Port | `5010` |
| Process manager | PM2 (runs as root — separate PM2 instance) |
| Session mechanism | Session cookies |

### Nginx `auth_request` Gate

Every request to every dashboard subdomain passes through an `auth_request` directive before being served:

```nginx
auth_request /auth/check;
auth_request_set $auth_plan_tier $upstream_http_x_auth_plan_tier;
```

The `/auth/check` endpoint on the auth server returns:
- **HTTP 200** — user is authenticated; continues to dashboard
- **HTTP 401** — user is unauthenticated; nginx triggers the 401 handler

The auth server also sets the response header:

```
X-Auth-Plan-Tier: pro   # or: basic
```

This header is forwarded to the dashboard process to enforce pro/basic tier logic.

### Login Loop Prevention

`auth_request` is **disabled** on the following location blocks to prevent authentication loops:

```nginx
location /auth/ {
    auth_request off;
    ...
}
location /webhook/ {
    auth_request off;
    ...
}
```

### Unauthenticated Redirect

```nginx
error_page 401 = @unauthenticated;
location @unauthenticated {
    return 302 https://quantitativegenius.com/paywall;
}
```

Unauthenticated users are redirected to the paywall, not shown an error page.

---

## 5. API Endpoint Protection

### Middleware Stack

| Middleware | Applied To | Effect |
|---|---|---|
| `requireAuth` | ALL GET `/api/*` endpoints, all 3 dashboards | Returns 401 if session invalid |
| `requirePro` | ALL export endpoints | Returns 403 if user is not pro tier |
| Localhost IP check | `POST /api/readings` | Returns 403 if source IP is not loopback |

### Protected API Endpoints by Dashboard

**Oil Markets Time Machine:**
- `GET /api/current` (requireAuth)
- `GET /api/history` (requireAuth)
- `GET /api/sp500-history` (requireAuth)
- `GET /api/bitcoin-history` (requireAuth — Thread 24)
- `GET /api/export/csv` (requireAuth + requirePro)
- `GET /api/export/json` (requireAuth + requirePro)
- `GET /api/user-tier` (requireAuth)
- `POST /api/readings` (localhost-only)

**World Markets Time Machine:**
- `GET /api/composite` (requireAuth)
- `GET /api/history` (requireAuth)
- `GET /api/country-history` (requireAuth)
- `GET /api/countries` (requireAuth)
- `GET /api/bitcoin-history` (requireAuth — Thread 24)
- `GET /api/export/csv` (requireAuth + requirePro)
- `GET /api/export/json` (requireAuth + requirePro)
- `GET /api/user-tier` (requireAuth)
- `GET /api/pro/latest` (requireAuth + requirePro)
- `GET /api/pro/history` (requireAuth + requirePro)
- `GET /api/pro/daily/:date` (requireAuth + requirePro)
- `GET /api/pro/dates` (requireAuth + requirePro)
- `POST /api/readings` (localhost-only)

**Cybersecurity Threat Index:**
- `GET /api/scores` (requireAuth)
- `GET /api/current` (requireAuth)
- `GET /api/export/csv` (requireAuth + requirePro)
- `GET /api/export/json` (requireAuth + requirePro)
- `GET /api/user-tier` (requireAuth)

**Bitcoin Market Index:**
- `GET /api/current` (requireAuth)
- `GET /api/bitcoin-history` (requireAuth)
- `GET /api/sp500-history` (requireAuth)
- `GET /api/nasdaq-history` (requireAuth)
- `GET /api/dji-history` (requireAuth)
- `GET /api/export/csv` (requireAuth + requirePro)
- `GET /api/export/json` (requireAuth + requirePro)
- `GET /api/user-tier` (requireAuth)

**Gold Time Machine:**
- `GET /api/current` (requireAuth)
- `GET /api/gold-history` (requireAuth)
- `GET /api/component-history` (requireAuth)
- `GET /api/bitcoin-history` (requireAuth)
- `GET /api/export/csv` (requireAuth + requirePro)
- `GET /api/export/json` (requireAuth + requirePro)
- `GET /api/user-tier` (requireAuth)

### POST /api/readings — Localhost Lock

The data ingestion endpoint is locked to **loopback IPs only**:

```javascript
const ALLOWED_IPS = ['127.0.0.1', '::1', '::ffff:127.0.0.1'];

function requireLocalhost(req, res, next) {
  const ip = req.socket.remoteAddress;
  if (!ALLOWED_IPS.includes(ip)) {
    return res.status(403).json({ error: 'Forbidden: localhost only' });
  }
  next();
}
```

This prevents any external actor from injecting fabricated financial data into the database, regardless of whether they hold a valid session or API key.

### API Key Validation

- Incoming `X-API-Key` header is checked against the auth server's `/auth/validate-key` endpoint.
- Results are cached in-memory for **60 seconds** to reduce auth server load.
- If the key is missing, malformed, or invalid, the endpoint returns HTTP 401.

### Bitcoin Fetch — HTTPS Security (Thread 24)

The Bitcoin price fetch uses the native Node.js `https` module to make an outbound HTTPS GET request to Yahoo Finance (BTC-USD). This is a read-only external call — no data is submitted to Yahoo Finance. The HTTPS protocol ensures the price data in transit is encrypted and cannot be intercepted or tampered with by a network attacker. No API key or authentication credential is required for this public data endpoint.

---

## 6. API Key System

### Key Format

```
qg_<32 random hex characters>
```

Example structure (not a real key): `qg_a3f8c2d1e4b7901245678abcdef90123`

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

The `checkSubscription()` function on the auth server verifies:
1. The key hash matches a stored hash.
2. The associated user has an **active subscription** that covers the specific product ID passed.

A user with a Pro subscription to Dashboard A cannot use their API key to access Dashboard B unless they also hold a subscription covering Dashboard B's product ID.

### Auth Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/api-key` | Generate new key (revokes old) |
| `DELETE` | `/auth/api-key` | Revoke current key |
| `GET` | `/auth/api-key-status` | Return key prefix and active status |
| `GET` | `/auth/validate-key?key=...&product=...` | Validate key + subscription for a product |

---

## 7. Stripe Hardening

### API Key Scope

The Stripe API key in use is a **restricted key** named `"Perplexity Computer"`. It has scoped permissions rather than account-level access. If this key is ever compromised, the blast radius is limited to the specific operations it is permitted to perform.

### Webhook Signature Verification

All incoming Stripe webhooks are verified using the webhook signing secret (`whsec_...`). Requests without a valid `Stripe-Signature` header are rejected before any processing occurs.

```javascript
const event = stripe.webhooks.constructEvent(
  req.rawBody,
  req.headers['stripe-signature'],
  process.env.STRIPE_WEBHOOK_SECRET
);
```

### Monitored Events

| Event | Action |
|---|---|
| `checkout.session.completed` | Provision subscription, update user tier |
| `customer.subscription.updated` | Re-derive tier from current price ID |
| `customer.subscription.deleted` | Downgrade user to basic |

### Pro Tier Derivation

A `PRO_PRICE_IDS` Set contains all Pro Stripe Price IDs (covering all dashboards and billing intervals). When a subscription event fires, the system checks whether the event's price ID is a member of this Set to determine if the user should be granted Pro tier.

> **Thread 26 (April 11, 2026):** 16 new price IDs were created for the 10x pricing increase ($390/$590/$790/$990 tiers). These new IDs must be added to the `PRO_PRICE_IDS` Set in `stripe-webhook.js`. Legacy $59/$590 IDs remain for existing subscribers. See QG-Master-Reference for the full price ID table.

```javascript
const PRO_PRICE_IDS = new Set([
  'price_XXXXXXXXXXXXXXXX', // Dashboard A monthly
  'price_XXXXXXXXXXXXXXXX', // Dashboard A annual
  // ... 6 more
]);
```

### Self-Restriction Rules

The following actions **must never be taken without explicit user confirmation**:

- Deleting Stripe products, prices, or coupons
- Modifying active customer subscriptions
- Issuing refunds
- Changing webhook endpoint configuration
- Rotating or revoking API keys in the Stripe dashboard

### 100% Off Promo Codes — Deprecated

100% off promotional codes have been **permanently deprecated**. They were found to allow circumvention of the paywall — a user could apply a 100% off coupon at checkout to gain Pro access for free indefinitely. No new 100% off coupons may be created.

---

## 8. Database Protection (deploy-guard System)

### Purpose

The deploy-guard system prevents the three most common causes of SQLite database corruption that have occurred in QG's incident history:

| Incident | Date | Cause |
|---|---|---|
| DB corruption #1 | April 6, 2026 | Auto-update cron ran `git pull` mid-write |
| DB corruption #2 | April 7, 2026 | Stale branch checkout overwrote DB file |
| DB corruption #3 | April 8, 2026 | `git reset --hard` executed while PM2 process was running |

### Database Tables Reference

**Oil Markets Time Machine (`oil_markets.db`):**

| Table | Description |
|---|---|
| `readings` | Main composite index readings (timestamp, value) |
| `oil_prices` | WTI and Brent price rows |
| `country_data` | S&P 500 data (cross-DB from World) |
| `bitcoin_data` | BTC price readings — Thread 24 (timestamp TEXT, price REAL) |

**World Markets Time Machine (`world_markets.db`):**

| Table | Description |
|---|---|
| `readings` | Main composite index readings |
| `country_data` | 20 country price rows + S&P 500 (ticker column) |
| `bitcoin_data` | BTC price readings — Thread 24 (timestamp TEXT, price REAL) |

**Cybersecurity Threat Index (`cybersecurity.db`):**

| Table | Description |
|---|---|
| `monthly_scores` | Monthly threat scores (year, month, score, level, events) |

**Bitcoin Market Index (`bitcoin_markets.db`):**

| Table | Description |
|---|---|
| `bitcoin_data` | BTC price readings (timestamp TEXT, price REAL) |
| `nasdaq_data` | NASDAQ price readings (timestamp TEXT, price REAL) |
| `dji_data` | DJI price readings (timestamp TEXT, price REAL) |

**Gold Time Machine (`gold_markets.db`):**

| Table | Description |
|---|---|
| `gold_data` | Gold futures (GC=F) price readings |
| `hui_data` | Gold BUGS Index (^HUI) readings |
| `gdx_data` | Gold Miners ETF (GDX) readings |
| `silver_data` | Silver futures (SI=F) readings |
| `xau_data` | Gold/Silver Sector (^XAU) readings |
| `bitcoin_data` | BTC price readings |

**Auth Server (`/opt/qg-auth/`):**

| Table | Description |
|---|---|
| `users` | User accounts (email, stripe_customer_id, plan_tier) |
| `sessions` | Active session tokens |
| `api_keys` | API key hashes (key_hash, key_prefix, user_id) |
| `subscriptions` | Stripe subscription records |

### deploy-guard.sh — MANDATORY BEFORE ANY VPS FILE MODIFICATION

Location: `/home/support/deploy-guard.sh`

**This script must be run before touching any file on the VPS.** Steps performed:

1. **Stop PM2 process** for the relevant dashboard — ensures no active writes to the database.
2. **Back up the database** with a timestamp suffix (e.g., `readings.db.2026-04-08T14-32-00.bak`).
3. **Run `PRAGMA integrity_check`** on the database.
4. **Abort with error** if the integrity check does not return `ok`. Deployment must not proceed against a corrupt database.

```bash
#!/bin/bash
# deploy-guard.sh — run BEFORE any VPS file change
DASHBOARD=$1
DB_PATH="/home/support/qg-${DASHBOARD}/readings.db"
BACKUP="${DB_PATH}.$(date +%Y-%m-%dT%H-%M-%S).bak"

echo "[deploy-guard] Stopping PM2 process: qg-${DASHBOARD}"
pm2 stop "qg-${DASHBOARD}"

echo "[deploy-guard] Backing up DB to ${BACKUP}"
cp "${DB_PATH}" "${BACKUP}"

echo "[deploy-guard] Running integrity check..."
RESULT=$(sqlite3 "${DB_PATH}" "PRAGMA integrity_check;")
if [ "$RESULT" != "ok" ]; then
  echo "[deploy-guard] INTEGRITY CHECK FAILED: ${RESULT}"
  echo "[deploy-guard] Aborting deployment. Restore from backup."
  exit 1
fi

echo "[deploy-guard] Integrity OK. Safe to proceed."
```

### deploy-done.sh — MANDATORY AFTER DEPLOYMENT

Location: `/home/support/deploy-done.sh`

**This script must be run after every deployment.** Steps performed:

1. **Restart the PM2 process** for the relevant dashboard.
2. **HTTP health check** — sends a request to the dashboard and confirms HTTP 200.
3. **DB integrity check** — runs `PRAGMA integrity_check` post-restart.
4. **Reports status** — exits non-zero and prints a warning if any check fails.

```bash
#!/bin/bash
# deploy-done.sh — run AFTER deployment is complete
DASHBOARD=$1
PORT=$2
DB_PATH="/home/support/qg-${DASHBOARD}/readings.db"

echo "[deploy-done] Restarting PM2 process: qg-${DASHBOARD}"
pm2 restart "qg-${DASHBOARD}"
sleep 2

echo "[deploy-done] HTTP health check on port ${PORT}..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:${PORT}/health)
if [ "$STATUS" != "200" ]; then
  echo "[deploy-done] WARNING: Health check returned HTTP ${STATUS}"
fi

echo "[deploy-done] Post-deploy integrity check..."
RESULT=$(sqlite3 "${DB_PATH}" "PRAGMA integrity_check;")
if [ "$RESULT" != "ok" ]; then
  echo "[deploy-done] WARNING: Post-deploy integrity check FAILED: ${RESULT}"
  exit 1
fi

echo "[deploy-done] All checks passed."
```

---

## 9. Infrastructure Hardening

### 2 GB Swap File

A 2 GB swap file is configured on the VPS to prevent out-of-memory (OOM) process kills during yfinance data collection. yfinance can spike memory usage during bulk historical data fetches; without swap, the kernel OOM killer can terminate the Node.js process mid-write, leaving the database in a partially written state.

**Incident (April 8, 2026):** The e2-micro VM (958MB RAM) had NO swap file. Running 3 Node.js servers + 2 Python fetchers + Google Ops Agent + nginx + snapd exhausted all physical memory. The kernel OOM killer fired at 09:32 UTC (killed `apt-check`), then systemd-journald and snapd watchdogs timed out, cascading into a full system freeze. GCP auto-rebooted the VM at 16:42 UTC — all 3 sites were down for approximately 7 hours. After reboot, PM2 auto-resurrected all processes but load average was 5.56 with only 64MB RAM free. The 2GB swap file was created immediately after this incident as a permanent fix (persisted in `/etc/fstab`).

```bash
# Verify swap is active
free -h
# Expected: Swap: 2.0Gi

# Verify swap survives reboots
grep swap /etc/fstab
# Expected: /swapfile none swap sw 0 0
```

### Auto-Update Cron — REMOVED

The auto-update cron that previously ran `git pull` on a schedule was **permanently removed on April 6, 2026**. It was identified as the root cause of DB corruption incident #1.

### Nightly Export Cron (Thread 25)

A system crontab runs `/home/support/nightly-export.sh` at 4:00 AM UTC (9:00 PM PDT) daily. This is the ONLY authorized cron entry for the `support` user. It safely stops Oil + World PM2 processes before running `generate_exports.py`, then restarts and health-checks. This prevents OOM crashes that occurred when exports ran alongside active dashboards.

**Verification command:**

```bash
crontab -l
# Expected output: 0 4 * * * /home/support/nightly-export.sh
# No other entries should exist
```

This must be verified on every deployment session. If any crontab entries OTHER than the nightly export are found, they must be investigated immediately.

### SSL / TLS

| Property | Value |
|---|---|
| Provider | Let's Encrypt |
| Renewal | Auto-renew via certbot |
| Current expiry | July 1, 2026 |
| Protocol | TLS 1.2 / 1.3 |

### Firewall Rules

Only the following TCP ports are open:

| Port | Service |
|---|---|
| 80 | HTTP (redirects to HTTPS) |
| 443 | HTTPS |
| 5000 | Dashboard 1 (internal — nginx proxy) |
| 5001 | Dashboard 2 (internal — nginx proxy) |
| 5002 | Dashboard 3 (internal — nginx proxy) |
| 5003 | Dashboard 4 — Bitcoin (internal — nginx proxy) |
| 5004 | Dashboard 5 — Gold (internal — nginx proxy) |

All other ports are blocked. The dashboard ports (5000–5004) are bound to localhost and not directly accessible from the internet — they are only reachable via nginx proxy_pass.

---

## 10. VPS Access Security

### SSH

- **SSH key-based authentication only** — password authentication is disabled.
- No shared or team SSH keys. Each operator uses their own key pair.

### User Privilege Model

| User | Sudo Access | Purpose |
|---|---|---|
| `support` | No passwordless sudo | Day-to-day operations, dashboard management |
| `root` | Full | Auth server PM2 instance; nginx config changes |

The `support` user's lack of passwordless sudo limits the blast radius of any session compromise. An attacker who gains a `support` shell cannot silently escalate to root or modify nginx/system configurations without a password.

### Auth Server Privileges

The auth server (`/opt/qg-auth/`) runs under a **separate PM2 instance as root** because it requires access to system-level operations. This is intentionally isolated from the `support` user's PM2 instance.

### Private Repository Security

- `qg-auth` and `qg-deploy` are **private repositories** that are never cloned onto the VPS.
- Sensitive files from these repos (server code, environment templates) are **embedded inline in deploy scripts** and written to the VPS during deployment.
- **No GitHub credentials** (tokens, SSH deploy keys, or `.gitconfig` entries) are stored on the VPS. The VPS cannot initiate outbound GitHub connections.

---

## 11. Data Integrity

### Glitch Protection

Incoming readings are validated before insertion. A reading is **rejected** if it represents a drop of more than **20%** from the most recent stored value. This prevents erroneous yfinance data or API glitches from corrupting the historical dataset.

```javascript
const MAX_DROP_FRACTION = 0.20;
if (previousValue && (previousValue - newValue) / previousValue > MAX_DROP_FRACTION) {
  return res.status(422).json({ error: 'Reading rejected: exceeds glitch threshold' });
}
```

### Duplicate Prevention

A reading is **silently skipped** if the change from the previous value is less than **0.01 points** (index readings) or **0.01%** (Bitcoin price readings). This prevents the database from accumulating redundant rows during periods of market inactivity.

### WAL Mode

All QG SQLite databases run in **Write-Ahead Logging (WAL) mode**:

```sql
PRAGMA journal_mode=WAL;
```

WAL mode provides:
- Better concurrent read/write performance (readers don't block writers)
- Improved crash recovery (no torn writes to the main database file)
- Reduced risk of corruption during unexpected process termination

### Cross-Dashboard Dependency

The **Oil dashboard** reads the S&P 500 value from the **World dashboard's database** for its correlation calculations. This dependency is documented here to ensure:
1. The World dashboard database path is stable and not changed without updating the Oil dashboard config.
2. deploy-guard is run on the World dashboard before any deployment that might affect its DB.
3. If the World DB is ever restored from backup, the Oil dashboard must be checked for data consistency.

---

## 12. Deployment Security Rules

These rules exist because of real incidents. **All rules are mandatory — no exceptions.**

### Git Operations

| Rule | Rationale |
|---|---|
| **NEVER use `git pull`** | Merges can run mid-write if PM2 is running; caused DB corruption April 6 |
| Use `git fetch origin main` then `git checkout origin/main -- <file>` | Fetches specific files without touching the DB or running merge logic |
| **NEVER use `git reset --hard`** while PM2 is running | Caused DB corruption April 8 — wipes working tree including live DB file |

### File Modification Rules

| Rule | Rationale |
|---|---|
| **NEVER use `sed` on VPS** | Regex errors can silently corrupt config or source files |
| **NEVER use `python3 -c` inline patches** | Unreliable; hard to audit; has caused partial writes |
| **NEVER create automated PM2 restart crons** | Restart during write = DB corruption; all restarts must be manual via deploy-done.sh |

### Pre-Deploy Validation

Always run `grep` to verify the correct content is present in a file **before** running `deploy-done.sh`. Never assume a file write succeeded without confirming.

```bash
grep "expectedFunction\|expectedRoute" /home/support/qg-dashboard/server.js
```

### Version Control Discipline

- **Push to GitHub first**, then deploy to VPS.
- GitHub is the source of truth. The VPS is a deployment target, not a development environment.
- Never make edits directly on the VPS that are not first committed to the repository.

### Deployment Order

When deploying multiple components in the same session:

```
1. Auth server (qg-auth) → deploy first
2. Dashboard(s) → deploy second
3. Nginx config → deploy LAST
```

Deploying nginx last ensures the auth server and dashboards are running and healthy before traffic is routed to them. Deploying nginx first with a broken backend causes 502 errors for live users.

---

## 13. Security Monitoring Checklist

Run this checklist at the start of every deployment session and after every deployment completes.

### Pre-Deployment Checks

- [ ] `crontab -l` shows ONLY the nightly export cron (`0 4 * * * /home/support/nightly-export.sh`) — no other entries
- [ ] All 5 dashboards return **HTTP 200** on their health endpoints
- [ ] All DBs pass `PRAGMA integrity_check` (returns `ok`)
- [ ] No deploy-guard lock files remain from previous sessions: `ls /tmp/deploy-guard-*.lock`
- [ ] PM2 processes all show status **`online`**: `pm2 list`
- [ ] Auth server is responding on port 5010: `curl -s http://localhost:5010/auth/check`
- [ ] Swap file is active: `free -h` shows Swap: 2.0Gi (Thread 24)

### Post-Deployment Checks

- [ ] All 5 dashboards return **HTTP 200** (confirmed by deploy-done.sh output)
- [ ] Auth server responding on port 5010 after restart
- [ ] Rate limit headers present in API responses: `curl -I https://<dashboard>/api/... | grep X-RateLimit`
- [ ] Export endpoints return **HTTP 403** for non-pro users (manual test or staging account)
- [ ] `POST /api/readings` returns **HTTP 403** from an external IP (test from local machine, not VPS)
- [ ] All DBs pass post-deploy `PRAGMA integrity_check` (confirmed by deploy-done.sh output)
- [ ] `pm2 list` shows all processes `online` with uptime increasing (not restarting in a loop)
- [ ] SSL certificate expiry confirmed: `echo | openssl s_client -connect quantitativegenius.com:443 2>/dev/null | openssl x509 -noout -dates`
- [ ] BTC endpoint responds: `curl -s http://localhost:5001/api/bitcoin-history?range=1H | head -c 100` (Thread 24)
- [ ] `bitcoin_data` table exists in oil, world, bitcoin, and gold DBs
- [ ] Bitcoin dashboard HTTP 200: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5003/health`
- [ ] Gold dashboard HTTP 200: `curl -s -o /dev/null -w "%{http_code}" http://localhost:5004/health`
- [ ] Bitcoin DB integrity: `sqlite3 /home/support/bitcoin-market-index-dashboard/data/bitcoin_markets.db "PRAGMA integrity_check;"`
- [ ] Gold DB integrity: `sqlite3 /home/support/gold-time-machine-dashboard/data/gold_markets.db "PRAGMA integrity_check;"`

### Periodic Checks (Monthly)

- [ ] SSL certificate expiry — renew before July 1, 2026
- [ ] Review Stripe restricted key permissions — confirm no scope creep
- [ ] Confirm crontab has only the nightly export: `crontab -l` for `support` (should show only `0 4 * * *`) and `root` (should be empty)
- [ ] Review PM2 logs for anomalous 403/429 spikes: `pm2 logs --lines 200`
- [ ] Confirm swap file still active: `free -h` (Thread 24 — added to monthly checklist)
- [ ] Confirm `bitcoin_data` tables are accumulating data in Oil, World, Bitcoin, and Gold DBs
- [ ] Confirm Gold DB (`gold_markets.db`) is accumulating data for all component tickers (GC=F, ^HUI, GDX, SI=F, ^XAU)

---

## Appendix A: Key File & Path Reference

| Component | Path |
|---|---|
| Auth server | `/opt/qg-auth/` |
| Auth server port | `5010` |
| deploy-guard script | `/home/support/deploy-guard.sh` |
| deploy-done script | `/home/support/deploy-done.sh` |
| nightly export script | `/home/support/nightly-export.sh` |
| nightly export log | `/home/support/nightly-export.log` |
| Nginx rate limit config | `/etc/nginx/snippets/rate-limit.conf` |
| Swap file | `/swapfile` (2GB, permanent via /etc/fstab) |
| Dashboard 1 (port 5000) | `/home/support/oil-markets-time-machine-dashboard/` |
| Dashboard 2 (port 5001) | `/home/support/world-markets-time-machine-dashboard/` |
| Dashboard 3 (port 5002) | `/home/support/cybersecurity-threat-index-dashboard/` |
| Dashboard 4 (port 5003) | `/home/support/bitcoin-market-index-dashboard/` |
| Dashboard 5 (port 5004) | `/home/support/gold-time-machine-dashboard/` |
| Rate limiter module | `<dashboard-repo>/middleware/rate-limiter.js` |
| Oil DB | `/home/support/oil-markets-time-machine-dashboard/data/oil_markets.db` |
| World DB | `/home/support/world-markets-time-machine-dashboard/data/world_markets.db` |
| Cyber DB | `/home/support/cybersecurity-threat-index-dashboard/data/cybersecurity.db` |
| Bitcoin DB | `/home/support/bitcoin-market-index-dashboard/data/bitcoin_markets.db` |
| Gold DB | `/home/support/gold-time-machine-dashboard/data/gold_markets.db` |

---

## Appendix B: Incident Log

| Date | Incident | Root Cause | Resolution |
|---|---|---|---|
| April 6, 2026 | DB corruption | Auto-update cron ran `git pull` mid-write | Removed cron; restored DB from backup |
| April 7, 2026 | DB corruption | Stale branch checkout overwrote DB file | Restored DB; switched to file-specific checkout |
| April 8, 2026 | DB corruption | `git reset --hard` ran while PM2 was running | Restored DB; deploy-guard system implemented |
| April 8, 2026 | All 3 sites down ~7 hours (OOM crash) | e2-micro (958MB RAM) with no swap; OOM killer cascaded into full freeze; GCP auto-rebooted after ~7h | Created 2GB `/swapfile` (permanent via `/etc/fstab`) |
| April 10, 2026 | OOM crash — load spike to 52 | Running `generate_exports.py` via screen while all 3 dashboards active; Python + Node.js exceeded RAM | Killed runaway Python; created nightly-export.sh that stops PM2 first; installed as system cron |
| April 10, 2026 | Oil ~18% fetch failures | Oil SQLite using `delete` journal mode; concurrent reads/writes caused "database is locked" | Switched to WAL mode: `PRAGMA journal_mode=WAL` |
| April 13, 2026 | Oil export zombie process (8+ min hang) | Correlated subquery O(N*M) in generate_exports.py — same pattern as April 10 | Killed zombie PID 485163; rewrote to dictionary-based lookups |

---

*End of QG-Security-Reference-v1.4.md*

---

## v1.5 — 2026-04-18 Hardening Pass

### Changes vs v1.4
1. **Secrets out of ecosystem.config.js.** Live Stripe/Resend/webhook keys moved to `/opt/qg-auth/.env` (chmod 600, owner support:support). `auth-server.js` loads them at boot via `dotenv.config({ path: require('path').join(__dirname, '.env') })`. `ecosystem.config.js` now contains only `name`, `script`, `max_memory_restart: '200M'`.
2. **All 13 dashboards rebound to 127.0.0.1.** Previously `app.listen(PORT, ...)` defaulted to 0.0.0.0 (publicly reachable on the VPS IP). Patched to `app.listen(PORT, '127.0.0.1', ...)`. nginx still proxies to them via localhost with no change.
3. **UFW firewall enabled.** Policy: default deny incoming, default allow outgoing. Allow-list: 22/tcp, 80/tcp, 443/tcp. No other ports open.
4. **SSH hardened.** Password auth disabled (was already off via cloud-init). Stale keys on root/authorized_keys pruned down to only `computer-agent-20260418`. `ubuntu` user locked (`usermod -L ubuntu`), removed from sudo group, `authorized_keys` cleared.
5. **Duplicate PM2 daemon killed.** Root's `/root/.pm2/` daemon was running a second copy of qg-auth in parallel with support's PM2 daemon. Removed root's PM2 systemd startup entry (`pm2 unstartup systemd -u root --hp /root`). Only `support` PM2 daemon now runs.
6. **.gitignore hardened.** `.env`, `*.bak.*`, `.old-backups/` excluded from qg-auth repo.

### New Deployment Checklist (append to QG-Deployment-Guide)
When deploying a new auth change:
```bash
# 1. Update /opt/qg-auth/.env if secrets changed (chmod 600)
ssh support@VPS 'chmod 600 /opt/qg-auth/.env && ls -la /opt/qg-auth/.env'

# 2. Update auth-server.js / auth-routes.js / etc
scp auth-*.js support@VPS:/opt/qg-auth/

# 3. Restart under support PM2 (NOT root PM2)
ssh support@VPS 'pm2 restart qg-auth --update-env && pm2 save'

# 4. Verify: dotenv loaded + endpoint live
ssh support@VPS 'pm2 logs qg-auth --nostream --lines 5' | grep "injected env"
curl -sI https://quantitativegenius.com/auth/login | head -1  # want 200
```

When deploying a new dashboard:
- server.js **must** bind `app.listen(PORT, '127.0.0.1', ...)` — not `0.0.0.0`.
- Add nginx upstream block; no UFW changes needed (ports stay loopback-only).

### Audit Results After v1.5
- Public ports: 22, 80, 443 (GCP edge may ACK TCP on others but no app listens)
- Dashboard ports 5000-5013: all bound to 127.0.0.1
- SSH keys on root: 1 (current)
- SSH keys on support: 1 (current)
- ubuntu user: locked, no keys, no sudo
- PM2 daemons: 1 (support)
- Plaintext secrets in /opt/qg-auth/*.{js,json}: 0 (excluding docs/comments)


---

## Thread 31 · Security Additions (2026-04-18)

### Expanded GitHub-first gate

Following error E9 (Stripe API writes without GitHub-first documentation), the pre-deploy gate is now explicitly defined to cover ALL system-of-record writes, not just VPS file writes.

Covered surfaces:
- VPS filesystem (all dashboards, configs, scripts)
- Stripe (products, prices, coupons, payment links, webhook config)
- DNS (A/AAAA/MX/TXT records at registrar)
- GitHub Pages (any deployed content)
- Nginx server blocks (via VPS files)
- SSL certificate issuance (renewals excluded)
- PM2 ecosystem files

### Upstream API credential handling (card dashboards)

The six card dashboards (baseball, basketball, football, hockey, soccer, pokemon) authenticate to an upstream card-pricing API using a token stored only in `/home/support/<sport>-card-time-machine-dashboard/.env` with chmod 600. The token never:

- Appears in git history (`.env` is .gitignored; `.env.example` contains only a placeholder).
- Appears in PM2 logs (server never logs the token value, only success/failure).
- Appears in HTTP response bodies (token is request-header-only).

### Cloudflare challenge handling

The card-pricing API sits behind Cloudflare. The dashboard fetcher:

- Sends a realistic browser User-Agent (`Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ... Chrome/120.0.0.0 Safari/537.36`).
- Sends `Accept: application/json, text/plain, */*` and `Accept-Language: en-US,en;q=0.9`.
- Detects Cloudflare challenges by checking if the response body begins with `<` (HTML challenge page).
- Retries 3x with 1.5s / 3s / 4.5s backoff.
- Non-CF errors surface immediately without retry.

This prevents log flooding during normal Cloudflare cycles without masking genuine upstream failures.

### Overlay endpoint auth

All overlay endpoints (`/api/sp500-history`, `/api/gold-history`, `/api/btc-history`) on the 7 overlay-enabled dashboards (auto + 6 sports + pokemon) pass through the standard `apiLimiter + requireAuth` chain. No overlay endpoint is publicly reachable without a valid auth cookie or API key.

### Market-hours gate as DoS absorption

The market-hours gate added to gold and stocks dashboards in Thread 31 (commits `228c43f`, `f794969`) is a side benefit from a security perspective: it reduces outbound fetch volume to Yahoo by ~33% (no weekend polling of gated tickers). This both reduces our upstream rate-limit risk and eliminates the ECONNRESET log noise that was masking legitimate errors.

### BTC-USD always-on rule (crypto 24/7)

BTC-USD is explicitly exempt from the market-hours gate on every dashboard that uses a gate. The exemption is encoded as a single function:

```js
function isMarketHoursTicker(ticker) {
  return ticker !== 'BTC-USD';
}
```

This is documented in the Master Reference (Thread 31 section 25) and in the public methodologies for each affected dashboard.
