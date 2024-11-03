"""
esg_data_processor.py

Module for processing and cleaning ESG data from Sustainalytics.
Handles data cleaning, filtering, and basic analysis tasks.
"""

import pandas as pd
import matplotlib.pyplot as plt
from typing import Tuple
import os

class ESGDataProcessor:
    """
    Class to process and clean ESG data for portfolio construction.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the processor with path to ESG data.
        
        Args:
            data_path: Path to the CSV file containing ESG data
        """
        os.makedirs('data/processed', exist_ok=True)
        os.makedirs('output/figures', exist_ok=True)
        
        self.df = pd.read_csv(data_path)
        
    def split_exchange_ticker(self) -> pd.DataFrame:
        """
        Split the ticker column into exchange and ticker symbols.
        """
        # Split ticker column on ':' and create new columns
        split_tickers = self.df['ticker'].str.split(':', expand=True)
        self.df['exchange'] = split_tickers[0]
        self.df['clean_ticker'] = split_tickers[1]
        
        # Handle cases where there's no exchange (marked with '-')
        mask = self.df['ticker'] == '-'
        self.df.loc[mask, 'exchange'] = None
        self.df.loc[mask, 'clean_ticker'] = None
        
        return self.df
    
    def filter_major_exchanges(self, exchanges: list = ['NAS', 'NYS']) -> pd.DataFrame:
        """
        Filter dataframe to keep only specified exchanges.
        """
        self.df = self.df[self.df['exchange'].isin(exchanges)]
        return self.df
    
    def categorize_risk(self) -> pd.DataFrame:
        """
        Create binary risk categories for portfolio construction.
        Low Risk = Negligible or Low ESG Risk
        High Risk = High or Severe ESG Risk
        """
        risk_mapping = {
            'Negligible ESG Risk': 'Low Risk',
            'Low ESG Risk': 'Low Risk',
            'Medium ESG Risk': 'Medium Risk',
            'High ESG Risk': 'High Risk',
            'Severe ESG Risk': 'High Risk'
        }
        
        self.df['risk_category'] = self.df['risk_level'].map(risk_mapping)
        return self.df
    
    def analyze_risk_distribution(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Analyze the distribution of risk levels and categories.
        
        Returns:
            Tuple containing:
            - Risk level distribution
            - Risk category distribution by exchange
        """
        risk_dist = self.df['risk_level'].value_counts()
        exchange_risk_dist = pd.crosstab(self.df['exchange'], self.df['risk_category'])
        
        return risk_dist, exchange_risk_dist
    
    def plot_risk_distribution(self):
        """
        Create visualizations of risk distributions.
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot risk level distribution
        self.df['risk_level'].value_counts().plot(
            kind='bar',
            ax=ax1,
            title='Distribution of Risk Levels'
        )
        ax1.set_xlabel('Risk Level')
        ax1.set_ylabel('Count')
        
        # Plot risk category by exchange
        pd.crosstab(self.df['exchange'], self.df['risk_category']).plot(
            kind='bar',
            ax=ax2,
            title='Risk Categories by Exchange'
        )
        ax2.set_xlabel('Exchange')
        ax2.set_ylabel('Count')
        
        plt.tight_layout()
        return fig

    def save_processed_data(self, output_path: str):
        """
        Save the processed dataframe to CSV.
        """
        self.df.to_csv(output_path, index=False)
        print(f"Processed data saved to: {output_path}")

# Direct script execution
if __name__ == "__main__":
    # Initialize processor with your scraped data
    processor = ESGDataProcessor('data/raw/esg_ratings_final.csv')
    
    # Process the data
    print("Processing data...")
    processor.split_exchange_ticker()
    processor.filter_major_exchanges()
    processor.categorize_risk()
    
    # Get distribution analysis
    risk_dist, exchange_risk_dist = processor.analyze_risk_distribution()
    
    print("\nRisk Level Distribution:")
    print(risk_dist)
    
    print("\nRisk Categories by Exchange:")
    print(exchange_risk_dist)
    
    # Create and save visualization
    fig = processor.plot_risk_distribution()
    plt.savefig('output/figures/risk_distribution.png')
    plt.close()
    
    # Save processed data
    processor.save_processed_data('data/processed/clean_esg_data.csv')
    
    # Display sample of processed data
    df = processor.df
    print("\nSample of processed data:")
    print(df[['company_name', 'exchange', 'clean_ticker', 'esg_score', 'risk_category']].head())