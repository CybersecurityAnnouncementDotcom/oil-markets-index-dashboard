<!-- MANDATORY: This filename MUST include the version number (e.g., HOF-Master-Reference-v1.0.md). -->

## v1.4 — 2026-04-23 (changelog)

**Phase 2 email migration + VPS IP correction:**
- Corrected VPS IP: `136.117.206.145` → **`35.233.231.75`**. Shared QG infrastructure is `35.233.231.75`, not the old stale IP (see QG-Parking-Lot §E4 and QG-Master-Reference-v32.4).
- HOF ImprovMX aliases now forward to `support@geniusmarketresearch.com` instead of `jq_007@yahoo.com`. Yahoo retained as account-recovery owner only.
- Pokemon HOF confirmed at 7 cards post-dedupe (2026-04-23).

**Older versions preserved:** v1.3, v1.2 remain in `docs/` as historical record.

---
<!-- When bumping the version, RENAME this file to the new version. NEVER use a plain filename without version. -->
<!-- SAFETY: HOF sites are static. All changes go through GitHub first. NEVER edit files directly on VPS. -->

# HOF (Hall of Fame) · Master Reference Guide

| Field | Value |
|---|---|
| **Last Updated** | April 21, 2026 |
| **Version** | 1.4 (Same as v1.2 + Thread 33 cross-references: methodology v2.4 (HOF overlay naming + chart presentation + data availability), chart presentation rule explicit (single y-axis, no dual-axis), data-availability honesty note) |
| **Owner** | jq_007@yahoo.com |
| **Brand** | (six standalone .com sites, no umbrella brand) |
| **Project Family** | HOF (one of three: QG · Scoring Systems · HOF — see Multi-Project-Index-v1.0.md) |

---

## ·· STOP · READ BEFORE ANY VPS WORK ··

1. **GitHub-first deployment is mandatory.** All HOF site changes must be committed to the `hofcards` repo and pushed to GitHub before touching any file on the VPS. This rule is formally documented in QG-Deployment-Guide v11.0. HOF inherits it unconditionally.
2. **NEVER edit HOF site files directly on VPS.** No `nano`, no `vi`, no `sed`, no inline patches. Push to GitHub; deploy via `git fetch` + `git checkout origin/main -- <file>`.
3. **HOF capture data lives in the QG VPS shared SQLite layer.** The `hof_card_meta` and `hof_sales` tables share the same VPS as QG dashboards. Run `deploy-guard` before any operation that could affect the database.
4. If you skip these rules, you risk data loss or site divergence from the repo. No exceptions.

---

## Table of Contents

1. Project Overview
2. The 6 HOF Sites
3. Site Architecture
4. HOF Sub-Index (Overview)
5. UI Naming Convention (CRITICAL)
6. Inducted Cards — Locked Decisions
7. Pokemon HOF Inducted Cards (10)
8. Capture Rules (Locked)
9. SEO Standards
10. Time Machine Predictions Cross-Link
11. Cross-Project Documents
12. Version History

---

## 1. Project Overview

- **6 standalone marketing sites** — one per sport (baseball, basketball, football, hockey, soccer, pokemon). No umbrella brand; each site operates independently under its own `.com` domain.
- **HOF sub-index** — integrated as a second trend line on each QG sport dashboard alongside the main Card Time Machine line.
- **Shared infrastructure with QG** — same VPS (GCP e2-micro, 35.233.231.75), same nginx, same GitHub-first git workflow.
- **Static-served** — no Node.js process, no PM2. Nginx serves HTML/CSS/assets directly from `/var/www/hofcards/`.
- **HOF-specific operating rules** (mandatory):
  - 1/1 cards permanently excluded from all indices
  - No interpolation of missing sales data
  - Full UI names always — never abbreviate "HOF" in any user-facing text

---

## 2. The 6 HOF Sites

| Domain | Status | Inducted Cards | Accent Color |
|---|---|---|---|
| baseballcardhalloffame.com | LIVE | 27 | Deep Red #c8102e (baseball traditional) |
| basketballcardhalloffame.com | LIVE | 17 | TBD |
| footballcardhalloffame.com | LIVE | 13 | TBD |
| hockeycardhalloffame.com | LIVE | 15 | TBD |
| soccercardhalloffame.com | LIVE | 12 | TBD |
| pokemoncardhalloffame.com | LIVE (DNS verified; nginx + SSL pending VPS deploy) | 7 | Pikachu Yellow #ffcb05 |
| **Total** | | **96** | |

> **Note:** pokemoncardhalloffame.com A records for `@` and `www` are now resolving to the VPS (35.233.231.75). nginx vhost config + certbot issuance remain pending on the VPS (queued after the GitHub push of commit `0a34466`). Bring-up follows the same pattern used for the 5 live domains (NameBright A record → certbot → nginx 443 block).

---

## 3. Site Architecture

### Repository

- **Repo:** `hofcards` (single mono-repo, GitHub user: CybersecurityAnnouncementDotcom)
- **VPS deploy path:** `/var/www/hofcards/`

### Directory Structure

```
hofcards/
  baseball/
    index.html
    members.html
    baseball.css
    assets/
  basketball/
    index.html
    members.html
    basketball.css
    assets/
  football/
    index.html
    members.html
    football.css
    assets/
  hockey/
    index.html
    members.html
    hockey.css
    assets/
  soccer/
    index.html
    members.html
    soccer.css
    assets/
  pokemon/
    index.html
    members.html
    pokemon.css
    assets/
  shared/
    css/       ← shared component styles
    js/        ← shared scripts
  nginx/
    baseballcardhalloffame.com.conf
    basketballcardhalloffame.com.conf
    footballcardhalloffame.com.conf
    hockeycardhalloffame.com.conf
    soccercardhalloffame.com.conf
    pokemoncardhalloffame.com.conf
  sitemap-index.xml
```

### Serving Model

- **Static only** — no PM2, no Node.js process
- nginx serves files directly; no reverse proxy to a backend port
- SSL via Let's Encrypt (certbot); 5 live domains have certs; pokemon cert pending

---

## 4. HOF Sub-Index (Overview)

### Data Capture

- Real CardLadder graded sales captured **manually** during the April 2026 HOF capture campaign
- Source: CardLadder (authenticated as jq_007@yahoo.com — see HOF-Security-Reference v1.0 §2)
- Capture follows the rules in §8 below

### SQLite Tables (QG VPS shared layer)

| Table | Description |
|---|---|
| `hof_card_meta` | One row per inducted HOF card — card ID, sport, player/set, year, grade-of-record |
| `hof_sales` | Sale records — card ID, sale date (ISO YYYY-MM-DD), price (cents integer) |

- Both tables live in the QG VPS SQLite shared layer alongside the existing sport dashboard databases
- WAL mode required (consistent with all other QG databases)

### Index Calculation

- Each card's price series is **normalized to first sale = 100**
- **Daily HOF sub-index** = median of all normalized series across inducted cards for that sport, for that day
- Loaded into QG sport dashboards as a **second trend line** alongside the main Card Time Machine line
- Full methodology: Sports_and_Pokemon_Card_Time_Machine_Methodology_v2.1.md

### Integration Point

- QG dashboard backend exposes `GET /api/hof-history?range=...` per sport
- Frontend renders HOF index as a second dataset on the same chart
- Legend entry: "{Sport} Card Hall of Fame Index" (see §5 — Naming Convention)

---

## 5. UI Naming Convention (CRITICAL)

These rules are **locked**. No deviations.

| UI Location | Required Text |
|---|---|
| Page header | `{Sport} Card Time Machine - {Sport} Card Hall of Fame Index` |
| Trend line legend | `{Sport} Card Hall of Fame Index` |
| Tooltip on hover | `{Sport} Card Hall of Fame Index` |

**Rules:**

- ALWAYS spell out the full name. **NEVER abbreviate "HOF"** in any user-facing UI element.
- **NO CardLadder (CL) branding** in the UI. Ever. CardLadder is an internal data source only.
- Sport name capitalized as written (Baseball, Basketball, Football, Hockey, Soccer, Pokemon).

**Examples:**

- ✅ `Baseball Card Hall of Fame Index`
- ✅ `Pokemon Card Hall of Fame Index`
- ❌ `Baseball HOF Index`
- ❌ `CL HOF Index`
- ❌ `HOF`

---

## 6. Inducted Cards — Locked Decisions

| Decision | Rule |
|---|---|
| 1/1 cards | **EXCLUDED** from all sport and pokemon HOF indices — no Trout 1/1, no Luka 1/1 |
| Pokemon ultra-rares | **INCLUDED** (Pikachu Illustrator, Magikarp Tamamushi, Kangaskhan Family Event are valid inductees) |
| Babe Ruth card | **1933 Goudey #53** — NOT the 1914 Baltimore News |
| Michael Jordan | **1986 Fleer #57** for the basketball HOF only — no baseball Jordan inductee |
| Single card per person (humans) | For every human athlete, exactly ONE card represents them — the **highest-value card** at the capture-selected grade. Parallels, star cards, and alternate rookies for the same player are not separately inducted. |
| Higher value + higher grade wins | If the same card exists at multiple qualifying grades, the **higher value and higher grade** version is the record. Applies uniformly (example: Pelé — public auction record, higher value + grade). |
| Pokemon dedupe exception | Because Pokemon cards depict characters not people, the **same character may appear multiple times** if each inductee is a **distinct card design** (e.g., Charizard Shadowless 1st Ed vs Charizard Japanese No Rarity vs Charizard Topsun Blue Back). Two copies of the **same design** at different grades are NOT both inductees. |
| Index = HOF (exact match) | Every inducted card contributes to the daily median. The inductee list and the index basket are **identical sets**. No separate "ultra rare excluded" carve-out in the index math. |
| Public auction only | Index math uses **public CardLadder auction data only**. Private sales, dealer trades, and reported record transactions may appear in editorial copy but **do NOT enter `hof_sales` or the daily median**. |
| Low grades valid | PSA 1-5, Authentic, and Raw are valid grade-of-record selections under the capture rules. Low-grade outcomes are not re-rolled. |

These decisions were finalized during the April 2026 capture campaign and are not subject to revision without a new version of this document.

---

## 7. Pokemon HOF Inducted Cards (7)

Authoritative list lives in `/home/user/workspace/qg-build/repos/hofcards/pokemon/members.html` and in the capture dataset at
`cl-dataset/recapture/hof_card_meta.csv` (filter: `sport = pokemon`). 7 inductees total after the April 23, 2026 dedupe — one card per character, highest-value variant wins. Previously 12 inductees (4 Charizard variants + 2 Pikachu variants + 6 singles); reduced to 7 to match the "one card per person" symmetry used across the other 5 sports.

**Current 7 Pokemon inductees:**

| Character | Card | Grade | Record public sale | Date |
|---|---|---|---|---|
| Pikachu | 1998 Pikachu Illustrator (Japanese Promo) | PSA 10 | $16,492,000 | Feb 2026 (Goldin, Logan Paul Break) |
| Charizard | 1999 Base Set Shadowless 1st Edition #4 | PSA 10 | $954,800 | Feb 2026 (Goldin, Logan Paul Break) |
| Kangaskhan | 1998 Japanese Promo Family Event Trophy | PSA 10 | $216,000 | (DB record) |
| Mewtwo | 1999 Base Set Shadowless 1st Edition #10 | PSA 10 | $72,000 | (DB record) |
| Magikarp | 1998 Japanese Promo Tamamushi University #129 | PSA 9 | $30,900 | (DB record) |
| Blastoise | 1999 Base Set Shadowless 1st Edition #2 | PSA 9 | $3,217 | (DB record) |
| Venusaur | 1999 Base Set Shadowless 1st Edition #15 | PSA 9 | $2,175 | (DB record) |

**Cards removed in the April 23, 2026 dedupe (5):**

- 1999 Base Set 1st Edition Unlimited #4 Charizard (broken/duplicate row, no data)
- 1999 Base Set Unlimited #4 Charizard PSA 9 (lesser Charizard variant)
- 1997 Charizard Japanese (`ZSul...`, lesser Charizard variant)
- 1996 Japanese Base Set No Rarity Charizard (lesser Charizard variant)
- 1995 Japanese Topsun Blue Back Charizard (lesser Charizard variant)
- 1998 Trophy Pikachu No. 2 Trainer (lesser Pikachu variant)

> **Notable public sale:** Logan Paul's PSA 10 1998 Pikachu Illustrator sold publicly on Goldin Auctions for $16,492,000 in February 2026, along with his 1st Edition Shadowless Charizard PSA 10 ($954,800). Both are verified public auction sales, in the index basket. (Previous $5.275M 2021 Logan Paul purchase of the Illustrator remains in price history as an earlier sale.)

---

## 8. Capture Rules (Locked)

These rules govern which grade's sales data is used for each HOF card. They are permanent and not adjusted per card.

### Grade Selection

1. Try grades highest-to-lowest: PSA 10 → PSA 9 → PSA 8 → … → Raw
2. **Stop at the first grade** that satisfies BOTH conditions:
   - ≥ 3 lifetime sales on CardLadder
   - Most recent sale on or after the rolling 3-year cutoff (currently **2023-04-20**)
3. If no grade satisfies both conditions: use the grade with the **most lifetime sales overall**

### Volume Cap

- If a grade has **100+ sales**: keep the most recent 50 + oldest 30 = **80 records max**
- Otherwise: use all available sales

### Data Format

| Field | Format |
|---|---|
| Prices | **Cents as integers** (e.g., $1,500.00 → `150000`) |
| Dates | **ISO YYYY-MM-DD** |

### Hard Rules

- **NEVER interpolate** missing dates. Gaps in the series are gaps — do not fill them.
- **NEVER use 1/1 cards** (excluded at the induction level; capture rule is irrelevant for them).

---

## 9. SEO Standards

All 6 HOF sites ship with a full SEO baseline. Each page includes:

- `<title>` tag — unique per page
- `<meta name="description">` — unique per page
- Open Graph tags (`og:title`, `og:description`, `og:url`, `og:image`)
- Twitter Card tags
- JSON-LD structured data (WebPage / ItemList schema as appropriate)
- Canonical URL — root URL for index pages (`https://baseballcardhalloffame.com/`)
- `robots.txt` — per-site
- Apple touch icon
- Google Search Console + Bing Webmaster verification placeholder `<meta>` tags in `<head>` (user to supply IDs; agent pastes + re-deploys per GitHub-first rule)

### Sitemaps

| File | Location |
|---|---|
| Per-site sitemaps (6) | `hofcards/{sport}/sitemap.xml` |
| Per-site robots.txt (6) | `hofcards/{sport}/robots.txt` |
| Global sitemap index | `hofcards/sitemap-index.xml` |

### Audit Baseline

- See `SEO_REPORT.md` for the full audit baseline established during the April 2026 SEO pass.

---

## 10. Time Machine Predictions Cross-Link

- **Color:** Gold `#FFD700`
- **Icon:** 🔮 emoji
- **Case:** UPPERCASE
- **Placement:** Top AND bottom of EVERY HOF page (both index.html and members.html for each sport)
- **Link target:** `https://quantitativegenius.com/meetings-checkout.html`
- **Format example:**

```html
<a href="https://quantitativegenius.com/meetings-checkout.html"
   style="color:#FFD700;">🔮 TIME MACHINE PREDICTIONS</a>
```

This link must be present and functional on all 12 HOF HTML pages (6 index + 6 members).

---

## 11. Cross-Project Documents

| Document | Scope |
|---|---|
| Sports_and_Pokemon_Card_Time_Machine_Methodology_v2.4.md | Full HOF sub-index methodology + capture rules detail; §7.5 HOF overlay chart presentation (single y-axis, no dual-axis); §13 data availability + cross-project parallel to Auto Market Index |
| Auto_Market_Index_Methodology_v2.0.md | Cross-reference only — AMI uses AMD (Manheim) backfill + AMI (Marketcheck) live splice; different solution to the same historical-data-availability problem HOF solves with the 3-card threshold |
| QG-Deployment-Guide v11.1 | Deploy rule applies to HOF; GitHub-first is formalized here; v11.1 adds auto-dashboard reference |
| QG-Security-Reference v1.6 | QG security controls — HOF inherits all; HOF-specific additions in HOF-Security-Reference v1.1 |
| HOF-Security-Reference v1.1 | HOF-specific: CardLadder creds, Resend domain IDs, ImprovMX aliases, NameBright DNS, SSL status |
| Multi-Project-Index-v1.1.md | Top-level index across all three project families (QG · Scoring Systems · HOF); v1.1 adds Thread 33 Auto Market Index v2.0 cross-reference |

---

## 12. Version History

| Version | Date | Notes |
|---|---|---|
| 1.0 | April 20, 2026 | Initial release. Documents 6-site architecture, HOF sub-index design, UI naming convention, capture rules, Pokemon HOF inductees (10), SEO standards, Time Machine Predictions cross-link. |
| 1.1 | April 20, 2026 | Per-sport card counts reconciled to final state after the capture campaign: **Baseball 27, Basketball 17, Football 13, Hockey 15, Soccer 12, Pokemon 12 (total 96)**. Three new locked rules added to §6: single card per person (highest-value card only; humans), Pokemon dedupe exception (unique card-design only), Index = HOF exact match (all inductees contribute; no ultra-rare carve-out), public-only auction data (private/record sales excluded from index math), and low grades (PSA 1-5 / Authentic / Raw) explicitly valid under capture rules. Pokemon site status updated from PENDING to LIVE (DNS verified; nginx + SSL pending VPS deploy of commit 0a34466). References updated to methodology v2.1 and HOF-Security-Reference v1.1. |
| 1.2 | April 23, 2026 | **Pokemon HOF dedupe: 12 → 7 cards.** One card per character rule extended to Pokemon (previously allowed multiple Charizard/Pikachu variants). Highest-value variant wins each character slot. Contaminated card_id `SXgazGqjoHSbiPTOPmlG` (ambiguous "Charizard 1999 PSA 10" with mixed Unlimited + 1st Ed Shadowless sales) retired; its Logan Paul $954,800 Feb 2026 sale reattributed to the clean `EXTERNAL:1999-base-1stEd-shadowless-charizard-4` card_id. Suspect $225K 2020 Pikachu Illustrator price deleted (lower-grade mislabel; only 1 PSA 10 exists). Total HOF cards: 96 → 91. Pokemon count in all other sources (members.html, meta/SEO, JSON-LD schema, HOF_Top_Sales_Consolidated CSV/XLSX, deploy-rules, methodology doc) updated to match. Splice rebalance preserved chart continuity. |
| 1.2 | April 20, 2026 | Fixed stale cross-reference in §4 (Index Calculation) that still pointed to methodology v2.0.md — now correctly points to v2.1.md. No other content changes. |
| 1.3 | April 21, 2026 | Thread 33 cross-reference bump: methodology v2.3 → v2.4 (adds HOF overlay naming lock, §7.5 chart presentation rule, §13 data availability). Added Auto_Market_Index_Methodology_v2.0 as a sibling cross-reference in §11 (“different solution, same historical-data problem”). Deployment guide reference bumped v11.0 → v11.1. No HOF math, capture, or basket changes — still 96 HOF cards, 6 sports, 3-card threshold, base 1000. Explicit reminder: dual-axis charts remain forbidden at the overlay-presentation layer. |
