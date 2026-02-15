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
  <a href="https://huggingface.co/joeddav/xlm-roberta-large-xnli"><img src="https://img.shields.io/badge/Model-XLM--RoBERTa--Large--XNLI-green.svg" alt="Model: XLM-RoBERTa-Large-XNLI" /></a>
</p>

## Overview

Border Neighbor Threat Index (BNTI) is a geopolitical monitoring platform that transforms multilingual regional news into a normalized threat signal for Türkiye's border environment.
The system combines transformer-based NLP classification, weighted event scoring, and time-aware aggregation to support continuous intelligence visibility.

For the public live product, use:
[https://akgularda.github.io/border-neighbor-threat-index/](https://akgularda.github.io/border-neighbor-threat-index/)

## Whitepaper

Read the full technical methodology here:
[BNTI Whitepaper (methodology.pdf)](methodology.pdf)

## Methodology Snapshot

- Data ingestion from regional RSS/Atom sources across neighboring countries
- Multilingual zero-shot classification using XLM-RoBERTa-Large-XNLI
- Threat weighting using a modified Goldstein-style event scale
- Confidence-weighted and time-decayed aggregation into per-country and composite scores
- Operational thresholding into `STABLE`, `ELEVATED`, and `CRITICAL` levels

## Repository Contents

| Path | Purpose |
|---|---|
| `bnti_data.json` | Latest intelligence dataset used by the dashboard |
| `js/` | Dashboard logic (core engine, map, stream, charts) |
| `css/` | Visual system and component styling |
| `.github/workflows/bnti_update.yml` | Hourly intelligence update and GitHub Pages deployment |
| `DEPLOYMENT_GUIDE.md` | Step-by-step zero-cost deployment guide |
| `methodology.pdf` | Whitepaper for methodology and scoring design |
| `BNTIndex.pdf` | Project report artifact |

## Operations and Deployment

The project is configured for automated hourly updates and publishing via GitHub Actions and GitHub Pages.

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
