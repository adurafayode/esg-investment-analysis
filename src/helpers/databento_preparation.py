"""
databento_preparation.py

Prepare ESG data for fetching stock prices from Databento.
"""

import pandas as pd
from typing import List, Dict
from databento import Historical

def prepare_databento_symbols(file_path: str) -> Dict[str, List[str]]:
    """
    Prepare stock symbols for Databento API call, organized by risk category.
    
    Args:
        file_path: Path to the processed ESG data CSV
        
    Returns:
        Dictionary containing lists of symbols for each risk category
    """
    # Read the processed ESG data
    print("Loading processed ESG data...")
    df = pd.read_csv(file_path)
    
    # Create lists of symbols for each risk category
    risk_symbols = {
        'low_risk': df[df['risk_category'] == 'Low Risk']['clean_ticker'].dropna().unique().tolist(),
        'medium_risk': df[df['risk_category'] == 'Medium Risk']['clean_ticker'].dropna().unique().tolist(),
        'high_risk': df[df['risk_category'] == 'High Risk']['clean_ticker'].dropna().unique().tolist()
    }
    
    # Print summary statistics
    print("\nSymbols by risk category:")
    for category, symbols in risk_symbols.items():
        print(f"{category}: {len(symbols)} unique symbols")
    
    return risk_symbols

def get_databento_data(api_key: str, risk_symbols: Dict[str, List[str]], 
                      start_date: str = '2023-01-01', 
                      end_date: str = '2024-09-30',
                      use_cached: bool = True,
                      cache_file: str = 'data/processed/stock_data.csv') -> pd.DataFrame:
    """
    Fetch or load stock price data for all risk categories.
    
    Args:
        api_key: Databento API key
        risk_symbols: Dictionary containing symbol lists by risk category
        start_date: Start date for data fetch
        end_date: End date for data fetch
        use_cached: Whether to use cached data if available
        cache_file: Path to cache file
        
    Returns:
        DataFrame containing stock price data
    """
    from pathlib import Path
    import requests
    from io import StringIO
    from requests.auth import HTTPBasicAuth
    
    # Check if we should use cached data
    if use_cached and Path(cache_file).exists():
        print(f"Loading cached data from {cache_file}")
        return pd.read_csv(cache_file)
    
    # Combine all symbols for the API call
    all_symbols = []
    for symbols in risk_symbols.values():
        all_symbols.extend(symbols)
    all_symbols = list(set(all_symbols))  # Remove any duplicates
    symbols_str = ','.join(all_symbols)
    
    url = 'https://hist.databento.com/v0/timeseries.get_range'
    auth = HTTPBasicAuth(api_key, '')

    payload = {
        'dataset': "XNAS.ITCH",
        'symbols': symbols_str,
        'schema': 'ohlcv-1d',
        'start': start_date,
        'end': end_date,
        'encoding': 'csv',
        'pretty_px': 'true',
        'pretty_ts': 'true',
        'map_symbols': 'true'
    }
    
    print(f"Fetching data for {len(all_symbols)} symbols...")
    response = requests.post(url, auth=auth, data=payload)
    
    csv_data = StringIO(response.content.decode('utf-8'))
    df = pd.read_csv(csv_data)
    
    # Save to cache
    df.to_csv(cache_file, index=False)
    print(f"Data saved to {cache_file}")
    
    return df

# Direct script execution
if __name__ == "__main__":
    import os
    
    # Ensure required directories exist
    os.makedirs('data/processed', exist_ok=True)
    
    # Set up parameters with clear defaults
    API_KEY = os.getenv('DATABENTO_API_KEY', "YOUR_DATABENTO_API_KEY_HERE")
    ESG_DATA_PATH = 'data/processed/clean_esg_data.csv'
    
    if not os.path.exists(ESG_DATA_PATH):
        print(f"Error: ESG data file not found at {ESG_DATA_PATH}")
        print("Please run the ESG data processing script first.")
        exit(1)
        
    if API_KEY == "YOUR_DATABENTO_API_KEY_HERE":
        print("Error: Please set your Databento API key")
        print("You can either:")
        print("1. Set the DATABENTO_API_KEY environment variable")
        print("2. Replace the default API_KEY value in this script")
        exit(1)
    
    try:
        # Prepare symbols
        risk_symbols = prepare_databento_symbols(ESG_DATA_PATH)
        
        # Get data (using cache by default)
        stock_data = get_databento_data(
            api_key=API_KEY,
            risk_symbols=risk_symbols,
            start_date='2023-01-01',
            end_date='2024-09-30',
            use_cached=True,
            cache_file='data/processed/stock_data.csv'
        )
        
        # Print summary using correct column names
        print("\nData summary:")
        print(f"Total rows: {len(stock_data)}")
        print(f"Unique symbols: {stock_data['symbol'].nunique()}")
        print(f"Date range: {stock_data['ts_event'].min()} to {stock_data['ts_event'].max()}")
        print("\nSample of data:")
        print(stock_data.head())
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        exit(1)