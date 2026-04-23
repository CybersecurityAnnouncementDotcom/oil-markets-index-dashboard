<!-- MANDATORY: This filename MUST include the version number (e.g., HOF-Security-Reference-v1.0.md). -->

## v1.2 — 2026-04-23 (changelog)

**Phase 2 email migration:**
- All 12 HOF ImprovMX aliases (6 domains × `*` + `support`) now forward to `support@geniusmarketresearch.com` (Google Workspace inbox, billed via Wix). Previously forwarded to `jq_007@yahoo.com`.
- Confirmed VPS A records for all 6 HOF domains resolve to `35.233.231.75`. Old IP `136.117.206.145` was Wix shared infra, not the VPS (see QG-Parking-Lot §E4).
- Rollback path: `bash /home/user/workspace/improvmx_migration/repoint_aliases.sh ROLLBACK`. Pre-migration snapshot at `/home/user/workspace/improvmx_migration/pre-migration-snapshot-20260423T083123Z.json`.
- Owner email on ImprovMX account remains `jq_007@yahoo.com` for account recovery.

**Older versions preserved:** v1.1 remains in `docs/` as historical record.

---
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- INTERNAL ONLY: This document contains security implementation details — credentials, domain IDs, DNS records. NEVER share externally or include in public methodology PDFs. -->

# HOF (Hall of Fame) · Security Reference Guide

| Field | Value |
|---|---|
| **Version** | 1.2 (Email infra fully provisioned — ImprovMX API key added, all 6 domains in ImprovMX with support@ + catch-all aliases, Resend DKIM keys generated for all 6 incl. Pokemon, NameBright DNS paste remaining as the only blocker) |
| **Last Updated** | April 20, 2026 |
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
| CardLadder credentials | jq_007@yahoo.com account used during April 2026 capture campaign — rotation required after campaign ends |
| Resend domain records | Per-domain DKIM/SPF records generated for all 6 HOF domains; NameBright paste pending (see §4) |
| ImprovMX API key | `sk_***REDACTED_ROTATED_20260423***` — stored here INTERNAL ONLY; rotate annually or on staff change |
| NameBright DNS | All 6 HOF domains registered at NameBright; DNS managed there (no public API — paste manually) |
| Static site attack surface | No Node.js backend on HOF sites — attack surface limited to nginx config and static files |

### Threat Model (HOF-Specific Additions)

| Threat | Mitigation |
|---|---|
| CardLadder credential exposure | Credential used manually; not stored in any script or `.env` file; rotate post-campaign |
| HOF data injection | `hof_sales` table lives in QG VPS SQLite shared layer; protected by deploy-guard + localhost-only write access |
| DNS hijack on HOF domains | A records at NameBright → GCP IP only; no third-party DNS services with write access |
| Email spoofing from HOF domains | SPF + DKIM records generated; pending NameBright paste. Until pasted, outbound will fail authentication. |
| ImprovMX API key theft | Key stored in this doc (INTERNAL) + on VPS env vars only; scope limited to domain/alias management |

---

## 2. CardLadder Credentials

| Field | Value |
|---|---|
| **Email** | jq_007@yahoo.com |
| **Password** | ***REDACTED_CARDLADDER_PW_20260423*** |
| **Purpose** | Manual HOF sales capture via CardLadder during April 2026 campaign |
| **Used for** | Reading graded sale records for inducted HOF cards |

> **⚠ TODO: Rotate this password after the HOF capture campaign ends.**
> This action item is also tracked in QG-Security-Reference v1.6 (Thread 32 section) and QG-Parking-Lot-9.md §44.

**Rules:**
- These credentials are for CardLadder only — never reused elsewhere.
- Never stored in any script, `.env` file, git repo, or PM2 config.
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

**Resend API Key:** `re_***REDACTED_ROTATED_20260423***`

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
| API key | `sk_***REDACTED_ROTATED_20260423***` (created April 21, 2026) |
| Model | Catch-all + named alias forwarding — no inbox to manage |
| Forwarding destination | jq_007@yahoo.com |
| Domains covered | All 6 HOF .com domains |

**All 6 domains now configured in ImprovMX with 2 aliases each:**
- `support@<domain>` → jq_007@yahoo.com
- `*@<domain>` (catch-all) → jq_007@yahoo.com

**Domain → alias IDs (for reference):**
| Domain | support@ ID | *@ catch-all ID |
|---|---|---|
| baseballcardhalloffame.com | 6369596 | 6369591 |
| basketballcardhalloffame.com | 6369597 | 6369592 |
| footballcardhalloffame.com | 6369598 | 6369593 |
| hockeycardhalloffame.com | 6369601 | 6367803 |
| soccercardhalloffame.com | 6369599 | 6369594 |
| pokemoncardhalloffame.com | 6369600 | 6369595 |

**Status:** All 6 domains show `active: false` in ImprovMX API response — this is expected; flips to `active: true` automatically once NameBright MX records are pasted and propagated.

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
| Model | Per-domain DKIM signing after DNS verification |
| Status | All 6 domains added; DKIM generated; DNS paste pending |

**After DNS is pasted, send-from addresses will be:**
- `support@baseballcardhalloffame.com`
- `support@basketballcardhalloffame.com`
- `support@footballcardhalloffame.com`
- `support@hockeycardhalloffame.com`
- `support@soccercardhalloffame.com`
- `support@pokemoncardhalloffame.com`

Because ImprovMX handles inbound on the same mailbox name, replies to any of these will arrive in jq_007@yahoo.com, and Resend can send as them for outbound — giving full bidirectional email from the HOF domain addresses.

**Cost note:** $20/mo Resend Pro covers all 6 HOF domains plus the existing QG domain. Not a separate charge.

---

## 9. Data Protection

- HOF capture data (`hof_card_meta`, `hof_sales`) lives in the **QG VPS SQLite shared layer**
- WAL mode required — consistent with all other QG databases
- **Backups** inherit the QG nightly export cron (`/home/support/nightly-export.sh`) — HOF tables are included in the same VPS backup envelope
- deploy-guard must be run before any operation touching the SQLite layer
- See QG-Security-Reference v1.6 §11 (Data Integrity) for glitch protection, duplicate prevention, and WAL mode specifications

---

## 10. Version History

| Version | Date | Notes |
|---|---|---|
| 1.0 | April 20, 2026 | Initial release. Documents CardLadder credentials, all 6 Resend HOF domain IDs, NameBright DNS pending state, SSL status (5 live / 1 pending), ImprovMX inbound ($9/mo), Resend outbound ($20/mo), HOF SQLite data protection. |
| 1.1 | April 20, 2026 | Email infrastructure fully provisioned via API. ImprovMX API key added; all 6 HOF domains registered in ImprovMX with `support@` + catch-all aliases (alias IDs documented). Resend DKIM generated for all 6 domains incl. Pokemon (which was previously missing). Live DNS snapshot added — 5 of 6 domains still have NameBright default MX; Pokemon still parked at NameBright ComingSoon ELB. Google Search Console placeholder-literal bug documented. Only remaining step: user pastes DNS at NameBright per `cl-dataset/resend/NAMEBRIGHT_DNS_INSTRUCTIONS.md`. |
