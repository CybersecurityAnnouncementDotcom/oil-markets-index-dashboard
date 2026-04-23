<!-- MANDATORY: This filename MUST include the version number (e.g., HOF-Security-Reference-v1.3.md). -->

## v1.3 — 2026-04-23 (changelog)

**SECURITY INCIDENT REMEDIATION — pointer pattern adoption:**

On 2026-04-23, a GitGuardian scan detected that live Resend and ImprovMX API keys had been committed in plaintext to v1.1 and v1.2 of this document. The v1.2 file was mirrored to 5 public dashboard repositories (oil, world, cybersecurity, bitcoin, gold markets) under `docs/`, making both keys publicly discoverable for approximately 3 days (2026-04-20 to 2026-04-23).

A third secret — the CardLadder account password — was also discovered in v1.2 during hardening review. It was never used in any script or `.env` file (interactive-use only), but it was present in plaintext alongside the email in this document.

Remediation actions completed 2026-04-23:
- Resend API key rotated and revoked; new key stored on VPS at `/opt/qg-auth/.env` only.
- ImprovMX API key rotated and the old key disabled via the ImprovMX dashboard.
- Both old keys scrubbed from git history in all 6 repos (qg-deploy + 5 mirrored dashboards) via `git-filter-repo --replace-text` and force-push.
- CardLadder password scrubbed from git history in the same pass with this v1.3 release.
- GitHub account 2FA enabled (Authy).
- Independent verification: both revoked keys return `401` from their respective service APIs.

**New policy — pointer pattern:** Starting in v1.3, this document NEVER contains live secret values. Every secret is referenced by a pointer describing where the live value is stored (VPS `/opt/qg-auth/.env`, password manager, or service dashboard). Rotation procedures are cross-referenced to the QG-Account-Recovery-Guide.

**Still pending user action:**
- Rotate the CardLadder password at cardladder.com (interactive; scrub-only here is insufficient — the password is still valid until the user changes it).
- Enable 2FA on ImprovMX, Resend, NameBright, Stripe, Google Cloud, Yahoo Mail. See §11.
- Store new ImprovMX API key in a password manager.

**Older versions preserved:** v1.1 and v1.2 remain in `docs/` as historical records, but all live secret values they contained have been overwritten in git history with redaction markers.

---
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- INTERNAL ONLY: This document contains security implementation details — domain IDs, DNS records, pointers to where live credentials are stored. NEVER commit live secret values into this file. Use the pointer pattern (§2, §7, §8) and store actual values on the VPS or in a password manager. -->

# HOF (Hall of Fame) · Security Reference Guide

| Field | Value |
|---|---|
| **Version** | 1.3 (Pointer pattern adopted post-incident; all live secret values removed from document; git history scrubbed) |
| **Last Updated** | April 23, 2026 |
| **Owner** | jq_007@yahoo.com |
| **Classification** | INTERNAL ONLY |
| **Scope** | HOF .com sites, capture credentials, email infrastructure for 6 HOF domains |
| **Project Family** | HOF |

---

## 1. Security Overview

### Inheritance from QG

HOF infrastructure shares the QG VPS (GCP e2-micro, 35.233.231.75). The vast majority of security controls are **inherited from QG-Security-Reference v1.6** and are not duplicated here. Refer to that document for:

- Rate limiting (nginx + Express)
- SSH hardening + UFW firewall
- deploy-guard / deploy-done workflow
- Database WAL mode + integrity checks
- Deployment security rules (GitHub-first, no `git pull`, no `sed`)
- VPS user privilege model (`support` user, no passwordless sudo)

### HOF-Specific Security Concerns

| Concern | Detail |
|---|---|
| CardLadder credentials | jq_007@yahoo.com account used during April 2026 capture campaign — password pointer in §2; rotation required after campaign ends |
| Resend domain records | Per-domain DKIM/SPF records generated for all 6 HOF domains; NameBright paste pending (see §4) |
| ImprovMX API key | Pointer in §7 (stored on VPS, not in this file); rotate annually or on staff change |
| NameBright DNS | All 6 HOF domains registered at NameBright; DNS managed there (no public API — paste manually) |
| Static site attack surface | No Node.js backend on HOF sites — attack surface limited to nginx config and static files |

### Threat Model (HOF-Specific Additions)

| Threat | Mitigation |
|---|---|
| CardLadder credential exposure | Credential used manually; not stored in any script or `.env` file; this doc no longer stores the password (pointer pattern §2); rotate post-campaign |
| HOF data injection | `hof_sales` table lives in QG VPS SQLite shared layer; protected by deploy-guard + localhost-only write access |
| DNS hijack on HOF domains | A records at NameBright → GCP IP only; no third-party DNS services with write access |
| Email spoofing from HOF domains | SPF + DKIM records generated; pending NameBright paste. Until pasted, outbound will fail authentication. |
| ImprovMX API key theft | Key stored on VPS `/opt/qg-auth/.env` (mode 600); scope limited to domain/alias management; scrubbed from all git history as of v1.3 |
| Secrets leaking to public repos | **v1.3 policy: no live secrets in any doc mirrored beyond qg-deploy.** Pointer pattern only. See §12 Secret Hygiene. |

---

## 2. CardLadder Credentials

| Field | Value |
|---|---|
| **Email** | jq_007@yahoo.com |
| **Password** | Stored in user's password manager (not in this document as of v1.3). Previously in plaintext in v1.1/v1.2 — scrubbed from git history on 2026-04-23. |
| **Purpose** | Manual HOF sales capture via CardLadder during April 2026 campaign |
| **Used for** | Reading graded sale records for inducted HOF cards |
| **Rotation procedure** | Log in at https://cardladder.com → Account → Change Password. Update password manager entry. No VPS or script updates required (interactive-use only). |

> **⚠ TODO: Rotate this password after the HOF capture campaign ends.**
> This action item is also tracked in QG-Security-Reference v1.6 (Thread 32 section) and QG-Parking-Lot-9.md §44. **The scrub from git history on 2026-04-23 does NOT rotate the password at CardLadder itself — the password remains valid until the user manually changes it.**

**Rules:**
- These credentials are for CardLadder only — never reused elsewhere.
- **Never stored in any script, `.env` file, git repo, PM2 config, or any document in `docs/`.**
- Used interactively / manually only.

---

## 3. Resend Domain IDs (6 HOF .com Domains)

Resend Pro ($20/mo) handles outbound transactional email for all 6 HOF domains.

| Domain | Resend Domain ID | Status |
|---|---|---|
| baseballcardhalloffame.com | `a0cd4848-d04c-4ef4-81dd-c3e81cd0e796` | not_started (DNS pending) |
| basketballcardhalloffame.com | `4faf6bfa-0425-4b42-aea0-c8e6f346297a` | not_started (DNS pending) |
| footballcardhalloffame.com | `9856eb2e-8c3d-4d74-9d6b-c3daa359f762` | not_started (DNS pending) |
| hockeycardhalloffame.com | `a4dc3397-8ea4-4ccc-978a-ff9633e5e580` | not_started (DNS pending) |
| soccercardhalloffame.com | `3490a706-734c-4b4a-8fd8-099e1fac396b` | not_started (DNS pending) |
| pokemoncardhalloffame.com | `0cb1da69-8131-4119-9d5a-4b2b8de8ccb9` | not_started (DKIM now generated) |

**Resend API Key (pointer):** stored in `/opt/qg-auth/.env` on VPS as `RESEND_API_KEY`.
- Retrieval: `ssh support@35.233.231.75 "sudo grep RESEND_API_KEY /opt/qg-auth/.env"`
- Rotation procedure: log in at https://resend.com/api-keys → create new key → update VPS `/opt/qg-auth/.env` → `pm2 restart qg-auth` → revoke old key in Resend dashboard. See QG-Account-Recovery-Guide §Secrets.
- Domain IDs above are non-secret (service identifiers) and safe to keep in this doc.

Cross-reference: QG-Security-Reference v1.6 Thread 32 mirrors the same 6 IDs.

---

## 4. NameBright DNS — Pending User Action

### Status

Complete paste-ready DNS records for all 6 HOF domains are in:

```
/home/user/workspace/cl-dataset/resend/NAMEBRIGHT_DNS_INSTRUCTIONS.md
```

This file covers: records to DELETE, records to ADD, combined SPF for `@` (ImprovMX + Resend in one record), Resend DKIM TXT, and the `send` subdomain MX/SPF for SES feedback.

### Live DNS Snapshot (April 20, 2026, 6:30 PM PDT)

| Domain | Current MX | ImprovMX | Resend DKIM | A root → VPS |
|---|---|---|---|---|
| baseballcardhalloffame.com | NameBright default | ❌ missing | ❌ missing | ✅ 35.233.231.75 |
| basketballcardhalloffame.com | NameBright default | ❌ missing | ❌ missing | ✅ 35.233.231.75 |
| footballcardhalloffame.com | NameBright default | ❌ missing | ❌ missing | ✅ 35.233.231.75 |
| hockeycardhalloffame.com | ImprovMX ✅ | ✅ live (SPF needs update) | ❌ missing | ✅ 35.233.231.75 |
| soccercardhalloffame.com | NameBright default | ❌ missing | ❌ missing | ✅ 35.233.231.75 |
| pokemoncardhalloffame.com | NameBright default | ❌ missing | ❌ missing | ❌ Parked (ELB) |

### pokemoncardhalloffame.com Full DNS Overhaul Needed

Root `A` still points to `54.165.131.183` / `52.44.244.98` (NameBright ComingSoon ELB) and there's a wildcard `*` CNAME intercepting all subdomains. The instructions file specifies:
- Delete wildcard CNAME, parking A records, default MX, default SPF
- Add A `@` + A `www` → `35.233.231.75`
- Add ImprovMX MX + Resend DKIM + `send` subdomain records
- Issue SSL via certbot after DNS propagates

---

## 5. Search Console / Bing Webmaster Verification

- Verification `<meta>` tag placeholder slots are present in every HOF page `<head>` (all 12 HTML files)
- **BUG (identified April 20, 2026):** Live DNS shows placeholder literal `google-site-verification=YourUniqueGoogleVerificationCode` on 5 domains — this was a paste-error in the DNS setup, not a real token. Must be removed when real tokens are added.
- **Action required:** User to provide Google Search Console and Bing Webmaster verification IDs
- Agent action: paste IDs into placeholder slots and re-deploy per GitHub-first rule
- One verification token per domain per service = 12 Search Console + 12 Bing entries total

---

## 6. SSL Certificates

| Domain | SSL Status | Notes |
|---|---|---|
| baseballcardhalloffame.com | ✅ Issued | Let's Encrypt R13; covers root + www |
| basketballcardhalloffame.com | ✅ Issued | Let's Encrypt R13; covers root + www |
| footballcardhalloffame.com | ✅ Issued | Let's Encrypt R13; covers root + www |
| hockeycardhalloffame.com | ✅ Issued | Let's Encrypt R13; covers root + www |
| soccercardhalloffame.com | ✅ Issued | Let's Encrypt R13; covers root + www |
| pokemoncardhalloffame.com | ⏳ Pending | Issue during domain bring-up (DNS + nginx first) |

**Renewal:**
- All 5 live certs auto-renew via `certbot.timer` (systemd)
- Add pokemoncardhalloffame.com to certbot during bring-up:
  ```bash
  certbot --nginx -d pokemoncardhalloffame.com -d www.pokemoncardhalloffame.com
  ```

---

## 7. Inbound Email (ImprovMX) — PROVISIONED April 20, 2026

| Property | Value |
|---|---|
| Provider | ImprovMX Premium — $9/mo |
| Account login | jq_007@yahoo.com |
| API key (pointer) | Stored in `/opt/qg-auth/.env` on VPS as `IMPROVMX_API_KEY`. Previous key rotated and disabled 2026-04-23. |
| Model | Catch-all + named alias forwarding — no inbox to manage |
| Forwarding destination | support@geniusmarketresearch.com (Google Workspace inbox) |
| Domains covered | All 6 HOF .com domains |

**API key retrieval:** `ssh support@35.233.231.75 "sudo grep IMPROVMX_API_KEY /opt/qg-auth/.env"`

**Rotation procedure:**
1. Log in at https://improvmx.com/account/api-keys
2. Click "Create new API key" → copy value
3. Update VPS: `ssh support@35.233.231.75 "sudo sed -i 's|^IMPROVMX_API_KEY=.*|IMPROVMX_API_KEY=<new>|' /opt/qg-auth/.env"` (or edit in $EDITOR — never commit to git)
4. Click "Disable" on the old key row in the ImprovMX dashboard (note: ImprovMX does not delete keys — disable is the only option; disabled keys return 401 and stay visible with a "Disabled:" timestamp)
5. Verify revocation: `curl -u 'api:<OLD_KEY>' https://api.improvmx.com/v3/account/` → expect `401`
6. Update password-manager entry

**All 6 domains configured in ImprovMX with 2 aliases each:**
- `support@<domain>` → support@geniusmarketresearch.com
- `*@<domain>` (catch-all) → support@geniusmarketresearch.com

**Domain → alias IDs (for reference; non-secret):**
| Domain | support@ ID | *@ catch-all ID |
|---|---|---|
| baseballcardhalloffame.com | 6369596 | 6369591 |
| basketballcardhalloffame.com | 6369597 | 6369592 |
| footballcardhalloffame.com | 6369598 | 6369593 |
| hockeycardhalloffame.com | 6369601 | 6367803 |
| soccercardhalloffame.com | 6369599 | 6369594 |
| pokemoncardhalloffame.com | 6369600 | 6369595 |

**Status:** All 6 domains show `active: false` in ImprovMX API response until NameBright MX records are pasted and propagated.

**MX records to paste at NameBright** (on root `@`):

| Record | Value | Priority |
|---|---|---|
| MX @ | `mx1.improvmx.com` | 10 |
| MX @ | `mx2.improvmx.com` | 20 |
| TXT @ | `v=spf1 include:spf.improvmx.com include:amazonses.com ~all` (combined SPF) | — |

> **Critical:** Delete any existing `mail1.namebrightmail.com` / `mail2.namebrightmail.com` MX records and the NameBright default SPF before pasting the ImprovMX records. Only one SPF TXT record per host is allowed — combine both services in ONE record.

---

## 8. Outbound Email (Resend) — DKIM GENERATED, DNS PENDING

| Property | Value |
|---|---|
| Provider | Resend Pro — $20/mo |
| API key (pointer) | Stored in `/opt/qg-auth/.env` on VPS as `RESEND_API_KEY`. Previous key rotated and revoked 2026-04-23. |
| Model | Per-domain DKIM signing after DNS verification |
| Status | All 6 domains added; DKIM generated; DNS paste pending |

**After DNS is pasted, send-from addresses will be:**
- `support@baseballcardhalloffame.com`
- `support@basketballcardhalloffame.com`
- `support@footballcardhalloffame.com`
- `support@hockeycardhalloffame.com`
- `support@soccercardhalloffame.com`
- `support@pokemoncardhalloffame.com`

Because ImprovMX handles inbound on the same mailbox name, replies to any of these will arrive in the Google Workspace inbox, and Resend can send as them for outbound — giving full bidirectional email from the HOF domain addresses.

**Cost note:** $20/mo Resend Pro covers all 6 HOF domains plus the existing QG domain. Not a separate charge.

---

## 9. Data Protection

- HOF capture data (`hof_card_meta`, `hof_sales`) lives in the **QG VPS SQLite shared layer**
- WAL mode required — consistent with all other QG databases
- **Backups** inherit the QG nightly export cron (`/home/support/nightly-export.sh`) — HOF tables are included in the same VPS backup envelope
- deploy-guard must be run before any operation touching the SQLite layer
- See QG-Security-Reference v1.6 §11 (Data Integrity) for glitch protection, duplicate prevention, and WAL mode specifications

---

## 10. Account 2FA Posture (status as of 2026-04-23)

| Account | 2FA Status | Priority |
|---|---|---|
| GitHub (CybersecurityAnnouncementDotcom) | ✅ Enabled (Authy, 2026-04-23) | Done |
| ImprovMX | ❌ Off — `is_otp_enabled: false` | P2 — enable |
| Resend | ❓ Status not exposed via API | P2 — verify + enable |
| NameBright | ❓ Unknown | P2 — enable (domain registrar = highest impact) |
| Stripe | ❓ Unknown | P2 — enable |
| Google Cloud | ❓ Unknown | P2 — enable |
| Yahoo Mail (jq_007@yahoo.com, recovery chain owner) | ❓ Unknown | P2 — enable (recovery root of trust) |

Recovery codes for GitHub 2FA stored by the user. See QG-Account-Recovery-Guide for policy on where to store recovery codes.

---

## 11. Secret Hygiene Policy (new in v1.3)

**Rules of the pointer pattern:**

1. **Never write a live secret value into any markdown doc in `docs/` — not even in a repo marked private.** Private repos can be made public accidentally, mirrored to public repos, or exfiltrated via a compromised developer machine.
2. **Every secret is referenced by three fields:** where it lives (VPS path + env var, or password manager, or service dashboard), how to retrieve it (exact shell command), and how to rotate it (step-by-step procedure).
3. **Non-secret identifiers** (domain IDs, alias IDs, domain names, IP addresses, public fingerprints) may still be documented inline — they are not sensitive.
4. **Private docs that must reference a secret by value** (rare) live in `/opt/qg-auth/` on the VPS, never in git.
5. **Before every commit that touches `docs/`, agents must grep for common secret patterns:**
   ```bash
   grep -rnE "(re_[A-Za-z0-9_]{20,}|sk_[a-f0-9]{32}|AKIA[0-9A-Z]{16})" docs/
   ```
   If any hits appear, abort the commit and use the pointer pattern.
6. **GitHub secret scanning + push protection must be enabled on every public repo.** Audit list maintained in `security_incident_20260423/Security-Hardening-Audit-2026-04-23.md`.
7. **On any accidental leak:** follow the 2026-04-23 incident runbook — rotate first, revoke second, scrub git history third, push protection fourth, document in changelog fifth.

---

## 12. Version History

| Version | Date | Notes |
|---|---|---|
| 1.0 | April 20, 2026 | Initial release. Documents CardLadder credentials, all 6 Resend HOF domain IDs, NameBright DNS pending state, SSL status (5 live / 1 pending), ImprovMX inbound ($9/mo), Resend outbound ($20/mo), HOF SQLite data protection. |
| 1.1 | April 20, 2026 | Email infrastructure fully provisioned via API. ImprovMX API key added (plaintext — leaked, rotated on 2026-04-23); all 6 HOF domains registered in ImprovMX with `support@` + catch-all aliases (alias IDs documented). Resend DKIM generated for all 6 domains incl. Pokemon (which was previously missing). Live DNS snapshot added. Google Search Console placeholder-literal bug documented. |
| 1.2 | April 23, 2026 | Phase 2 email migration: 12 HOF ImprovMX aliases repointed from jq_007@yahoo.com → support@geniusmarketresearch.com (Google Workspace). Confirmed all 6 HOF A records resolve to VPS 35.233.231.75. Rollback path documented. (Note: v1.2 also contained leaked API keys and CardLadder password — rotated and scrubbed from git history on 2026-04-23 as part of v1.3.) |
| 1.3 | April 23, 2026 | **Security incident remediation + pointer pattern adoption.** Removed all live secret values from this document. Added §10 Account 2FA Posture, §11 Secret Hygiene Policy. Git history scrubbed via `git-filter-repo --replace-text` across qg-deploy + 5 mirrored dashboard repos. Old Resend + ImprovMX keys rotated and revoked (verified 401). GitHub 2FA enabled. CardLadder password password-manager-only going forward (rotation at CardLadder still pending user action). |
