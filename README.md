# Border Neighbor Threat Index (BNTI)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AI Model](https://img.shields.io/badge/AI-XLM--RoBERTa--Large--XNLI-green.svg)](https://huggingface.co/joeddav/xlm-roberta-large-xnli)
[![Dashboard](https://img.shields.io/badge/Dashboard-Live-brightgreen.svg)](https://akgularda.github.io/border-neighbor-threat-index/)

> A real-time geopolitical threat assessment system using multilingual NLP and weighted event classification for Turkey's border regions.

---

## Abstract

The **Border Neighbor Threat Index (BNTI)** is an automated intelligence monitoring system designed to quantify and track geopolitical risk levels across Turkey's neighboring countries. The system employs a transformer-based multilingual NLP model (XLM-RoBERTa-Large-XNLI) for zero-shot classification of news articles, combined with a modified Goldstein scale weighting scheme to produce a normalized threat index (1.0–10.0) for each monitored region.

The index is updated hourly via automated pipelines and serves as an early warning indicator for regional security developments enabling continuous situational awareness without manual intervention.

---

## Methodology

### 1. Data Collection

The system monitors **50+ RSS/Atom feeds** from regional news outlets across seven countries in their native languages:

| Country  | Languages | Primary Sources |
|----------|-----------|-----------------|
| Armenia  | Armenian, English | Aravot, 168.am, News.am, Hetq |
| Georgia  | Georgian, English | IPN, Radio Tavisupleba, Netgazeti |
| Greece   | Greek, English | Kathimerini, Skai, News247, In.gr |
| Iran     | Persian, English | IRNA, ISNA, Fars News, Tasnim |
| Iraq     | Arabic, Kurdish | Rudaw, Kurdistan24, Al Mayadeen |
| Syria    | Arabic, English | Enab Baladi, SANA, Al Arabiya |
| Bulgaria | Bulgarian, English | Dnevnik, 24 Chasa, Nova.bg |

Data is fetched hourly with automatic retry mechanisms and cached to prevent duplicate processing.

### 2. Natural Language Processing

Each article headline is processed using **XLM-RoBERTa-Large-XNLI**, a cross-lingual transformer model trained for natural language inference. This architecture enables:

- **Multilingual understanding** across 100+ languages without language-specific training data
- **Zero-shot classification** into predefined threat categories using entailment-based inference
- **Confidence scoring** (0.0–1.0) for each classification decision

Headlines are displayed in English (auto-translated) with the original language available on hover for verification.

### 3. Threat Categorization

Articles are classified into categories with associated weights based on a **Modified Goldstein Scale**:

| Category | Weight | Description |
|----------|--------|-------------|
| Military Conflict | +10.0 | Active warfare, kinetic operations |
| Terrorist Act | +9.0 | Terrorism, insurgent attacks |
| Violent Protest | +7.0 | Riots, civil unrest with violence |
| Political Crisis | +6.0 | Coups, instability, escalations |
| Border Security | +5.0 | Border incidents, migration pressure |
| Economic Crisis | +4.0 | Sanctions, economic collapse |
| Humanitarian | +3.0 | Refugee crises, disasters |
| Diplomatic Tension | +2.5 | Expelled diplomats, warnings |
| Peaceful Diplomacy | −2.0 | Treaties, agreements |
| Neutral | 0.0 | Non-threat events |

### 4. Index Calculation

The per-country threat index is computed as:

```
I_country = Σ(w_i × c_i × d_i) / N
```

Where:
- `w_i` = category weight for event *i*
- `c_i` = model confidence score (0–1)
- `d_i` = temporal decay (exponential, τ = 24h)
- `N` = normalization factor

The composite BNTI is the weighted average across all monitored countries, scaled to 1.0–10.0.

### 5. Threat Classification Thresholds

| Level | Score | Interpretation |
|-------|-------|----------------|
| **Stable** | 1.0 – 3.9 | Normal background risk |
| **Elevated** | 4.0 – 6.9 | Heightened monitoring advised |
| **Critical** | 7.0 – 10.0 | Active crisis indicators |

### 6. Forecasting

Short-term trend prediction uses **Weighted Linear Regression** with exponentially decaying weights favoring recent observations. This provides 6–24 hour directional indicators while acknowledging inherent forecast uncertainty in geopolitical systems.

---

## Installation

### Requirements

- Python 3.11+
- 4GB RAM minimum (8GB recommended)
- Internet connection

### Setup

```bash
git clone https://github.com/akgularda/border-neighbor-threat-index.git
cd border-neighbor-threat-index
pip install -r requirements.txt
python borderneighboursthreatindex.py
```

> The transformer model (~1.5GB) downloads automatically on first run.

---

## Deployment

The system includes automated CI/CD via GitHub Actions:

1. Fork this repository
2. Enable GitHub Pages (Settings → Pages → Source: **GitHub Actions**)
3. The workflow runs hourly automatically

Dashboard URL: `https://YOUR_USERNAME.github.io/border-neighbor-threat-index/`

---

## Output Files

| File | Description |
|------|-------------|
| `bnti_data.json` | Complete dataset with events and indices |
| `bnti_history.csv` | Historical values for time-series analysis |
| `index.html` | Interactive dashboard |

---

## System Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   RSS Feeds     │────▶│  XLM-RoBERTa     │────▶│  Index Engine   │
│  (50+ sources)  │     │  Zero-Shot NLI   │     │  + Forecasting  │
└─────────────────┘     └──────────────────┘     └────────┬────────┘
                                                          │
               ┌──────────────────────────────────────────┼─────┐
               ▼                          ▼                     ▼
     ┌─────────────────┐        ┌─────────────────┐   ┌─────────────────┐
     │  JSON/JS Data   │        │  Dashboard      │   │  CSV History    │
     └─────────────────┘        └─────────────────┘   └─────────────────┘
```

---

## References

1. Goldstein, J.S. (1992). *A Conflict-Cooperation Scale for WEIS Events Data*. Journal of Conflict Resolution, 36(2), 369–385.
2. Conneau, A. et al. (2020). *Unsupervised Cross-lingual Representation Learning at Scale*. Proceedings of ACL.
3. Yin, W. et al. (2019). *Benchmarking Zero-shot Text Classification*. Proceedings of EMNLP.

---

## Citation

```bibtex
@software{bnti2026,
  author = {Akgül, Arda},
  title = {Border Neighbor Threat Index: Multilingual Geopolitical Risk Assessment},
  year = {2026},
  url = {https://github.com/akgularda/border-neighbor-threat-index}
}
```

---

## License

Apache License 2.0 — see [LICENSE](LICENSE).

---

<p align="center"><strong>Continuous Intelligence • AI-Powered Analysis • Real-Time Monitoring</strong></p>
