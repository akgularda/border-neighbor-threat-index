# Border Neighbor Threat Index (BNTI)

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![AI Model](https://img.shields.io/badge/AI-XLM--RoBERTa--Large--XNLI-green.svg)](https://huggingface.co/joeddav/xlm-roberta-large-xnli)
[![GitHub Pages](https://img.shields.io/badge/Dashboard-Live-brightgreen.svg)](https://akgularda.github.io/border-neighbor-threat-index/)

> A real-time geopolitical threat assessment system using multilingual NLP and weighted event classification for Turkey's border regions.

![BNTI Dashboard](bnti.png)

---

## Abstract

The **Border Neighbor Threat Index (BNTI)** is an automated intelligence monitoring system designed to quantify and track geopolitical risk levels across Turkey's neighboring countries. The system employs a transformer-based multilingual NLP model (XLM-RoBERTa) for zero-shot classification of news articles, combined with a modified Goldstein scale weighting scheme to produce a normalized threat index (1.0–10.0) for each monitored country.

The index is updated hourly via automated pipelines and serves as an early warning indicator for regional security developments.

---

## Methodology

### 1. Data Collection

The system monitors **50+ RSS/Atom feeds** from regional news outlets across 7 countries:

| Country  | Languages Monitored | Primary Sources |
|----------|---------------------|-----------------|
| Armenia  | Armenian, English   | Hetq, Aravot, 168.am, CivilNet |
| Georgia  | Georgian, English   | InterPressNews, Civil.ge, Netgazeti |
| Greece   | Greek, English      | Kathimerini, Skai, Protothema, In.gr |
| Iran     | Persian, English    | IRNA, ISNA, Fars News, Tasnim |
| Iraq     | Arabic, Kurdish, English | Al Mayadeen, Rudaw, Kurdistan24 |
| Syria    | Arabic, English     | SANA, Enab Baladi, Syrian Observer |
| Bulgaria | Bulgarian, English  | Dnevnik, 24 Chasa, Nova.bg |

Data is fetched hourly with automatic retry mechanisms and cached to prevent duplicate processing.

### 2. Natural Language Processing

Each article headline is processed using **XLM-RoBERTa-Large-XNLI**, a multilingual transformer model trained for zero-shot classification. This architecture enables:

- **Cross-lingual understanding** across 40+ languages without language-specific training
- **Zero-shot classification** into predefined threat categories
- **Confidence scoring** (0.0–1.0) for each classification

### 3. Threat Categorization

Articles are classified into the following categories with associated weights based on a **Modified Goldstein Scale**:

| Category | Weight | Description |
|----------|--------|-------------|
| Military Conflict | +10.0 | Active warfare, kinetic operations |
| Terrorist Act | +9.0 | Terrorism, insurgent attacks |
| Violent Protest | +7.0 | Riots, civil unrest, violent demonstrations |
| Political Crisis | +6.0 | Coups, political instability, diplomatic tensions |
| Economic Crisis | +4.0 | Market crashes, sanctions, economic collapse |
| Humanitarian Crisis | +3.0 | Refugee movements, natural disasters |
| Peaceful Diplomacy | -2.0 | Treaties, alliances, peace agreements |
| Neutral News | 0.0 | Background noise, non-threat events |

### 4. Index Calculation

The per-country index is computed as:

```
I_country = Σ(w_i × c_i × d_i)
```

Where:
- `w_i` = category weight for event *i*
- `c_i` = AI confidence score for event *i*
- `d_i` = temporal decay factor (exponential, half-life = 24h)

The composite BNTI is the weighted average across all monitored countries, normalized to a 1.0–10.0 scale.

### 5. Threat Classification Thresholds

| Level | Score Range | Interpretation |
|-------|-------------|----------------|
| 🟢 **Stable** | 1.0 – 3.9 | Normal background risk |
| 🟡 **Elevated** | 4.0 – 6.9 | Heightened monitoring recommended |
| 🔴 **Critical** | 7.0 – 10.0 | Active crisis/conflict indicators |

### 6. Forecasting

Short-term trend prediction uses **Weighted Linear Regression** with exponentially decaying weights favoring recent observations. This provides 24-hour directional indicators while acknowledging inherent forecast uncertainty.

---

## Installation

### Prerequisites

- Python 3.11+
- 4GB RAM minimum (8GB recommended for model loading)
- Internet connection for RSS feed access

### Setup

```bash
# Clone the repository
git clone https://github.com/akgularda/border-neighbor-threat-index.git
cd border-neighbor-threat-index

# Install dependencies
pip install -r requirements.txt

# Run the analyzer
python borderneighboursthreatindex.py
```

> **Note:** The AI model (~1.5GB) will be downloaded automatically on first run.

---

## Cloud Deployment (GitHub Actions)

The system includes automated CI/CD for continuous monitoring:

1. **Fork this repository**
2. **Enable GitHub Pages** (Settings → Pages → Source: GitHub Actions)
3. **Enable Actions** (The workflow runs automatically every hour)

Your live dashboard will be available at:
```
https://YOUR_USERNAME.github.io/border-neighbor-threat-index/
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## Output Files

| File | Description |
|------|-------------|
| `bnti_data.json` | Full JSON dataset with all events and indices |
| `bnti_data.js` | JavaScript-compatible data for dashboard |
| `bnti_history.csv` | Historical index values for time-series analysis |
| `threat_contributions.xlsx` | Per-event threat analysis breakdown |
| `index.html` | Live interactive dashboard |

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   RSS Feeds     │────▶│  XLM-RoBERTa     │────▶│  Threat Index   │
│  (50+ sources)  │     │  Zero-Shot NLI   │     │  Calculation    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                                                         │
                              ┌──────────────────────────┼──────────────────────────┐
                              ▼                          ▼                          ▼
                    ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
                    │  JSON Export    │        │  Dashboard      │        │  Historical     │
                    │  (bnti_data)    │        │  (index.html)   │        │  (CSV/Excel)    │
                    └─────────────────┘        └─────────────────┘        └─────────────────┘
```

---

## References

- Goldstein, J.S. (1992). *A Conflict-Cooperation Scale for WEIS Events Data*. Journal of Conflict Resolution.
- Conneau, A. et al. (2020). *Unsupervised Cross-lingual Representation Learning at Scale*. ACL.
- Yin, W. et al. (2019). *Benchmarking Zero-shot Text Classification*. EMNLP.

---

## Citation

If you use BNTI in academic research, please cite:

```bibtex
@software{bnti2026,
  author = {Akgül, Arda},
  title = {Border Neighbor Threat Index: A Multilingual Geopolitical Risk Assessment System},
  year = {2026},
  url = {https://github.com/akgularda/border-neighbor-threat-index}
}
```

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <strong>🌍 Continuous Intelligence • 🤖 AI-Powered Analysis • 📊 Real-Time Monitoring</strong>
</p>
