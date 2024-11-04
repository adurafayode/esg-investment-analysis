# ESG Data Pipeline Helpers

A collection of Python modules for building an ESG-based stock analysis pipeline, from data collection to processing and market data integration.

## Overview

This pipeline consists of three main components:

1. ESG data scraping from Sustainalytics
2. Data cleaning and risk categorization
3. Stock price data integration via Databento

## Modules

### sustainalytics_scraper.py

Robust web scraper for Sustainalytics ESG ratings using Selenium and BeautifulSoup.

**Key Features:**
- Headless Chrome automation
- Smart pagination with retry logic
- Automatic checkpoint saving
- Configurable page ranges
- Comprehensive error handling

**Usage:**
```bash
# Test mode (2 pages)
python src/helpers/sustainalytics_scraper.py

# Full scrape
python src/helpers/sustainalytics_scraper.py --full
```

### esg_data_processor.py

Processes and cleans raw ESG data for portfolio analysis.

**Key Features:**
- Exchange/ticker separation
- Risk categorization (High/Medium/Low)
- Major exchange filtering (NYSE/NASDAQ)
- Distribution analysis
- Visualization generation

**Usage:**
```bash
python src/helpers/esg_data_processor.py
```

### databento_preparation.py

Prepares and fetches stock price data from Databento API.

**Key Features:**
- Symbol organization by risk category
- Automatic data caching
- Configurable date ranges
- Environment variable support

**Usage:**

1. Set your Databento API key:
```bash
export DATABENTO_API_KEY="your-key-here"
```

2. Run the script:
```bash
python src/helpers/databento_preparation.py
```

## Data Flow

1. `sustainalytics_scraper.py` → `data/raw/esg_ratings_final.csv`
   - Raw ESG ratings data
   - Includes company names, tickers, scores, and risk levels

2. `esg_data_processor.py` → `data/processed/clean_esg_data.csv`
   - Cleaned and categorized ESG data
   - Separated exchange/ticker information
   - Risk categorization applied

3. `databento_preparation.py` → `data/processed/stock_data.csv`
   - Daily stock price data
   - OHLCV format
   - Filtered for analysis period

## Error Handling

Each module includes robust error handling:

- **sustainalytics_scraper.py**:
  - Automatic retry on navigation failures
  - Checkpoint saving on errors
  - Page verification checks
  - Exception logging

- **esg_data_processor.py**:
  - Data validation checks
  - Missing data handling
  - Exchange filtering validation

- **databento_preparation.py**:
  - API error handling
  - Data validation
  - Cache management
  - Environment variable checks

## Output Files

- `data/raw/esg_ratings_final.csv`: Raw ESG data
- `data/raw/esg_ratings_checkpoint_*.csv`: Scraping checkpoints
- `data/processed/clean_esg_data.csv`: Processed ESG data
- `data/processed/stock_data.csv`: Stock price data
- `output/figures/risk_distribution.png`: Risk analysis plots

## Dependencies

See `requirements.txt` in the root directory for full list of dependencies.

Core requirements:
- pandas
- selenium
- beautifulsoup4
- matplotlib
- databento

