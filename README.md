<div align="center">
  <img src="docs/logo.png" alt="BNTI — Border-Neighbor Threat Index logo" width="140"/>
  <!-- CODEX: generate a clean, corporate product logo for "BNTI — Border-Neighbor Threat Index": a minimalist heraldic/cartographic mark (e.g. a stylized border arc or shield over a map graticule) in deep navy (#0b1f3a) and signal-amber, transparent background, square, suitable as a 140px avatar. -->

  # Border-Neighbor Threat Index
  ### Multilingual geopolitical threat intelligence for Türkiye's border neighbors

  <!-- badge row: keep these literal, they render fine -->
  ![status](https://img.shields.io/badge/status-active-brightgreen)
  ![division](https://img.shields.io/badge/Strategic%20Data%20Company%20of%20Ankara-0b1f3a)
  ![Monarch Castle](https://img.shields.io/badge/Monarch%20Castle-Holdings-1f6feb)
  ![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
  ![Model](https://img.shields.io/badge/LLM-openrouter%2Ffree-orange)
  ![license](https://img.shields.io/badge/license-Apache%202.0-lightgrey)

  **[Live dashboard](https://sdcofa.github.io/border-neighbor-threat-index/)** · **[Whitepaper](methodology.pdf)** · **[Deployment guide](DEPLOYMENT_GUIDE.md)**
</div>

> **Executive summary** — BNTI is an automated geopolitical monitoring platform that converts multilingual regional news from Türkiye's seven border neighbors into a normalized, repeatable threat signal. It ingests open-source RSS/Atom reporting, uses a large language model to attribute each headline to a country and a canonical threat category, then maps those categories onto fixed deterministic weights to produce per-country scores and a composite national index. It is built for analysts, desk officers, and decision-makers who need a defensible, continuously refreshed read on the regional threat environment rather than an unstructured news feed.

## ✨ Highlights
- **Seven-country coverage** — continuous monitoring of Armenia, Georgia, Greece, Iran, Iraq, Syria, and Bulgaria against Türkiye's border environment.
- **LLM-assisted attribution** — candidate headlines are batched through `openrouter/free`, which selects the final border-country attribution and the canonical threat label for each item.
- **Deterministic, repeatable scoring** — LLM-selected categories map to fixed weights, so the same inputs always yield the same score; the model classifies, the math is auditable.
- **Calibrated 1–10 index with operational tiers** — per-country and composite scores resolve into `STABLE`, `ELEVATED`, and `CRITICAL` thresholds.
- **Strict no-publish gating** — a run that cannot meet minimum signal volume and country-coverage criteria is rejected, leaving the last validated snapshot live rather than shipping a degraded one.
- **Fully automated operations** — a GitHub Actions workflow refreshes the intelligence picture every two hours and redeploys the public dashboard with zero manual intervention.
- **Multilingual ingestion** — native-language sources (Armenian, Georgian, Greek, Persian, Arabic, Bulgarian) are normalized and translated for summary briefings.

## 🖼️ Preview
<!-- CODEX: drop product screenshots into docs/ -->
![BNTI — main dashboard view](docs/screenshot-1.png)
<!-- CODEX: capture the live dashboard at https://sdcofa.github.io/border-neighbor-threat-index/ — the main view showing the composite Türkiye index gauge, the regional map with per-country threat shading, and the status banner. 1600px wide. -->

![BNTI — country detail and threat stream](docs/screenshot-2.png)
<!-- CODEX: capture a detail view — the live threat stream of attributed headlines plus the per-country score breakdown and history/forecast charts. 1600px wide. -->

## 🧭 What it does
BNTI turns the noise of regional reporting into a structured, decision-grade signal and presents it as a continuously updated public dashboard.

### Ingestion
The analyzer pulls headlines from a curated set of RSS/Atom feeds spanning each neighboring country — a mix of English-language outlets, international wire services, and native-language sources. Items are time-filtered to a recent window and deduplicated by source link.

### Attribution & classification
Candidate headlines are batched and submitted to `openrouter/free` over the OpenRouter API. The model performs two jobs per item: it chooses the final **border-country attribution** and assigns a **canonical threat category** from a fixed taxonomy (military conflict, terrorism, border security, political instability, humanitarian crisis, diplomatic tensions, trade agreement, or neutral). Primary/backup API-key failover keeps the pipeline resilient.

### Scoring
Each selected category carries a fixed weight (for example `military_conflict = 8.0`, `terrorism = 7.0`, `trade_agreement = -2.0`). Per-country scores are computed on a 1–10 scale via a saturating transform, and the composite Türkiye index is a strategic-importance-weighted average of the per-country scores. Scores resolve into operational tiers:

| Tier | Range |
|---|---|
| `STABLE` | 1.0 – 4.0 |
| `ELEVATED` | 4.0 – 7.0 |
| `CRITICAL` | 7.0 – 10.0 |

### Publish gating
Before anything goes live, a run must clear minimum thresholds for total signals, active countries, and coverage ratios. If it cannot validate, the live files are left untouched — BNTI prefers a stale-but-trustworthy snapshot over a published-but-thin one.

### Presentation
The static dashboard renders the composite index, a regional map, a live attributed-headline stream, and history/forecast charts, all driven by the generated data files.

## 🗂️ Data & provenance
Per Monarch Castle doctrine — **evidence before assertion**. BNTI is built exclusively on open, lawfully accessible sources (public RSS/Atom feeds), with no scraping behind authentication.

- **Sources** — curated public news feeds for each of the seven border countries, including native-language and international wire outlets.
- **Provenance carried per signal** — every attributed event retains its original title, translated title, **source link (source URL)**, **publication timestamp**, attributed country, and chosen threat category, so any score is traceable back to the headlines that produced it.
- **Outputs** — `bnti_data.json` and `bnti_data.js` hold the latest dashboard dataset (including the methodology block, weights, scale, and thresholds), and `bnti_history.csv` preserves the per-country and composite time series for trend and forecast views.
- **Reproducibility** — because classification is the only non-deterministic step and all weighting is fixed and published in the data file, the path from source headline to final score is auditable end to end.

## 🛠️ Tech stack
- **Intelligence engine (Python 3.11)** — `feedparser`, `pandas`, `numpy`, `python-dateutil`, `requests`, `googletrans`.
- **LLM layer** — OpenRouter (`openrouter/free`) for country re-attribution and canonical threat labeling, with primary/backup key failover.
- **Dashboard (front end)** — HTML, CSS, and vanilla JavaScript (`js/core.js`, `js/map.js`, `js/stream.js`, `js/charts.js`) with Chart.js for visualization.
- **Automation** — GitHub Actions (`.github/workflows/bnti_update.yml`), cron-scheduled every two hours plus manual `workflow_dispatch`.
- **Hosting** — GitHub Pages (static deploy).
- **Methodology** — LaTeX source (`methodology.tex`) compiled to `methodology.pdf`.

### Repository layout
| Path | Purpose |
|---|---|
| `borderneighboursthreatindex.py` | The BNTI analyzer — ingestion, LLM attribution, scoring, gating, and data generation |
| `index.html` | Dashboard entry point |
| `js/` | Dashboard logic (core engine, map, threat stream, charts) |
| `css/` | Visual system and component styling |
| `bnti_data.json` / `bnti_data.js` | Latest intelligence dataset consumed by the dashboard |
| `bnti_history.csv` | Per-country and composite score history |
| `.github/workflows/bnti_update.yml` | 2-hour intelligence update and GitHub Pages deployment |
| `methodology.tex` / `methodology.pdf` | Whitepaper — methodology and scoring design |
| `BNTIndex.pdf` | Project report artifact |
| `DEPLOYMENT_GUIDE.md` | Step-by-step zero-cost deployment guide |
| `requirements.txt` | Python dependencies |

## 🚀 Getting started
**Use the live product:** [https://sdcofa.github.io/border-neighbor-threat-index/](https://sdcofa.github.io/border-neighbor-threat-index/)

**Run the analyzer locally:**
```bash
git clone https://github.com/SDCofA/border-neighbor-threat-index.git
cd border-neighbor-threat-index
pip install -r requirements.txt

# Provide an OpenRouter API key (a free model route is used by default)
export OPENROUTER_API_KEY="sk-or-..."
export OPENROUTER_MODEL="openrouter/free"   # optional, this is the default

python borderneighboursthreatindex.py
```
The run regenerates `bnti_data.json`, `bnti_data.js`, and `bnti_history.csv` in place. Open `index.html` to preview the dashboard against the freshly generated data.

**Automated deployment:** the `BNTI Intelligence Update` workflow runs every two hours, executes the analyzer (with `OPENROUTER_API_KEY` / `OPENROUTER_API_KEY_BACKUP` provided as repository secrets), commits any updated data files, and redeploys to GitHub Pages. It can also be triggered manually, including a deploy-only mode. See **[`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md)** for the full zero-cost setup.

## 🧱 Part of Monarch Castle
> A product of **Strategic Data Company of Ankara** — an operating company of **[Monarch Castle Holdings](https://github.com/MonarchCastleHoldings)**.
> Sister companies: [Monarch Castle Technologies](https://github.com/monarchcastletech) · [Strategic Data Company of Ankara](https://github.com/SDCofA)

## 📜 License
Licensed under Apache License 2.0. See [`LICENSE`](LICENSE) for details. © 2026 Monarch Castle Holdings · Ankara, Türkiye.

### Citation
```bibtex
@software{bnti2026,
  author = {Akgul, Arda},
  title  = {Border Neighbor Threat Index: Multilingual Geopolitical Risk Assessment},
  year   = {2026},
  url    = {https://github.com/SDCofA/border-neighbor-threat-index}
}
```

<div align="center"><sub>🏰 Monarch Castle Holdings — turning open-source noise into lawful, verified, decision-grade intelligence.</sub></div>
