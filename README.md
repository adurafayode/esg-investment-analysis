# ESG-Based Portfolio Strategy Analysis

A comprehensive pipeline for analyzing portfolio performance using ESG (Environmental, Social, and Governance) risk ratings. The strategy implements a long-short approach based on Sustainalytics ESG risk scores.

## Strategy Overview

- **Long Portfolio**: Low ESG risk stocks, weighted by inverse ESG scores
- **Short Portfolio**: High ESG risk stocks, weighted by ESG scores
- **Universe**: US stocks (NYSE and NASDAQ)
- **Period**: 21 months of daily returns
- **Data Sources**: 
  - ESG Ratings: Sustainalytics
  - Market Data: Databento

## Project Structure

```
├── src/
│   ├── helpers/           # Data collection and processing
│   │   ├── sustainalytics_scraper.py
│   │   ├── esg_data_processor.py
│   │   ├── databento_preparation.py
│   │   └── README.md     # Detailed pipeline documentation
│   │
│   └── analysis/         # Portfolio analysis
│       └── portfolio_performance.py
│
├── data/
│   ├── raw/             # Raw scraped ESG data
│   └── processed/       # Cleaned data ready for analysis
│
├── output/
│   └── figures/         # Generated plots and visualizations
│
└── .gitignore
```

## Quick Start

1. **Environment Setup**
```bash
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. **Set Databento API Key**
```bash
export DATABENTO_API_KEY="your-key-here"
```

3. **Run Data Pipeline**
```bash
# Scrape ESG data
python src/helpers/sustainalytics_scraper.py --full

# Process ESG data
python src/helpers/esg_data_processor.py

# Fetch market data
python src/helpers/databento_preparation.py
```

4. **Run Analysis**
```bash
python src/analysis/portfolio_performance.py
```

## Analysis Methodology

1. **Portfolio Construction**
   - Filter stocks into long/short portfolios based on ESG risk
   - Clean returns data (remove stocks with >10% missing values)
   - Weight portfolios based on ESG scores (inverse weighting for long)
   - Calculate daily strategy returns (long minus short)

2. **Performance Analysis**
   - Generate visualizations:
     - Strategy component returns: Long and short portfolio value growth
     - Returns distribution: Distribution of daily strategy returns
     - Risk category distribution: ESG risk levels across companies in the scraped data

## Results

The analysis generates several key outputs:

- **Performance Metrics** in terminal output
- **Visualizations** in `output/figures/`:
  - `strategy_components.png`: Portfolio value growth
  - `returns_distribution.png`: Strategy returns distribution

## Dependencies

Core requirements:
- pandas
- numpy
- matplotlib
- seaborn
- databento
- selenium
- beautifulsoup4

Full list in `requirements.txt`

## Documentation

- [Data Pipeline Documentation](src/helpers/README.md) - Detailed guide for data collection and processing
- [API Documentation](https://databento.com/docs) - Databento API reference

## License

MIT License