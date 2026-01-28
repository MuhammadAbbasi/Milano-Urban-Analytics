# Milan’s Urban Divide: Mapping the Intersection of Socio-Economic Wealth, Climate Vulnerability, and Safety Resilience

**Author**: Muhammad Abbasi  
**Institution**: Università degli studi di Milano-Bicocca, Data Science Lab for Smart Cities  
**Date**: January 2026

## Abstract
This project challenges the prevailing assumption that economic prosperity correlates with reduced environmental vulnerability. Through spatial analysis of Milan's 88 *Nuclei di Identità Locale* (NILs), we reveal a "Resilience Gap" where high-income central districts (the "Gilded Cage") suffer from chronic traffic congestion and pollution, while low-income peripheral areas ("The Forgotten Periphery") face structural decay and abandonment. This repository contains the data processing pipelines, analysis scripts, and visualization tools used to demonstrate this phenomenon.

---

## 🏗️ Project Structure
The codebase is organized to support the data pipeline from raw municipal data to final visualization:

```
.
├── code_v8_quadrants.py            # Generates the Quadrant Analysis (Wealth vs. Risk)
├── code_v8_auggestion_area_c_map.py # Generates the Map for Area C Expansion Proposal
├── dataset/                        # Contains processed CSVs and GeoJSONs
│   ├── milan_real_comprehensive_data.csv
│   └── milan_districts_master_v3.geojson
├── viz/                            # Output folder for generated charts
└── README.md                       # This documentation
```

## 📊 Key Findings & Methodology

### 1. The "Gilded Cage" vs. "The Forgotten"
Our analysis identifies distinct vulnerability profiles based on socioeconomic status:
- **The Gilded Cage (High Wealth, High Traffic)**: Affluent central neighborhoods (e.g., Duomo, Brera) experience traffic densities exceeding 20,000 m/km², acting as a proxy for air pollution and noise.
- **The Forgotten Periphery (Low Wealth, High Decay)**: Marginalized areas (e.g., Lambrate, Gorla) show significantly higher rates of abandoned buildings and structural neglect.

### 2. Methodological Approach
- **Traffic Density Calculation**: `(Total Road Length + Intersection Count * 100m) / Neighborhood Area`. Validated as a proxy for NO₂ and PM2.5 exposure.
- **Composite Risk Score**: A weighted index combining Environmental Risk (Traffic) and Physical Risk (Decay/Hydrogeological hazard).
- **Data Sources**: 
  - *Income*: IRPEF 2023 taxation records (CAP-to-NIL mapped).
  - *Infrastructure*: OpenStreetMap road networks.
  - *Decay*: Municipal building surveys.

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Libraries: `pandas`, `geopandas`, `matplotlib`, `seaborn`, `numpy`

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/MuhammadAbbasi/Milano-Urban-Analytics.git
   cd Milano-Urban-Analytics
   ```
2. Install dependencies:
   ```bash
   pip install pandas geopandas matplotlib seaborn numpy
   ```

### Usage
**Generate the Quadrant Analysis Chart:**
Run the script to produce the wealth vs. vulnerability scatter plot (`milan_quadrants.png`):
```bash
python code_v8_quadrants.py
```

**Generate the Policy Suggestion Map:**
Run the script to visualize the proposed Area C expansion (`milan_area_c_expansion.png`):
```bash
python code_v8_auggestion_area_c_map.py
```

## 📈 Visualizations used in the Paper

| Visualization | Description | Script |
|:---:|---|---|
| **Quadrant Analysis** | Scatter plot dividing NILs into 4 typologies: Elite, Gilded Cage, Resilient Poor, Forgotten. | `code_v8_quadrants.py` |
| **Expansion Map** | Strategic map proposing extension of Low Emission Zones to high-traffic wealthy districts. | `code_v8_auggestion_area_c_map.py` |

## 🤝 Contribution & License
This project was developed for the Data Science Lab for Smart Cities final essay.
**License**: CC BY-NC-SA 3.0
