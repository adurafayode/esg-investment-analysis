import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

"""
Portfolio performance analysis for ESG-based long-short strategy.
Long position: Low ESG risk stocks (weighted by inverse ESG scores)
Short position: High ESG risk stocks (weighted by ESG scores)
"""

# Constants with explanations
NAN_THRESHOLD = 0.1  # Maximum allowed proportion of NaN values per stock
DATA_PATH = Path('data/processed')
OUTPUT_PATH = Path('output/figures')

# Load data
clean_esg_data = pd.read_csv(DATA_PATH / 'clean_esg_data.csv')
stock_data = pd.read_csv(DATA_PATH / 'stock_data.csv')

# Transform price data to wide format
price_data_wide = stock_data.pivot(index='ts_event', columns='symbol', values='close')

# Calculate daily returns
daily_returns = price_data_wide.pct_change()
daily_returns = daily_returns.iloc[1:]  # Drop first row containing NaNs dynamically

print("Returns data shape:", daily_returns.shape)
print(daily_returns.head(10))

# Extract the list of symbols belonging to long/short portfolios
long_portfolio_symbols = clean_esg_data[clean_esg_data['risk_category'] == 'Low Risk']['clean_ticker'].tolist()
short_portfolio_symbols = clean_esg_data[clean_esg_data['risk_category'] == 'High Risk']['clean_ticker'].tolist()

# Identify symbols in both portfolios that have corresponding return data
valid_long_symbols = list(set(long_portfolio_symbols) & set(daily_returns.columns))
valid_short_symbols = list(set(short_portfolio_symbols) & set(daily_returns.columns))

# Extract the return data for both portfolios
long_portfolio_returns = daily_returns[valid_long_symbols]
short_portfolio_returns = daily_returns[valid_short_symbols]

# Print the shape of the returns DataFrame for both categories to confirm the data selection
print("Long portfolio returns shape:", long_portfolio_returns.shape)
print("Short portfolio returns shape:", short_portfolio_returns.shape)

# Clean the returns data using the same function from P/B project
def clean_and_fill_returns(df, nan_threshold=NAN_THRESHOLD):
    """
    Clean returns data by removing stocks with excessive missing values.
    
    Args:
        df (pd.DataFrame): Returns dataframe with stocks as columns
        nan_threshold (float): Maximum allowed proportion of NaN values
    
    Returns:
        pd.DataFrame: Cleaned returns with NaNs filled using column means
    """
    # Calculate the proportion of NaN values in each column
    nan_proportion = df.isnull().mean()
    
    # Identify columns to keep (those with NaN proportion below the threshold)
    columns_to_keep = nan_proportion[nan_proportion <= nan_threshold].index
    
    # Keep only the good columns
    df_cleaned = df[columns_to_keep]
    
    # Fill remaining NaNs with column means
    df_filled = df_cleaned.fillna(df_cleaned.mean())
    
    return df_filled

# Clean returns
long_portfolio_returns_clean = clean_and_fill_returns(long_portfolio_returns, nan_threshold=0.1)
short_portfolio_returns_clean = clean_and_fill_returns(short_portfolio_returns, nan_threshold=0.1)

# Convert to gross returns
gross_long_returns = long_portfolio_returns_clean.add(1)
gross_short_returns = short_portfolio_returns_clean.add(1)

# Update the list of valid symbols based on the cleaned returns data
valid_long_symbols = list(long_portfolio_returns_clean.columns)
valid_short_symbols = list(short_portfolio_returns_clean.columns)

# Output the number of valid symbols available for each category
print(f"Number of valid long portfolio symbols: {len(valid_long_symbols)}")
print(f"Number of valid short portfolio symbols: {len(valid_short_symbols)}")

# Filter the ESG scores for the valid symbols in both categories
long_portfolio_scores = clean_esg_data[clean_esg_data['clean_ticker'].isin(valid_long_symbols)].set_index('clean_ticker')['esg_score']
short_portfolio_scores = clean_esg_data[clean_esg_data['clean_ticker'].isin(valid_short_symbols)].set_index('clean_ticker')['esg_score']

# Output the number of stocks with ESG scores in each category
print(f"Number of stocks with ESG scores in long portfolio: {len(long_portfolio_scores)}")
print(f"Number of stocks with ESG scores in short portfolio: {len(short_portfolio_scores)}")

# Verify that all stocks in the returns data have corresponding ESG scores
missing_scores_long = set(valid_long_symbols) - set(long_portfolio_scores.index)
missing_scores_short = set(valid_short_symbols) - set(short_portfolio_scores.index)

if missing_scores_long:
    print(f"Warning: {len(missing_scores_long)} stocks in long portfolio returns data are missing ESG scores")
if missing_scores_short:
    print(f"Warning: {len(missing_scores_short)} stocks in short portfolio returns data are missing ESG scores")

if not missing_scores_long and not missing_scores_short:
    print("All stocks in the returns data have corresponding ESG scores")

# Calculate weights for the short portfolio (high ESG risk)
# Higher weight for higher ESG risk scores
short_weights = short_portfolio_scores / short_portfolio_scores.sum()

# Calculate weights for the long portfolio (low ESG risk)
# Higher weight for lower ESG risk scores (inverse weighting)
long_weights = (1 / long_portfolio_scores) / (1 / long_portfolio_scores).sum()

# Verify that the weights sum to 1 for each portfolio
print("Sum of short weights:", short_weights.sum())
print("Sum of long weights:", long_weights.sum())

# Display the first few calculated weights for both portfolios
print("\nShort portfolio weights (first few):")
print(short_weights.head())
print("\nLong portfolio weights (first few):")
print(long_weights.head())

# Convert index to datetime
gross_long_returns.index = pd.to_datetime(gross_long_returns.index)
gross_short_returns.index = pd.to_datetime(gross_short_returns.index)

# Determine the earliest date in the returns data for both categories
earliest_date = min(gross_long_returns.index.min(), gross_short_returns.index.min())

# Prepare the initial weight row for the short portfolio
initial_short = pd.DataFrame(short_weights).T
initial_short.index = [earliest_date - pd.Timedelta(days=1)]

# Prepend the initial weight row to the gross returns DataFrame for short portfolio
gross_short_returns = pd.concat([initial_short, gross_short_returns])

# Prepare the initial weight row for the long portfolio
initial_long = pd.DataFrame(long_weights).T
initial_long.index = [earliest_date - pd.Timedelta(days=1)]

# Prepend the initial weight row to the gross returns DataFrame for long portfolio
gross_long_returns = pd.concat([initial_long, gross_long_returns])

# Calculate the compounded returns for the long portfolio (low risk)
long_portfolio_value = gross_long_returns.cumprod()

# Calculate the compounded returns for the short portfolio (high risk)
short_portfolio_value = gross_short_returns.cumprod()

# Calculate portfolio values
long_portfolio_value['portfolio_value'] = long_portfolio_value.sum(axis=1)
short_portfolio_value['portfolio_value'] = short_portfolio_value.sum(axis=1)

# Calculate strategy returns (Long Low Risk - Short High Risk)
strategy_returns = pd.DataFrame({
    'Long (Low Risk)': long_portfolio_value['portfolio_value'],
    'Short (High Risk)': short_portfolio_value['portfolio_value'],
    'Long-Short': long_portfolio_value['portfolio_value'] - short_portfolio_value['portfolio_value']
})

# Plotting configurations
PLOT_STYLE = "darkgrid"
PLOT_DIMENSIONS = {
    'strategy': (12, 6),
    'distribution': (10, 6)
}

sns.set_style(PLOT_STYLE)

def save_strategy_plot(strategy_returns):
    """
    Generate and save plot showing performance of strategy components.
    Plots the growth of $1 invested in each portfolio component.
    """
    plt.figure(figsize=PLOT_DIMENSIONS['strategy'])
    strategy_returns.plot()
    plt.title('ESG Strategy Performance: Portfolio Components')
    plt.xlabel('Date')
    plt.ylabel('Portfolio Value ($)')
    plt.grid(True)
    plt.savefig(OUTPUT_PATH / 'strategy_components.png')
    plt.close()

def save_distribution_plot(long_portfolio_returns, short_portfolio_returns, 
                         long_portfolio_weights, short_portfolio_weights):
    """
    Generate and save histogram and KDE plot of strategy returns distribution.
    """
    # Calculate weighted returns for each portfolio
    long_weighted_returns = (long_portfolio_returns * long_portfolio_weights).sum(axis=1)
    short_weighted_returns = (short_portfolio_returns * short_portfolio_weights).sum(axis=1)
    
    # Calculate long-short strategy returns
    strategy_returns = long_weighted_returns - short_weighted_returns
    
    plt.figure(figsize=PLOT_DIMENSIONS['distribution'])
    strategy_returns.hist(bins=50, density=True)
    strategy_returns.plot(kind='kde')
    plt.title('Distribution of Daily Strategy Returns')
    plt.xlabel('Daily Return')
    plt.ylabel('Density')
    plt.savefig(OUTPUT_PATH / 'returns_distribution.png')
    plt.close()

# Generate plots
save_strategy_plot(strategy_returns)
save_distribution_plot(
    long_portfolio_returns_clean, 
    short_portfolio_returns_clean,
    long_weights,
    short_weights
)