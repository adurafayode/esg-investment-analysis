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
doc_db_wide = stock_data.pivot(index='ts_event', columns='symbol', values='close')

# Calculate daily returns
returns_db = doc_db_wide.pct_change()
returns_db = returns_db.iloc[1:]  # Drop first row containing NaNs dynamically

print("Returns data shape:", returns_db.shape)
print(returns_db.head(10))

# Extract the list of symbols belonging to low ESG risk category
low_risk_symbols = clean_esg_data[clean_esg_data['risk_category'] == 'Low Risk']['clean_ticker'].tolist()

# Extract the list of symbols belonging to high ESG risk category
high_risk_symbols = clean_esg_data[clean_esg_data['risk_category'] == 'High Risk']['clean_ticker'].tolist()

# Identify symbols in both categories that have corresponding return data
valid_low_risk_symbols = list(set(low_risk_symbols) & set(returns_db.columns))
valid_high_risk_symbols = list(set(high_risk_symbols) & set(returns_db.columns))

# Extract the return data for both valid low and high risk symbols
low_risk_returns = returns_db[valid_low_risk_symbols]
high_risk_returns = returns_db[valid_high_risk_symbols]

# Print the shape of the returns DataFrame for both categories to confirm the data selection
print("Low risk returns shape:", low_risk_returns.shape)
print("High risk returns shape:", high_risk_returns.shape)

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

# Apply the cleaning function to both categories
low_risk_returns_cleaned = clean_and_fill_returns(low_risk_returns, nan_threshold=0.1)
high_risk_returns_cleaned = clean_and_fill_returns(high_risk_returns, nan_threshold=0.1)

# Print results
for name, original, cleaned in [("Low Risk", low_risk_returns, low_risk_returns_cleaned),
                              ("High Risk", high_risk_returns, high_risk_returns_cleaned)]:
    print(f"\nResults for {name}:")
    print(f"Original shape: {original.shape}")
    print(f"Cleaned shape: {cleaned.shape}")
    print(f"Columns removed: {original.shape[1] - cleaned.shape[1]}")
    print(f"NaN count before: {original.isnull().sum().sum()}")
    print(f"NaN count after: {cleaned.isnull().sum().sum()}")

# Verify that there are no NaNs left
assert low_risk_returns_cleaned.isnull().sum().sum() == 0, "NaNs remain in low risk"
assert high_risk_returns_cleaned.isnull().sum().sum() == 0, "NaNs remain in high risk"
print("\nVerification passed: No NaNs remain in the cleaned data.")

# Convert to gross returns
gross_low_risk_returns = low_risk_returns_cleaned.add(1)
gross_high_risk_returns = high_risk_returns_cleaned.add(1)

# Update the list of valid symbols based on the cleaned returns data
valid_low_risk_symbols = list(low_risk_returns_cleaned.columns)
valid_high_risk_symbols = list(high_risk_returns_cleaned.columns)

# Output the number of valid symbols available for each category
print(f"Number of valid low risk symbols: {len(valid_low_risk_symbols)}")
print(f"Number of valid high risk symbols: {len(valid_high_risk_symbols)}")

# Filter the ESG scores for the valid symbols in both categories
low_risk_scores = clean_esg_data[clean_esg_data['clean_ticker'].isin(valid_low_risk_symbols)].set_index('clean_ticker')['esg_score']
high_risk_scores = clean_esg_data[clean_esg_data['clean_ticker'].isin(valid_high_risk_symbols)].set_index('clean_ticker')['esg_score']

# Output the number of stocks with ESG scores in each category
print(f"Number of stocks with ESG scores in low risk category: {len(low_risk_scores)}")
print(f"Number of stocks with ESG scores in high risk category: {len(high_risk_scores)}")

# Verify that all stocks in the returns data have corresponding ESG scores
missing_scores_low = set(valid_low_risk_symbols) - set(low_risk_scores.index)
missing_scores_high = set(valid_high_risk_symbols) - set(high_risk_scores.index)

if missing_scores_low:
    print(f"Warning: {len(missing_scores_low)} stocks in low risk returns data are missing ESG scores")
if missing_scores_high:
    print(f"Warning: {len(missing_scores_high)} stocks in high risk returns data are missing ESG scores")

if not missing_scores_low and not missing_scores_high:
    print("All stocks in the returns data have corresponding ESG scores")

# Calculate weights for the short portfolio (high ESG risk)
# Higher weight for higher ESG risk scores
short_weights = high_risk_scores / high_risk_scores.sum()

# Calculate weights for the long portfolio (low ESG risk)
# Higher weight for lower ESG risk scores (inverse weighting)
long_weights = (1 / low_risk_scores) / (1 / low_risk_scores).sum()

# Verify that the weights sum to 1 for each portfolio
print("Sum of short weights:", short_weights.sum())
print("Sum of long weights:", long_weights.sum())

# Display the first few calculated weights for both portfolios
print("\nShort portfolio weights (first few):")
print(short_weights.head())
print("\nLong portfolio weights (first few):")
print(long_weights.head())

# Convert index to datetime
gross_low_risk_returns.index = pd.to_datetime(gross_low_risk_returns.index)
gross_high_risk_returns.index = pd.to_datetime(gross_high_risk_returns.index)

# Determine the earliest date in the returns data for both categories
earliest_date = min(gross_low_risk_returns.index.min(), gross_high_risk_returns.index.min())

# Prepare the initial weight row for the high risk (short portfolio)
initial_short = pd.DataFrame(short_weights).T
initial_short.index = [earliest_date - pd.Timedelta(days=1)]

# Prepend the initial weight row to the gross returns DataFrame for high risk
gross_high_risk_returns = pd.concat([initial_short, gross_high_risk_returns])

# Prepare the initial weight row for the low risk (long portfolio)
initial_long = pd.DataFrame(long_weights).T
initial_long.index = [earliest_date - pd.Timedelta(days=1)]

# Prepend the initial weight row to the gross returns DataFrame for low risk
gross_low_risk_returns = pd.concat([initial_long, gross_low_risk_returns])

# Calculate the compounded returns for the long portfolio (low risk)
long_portfolio_value = gross_low_risk_returns.cumprod()

# Calculate the compounded returns for the short portfolio (high risk)
short_portfolio_value = gross_high_risk_returns.cumprod()

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
FIGURE_SIZES = {
    'strategy': (12, 6),
    'distribution': (10, 6)
}

sns.set_style(PLOT_STYLE)

def save_strategy_plot(strategy_returns):
    """
    Generate and save plot showing performance of strategy components.
    Includes long portfolio (low ESG risk), short portfolio (high ESG risk),
    and combined long-short returns.
    """
    plt.figure(figsize=FIGURE_SIZES['strategy'])
    strategy_returns.plot()
    plt.title('ESG Strategy Returns: Portfolio Components')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.grid(True)
    plt.savefig(OUTPUT_PATH / 'strategy_components.png')
    plt.close()

def save_distribution_plot(strategy_returns):
    """
    Generate and save histogram and KDE plot of strategy returns distribution.
    """
    plt.figure(figsize=FIGURE_SIZES['distribution'])
    strategy_returns['Long-Short'].hist(bins=50, density=True)
    strategy_returns['Long-Short'].plot(kind='kde')
    plt.title('Distribution of Strategy Returns')
    plt.xlabel('Return')
    plt.ylabel('Density')
    plt.savefig(OUTPUT_PATH / 'returns_distribution.png')
    plt.close()

# Generate plots
save_strategy_plot(strategy_returns)
save_distribution_plot(strategy_returns)

# Calculate performance metrics
total_return = strategy_returns['Long-Short'].iloc[-1] - strategy_returns['Long-Short'].iloc[0]

# Calculate actual number of trading days in our period
trading_days = len(strategy_returns)
print(f"Number of trading days in sample: {trading_days}")

# Calculate returns and volatility based on actual trading days
period_return = strategy_returns['Long-Short'].mean() * trading_days
period_vol = strategy_returns['Long-Short'].std() * np.sqrt(trading_days)
sharpe_ratio = period_return / period_vol

print("\nPerformance Metrics:")
print(f"Total Return: {total_return:.2%}")
print(f"Period Return (21 months): {period_return:.2%}")
print(f"Period Volatility: {period_vol:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")