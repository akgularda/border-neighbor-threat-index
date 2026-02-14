---
description: BNTI Phase 1 implementation workflow — Bloomberg-style architecture restructuring
---

# BNTI Phase 1: Bloomberg Terminal Overhaul

## Prerequisites
- Working directory: `border-neighbor-threat-index-main/`
- Current `index.html` contains all CSS, JS, SVG inline (~1302 lines)
- Python engine: `borderneighboursthreatindex.py`

---

## Step 1: Create Directory Structure
// turbo
```bash
mkdir -p css js data
```

## Step 2: Extract CSS to Separate Files

### 2a: `css/variables.css`
Extract CSS custom properties (`:root` block, lines 11-28) and restyle with Bloomberg palette:
- Background: `#000000`
- Panel bg: `#0a0a0a` / `#111111`
- Accent: `#FF6600` (Bloomberg orange)
- Borders: `#1a1a1a` with accent highlights
- Text: `#e0e0e0` primary, `#888888` secondary

### 2b: `css/layout.css`
Extract grid system, topbar, responsive breakpoints (lines 30-60, 173-181, 561-604)

### 2c: `css/components.css`
Extract panel, card, badge, map, feed, chart styles (lines 183-560). Restyle for Bloomberg aesthetic:
- Remove rounded corners on data panels
- Add colored top-border accents (orange/cyan)
- Dense data layout
- Monospaced data values

## Step 3: Extract JavaScript to Separate Files

### 3a: `js/core.js`
- Data loading and parsing functions
- State management (`data` variable)
- `renderAll()` orchestrator
- `startDataPoller()` — keep 60s poll interval
- Helper utilities (date formatting, status classes)

### 3b: `js/map.js`
- `updateMap()` function
- SVG polygon loading from `data/map-paths.json`
- Country hover/click handlers
- Map overlay stats

### 3c: `js/charts.js`
- `initChart()` function
- Chart.js configuration
- Trend chart rendering

### 3d: `js/stream.js`
- `updateFeed()` function
- Intelligence stream item rendering
- Source badge display

## Step 4: Extract SVG Map Data

Convert inline SVG polygon points from `index.html` (lines 660-800+) into `data/map-paths.json`:
```json
{
  "viewBox": "0 0 800 500",
  "countries": {
    "Syria": { "polygons": [["302.3,315.6 302.7,314.8 ..."]] },
    "Georgia": { "polygons": [["400.9,85.6 400.0,80.0 ..."]] },
    "Turkey": { "polygons": [["433.0,116.5 ..."], ["170.5,95.9 ..."], ...] },
    "Armenia": { "polygons": [["459.6,112.1 ..."], ["468.3,128.5 ..."]] },
    "Greece": { "polygons": [["50.5,122.6 ..."], ...] },
    "Iran": { "polygons": [["..."]] },
    "Iraq": { "polygons": [["..."]] },
    "Bulgaria": { "polygons": [["..."]] }
  }
}
```
Note: Greece has many island polygons, Turkey has multiple landmasses.

## Step 5: Rebuild `index.html`

Clean HTML-only file that:
- Links to `css/variables.css`, `css/layout.css`, `css/components.css`
- Links to `assets/chart.umd.min.js`
- Links to `js/core.js`, `js/map.js`, `js/charts.js`, `js/stream.js`
- Contains only HTML structure (no inline CSS or JS)
- SVG map container is empty (populated dynamically by `js/map.js`)
- Update subtitle text to "updated every 30 minutes"

## Step 6: Update RSS Sources in Python

In `borderneighboursthreatindex.py`:
- Add wire service feeds (Reuters, AP regional RSS)
- Replace biased mirror queries with neutral ones
- Keep per-country article normalization

## Step 7: Update Dashboard Text

- Change "updated hourly" to "updated every 30 minutes"
- Ensure poller displays correct next-update time (30 min from last)

## Step 8: Verify

// turbo
```bash
python -c "import json; d=json.load(open('data/map-paths.json')); print(f'Countries: {len(d[\"countries\"])}')"
```

Open `index.html` in browser and verify:
- All panels render correctly
- Map loads from JSON data
- Chart displays
- Feed populates
- Bloomberg styling applied
- No console errors

---

## File Change Summary

| File | Action |
|---|---|
| `css/variables.css` | **NEW** — Design tokens, Bloomberg palette |
| `css/layout.css` | **NEW** — Grid, responsive breakpoints |
| `css/components.css` | **NEW** — All component styles |
| `js/core.js` | **NEW** — Data loading, poller, state |
| `js/map.js` | **NEW** — SVG map rendering |
| `js/charts.js` | **NEW** — Chart.js configuration |
| `js/stream.js` | **NEW** — Intelligence feed |
| `data/map-paths.json` | **NEW** — Extracted SVG coordinates |
| `index.html` | **MODIFY** — Strip to HTML only, link externals |
| `borderneighboursthreatindex.py` | **MODIFY** — RSS sources, mirror queries |
