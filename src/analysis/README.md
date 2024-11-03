# Portfolio Performance Analysis

Analyzes performance of ESG-based long-short strategy using the following approach:

## Strategy Details
- **Long Portfolio**: Low ESG risk stocks, weighted by inverse ESG scores
- **Short Portfolio**: High ESG risk stocks, weighted by ESG scores
- **Period**: 21 months of daily returns

## Key Files
- `portfolio_performance.py`: Main analysis script
- `../data/processed/clean_esg_data.csv`: Cleaned ESG scores and risk categories
- `../data/processed/stock_data.csv`: Daily stock price data

## Methodology
1. Filter stocks into high/low ESG risk categories
2. Clean returns data (remove stocks with >10% missing values)
3. Weight portfolios based on ESG scores
4. Calculate daily strategy returns (long - short)
5. Generate performance metrics and visualizations

## Outputs
- Strategy performance plots in `output/figures/`
- Key metrics: total return, period return, volatility, Sharpe ratio

## Usage
1. Ensure required data files are in `data/processed/`:
   - `clean_esg_data.csv`
   - `stock_data.csv`

2. Run the analysis:
   ```bash
   python src/analysis/portfolio_performance.py
   ```

3. Check results in:
   - Terminal output for performance metrics
   - `output/figures/` for visualization plots:
     - `strategy_components.png`
     - `returns_distribution.png`

## Dependencies
- pandas
- numpy
- matplotlib
- seaborn 
- scipy