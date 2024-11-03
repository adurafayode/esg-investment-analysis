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
│   │   └── README.md
│   │
│   └── analysis/         # Portfolio analysis
│       ├── portfolio_performance.py
│       └── README.md
│
├── data/
│   ├── raw/             # Raw scraped ESG data
│   └── processed/       # Cleaned data ready for analysis
│
├── output/
│   └── figures/         # Generated plots and visualizations
│
└── .gitignore         # Ignored files and directories
```

## Getting Started

1. **Environment Setup**
```
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
```

2. **Set Databento API Key**
```bash
export DATABENTO_API_KEY="your-key-here"
```

3. **Run Data Pipeline**
```
# Scrape ESG data
python src/helpers/sustainalytics_scraper.py --full

# Process ESG data
python src/helpers/esg_data_processor.py

# Fetch market data
python src/helpers/databento_preparation.py
```

4. **Run Analysis**
```
python src/analysis/portfolio_performance.py
```

## Key Features

- **Robust Data Collection**
  - Automated ESG ratings scraping
  - Smart pagination and retry logic
  - Checkpoint saving
  - Comprehensive error handling

- **Data Processing**
  - Exchange/ticker separation
  - Risk categorization
  - Major exchange filtering
  - Missing data handling

- **Portfolio Analysis**
  - ESG-weighted portfolio construction
  - Long-short strategy implementation
  - Performance metrics calculation
  - Risk analysis visualization

## Results

The analysis generates several key outputs:

- **Performance Metrics**
  - Total Return
  - Period Return (21 months)
  - Volatility
  - Sharpe Ratio

- **Visualizations**
  - Strategy component returns
  - Returns distribution
  - Risk category distribution

## Dependencies

- pandas
- numpy
- selenium
- beautifulsoup4
- matplotlib
- seaborn
- databento
- requests
- typing

## Notes

- ESG data is scraped from publicly available Sustainalytics ratings (currently 780/1393 pages)
- Market data requires a valid Databento API key
- Default analysis period is 21 months
- Strategy assumes equal capital allocation to long and short portfolios

## License

MIT License