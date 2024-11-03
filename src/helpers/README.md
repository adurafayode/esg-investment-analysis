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

# Test mode (2 pages)
```
python src/helpers/sustainalytics_scraper.py
```
# Full scrape
```
python src/helpers/sustainalytics_scraper.py --full
```

### esg_data_processor.py

Processes and cleans raw ESG data for portfolio analysis.

**Key Features:**
- Exchange/ticker separation
- Risk categorization (High/Medium/Low)
- Major exchange filtering
- Distribution analysis
- Visualization generation

**Usage:**

```
python src/helpers/esg_data_processor.py
```

### databento_preparation.py

Prepares and fetches stock price data from Databento API.

**Key Features:**
- Symbol organization by risk category
- Automatic data caching
- Configurable date ranges
- Error handling and validation
- Environment variable support

**Usage:**

1. Set your Databento API key in one of two ways:

   a. As an environment variable (recommended):
   ```
   export DATABENTO_API_KEY="your-key-here"
   ```

   b. Or directly in the script:
   ```
   API_KEY = "YOUR_DATABENTO_API_KEY_HERE"  # Replace with your actual key
   ```

2. Run the script:
```
python src/helpers/databento_preparation.py
```

## Data Flow

1. `sustainalytics_scraper.py` → `data/raw/esg_ratings_final.csv`
2. `esg_data_processor.py` → `data/processed/clean_esg_data.csv`
3. `databento_preparation.py` → `data/processed/stock_data.csv`

## Dependencies
- pandas
- selenium
- beautifulsoup4
- matplotlib
- databento
- requests
- typing

## Directory Structure

```
src/helpers/
  ├── __init__.py
  ├── sustainalytics_scraper.py
  ├── esg_data_processor.py
  ├── databento_preparation.py
  └── README.md
```

## Error Handling

All modules include:
- Automatic directory creation
- Data validation checks
- Descriptive error messages
- Graceful failure modes

## Output Files

- `data/raw/esg_ratings_final.csv`: Raw ESG data
- `data/raw/esg_ratings_checkpoint_*.csv`: Scraping checkpoints
- `data/processed/clean_esg_data.csv`: Processed ESG data
- `data/processed/stock_data.csv`: Stock price data
- `output/figures/risk_distribution.png`: Risk analysis plots

