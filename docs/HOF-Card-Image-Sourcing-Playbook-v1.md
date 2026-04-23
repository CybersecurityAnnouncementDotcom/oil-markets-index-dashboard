# HOF Card Image Sourcing Playbook — v1.0

| Field | Value |
|---|---|
| **Version** | 1.0 |
| **Created** | April 23, 2026 |
| **Scope** | All 6 HOF sites (baseball, basketball, football, hockey, soccer, pokemon) — fronts AND backs |
| **Companion doc** | `HOF-Card-Image-Spec-v1.md` (cropping / encoding / filename spec) |
| **Owner** | jq_007@yahoo.com |

**Purpose:** This is the operational playbook for collecting, verifying, staging, and shipping the front + back images for every card across all 6 HOF sites. The companion **Image Spec** (`HOF-Card-Image-Spec-v1.md`) defines the WHAT (technical format). This Playbook defines the HOW (workflow, storage, verification, tracking).

---

## 1. Cardinal rule — "Same card, same source"

> *"For the pictures be extra careful and sure you are getting the same front and back from the same cards."* — user, 2026-04-23

**The single rule that drives everything in this doc: front and back of a given card MUST come from the same physical specimen, captured on the same source page.**

Why this matters:
- A "matching" back from a different copy can be a different print run, different shadowless/unlimited variant, different regional printing (OPC vs Topps vs Japanese), or a reprint.
- Auction listings typically show BOTH sides of the exact graded copy being sold → that's the gold-standard source.
- Mixing fronts and backs from different copies is the failure mode this playbook exists to prevent.

**Operational test before shipping any pair:**
1. I can point at ONE source URL that shows BOTH sides of the SAME graded copy.
2. The grade shown on the slab / flip label matches what the HOF site says.
3. The year / set / variant / parallel markers on the back match the front's variant (Shadowless vs Unlimited vs 1st Edition, OPC vs Topps, etc.).

If any of those three fail → do not ship the pair. Either find a better source or leave the card front-only (the flip UI gracefully hides the Flip button when `data-back` is absent — see Image Spec §4).

---

## 2. Storage layout (on disk)

All sourced images + provenance live under a single tree:

```
/home/user/workspace/hof_images/
  <sport>/                           # baseball | basketball | football | hockey | soccer | pokemon
    <card_id>/                       # stable slug from the filename in hofcards/<sport>/assets/cards/
      front.jpg                      # raw source download (uncropped) — archival copy
      back.jpg                       # raw source download (uncropped) — archival copy
      front_processed.jpg            # cropped per Image Spec §1-2, ready to ship
      back_processed.jpg             # cropped per Image Spec §1-2, ready to ship
      source.txt                     # provenance metadata (see §2.1)
      source_screenshot.png          # full-page screenshot of the source listing (evidence)
      notes.md                       # optional — edge cases, variant notes, reject reasons
```

`<card_id>` = the current filename stem used in the live site's `assets/cards/` folder.
Example: `Mickey_Mantle_1952.jpg` → `<card_id>` = `Mickey_Mantle_1952`
Example: `pikachu_illustrator_1998.jpg` → `<card_id>` = `pikachu_illustrator_1998`

This way every card's working directory name matches the file stem already wired into the site's HTML.

### 2.1 `source.txt` format (required for every card directory)

Plain-text, one key per line:

```
card_id:        pikachu_illustrator_1998
sport:          pokemon
player_subject: Pikachu
year:           1998
set:            CoroCoro Illustration Contest (Trophy)
variant:        Illustrator
grade:          PSA 10
grader:         PSA
cert_number:    28093247                # if visible on source
source_url:     https://www.goldin.co/item/1998-pokemon-trophy-illustrator-pikachu-psa-10-<id>
source_type:    auction_archive          # auction_archive | psa_cardfacts | tcdb | publisher | bulbapedia | other
captured_date:  2026-04-23
captured_by:    computer-agent
front_present:  yes
back_present:   yes
license_note:   Public auction listing; used here as reference imagery with attribution.
same_copy_verified: yes                  # yes | no — §1 check
notes:          Flip label on back matches PSA cert # on front slab.
```

If `back_present: no`, we ship front-only (Image Spec §4) and the card stays on the back-pending list.

### 2.2 Why raw + processed

- **Raw** = untouched download. If our crop / rotation was wrong, we re-do from raw without going back to the web. Protects against source pages going dead (auction archives rotate).
- **Processed** = ready to ship into `hofcards/<sport>/assets/cards/` per the filename convention in Image Spec §3.

### 2.3 Is `hof_images/` committed to git?

**No.** Too many raw screenshots + untouched high-res scans would balloon the repo. Processed final files are what get committed (to `hofcards/<sport>/assets/cards/`). The raw staging tree lives only in the workspace + any backups you choose to make.

If you want a GitHub-backed archive of the raw sources, we can create a `hofcards-assets` private repo later — not in scope for v1.

---

## 3. Preferred sources (ranked)

From the Image Spec §5, with operational notes added:

| Rank | Source | Typical URL pattern | When it wins | Gotchas |
|---|---|---|---|---|
| 1 | **PSA CardFacts** | `psacard.com/cardfacts/...` | Vintage / mainstream US issues. Official back scans by manufacturer. | No grade; show the card type, not a specific copy. Use ONLY when §1 same-copy rule is already satisfied by another source OR when the back is invariant across all copies of that card (most pre-1980 issues). |
| 2 | **Auction archives — Heritage** | `ha.com/.../lot/...` | Vintage baseball, mid-century football + hockey. Usually both sides on the lot page. | Some lots only show the front in the thumbnail but both sides in the detail gallery — expand the gallery before deciding there's no back. |
| 3 | **Auction archives — Goldin** | `goldin.co/item/...` | Modern sports, Pokemon trophy cards, ultra-high-end. | Same-page front+back is standard for graded items. Pokemon Illustrator, Charizard, Magikarp Tamamushi are all archived here. |
| 4 | **Auction archives — PWCC** | `pwccmarketplace.com/items/...` | Modern baseball / basketball / football. | Listings expire; grab the screenshot when you grab the image. |
| 5 | **TCDb** | `tcdb.com/Person.cfm?...` / `tcdb.com/ViewCard.cfm?...` | Modern issues not covered by the auction houses; international issues. | User-contributed; quality is variable. Cross-reference against a second source if possible. |
| 6 | **Publisher galleries** | `topps.com`, `panini.com`, `upperdeck.com`, `pokemon.com/tcg/...` | Modern licensed issues, currently-in-production sets. | Marketing shots often have weird lighting / drop shadows → more crop work. |
| 7 | **Bulbapedia** (Pokemon only) | `bulbapedia.bulbagarden.net/wiki/...` | Japanese exclusives, promos, tournament cards without auction history. | Fan-sourced; verify the scan matches the variant we want (back design differs between Japanese and WOTC English printings). |

**Hard "never use" list:**
- Social media posts (Twitter/X, Reddit threads without linked auction) — unverifiable.
- eBay Buy-It-Now / active listings — listings disappear; images may be stolen.
- Third-party reprint sellers / "reverse mockups" / custom art renderings.
- Any image showing an intact slab, watermark, price tag, or authentication overlay that can't be cropped away cleanly (Image Spec §1).

---

## 4. Sourcing workflow — card by card

For each card we process one at a time (the user has explicitly asked for this pace for Pokemon; same pattern applies to all sports):

### Step 1 — Set the target
Record in `source.txt` (template §2.1): card_id, sport, player/subject, year, set, variant, grade the site currently displays, graded by.

### Step 2 — Propose source candidates
Computer-agent searches (in priority order from §3) and returns 2–3 candidate URLs with thumbnails. **Do NOT download yet.** User approves the winning source.

### Step 3 — Verify "same copy" (Cardinal Rule §1)
Before any download:
- ✅ One URL shows both sides
- ✅ Grade on slab / flip matches (or the source has a clearly-labeled matching graded copy)
- ✅ Variant matches (Shadowless/Unlimited/1st Ed/OPC/Japanese base etc.)

If any check fails → go back to Step 2 with a different candidate.

### Step 4 — Download raw
Save highest-resolution image(s) available from the approved source to:
- `hof_images/<sport>/<card_id>/front.jpg`
- `hof_images/<sport>/<card_id>/back.jpg`

Take a full-page screenshot of the source page → `source_screenshot.png`. This is our evidence if the source ever goes dead.

### Step 5 — Crop & process (per Image Spec §1-2)
- Tight crop to printed card edges
- Rotate to square
- No slab / background / watermark
- JPG q85, long-edge 1000–1400 px, natural aspect ratio preserved
- Save:
  - `front_processed.jpg`
  - `back_processed.jpg`

### Step 6 — Write `source.txt` (fully — every field in §2.1)

### Step 7 — Preview in isolation
Open `front_processed.jpg` and `back_processed.jpg` side by side locally. Sanity check:
- Same card (same centering pattern, same print defects, same grade visible on archived raw)
- Back's set / year markers match front's set / year
- No crop artifacts

### Step 8 — Ship
1. Copy `front_processed.jpg` → `hofcards/<sport>/assets/cards/<card_id>.jpg` (overwriting existing front only if it's actually better — else skip this part and only add the back).
2. Copy `back_processed.jpg` → `hofcards/<sport>/assets/cards/<card_id>_back.jpg`.
3. Run `python3 /home/user/workspace/banner-work/apply_card_flip.py` — wires `data-back="assets/cards/<card_id>_back.jpg"` onto the matching button in `members.html`.
4. `git add -A && git commit -m "<sport>: add back for <card_id> (source: <source_type>)" && git push origin master`
5. Deploy to VPS per `sport_card_deploy_rules.md` Steps 1-8 — **NEVER bypass deploy-guard / deploy-done**.

### Step 9 — Acceptance test (per Image Spec §7)
On an iPhone-width viewport (≤480 px):
- Tap card → lightbox opens
- Tap card image or "Flip" → rotates 180° to back
- Back fills same card-shaped area
- No slab / background / watermark visible
- Tap again → smooth reverse

If any step fails → re-crop from raw (don't re-download), redeploy.

### Step 10 — Mark tracker complete
Update `hof_images/tracker.csv` (see §6) with `status: shipped` + commit SHA.

---

## 5. Current inventory (as of 2026-04-23)

Source of truth: `ls /home/user/workspace/qg-build/repos/hofcards/<sport>/assets/cards/`

| Sport | Cards in basket (DB) | Fronts on disk | Backs on disk | Pending work |
|---|---|---|---|---|
| Baseball | 27 | 27 | 0 | 27 backs |
| Basketball | ~30 | 17 | 0 | 13 new fronts + 30 backs |
| Football | ~30 | 14 | 0 | 16 new fronts + 30 backs |
| Hockey | ~30 | 15 | 0 | 15 new fronts + 30 backs |
| Soccer | ~30 | 12 | 0 | 18 new fronts + 30 backs |
| **Pokemon** | **7** | **12** | **1** | **Cleanup 5 orphans + 6 backs** (see §5.1) |

> The DB-basket counts come from `sport_card_deploy_rules.md` §C (per-sport baseline). Some sports' `assets/cards/` folders are behind the DB — fronts still need to be sourced first before their backs. That's in scope for this playbook: fronts AND backs, same rules.

### 5.1 Pokemon-specific — orphan cleanup

After the 2026-04-23 Pokemon dedupe (12 → 7), there are 12 front images in `hofcards/pokemon/assets/cards/` but only 7 cards in the live basket. The 5 orphans:

Currently on disk:
```
blastoise_1999_base_shadowless_1st_ed.jpg
charizard_1995_japanese_topsun_blue_back.jpg    <-- orphan (not in final 7)
charizard_1996_japanese_no_rarity.jpg           <-- orphan
charizard_1999_base_1st_ed_unlimited.jpg        <-- orphan (dedupe chose Shadowless #4)
charizard_1999_base_shadowless_1st_ed.jpg       ✓ live — this is the $954,800 Shadowless
charizard_1999_base_unlimited_psa9.jpg          <-- orphan
kangaskhan_1998_japanese_family_event_trophy.jpg
magikarp_1998_japanese_tamamushi_promo.jpg
mewtwo_1999_base_shadowless_1st_ed.jpg
pikachu_illustrator_1998.jpg
trophy_pikachu_no2_trainer_1998.jpg             <-- orphan
venusaur_1999_base_shadowless_1st_ed.jpg
```

Final 7 (live in DB per Wake-Up §7):
1. `pikachu_illustrator_1998.jpg` — Pikachu Illustrator PSA 10 — $16.49M
2. `charizard_1999_base_shadowless_1st_ed.jpg` — Charizard Shadowless 1st Ed #4 PSA 10 — $954,800
3. `kangaskhan_1998_japanese_family_event_trophy.jpg` — Kangaskhan Family Event PSA 10 — $216K
4. `mewtwo_1999_base_shadowless_1st_ed.jpg` — Mewtwo Shadowless 1st Ed PSA 10 — $72K
5. `magikarp_1998_japanese_tamamushi_promo.jpg` — Magikarp Tamamushi PSA 9 — $30,900
6. `blastoise_1999_base_shadowless_1st_ed.jpg` — Blastoise Shadowless 1st Ed PSA 9 — $3,217
7. `venusaur_1999_base_shadowless_1st_ed.jpg` — Venusaur Shadowless 1st Ed PSA 9 — $2,175

**Cleanup pass (before we start backs for Pokemon):**
1. Move the 5 orphans to `hof_images/pokemon/_orphans/` (don't delete — archival).
2. Verify `members.html` only references the 7 live card filenames.
3. Commit the orphan removal from `hofcards/pokemon/assets/cards/` separately from any back-sourcing work.

---

## 6. Tracking — `hof_images/tracker.csv`

A single CSV at `/home/user/workspace/hof_images/tracker.csv` tracks the status of every card across all 6 sports. Rebuild it any time from the filesystem; it's the dashboard, not the source of truth.

Columns:

```csv
sport,card_id,player_subject,year,variant,grade,front_status,back_status,source_type,source_url,same_copy_verified,captured_date,committed_sha,shipped_to_vps,notes
```

**Status values:**
- `front_status`: `missing` / `staged_raw` / `staged_processed` / `shipped`
- `back_status`: same set
- `same_copy_verified`: `yes` / `no` / `n/a` (n/a when front & back come from separate sources that both pass the back-authenticity rule in Image Spec §4, e.g. PSA CardFacts for invariant pre-1980 backs)
- `shipped_to_vps`: `yes` / `no` — whether the current version is live on VPS

Update the tracker at Step 1 (add the row), Step 4 (status → staged_raw), Step 5 (→ staged_processed), Step 8 (→ shipped + SHA), Step 9 (→ shipped_to_vps: yes).

---

## 7. Back-image authenticity — variant matrix

Backs are the trap. Same front design, different era's back.

### 7.1 Common traps

| Front | Correct back identifier |
|---|---|
| 1952 Topps Mantle | Pink/red team diagram, write-in stat lines, "Topps Base Ball" banner, card # 311 |
| 1909 T206 Honus Wagner | Cigarette advertiser (Sweet Caporal / Piedmont / etc.) — specify brand. NEVER use a T207 (1912) brown border back. |
| 1986-87 Fleer Jordan #57 | Fleer logo, blue + yellow, career stats at Chapel Hill |
| 1979-80 O-Pee-Chee Gretzky | OPC French-English bilingual, team logo top-right. NOT Topps (different photo, English-only). |
| 1999 Pokemon Base Charizard Shadowless | Subtle — shadow is missing on the front art box; back still has the blue Pokémon pattern with "© 1995, 96, 98, 99 Nintendo, Creatures, GAMEFREAK." Must match the same 4-date copyright. |
| 1999 Pokemon Base Charizard 1st Ed vs Unlimited | Front differs (1st Ed stamp); **back is identical** between these two variants. Same-copy rule still requires pairing the correct front → correct back of the same SLAB. |
| 1998 Pokemon Japanese Trophy (Illustrator, Tamamushi, Family Event) | Back is a distinct trophy-card back — NOT the standard blue Pokémon pattern. Often has "トレーナーズマガジン" or tournament imprint. Verify via Bulbapedia + Goldin archive. |
| 2013 Bowman Chrome Trout (any refractor parallel) | Front changes (refractor, gold, superfractor 1/1), back is the same. Match the slab. |

### 7.2 When to skip the back

If the back cannot be authenticated with high confidence → ship front-only. The flip UI hides the Flip button when `data-back` is absent. That's a feature, not a regression.

Never ship:
- A generic "same-era" back from a different card
- A reverse render / reproduction
- A placeholder

---

## 8. Licensing / attribution

This is a public-facing index site. We're using auction-archive and publisher imagery as reference, not reselling.

**Safe posture:**
- Use public listings and public card-database scans.
- No watermarks (Image Spec §1).
- Each card's `source.txt` names the origin; if challenged, we point to `source_screenshot.png`.
- Do not misrepresent our crop as auction-house branding.

**Explicit don'ts:**
- Do not expose auction house logos / price stamps / grading-service watermarks in the shipped image.
- Do not claim ownership of the card image — it's reference material.
- Do not use scans from subscription-gated archives (CardLadder graded-sales galleries, for example — we subscribe to CardLadder for pricing data but should not re-publish their thumbnails; use PSA / auction archives instead).

---

## 9. What the agent does vs. what the user does

### Agent does (unattended)
- Search for candidate sources
- Download raw front + back from approved URLs
- Crop, rotate, encode per Image Spec
- Write `source.txt`
- Run `apply_card_flip.py`
- Commit + push to GitHub
- SCP to VPS through deploy-guard / deploy-done
- Update tracker CSV

### User approves (one at a time, for each card)
- Step 2 → Step 3 handoff: "Use source candidate #1" / "Try a different source"
- Step 7 → Step 8 handoff: "Ship it" / "Re-crop — centering looks off"

This is explicitly the pace the user asked for:
> *"be extra careful and sure you are getting the same front and back from the same cards"* (2026-04-23)
> *"save all the fronts and backs from the same sources together somewhere in your files"* (2026-04-23)

### Hard "ask before doing" gates (from `sport_card_deploy_rules.md` + Wake-Up §12)
- Any `git reset --hard`, `sed`, `python3 -c` on VPS → NEVER (forbidden)
- Any deploy without deploy-guard / deploy-done → NEVER
- Shipping a back the user hasn't approved → NEVER

---

## 10. Session startup checklist (for any new thread that resumes image sourcing)

Run these in the new thread's first few commands:

```bash
# 1. Confirm the playbook version
ls /home/user/workspace/qg-deploy/docs/HOF-Card-Image-Sourcing-Playbook-v*.md | sort | tail -1

# 2. Check what's already done
cat /home/user/workspace/hof_images/tracker.csv 2>/dev/null | head -5

# 3. Check current front inventory per sport
for sport in baseball basketball football hockey soccer pokemon; do
  n=$(ls /home/user/workspace/qg-build/repos/hofcards/$sport/assets/cards/*.jpg 2>/dev/null | wc -l)
  b=$(ls /home/user/workspace/qg-build/repos/hofcards/$sport/assets/cards/*_back.jpg 2>/dev/null | wc -l)
  echo "$sport: $n total, $b backs"
done

# 4. Pick the next card: first row where back_status=missing, sorted by sport priority
#    (user's stated order to date: pokemon first, then whatever order the user calls out)
```

---

## 11. Order of operations

The user has named Pokemon as the first batch. Suggested order after Pokemon:

1. **Pokemon** (7 cards, 6 backs pending + 1 already present) — active now
2. **Baseball** (27 cards, 27 backs pending) — vintage-heavy, great auction coverage
3. **Basketball** (missing fronts + backs) — modern era, PWCC / Goldin
4. **Football** (missing fronts + backs)
5. **Hockey** (missing fronts + backs)
6. **Soccer** (missing fronts + backs) — hardest, smallest US auction footprint

Order is a suggestion — user may reprioritize any time.

---

## 12. Version history

- **v1.0 — 2026-04-23** (this doc) — Initial playbook. Captures Cardinal Rule (same-copy sourcing), storage layout, workflow, inventory snapshot, tracker spec, variant matrix, attribution posture.

Future bumps per user rule: bump version + filename on any material change. Keep old versions in `docs/` as historical.

---

## Related docs

- `HOF-Card-Image-Spec-v1.md` — cropping, filename, encoding standards
- `HOF-Master-Reference-v1.4.md` (or later) — overall HOF architecture
- `sport_card_deploy_rules.md` — deploy sequence (deploy-guard / deploy-done)
- `QG-Parking-Lot.md` — lessons-learned log; add image-sourcing incidents here as they arise

---

*End of HOF-Card-Image-Sourcing-Playbook-v1.md*
