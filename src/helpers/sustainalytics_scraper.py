"""
sustainalytics_scraper.py

This module provides functionality to scrape ESG (Environmental, Social, and Governance) ratings 
from Sustainalytics website. It uses Selenium WebDriver with Chrome to navigate through pages
and BeautifulSoup for parsing the extracted data.

"""

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
from typing import List, Dict

class SustainalyticsESGScraper:
    """
    A class to scrape ESG ratings data from Sustainalytics website.
    
    Attributes:
        base_url (str): The base URL for Sustainalytics ESG ratings page
        driver (webdriver.Chrome): Chrome WebDriver instance
        save_path (str): Directory path for saving output files
    """
    
    def __init__(self, save_path: str = './data/raw'):
        """
        Initialize the scraper with configuration settings.
        
        Args:
            save_path (str): Directory path where scraped data will be saved
        """
        self.base_url = "https://www.sustainalytics.com/esg-ratings"
        self.save_path = save_path
        self._ensure_save_directory()
        
    def _ensure_save_directory(self):
        """Create the save directory if it doesn't exist."""
        os.makedirs(self.save_path, exist_ok=True)

    def _setup_driver(self) -> webdriver.Chrome:
        """
        Configure and initialize Chrome WebDriver with appropriate settings.
        
        Returns:
            webdriver.Chrome: Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        return webdriver.Chrome(options=chrome_options)

    def _navigate_to_page(self, driver: webdriver.Chrome, target_page: int) -> bool:
        """
        Navigate to a specific page number in the pagination.
        
        Args:
            driver: Chrome WebDriver instance
            target_page: Desired page number to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        try:
            pagination = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "victor-pagination"))
            )
            
            page_links = pagination.find_elements(By.CLASS_NAME, "pagination-page")
            current_page = 1
            
            for link in page_links:
                if 'selected' in link.get_attribute('class'):
                    current_page = int(link.text)
                    break
            
            print(f"Currently on page {current_page}, targeting page {target_page}")
            
            # Handle large page jumps
            if target_page > current_page + 10:
                visible_pages = [int(link.text) for link in page_links if link.text.isdigit()]
                jump_point = max([p for p in visible_pages if p < target_page], default=current_page)
                
                if jump_point > current_page:
                    print(f"Making intermediate jump to page {jump_point}")
                    for link in page_links:
                        if link.text.isdigit() and int(link.text) == jump_point:
                            driver.execute_script("arguments[0].scrollIntoView(true);", link)
                            time.sleep(1)
                            driver.execute_script("arguments[0].click();", link)
                            time.sleep(2)
                            return self._navigate_to_page(driver, target_page)
            
            # Direct navigation to target page
            for link in page_links:
                if link.text.isdigit() and int(link.text) == target_page:
                    driver.execute_script("arguments[0].scrollIntoView(true);", link)
                    time.sleep(1)
                    driver.execute_script("arguments[0].click();", link)
                    time.sleep(2)
                    return self._verify_page_change(driver, target_page)
            
            return False
            
        except Exception as e:
            print(f"Navigation error to page {target_page}: {e}")
            return False

    def _verify_page_change(self, driver: webdriver.Chrome, target_page: int) -> bool:
        """
        Verify successful navigation to target page.
        
        Args:
            driver: Chrome WebDriver instance
            target_page: Expected page number
            
        Returns:
            bool: True if on correct page, False otherwise
        """
        try:
            time.sleep(2)
            pagination = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "victor-pagination"))
            )
            selected = pagination.find_element(By.CLASS_NAME, "selected")
            return selected.get_attribute("id") == str(target_page)
        except Exception:
            return False

    def _extract_page_data(self, driver: webdriver.Chrome, page_number: int) -> List[Dict]:
        """
        Extract ESG rating data from current page.
        
        Args:
            driver: Chrome WebDriver instance
            page_number: Current page number being scraped
            
        Returns:
            List[Dict]: List of dictionaries containing company ESG data
        """
        companies_data = []
        
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "company-row"))
            )
            
            if not self._verify_page_change(driver, page_number):
                print(f"Warning: Page verification failed for page {page_number}")
                return []
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            company_rows = soup.find_all('div', class_='company-row d-flex')
            
            for row in company_rows:
                try:
                    if 'no-border' in row.get('class', []):
                        continue
                    
                    company_div = row.find('div', class_='w-50')
                    company_link = company_div.find('a')
                    company_name = company_link.text.strip()
                    company_ticker = company_div.find('small').text.strip()
                    
                    score_div = row.find('div', class_='company-score')
                    if score_div:
                        score = score_div.find('div', class_='col-2').text.strip()
                        risk_level = score_div.find('div', class_='col-lg-6 col-md-10').text.strip()
                        
                        companies_data.append({
                            'company_name': company_name,
                            'ticker': company_ticker,
                            'esg_score': float(score),
                            'risk_level': risk_level,
                            'page_number': page_number
                        })
                        
                except Exception as e:
                    print(f"Error processing company on page {page_number}: {e}")
                    continue
                    
            return companies_data
            
        except Exception as e:
            print(f"Error extracting data from page {page_number}: {e}")
            return []

    def scrape(self, start_page: int = 1, end_page: int = None, 
               save_frequency: int = 10) -> pd.DataFrame:
        """
        Main method to scrape ESG ratings data.
        
        Args:
            start_page: First page to scrape (default: 1)
            end_page: Last page to scrape (default: None, scrapes all available pages)
            save_frequency: Save progress after every N pages (default: 10)
            
        Returns:
            pd.DataFrame: DataFrame containing all scraped ESG data
            
        Raises:
            Exception: If critical error occurs during scraping
        """
        driver = self._setup_driver()
        all_companies_data = []
        
        try:
            driver.get(self.base_url)
            time.sleep(3)
            
            if not end_page:
                pagination = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "victor-pagination"))
                )
                pages = pagination.find_elements(By.CLASS_NAME, "pagination-page")
                end_page = max(int(page.text) for page in pages if page.text.isdigit())
            
            print(f"Initiating scrape for pages {start_page} to {end_page}")
            
            for page in range(start_page, end_page + 1):
                try:
                    print(f"Processing page {page}/{end_page}")
                    
                    if page > start_page:
                        if not self._navigate_to_page(driver, page):
                            print(f"Navigation failed for page {page}, retrying...")
                            driver.get(self.base_url)
                            time.sleep(3)
                            if not self._navigate_to_page(driver, page):
                                continue
                    
                    page_data = self._extract_page_data(driver, page)
                    if page_data:
                        all_companies_data.extend(page_data)
                        print(f"Successfully scraped {len(page_data)} companies from page {page}")
                        
                        if len(all_companies_data) % save_frequency == 0:
                            self._save_checkpoint(all_companies_data)
                    
                except Exception as e:
                    print(f"Error processing page {page}: {e}")
                    self._save_checkpoint(all_companies_data)
                    continue
        
        finally:
            driver.quit()
            if all_companies_data:
                self._save_final(all_companies_data)
        
        return pd.DataFrame(all_companies_data)

    def _save_checkpoint(self, data: List[Dict]):
        """Save intermediate results during scraping."""
        if not data:
            return
            
        df = pd.DataFrame(data)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        checkpoint_path = os.path.join(self.save_path, f'esg_ratings_checkpoint_{timestamp}.csv')
        df.to_csv(checkpoint_path, index=False)
        print(f"Checkpoint saved: {checkpoint_path}")

    def _save_final(self, data: List[Dict]):
        """Save final results after scraping completion."""
        if not data:
            return
            
        df = pd.DataFrame(data)
        final_path = os.path.join(self.save_path, 'esg_ratings_final.csv')
        df.to_csv(final_path, index=False)
        print(f"Final dataset saved: {final_path}")

# Direct script execution
if __name__ == "__main__":
    import sys
    
    # Default to test mode
    scraper = SustainalyticsESGScraper()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--full':
        # Full scraping mode
        print("Starting full data scrape...")
        df = scraper.scrape()  # Will scrape all available pages
        print(f"Completed full scraping with {len(df)} companies collected")
    else:
        # Test mode
        print("Starting test scrape of first 2 pages...")
        df = scraper.scrape(start_page=1, end_page=2)
        print(f"\nFound {len(df)} companies")
        print("\nFirst few rows:")
        print(df.head())
        print("\nFor full scraping, run with: python src/helpers/sustainalytics_scraper.py --full")