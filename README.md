<p align="center">
  <img src="logo.png" alt="Monarch Castle Technologies logo" width="180" />
</p>

<h1 align="center">Border Neighbor Threat Index (BNTI)</h1>

<p align="center"><strong>Monarch Castle Technologies | Defense Intelligence.</strong></p>

<p align="center">
  <a href="https://akgularda.github.io/border-neighbor-threat-index/">Live Dashboard</a>
  |
  <a href="methodology.pdf">Whitepaper</a>
  |
  <a href="DEPLOYMENT_GUIDE.md">Deployment Guide</a>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/Apache-2.0"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg" alt="License: Apache-2.0" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.11%2B-blue.svg" alt="Python 3.11+" /></a>
  <a href="https://openrouter.ai/"><img src="https://img.shields.io/badge/Model-openrouter%2Ffree-orange.svg" alt="Model: openrouter/free" /></a>
</p>

## Overview

Border Neighbor Threat Index (BNTI) is a geopolitical monitoring platform that transforms multilingual regional news into a normalized threat signal for Turkiye's border environment.
The system batches candidate headlines through `openrouter/free`, lets the LLM choose the final border-country attribution and canonical threat label, and then maps those labels onto deterministic weights for repeatable scoring.

For the public live product, use:
[https://akgularda.github.io/border-neighbor-threat-index/](https://akgularda.github.io/border-neighbor-threat-index/)

## Whitepaper

Read the full technical methodology here:
[BNTI Whitepaper (methodology.pdf)](methodology.pdf)

## Methodology Snapshot

- Data ingestion from regional RSS/Atom sources across neighboring countries
- Batched LLM attribution and canonical threat labeling using `openrouter/free`
- Fixed weight mapping from LLM-selected categories into per-country scores
- Strict no-publish gating when a run cannot fully validate
- Operational thresholding into `STABLE`, `ELEVATED`, and `CRITICAL` levels

## Repository Contents

| Path | Purpose |
|---|---|
| `bnti_data.json` | Latest intelligence dataset used by the dashboard |
| `js/` | Dashboard logic (core engine, map, stream, charts) |
| `css/` | Visual system and component styling |
| `.github/workflows/bnti_update.yml` | 2-hour intelligence update and GitHub Pages deployment |
| `DEPLOYMENT_GUIDE.md` | Step-by-step zero-cost deployment guide |
| `methodology.pdf` | Whitepaper for methodology and scoring design |
| `BNTIndex.pdf` | Project report artifact |

## Operations and Deployment

The project is configured for automated 2-hour updates and publishing via GitHub Actions and GitHub Pages.

- Workflow: `.github/workflows/bnti_update.yml`
- Deployment instructions: `DEPLOYMENT_GUIDE.md`
- Public endpoint: `https://akgularda.github.io/border-neighbor-threat-index/`

## Citation

```bibtex
@software{bnti2026,
  author = {Akgul, Arda},
  title = {Border Neighbor Threat Index: Multilingual Geopolitical Risk Assessment},
  year = {2026},
  url = {https://github.com/akgularda/border-neighbor-threat-index}
}
```

## License

Licensed under Apache License 2.0. See `LICENSE` for details.

