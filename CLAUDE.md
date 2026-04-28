# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**BG3 Spellbook** is a single-file static web application (`index.html`, ~700 KB) that serves as a reference and planning tool for Baldur's Gate 3 spells. All application code — HTML, CSS (~384 rules), and JavaScript (~135 functions) — lives in that one file. The Python scripts are **offline maintenance tools** only; they are never deployed.

---

## Architecture

### The HTML File

`index.html` is divided into three major zones:

| Zone | Approx line | Content |
|---|---|---|
| `<style>` block | 12 – ~1 389 | All CSS. Starts with CSS tokens/theme (`:root` dark, `.light` overrides). |
| Inline `<script>` blocks (top) | ~1 390 – ~2 040 | Emergency localStorage wipe, export helper functions. |
| `EMBEDDED_DATA` IIFE | ~2 041 – ~467 000 | Self-contained IIFE that holds the entire spell database as a JS literal (`var spells=[…]`) plus `chars`, `charInfo`. Returns `{spells, chars, charInfo}`. This block is what Python scripts patch. |
| Main `<script>` block | ~467 000 – ~710 000 | All runtime JS: state, helpers, chip renderers, multi-select widgets, filter engine, sort, render, modals, party builder, mobile UI. |
| `<body>` HTML | ~53 000 – ~73 500 | Static markup: filter panel, spell table `#spellTable`, all modal overlays, mobile drawers. |

### Key JS Sections (in order, marked with `// ═══…`)

1. **FLAG LOOKUP SETS** – `CONC`, `RITUAL`, `VERBAL` etc. as `Set<string>` for O(1) flag lookup.
2. **EMBEDDED SPELL DATA** – The `EMBEDDED_DATA` IIFE. Never modify this section by hand — use the Python pipeline.
3. **PARTY BUILDER DATA** – `PARTY_CLASSES` map (class → subclasses), `PARTY_RACES` map (race → subraces), `S2C` (subclass→class), `S2R` (subrace→race).
4. **STATE** – All mutable global state: `all` (spell array), `CHARS`, `CHAR_INFO`, `CHC` (char colours), `pinned`, `notes`, filter Sets (`aCls`, `aRac`, `aSrc`, etc.), sort state, dark mode flag.
5. **HELPERS** – Small pure utilities: `hc` (hash→colour), `il` (is-light-colour), `esc`, `notify`, `spellMinLvl`, `charCanHave`, `charPrepLimit`, `bareTokens`, etc.
6. **ICON MAPS** – `classIcons`, `raceIcons`, `schoolIcons` (static CDN URLs). `wikiIconMap` / `wikiIconFb` (spell icons, MD5-path formula). `scrollIconMap`, `itemIconMap`, `featIconMap` (injected by `fetch_chip_icons.py`).
7. **CHIP RENDERERS** – `classChips`, `raceChips`, `featChips`, `scrollChips`, `itemChips` — each takes a raw semicolon/comma-delimited string from a spell's field and returns HTML anchor chips with icons.
8. **MULTI-SELECT WIDGETS** (`initMultiSelects`, `msOpen`, `msTick`, `buildMsWrapDynamic`) – Custom dropdown multi-select used for every filter. `buildFilterDropdowns` populates options from live data.
9. **FILTER** – `doFilter()` iterates `all`, evaluates every active filter Set, calls `render()`.
10. **RENDER** – `render()` builds the table HTML via `spellRow()` + `section()`. `spellRow` produces one `<tr>` per spell, including all chips.
11. **MODALS** – Prepare Spells, Party, Compare, Import, Spell Detail, Print Cards.
12. **MOBILE UI** – Mirrors desktop filters into a slide-out drawer; uses `syncFilter` / `syncSearch`.

### Persistence (localStorage keys)

| Key | Content |
|---|---|
| `bg3p` | JSON array of pinned spell names |
| `bg3n` | JSON object of `{spellName: noteText}` |
| `bg3dark` | `"1"` or `"0"` |
| `bg3charInfo` | `CHAR_INFO` object (character spell-mod / prep-limit overrides) |
| `bg3chars` | `CHARS` array (party member names) |
| `bg3prepared` | `{spellName: {charName: "✅"}}` map |
| `bg3known` | `{charName: {cantrips: string[], spells: string[]}}` — explicitly chosen known spells |
| `bg3removed` | JSON array of spell names the user has hidden |

Spell data is **always taken from the embedded `EMBEDDED_DATA`**. The app explicitly wipes `bg3spells` on load to prevent stale overrides.

### Icon URL Patterns

- **Spell icons** – MD5 formula: `md5(SpellName_Icon.webp)[0] / md5[:2] / SpellName_Icon.webp` on `https://bg3.wiki/w/images/`. Computed by `compute_icons.py` into `wikiIconMap`.
- **Scroll / Item / Feature icons** – Fetched by `fetch_chip_icons.py`, stored in `chip_icons.json`, injected as `scrollIconMap` / `itemIconMap` / `featIconMap` before the `// CHIP RENDERERS` comment.
- **Class / Race / School icons** – Hard-coded CDN URLs in `classIcons`, `raceIcons`, `schoolIcons` near the ICON MAPS section.
- **Fallback** – `siUrl(n)` / `siFallback(img,n)` for spells; `featIco(name)` / `itemIco(name)` use `Special:Filepath` for features/items not in the map.

---

## Python Maintenance Pipeline

All scripts live in `tools/` and data files live in `data/`. No install step needed — stdlib only. Scripts resolve paths relative to the project root automatically (`pathlib` `ROOT = Path(__file__).parent.parent`).

### Typical full-refresh workflow

```
# 1. Verify all spell wiki pages still exist, remove dead ones
python tools/clean_spells.py           # phase 1: writes data/checked_spells.json
python tools/clean_spells.py --apply   # phase 2: removes dead spells

# 2. Fetch wiki data (descriptions, ranges, icons) into data/wiki_data.json
python tools/fetch_wiki.py

# 3. Inject wiki data into the HTML spell array
python tools/inject_wiki.py

# 4. Compute MD5 spell icon URLs → wikiIconMap / wikiIconFb
python tools/compute_icons.py

# 5. Fetch scroll/item/feature icons from wiki pages
python tools/fetch_chip_icons.py  # writes data/chip_icons.json, injects 3 maps into HTML
```

### Adding / updating spells

Edit `data/current_spells.json` (the master spell list), then run:

```
python tools/sync_html.py    # adds spells present in current_spells.json but missing from HTML
python tools/inject_wiki.py  # re-merges wiki_data into the updated array
python tools/compute_icons.py
```

### Rebuilding chip name lists

`data/chip_names.json` lists every unique scroll / item / feature chip value that actually appears in the HTML spell array. Rebuild it by scanning the spell array:

```python
# Features split on ',' — each token is one chip
# Items / Scrolls are semicolon-delimited, with optional '|icon-url' suffix
```

`tools/fetch_chip_icons.py` reads `data/chip_names.json` and writes `data/chip_icons.json` (safe to re-run; skips cached entries).

### Icon extraction notes

`extract_icon()` inside `fetch_chip_icons.py` uses a **largest-thumbnail-wins** strategy: it collects all `/w/images/thumb/…/NNpx-` URLs from the page, de-duplicates by filename (keeping max size), skips a SKIP regex of known UI/chrome icons, and returns the highest-pixel URL. The SKIP regex must be kept up to date — known pitfalls:
- `Race_` must be `(?<![A-Za-z])Race_` to avoid matching `Embrace_Icon`.
- Dye gallery images (`ReapersEmbrace-UncommonDyes.webp`) are blocked by `Dyes\.`.
- Model renders (`_Front_Model`, `_Back_Model`) are blocked by their name patterns.

---

## Project Structure

```
index.html      ← deployable app (single static file)
CLAUDE.md               ← this file
data/
  current_spells.json   ← master spell list (source of truth)
  wiki_data.json        ← cached wiki data per spell
  chip_names.json       ← unique chip values (scrolls/items/features)
  chip_icons.json       ← CDN icon URL cache for chips
  checked_spells.json   ← output of clean_spells.py phase 1
  removed_spells.json   ← archive of removed spells
tools/
  clean_spells.py       ← two-phase wiki-page health check
  fetch_wiki.py         ← scrapes descriptions/ranges/icons from bg3.wiki
  inject_wiki.py        ← injects wiki_data.json into HTML spell array
  compute_icons.py      ← computes MD5 spell icon CDN URLs
  sync_html.py          ← adds new spells from current_spells.json to HTML
  fetch_chip_icons.py   ← fetches scroll/item/feature icons from wiki
  update_spells.py      ← ad-hoc spell database patch script
  transform.py          ← one-time structural transform (historical)
archive/
  fix_*.py              ← one-time bug-fix scripts (no longer needed)
```

## Data Files

| File | Purpose |
|---|---|
| `data/current_spells.json` | **Master spell list** (~490 spells). Source of truth for what goes in the HTML. Edit this to add/remove spells, then run the pipeline. |
| `data/wiki_data.json` | Cached wiki data per spell: `description`, `range`, `area`, `duration`, `recharge`, `icon`. Keyed by spell name. |
| `data/chip_names.json` | Lists all unique scroll / item / feature chip names extracted from the HTML. Rebuilt manually when chip content changes. |
| `data/chip_icons.json` | CDN icon URL cache for scrolls/items/features. Keyed by display name. Empty string = no usable icon found. Safe to delete and re-fetch. |
| `data/checked_spells.json` | Output of `clean_spells.py` phase 1. Maps spell name → `true`/`false` (wiki page exists). |
| `data/removed_spells.json` | Archive of spell objects that were removed from `current_spells.json`. |

---

## Spell Object Schema

Each object in the embedded `spells` array:

```json
{
  "name":        "Fireball",
  "url":         "https://bg3.wiki/wiki/Fireball",
  "school":      "Evocation",
  "level":       "Level 3",
  "classes":     "Sorcerer (Lv 3), Wizard (Lv 3)",
  "races":       "",
  "features":    "Magic Initiate: Wizard, Spell Sniper",
  "items":       "Necklace of Fireball",
  "scrolls":     "Scroll of Fireball",
  "description": "...",
  "range":       "18 m",
  "area":        "6 m radius",
  "duration":    "Instantaneous",
  "recharge":    "",
  "wiki_icon":   "https://bg3.wiki/w/images/…"
}
```

`classes` / `races` / `features` / `items` / `scrolls` are **comma-delimited** strings. Each token becomes one chip rendered by the corresponding chip function. Items and scrolls support an optional `|icon-url` suffix to hard-code an icon.

---

## Filter Logic

`doFilter()` in the FILTER section evaluates these Sets against each spell:

| Set | Field | Logic |
|---|---|---|
| `aLvl` | `level` | OR |
| `aUsg` | derived (cantrip/ritual/concentration/prepared) | AND-within-group, OR-across |
| `aAct` | `action_type` | OR |
| `aSv` | `save` | OR |
| `aFlg` | flags | OR |
| `aSrc` | source (feat/item/scroll) | OR; `scroll` = has `scrolls` field |
| `aDmg` | `damage` | OR |
| `aCond` | `conditions` | OR |
| `aTag` | `tags` | OR |
| `aCls` | `classes` chip tokens | OR |
| `aRac` | `races` chip tokens | OR |
| `aRng` | `range` | OR |
| `aAoe` | `area` | OR |
| `aRch` | `recharge` | OR |
| School pills | `school` | OR |

Text search runs against `name`, `school`, `classes`, `features`, `items`, `scrolls`, and `description`.

---

## Deployment

The app is a **single static file** (`index.html`) with no build step and no server-side dependencies. All external resources are:
- Google Fonts (Cinzel, Crimson Pro) via CDN
- bg3.wiki CDN for icon images (loaded on demand, hidden on error)

To deploy: serve `index.html` from any static host (Netlify, GitHub Pages, Vercel, S3+CloudFront, etc.). No environment variables, no backend.
