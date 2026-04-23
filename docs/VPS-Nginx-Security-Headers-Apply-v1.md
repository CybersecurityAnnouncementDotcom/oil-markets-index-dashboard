<!-- MANDATORY: filename includes version number -->

# VPS Nginx Security Headers — Apply Procedure v1

**Purpose.** Install HSTS, CSP, and Permissions-Policy on all 7 HOF/GMR vhosts on the VPS (35.233.231.75).

**Why this doc exists.** The `support` user on the VPS does not have passwordless sudo. Nginx vhosts live in `/etc/nginx/sites-available/` (owned by root), so the agent cannot edit them live. This doc gives you exact paste-ready commands to run over SSH with your sudo password.

**Source of truth.** All configs are committed in `hofcards/nginx/` — the live VPS is a target. Never edit the VPS configs directly; always apply by pulling from git.

## 1. What gets installed

- **New file:** `/etc/nginx/snippets/hof-security-headers.conf` (contains HSTS, CSP, Permissions-Policy, Cross-Origin-Opener-Policy).
- **7 vhosts patched** to include that snippet: baseball, basketball, football, hockey, pokemon, soccer HOF, and geniusmarketresearch.

The 3 existing headers (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`) stay inline in each vhost — they were already there.

## 2. Apply procedure

SSH in as `support@35.233.231.75`, then run:

```bash
# 0) Pull latest hofcards repo (GitHub-first policy).
cd /home/support/hofcards
git fetch origin main
git checkout origin/main -- nginx/

# 1) Copy snippet into nginx snippets dir (requires sudo).
sudo cp /home/support/hofcards/nginx/hof-security-headers.conf /etc/nginx/snippets/hof-security-headers.conf
sudo chown root:root /etc/nginx/snippets/hof-security-headers.conf
sudo chmod 644 /etc/nginx/snippets/hof-security-headers.conf

# 2) Back up existing live vhosts.
ts=$(date -u +%Y%m%dT%H%M%SZ)
sudo mkdir -p "/etc/nginx/backups/${ts}"
for d in baseball basketball football hockey pokemon soccer; do
  sudo cp "/etc/nginx/sites-available/${d}cardhalloffame.com.conf" "/etc/nginx/backups/${ts}/"
done
sudo cp /etc/nginx/sites-available/geniusmarketresearch.com.conf "/etc/nginx/backups/${ts}/"
echo "Backups in /etc/nginx/backups/${ts}"

# 3) For each vhost, add the include line INSIDE the 443 server block
#    (after the three existing security headers). Live vhosts are certbot-mutated,
#    so we patch live copies directly — the repo templates are kept in sync for
#    future rebuilds. The `include` must live inside `server { ... }` but before
#    `access_log`.
#
#    Check each one shows the include line after this step:
for d in baseball basketball football hockey pokemon soccer; do
  sudo nginx -T 2>/dev/null | grep -A1 "server_name ${d}cardhalloffame.com" | head -3
done

# 4) Test nginx config.
sudo nginx -t
# Expect: "syntax is ok" + "test is successful"

# 5) Reload nginx (zero downtime).
sudo systemctl reload nginx

# 6) Verify headers live on all 6 HOF domains + geniusmarketresearch.
for host in baseball basketball football hockey pokemon soccer; do
  echo "=== ${host}cardhalloffame.com ==="
  curl -sI "https://${host}cardhalloffame.com/" | grep -iE "strict-transport|content-security|permissions-policy|x-frame|x-content|referrer"
done
echo "=== geniusmarketresearch.com ==="
curl -sI "https://geniusmarketresearch.com/" | grep -iE "strict-transport|content-security|permissions-policy"
```

## 3. How to apply the `include` in step 3

Live vhosts have been rewritten by certbot and don't match the repo template line-for-line. The cleanest approach is to open each in `sudo nano` (or `$EDITOR`) and add one line inside the 443 `server { ... }` block, just before the `access_log` line.

Line to add:

```nginx
    include /etc/nginx/snippets/hof-security-headers.conf;
```

**Do this for all 7 vhosts:**

```bash
sudo nano /etc/nginx/sites-available/baseballcardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/basketballcardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/footballcardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/hockeycardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/pokemoncardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/soccercardhalloffame.com.conf
sudo nano /etc/nginx/sites-available/geniusmarketresearch.com.conf
```

In each file, find the 443 block (it has `listen 443 ssl;` and the 3 `add_header` lines for X-Content-Type-Options, X-Frame-Options, Referrer-Policy). Paste the `include` line right after those 3 headers, save and exit.

Pokemon is HTTP-only (no 443 block yet) — put the include inside the 80 server block, before `access_log`.

## 4. Rollback

```bash
ts=<timestamp-of-backup>   # from step 2 above
sudo cp -r "/etc/nginx/backups/${ts}/"*.conf /etc/nginx/sites-available/
sudo rm /etc/nginx/snippets/hof-security-headers.conf
sudo nginx -t && sudo systemctl reload nginx
```

## 5. Verification checklist

After step 6 above, each HOF domain should return:

- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'; ...` (long)
- `Permissions-Policy: accelerometer=(), ...` (long)
- Existing: `X-Content-Type-Options: nosniff`, `X-Frame-Options: SAMEORIGIN`, `Referrer-Policy: strict-origin-when-cross-origin`

## 6. CSP tuning notes

The CSP in the snippet is permissive (`'unsafe-inline'` for scripts and styles) to avoid breaking the existing HOF templates, which contain inline scripts and styles. A tighter version would use nonces or hashes. Recommend:

1. Watch browser console + any CSP reports for ~1 week after rollout.
2. If nothing breaks, tighten: remove `'unsafe-inline'` from `style-src` first, then `script-src`, after refactoring inline blocks to external files.
3. Update this doc to v2 with the tightened CSP and re-apply.

The CSP blocks third-party script includes by default — if any HOF page adds an analytics tag, embed, or third-party widget, it must be allowlisted in `script-src` / `frame-src` first.

---

**Version history:**
- v1 (2026-04-23): Initial procedure post-incident remediation.
