# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import time
# import pandas as pd
# import os


# def scrape_shareholder_data(company_ticker):
#     """
#     Scrape shareholder data for a given company from Screener.in
    
#     Args:
#         company_ticker: Stock ticker symbol (e.g., 'INFY', 'TCS')
#     """
#     # --- Chrome Setup ---
#     options = Options()
#     options.add_argument("--start-maximized")
#     # Uncomment for headless mode
#     # options.add_argument("--headless=new")
#     options.add_experimental_option("detach", True)
    
#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, 30)
    
#     all_shareholder_data = []
    
#     try:
#         # Navigate directly to the company's shareholding page
#         url = f"https://www.screener.in/company/{company_ticker}/consolidated/#shareholding"
#         driver.get(url)
#         print(f"✓ Opened: {url}")
#         time.sleep(3)  # Wait for page to load completely
        
#         # Scroll to shareholding section
#         try:
#             shareholding_section = wait.until(
#                 EC.presence_of_element_located((By.ID, "shareholding"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", shareholding_section)
#             time.sleep(1)
#         except TimeoutException:
#             print("❌ Could not find shareholding section")
#             return
        
#         # Define shareholder categories to scrape
#         categories = [
#             ('promoters', 'Promoters'),
#             ('foreign_institutions', 'FIIs'),
#             ('domestic_institutions', 'DIIs'),
#             ('government', 'Government'),
#             ('public', 'Public'),
#             ('others', 'Others')
#         ]
        
#         # Extract table headers (only for display purposes)
#         print("\n📊 Extracting shareholder names...")
        
#         # Process each category
#         for category_id, category_name in categories:
#             print(f"\n🔍 Processing: {category_name}")
            
#             try:
#                 # Find and click the button to expand shareholders
#                 button_selector = f"button[data-tab-id='quarterly-shp'][onclick*=\"showShareholders('{category_id}'\"]"
                
#                 # Try to find the button
#                 buttons = driver.find_elements(By.CSS_SELECTOR, "button.button-plain")
#                 target_button = None
                
#                 for btn in buttons:
#                     onclick_attr = btn.get_attribute("onclick")
#                     if onclick_attr and category_id in onclick_attr and "quarterly" in onclick_attr:
#                         # Check if button shows "+" (collapsed) or "-" (expanded)
#                         icon = btn.find_element(By.CSS_SELECTOR, "span.blue-icon")
#                         if icon.text == "+":
#                             target_button = btn
#                             break
                
#                 if not target_button:
#                     print(f"  ⚠ Button already expanded or not found for {category_name}")
#                     # Try to find expanded data anyway
#                 else:
#                     # Click to expand
#                     driver.execute_script("arguments[0].scrollIntoView(true);", target_button)
#                     time.sleep(0.5)
#                     driver.execute_script("arguments[0].click();", target_button)
#                     print(f"  ✓ Clicked {category_name} button")
#                     time.sleep(2)  # Wait for data to load
                
#                 # Extract shareholder rows
#                 shareholder_rows = driver.find_elements(
#                     By.CSS_SELECTOR, 
#                     "#quarterly-shp table tbody tr[data-person-url]"
#                 )
                
#                 if not shareholder_rows:
#                     print(f"  ℹ No individual shareholders found for {category_name}")
#                     continue
                
#                 print(f"  📝 Found {len(shareholder_rows)} shareholders")
                
#                 # Extract data from each row
#                 for row in shareholder_rows:
#                     try:
#                         # Get shareholder name
#                         name_elem = row.find_element(By.CSS_SELECTOR, "td.text span")
#                         shareholder_name = name_elem.text.strip()
                        
#                         # Create row data with only name and category
#                         row_data = {
#                             'Shareholder Name': shareholder_name,
#                             'Category': category_name
#                         }
                        
#                         all_shareholder_data.append(row_data)
                        
#                     except Exception as e:
#                         print(f"  ⚠ Error extracting row: {e}")
#                         continue
                
#                 # Collapse the section (click again)
#                 if target_button:
#                     try:
#                         driver.execute_script("arguments[0].click();", target_button)
#                         time.sleep(0.5)
#                     except:
#                         pass
                        
#             except Exception as e:
#                 print(f"  ❌ Error processing {category_name}: {e}")
#                 continue
        
#         # Save to CSV
#         if all_shareholder_data:
#             df = pd.DataFrame(all_shareholder_data)
#             filename = f"{company_ticker}_shareholders.csv"
#             df.to_csv(filename, index=False, encoding="utf-8-sig")
#             print(f"\n✅ Data saved to {os.path.abspath(filename)}")
#             print(f"📊 Total shareholders extracted: {len(all_shareholder_data)}")
            
#             # Display summary
#             print("\n📈 Summary by Category:")
#             print(df['Category'].value_counts())
#         else:
#             print("\n⚠ No shareholder data extracted")
    
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
    
#     finally:
#         print("\n🔚 Closing browser...")
#         driver.quit()


# def scrape_multiple_companies(tickers):
#     """
#     Scrape shareholder data for multiple companies
    
#     Args:
#         tickers: List of stock ticker symbols
#     """
#     for ticker in tickers:
#         print(f"\n{'='*60}")
#         print(f"Starting scrape for: {ticker}")
#         print(f"{'='*60}")
#         scrape_shareholder_data(ticker)
#         time.sleep(3)  # Wait between companies


# if __name__ == "__main__":
#     # Single company example
#     scrape_shareholder_data("HDFCBANK")
    
#     # Multiple companies example (uncomment to use)
#     # companies = ["INFY", "TCS", "WIPRO"]
#     # scrape_multiple_companies(companies)

# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import time
# import pandas as pd
# import os
# import re
# from urllib.parse import quote


# def get_networth_from_trendlyne(driver, shareholder_name):
#     """
#     Fetch net worth for a shareholder from Trendlyne
    
#     Args:
#         driver: Selenium webdriver instance
#         shareholder_name: Name of the shareholder
        
#     Returns:
#         Net worth as string or None if not found
#     """
#     try:
#         # Encode the name for URL
#         encoded_name = quote(shareholder_name)
#         url = f"https://trendlyne.com/portfolio/superstar-shareholders/custom/?query={encoded_name}"
        
#         print(f"    🔍 Checking Trendlyne for: {shareholder_name}")
#         driver.get(url)
#         time.sleep(3)
        
#         # Try to find the net worth element with class fw500
#         try:
#             # Wait for the specific element to load
#             wait = WebDriverWait(driver, 5)
            
#             # Find the span element with class fw500
#             networth_element = wait.until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "span.fw500"))
#             )
            
#             # Get the text from the element
#             full_text = networth_element.text.strip()
            
#             # Extract net worth using regex
#             # Pattern: "2 stocks with a net worth of over Rs 14,048.3 Cr"
#             match = re.search(r'net worth of over\s*Rs\s*([\d,]+\.?\d*)\s*Cr', full_text)
            
#             if match:
#                 networth = match.group(1)
#                 print(f"    ✓ Found net worth: Rs {networth} Cr")
#                 return f"Rs {networth} Cr"
#             else:
#                 print(f"    ℹ No net worth pattern found in: {full_text}")
#                 return None
                
#         except TimeoutException:
#             print(f"    ℹ No net worth element found (span.fw500)")
#             return None
#         except Exception as e:
#             print(f"    ⚠ Error extracting net worth: {e}")
#             return None
            
#     except Exception as e:
#         print(f"    ❌ Error accessing Trendlyne: {e}")
#         return None


# def scrape_shareholder_data(company_ticker):
#     """
#     Scrape shareholder data for a given company from Screener.in
#     and fetch net worth from Trendlyne
    
#     Args:
#         company_ticker: Stock ticker symbol (e.g., 'INFY', 'TCS')
#     """
#     # --- Chrome Setup ---
#     options = Options()
#     options.add_argument("--start-maximized")
#     # Uncomment for headless mode
#     # options.add_argument("--headless=new")
#     options.add_experimental_option("detach", True)
    
#     driver = webdriver.Chrome(options=options)
#     wait = WebDriverWait(driver, 30)
    
#     all_shareholder_data = []
    
#     try:
#         # Navigate directly to the company's shareholding page
#         url = f"https://www.screener.in/company/{company_ticker}/consolidated/#shareholding"
#         driver.get(url)
#         print(f"✓ Opened: {url}")
#         time.sleep(3)  # Wait for page to load completely
        
#         # Scroll to shareholding section
#         try:
#             shareholding_section = wait.until(
#                 EC.presence_of_element_located((By.ID, "shareholding"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", shareholding_section)
#             time.sleep(1)
#         except TimeoutException:
#             print("❌ Could not find shareholding section")
#             return
        
#         # Define shareholder categories to scrape
#         categories = [
#             ('promoters', 'Promoters'),
#             ('foreign_institutions', 'FIIs'),
#             ('domestic_institutions', 'DIIs'),
#             ('government', 'Government'),
#             ('public', 'Public'),
#             ('others', 'Others')
#         ]
        
#         # Extract table headers (only for display purposes)
#         print("\n📊 Extracting shareholder names and net worth...")
        
#         # Process each category
#         for category_id, category_name in categories:
#             print(f"\n🔍 Processing: {category_name}")
            
#             try:
#                 # Find and click the button to expand shareholders
#                 button_selector = f"button[data-tab-id='quarterly-shp'][onclick*=\"showShareholders('{category_id}'\"]"
                
#                 # Try to find the button
#                 buttons = driver.find_elements(By.CSS_SELECTOR, "button.button-plain")
#                 target_button = None
                
#                 for btn in buttons:
#                     onclick_attr = btn.get_attribute("onclick")
#                     if onclick_attr and category_id in onclick_attr and "quarterly" in onclick_attr:
#                         # Check if button shows "+" (collapsed) or "-" (expanded)
#                         icon = btn.find_element(By.CSS_SELECTOR, "span.blue-icon")
#                         if icon.text == "+":
#                             target_button = btn
#                             break
                
#                 if not target_button:
#                     print(f"  ⚠ Button already expanded or not found for {category_name}")
#                     # Try to find expanded data anyway
#                 else:
#                     # Click to expand
#                     driver.execute_script("arguments[0].scrollIntoView(true);", target_button)
#                     time.sleep(0.5)
#                     driver.execute_script("arguments[0].click();", target_button)
#                     print(f"  ✓ Clicked {category_name} button")
#                     time.sleep(2)  # Wait for data to load
                
#                 # Extract shareholder rows
#                 shareholder_rows = driver.find_elements(
#                     By.CSS_SELECTOR, 
#                     "#quarterly-shp table tbody tr[data-person-url]"
#                 )
                
#                 if not shareholder_rows:
#                     print(f"  ℹ No individual shareholders found for {category_name}")
#                     continue
                
#                 print(f"  📝 Found {len(shareholder_rows)} shareholders")
                
#                 # First, collect all shareholder names before navigating away
#                 shareholder_names = []
#                 for row in shareholder_rows:
#                     try:
#                         name_elem = row.find_element(By.CSS_SELECTOR, "td.text span")
#                         shareholder_name = name_elem.text.strip()
#                         shareholder_names.append(shareholder_name)
#                     except Exception as e:
#                         print(f"  ⚠ Error extracting name: {e}")
#                         continue
                
#                 print(f"  📋 Collected {len(shareholder_names)} names")
                
#                 # Now process each shareholder name
#                 for idx, shareholder_name in enumerate(shareholder_names, 1):
#                     try:
#                         print(f"  [{idx}/{len(shareholder_names)}] Processing: {shareholder_name}")
                        
#                         # Get net worth from Trendlyne
#                         networth = get_networth_from_trendlyne(driver, shareholder_name)
                        
#                         # Only add to CSV if net worth is found
#                         if networth:
#                             row_data = {
#                                 'Shareholder Name': shareholder_name,
#                                 'Category': category_name,
#                                 'Net Worth': networth
#                             }
#                             all_shareholder_data.append(row_data)
#                             print(f"    ✅ Added: {shareholder_name}")
#                         else:
#                             print(f"    ⏭ Skipped (no net worth): {shareholder_name}")
                        
#                     except Exception as e:
#                         print(f"  ⚠ Error processing {shareholder_name}: {e}")
#                         continue
                
#                 # Collapse the section (click again)
#                 if target_button:
#                     try:
#                         driver.execute_script("arguments[0].click();", target_button)
#                         time.sleep(0.5)
#                     except:
#                         pass
                        
#             except Exception as e:
#                 print(f"  ❌ Error processing {category_name}: {e}")
#                 continue
        
#         # Save to CSV
#         if all_shareholder_data:
#             df = pd.DataFrame(all_shareholder_data)
#             filename = f"{company_ticker}_shareholders_with_networth.csv"
#             df.to_csv(filename, index=False, encoding="utf-8-sig")
#             print(f"\n✅ Data saved to {os.path.abspath(filename)}")
#             print(f"📊 Total shareholders with net worth extracted: {len(all_shareholder_data)}")
            
#             # Display summary
#             print("\n📈 Summary by Category:")
#             print(df['Category'].value_counts())
#         else:
#             print("\n⚠ No shareholder data with net worth extracted")
    
#     except Exception as e:
#         print(f"❌ Error: {e}")
#         import traceback
#         traceback.print_exc()
    
#     finally:
#         print("\n🔚 Closing browser...")
#         driver.quit()


# def scrape_multiple_companies(tickers):
#     """
#     Scrape shareholder data for multiple companies
    
#     Args:
#         tickers: List of stock ticker symbols
#     """
#     for ticker in tickers:
#         print(f"\n{'='*60}")
#         print(f"Starting scrape for: {ticker}")
#         print(f"{'='*60}")
#         scrape_shareholder_data(ticker)
#         time.sleep(3)  # Wait between companies


# if __name__ == "__main__":
#     # Single company example
#     scrape_shareholder_data("INFY")
    
#     # Multiple companies example (uncomment to use)
#     # companies = ["INFY", "TCS", "WIPRO"]
#     # scrape_multiple_companies(companies)




# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException, NoSuchElementException
# import time
# import pandas as pd
# import os
# import re
# import json
# from urllib.parse import quote
# from datetime import datetime


# def load_stock_tickers_from_json(json_file="market_data.json"):
#     """
#     Load stock tickers from market_data.json
    
#     Args:
#         json_file: Path to the JSON file
        
#     Returns:
#         List of stock ticker symbols (without .NS suffix)
#     """
#     try:
#         with open(json_file, 'r') as f:
#             data = json.load(f)
        
#         # Extract stock names from the 'stocks' section
#         stock_tickers = []
#         if 'stocks' in data:
#             for stock_name, stock_data in data['stocks'].items():
#                 # Use the key (e.g., 'INFY', 'RELIANCE') as the ticker
#                 stock_tickers.append(stock_name)
        
#         print(f"✓ Loaded {len(stock_tickers)} stock tickers from {json_file}")
#         print(f"📋 Tickers: {', '.join(stock_tickers)}")
#         return stock_tickers
    
#     except FileNotFoundError:
#         print(f"❌ File not found: {json_file}")
#         return []
#     except Exception as e:
#         print(f"❌ Error loading JSON: {e}")
#         return []


# def get_networth_from_trendlyne(driver, shareholder_name):
#     """
#     Fetch net worth for a shareholder from Trendlyne
    
#     Args:
#         driver: Selenium webdriver instance
#         shareholder_name: Name of the shareholder
        
#     Returns:
#         Net worth as string or None if not found
#     """
#     try:
#         # Encode the name for URL
#         encoded_name = quote(shareholder_name)
#         url = f"https://trendlyne.com/portfolio/superstar-shareholders/custom/?query={encoded_name}"
        
#         print(f"    🔍 Checking Trendlyne for: {shareholder_name}")
#         driver.get(url)
#         time.sleep(3)
        
#         # Try to find the net worth element with class fw500
#         try:
#             # Wait for the specific element to load
#             wait = WebDriverWait(driver, 5)
            
#             # Find the span element with class fw500
#             networth_element = wait.until(
#                 EC.presence_of_element_located((By.CSS_SELECTOR, "span.fw500"))
#             )
            
#             # Get the text from the element
#             full_text = networth_element.text.strip()
            
#             # Extract net worth using regex
#             # Pattern: "2 stocks with a net worth of over Rs 14,048.3 Cr"
#             match = re.search(r'net worth of over\s*Rs\s*([\d,]+\.?\d*)\s*Cr', full_text)
            
#             if match:
#                 networth = match.group(1)
#                 print(f"    ✓ Found net worth: Rs {networth} Cr")
#                 return f"Rs {networth} Cr"
#             else:
#                 print(f"    ℹ No net worth pattern found in: {full_text}")
#                 return None
                
#         except TimeoutException:
#             print(f"    ℹ No net worth element found (span.fw500)")
#             return None
#         except Exception as e:
#             print(f"    ⚠ Error extracting net worth: {e}")
#             return None
            
#     except Exception as e:
#         print(f"    ❌ Error accessing Trendlyne: {e}")
#         return None


# def scrape_shareholder_data(driver, company_ticker, all_data_list):
#     """
#     Scrape shareholder data for a given company from Screener.in
#     and fetch net worth from Trendlyne
    
#     Args:
#         driver: Selenium webdriver instance (reused)
#         company_ticker: Stock ticker symbol (e.g., 'INFY', 'TCS')
#         all_data_list: List to append shareholder data to
#     """
#     wait = WebDriverWait(driver, 30)
    
#     try:
#         # Navigate directly to the company's shareholding page
#         url = f"https://www.screener.in/company/{company_ticker}/consolidated/#shareholding"
#         driver.get(url)
#         print(f"✓ Opened: {url}")
#         time.sleep(3)  # Wait for page to load completely
        
#         # Scroll to shareholding section
#         try:
#             shareholding_section = wait.until(
#                 EC.presence_of_element_located((By.ID, "shareholding"))
#             )
#             driver.execute_script("arguments[0].scrollIntoView(true);", shareholding_section)
#             time.sleep(1)
#         except TimeoutException:
#             print("❌ Could not find shareholding section")
#             return
        
#         # Define shareholder categories to scrape
#         categories = [
#             ('promoters', 'Promoters'),
#             ('foreign_institutions', 'FIIs'),
#             ('domestic_institutions', 'DIIs'),
#             ('government', 'Government'),
#             ('public', 'Public'),
#             ('others', 'Others')
#         ]
        
#         # Extract table headers (only for display purposes)
#         print("\n📊 Extracting shareholder names and net worth...")
        
#         # Process each category
#         for category_id, category_name in categories:
#             print(f"\n🔍 Processing: {category_name}")
            
#             try:
#                 # Find and click the button to expand shareholders
#                 buttons = driver.find_elements(By.CSS_SELECTOR, "button.button-plain")
#                 target_button = None
                
#                 for btn in buttons:
#                     onclick_attr = btn.get_attribute("onclick")
#                     if onclick_attr and category_id in onclick_attr and "quarterly" in onclick_attr:
#                         # Check if button shows "+" (collapsed) or "-" (expanded)
#                         icon = btn.find_element(By.CSS_SELECTOR, "span.blue-icon")
#                         if icon.text == "+":
#                             target_button = btn
#                             break
                
#                 if not target_button:
#                     print(f"  ⚠ Button already expanded or not found for {category_name}")
#                 else:
#                     # Click to expand
#                     driver.execute_script("arguments[0].scrollIntoView(true);", target_button)
#                     time.sleep(0.5)
#                     driver.execute_script("arguments[0].click();", target_button)
#                     print(f"  ✓ Clicked {category_name} button")
#                     time.sleep(2)  # Wait for data to load
                
#                 # Extract shareholder rows
#                 shareholder_rows = driver.find_elements(
#                     By.CSS_SELECTOR, 
#                     "#quarterly-shp table tbody tr[data-person-url]"
#                 )
                
#                 if not shareholder_rows:
#                     print(f"  ℹ No individual shareholders found for {category_name}")
#                     continue
                
#                 print(f"  📝 Found {len(shareholder_rows)} shareholders")
                
#                 # First, collect all shareholder names before navigating away
#                 shareholder_names = []
#                 for row in shareholder_rows:
#                     try:
#                         name_elem = row.find_element(By.CSS_SELECTOR, "td.text span")
#                         shareholder_name = name_elem.text.strip()
#                         shareholder_names.append(shareholder_name)
#                     except Exception as e:
#                         print(f"  ⚠ Error extracting name: {e}")
#                         continue
                
#                 print(f"  📋 Collected {len(shareholder_names)} names")
                
#                 # Now process each shareholder name
#                 for idx, shareholder_name in enumerate(shareholder_names, 1):
#                     try:
#                         print(f"  [{idx}/{len(shareholder_names)}] Processing: {shareholder_name}")
                        
#                         # Get net worth from Trendlyne
#                         networth = get_networth_from_trendlyne(driver, shareholder_name)
                        
#                         # Only add if net worth is found
#                         if networth:
#                             row_data = {
#                                 'Stock': company_ticker,
#                                 'Shareholder Name': shareholder_name,
#                                 'Category': category_name,
#                                 'Net Worth': networth
#                             }
#                             all_data_list.append(row_data)
#                             print(f"    ✅ Added: {shareholder_name}")
#                         else:
#                             print(f"    ⏭ Skipped (no net worth): {shareholder_name}")
                        
#                     except Exception as e:
#                         print(f"  ⚠ Error processing {shareholder_name}: {e}")
#                         continue
                
#                 # Collapse the section
#                 if target_button:
#                     try:
#                         driver.execute_script("arguments[0].click();", target_button)
#                         time.sleep(0.5)
#                     except:
#                         pass
                        
#             except Exception as e:
#                 print(f"  ❌ Error processing {category_name}: {e}")
#                 continue
    
#     except Exception as e:
#         print(f"❌ Error scraping {company_ticker}: {e}")
#         import traceback
#         traceback.print_exc()


# def scrape_all_stocks(stock_tickers, output_filename="all_shareholders_networth.csv"):
#     """
#     Scrape shareholder data for all stocks and save to single CSV
    
#     Args:
#         stock_tickers: List of stock ticker symbols
#         output_filename: Name of the output CSV file
#     """
#     # --- Chrome Setup ---
#     options = Options()
#     options.add_argument("--start-maximized")
#     # Uncomment for headless mode
#     # options.add_argument("--headless=new")
#     options.add_experimental_option("detach", True)
    
#     driver = webdriver.Chrome(options=options)
#     all_shareholder_data = []
    
#     try:
#         total_stocks = len(stock_tickers)
        
#         for idx, ticker in enumerate(stock_tickers, 1):
#             print(f"\n{'='*70}")
#             print(f"📈 [{idx}/{total_stocks}] Processing Stock: {ticker}")
#             print(f"{'='*70}")
            
#             scrape_shareholder_data(driver, ticker, all_shareholder_data)
            
#             print(f"\n✓ Completed {ticker}")
#             print(f"📊 Total shareholders collected so far: {len(all_shareholder_data)}")
            
#             # Small delay between stocks
#             if idx < total_stocks:
#                 time.sleep(2)
        
#         # Save all data to single CSV
#         if all_shareholder_data:
#             df = pd.DataFrame(all_shareholder_data)
            
#             # Add timestamp
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             final_filename = f"{timestamp}_{output_filename}"
            
#             df.to_csv(final_filename, index=False, encoding="utf-8-sig")
            
#             print(f"\n{'='*70}")
#             print(f"✅ ALL DATA SAVED TO: {os.path.abspath(final_filename)}")
#             print(f"{'='*70}")
#             print(f"📊 Total shareholders with net worth: {len(all_shareholder_data)}")
#             print(f"\n📈 Summary by Stock:")
#             print(df['Stock'].value_counts())
#             print(f"\n📈 Summary by Category:")
#             print(df['Category'].value_counts())
#             print(f"{'='*70}")
#         else:
#             print("\n⚠ No shareholder data with net worth was extracted")
    
#     except Exception as e:
#         print(f"❌ Fatal Error: {e}")
#         import traceback
#         traceback.print_exc()
    
#     finally:
#         print("\n🔚 Closing browser...")
#         driver.quit()


# if __name__ == "__main__":
#     print("="*70)
#     print("🚀 MULTI-STOCK SHAREHOLDER NET WORTH SCRAPER")
#     print("="*70)
    
#     # Load stock tickers from market_data.json
#     stock_tickers = load_stock_tickers_from_json("market_data.json")
    
#     if not stock_tickers:
#         print("❌ No stock tickers found. Exiting...")
#     else:
#         # Scrape all stocks and save to single CSV
#         scrape_all_stocks(stock_tickers)
        
#     print("\n✅ Script completed!")




from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
import pandas as pd
import os
import re
import json
from urllib.parse import quote
from datetime import datetime


def load_stock_tickers_from_json(json_file="market_data.json"):
    """
    Load stock tickers from market_data.json
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        List of stock ticker symbols
    """
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        stock_tickers = []
        if 'stocks' in data:
            for stock_name in data['stocks'].keys():
                stock_tickers.append(stock_name)
        
        print(f"✓ Loaded {len(stock_tickers)} stock tickers from {json_file}")
        print(f"📋 Tickers: {', '.join(stock_tickers)}")
        return stock_tickers
    
    except FileNotFoundError:
        print(f"❌ File not found: {json_file}")
        return []
    except Exception as e:
        print(f"❌ Error loading JSON: {e}")
        return []


def scrape_shareholders_only(driver, company_ticker):
    """
    PHASE 1: Scrape only shareholder names (no net worth lookup)
    
    Args:
        driver: Selenium webdriver instance
        company_ticker: Stock ticker symbol
        
    Returns:
        List of dictionaries with stock, name, and category
    """
    wait = WebDriverWait(driver, 30)
    shareholders = []
    
    try:
        url = f"https://www.screener.in/company/{company_ticker}/consolidated/#shareholding"
        driver.get(url)
        print(f"  ✓ Opened: {url}")
        time.sleep(3)
        
        # Scroll to shareholding section
        try:
            shareholding_section = wait.until(
                EC.presence_of_element_located((By.ID, "shareholding"))
            )
            driver.execute_script("arguments[0].scrollIntoView(true);", shareholding_section)
            time.sleep(1)
        except TimeoutException:
            print("  ❌ Could not find shareholding section")
            return shareholders
        
        categories = [
            ('promoters', 'Promoters'),
            ('foreign_institutions', 'FIIs'),
            ('domestic_institutions', 'DIIs'),
            ('government', 'Government'),
            ('public', 'Public'),
            ('others', 'Others')
        ]
        
        # Process each category
        for category_id, category_name in categories:
            try:
                # Find and click the button to expand shareholders
                buttons = driver.find_elements(By.CSS_SELECTOR, "button.button-plain")
                target_button = None
                
                for btn in buttons:
                    onclick_attr = btn.get_attribute("onclick")
                    if onclick_attr and category_id in onclick_attr and "quarterly" in onclick_attr:
                        icon = btn.find_element(By.CSS_SELECTOR, "span.blue-icon")
                        if icon.text == "+":
                            target_button = btn
                            break
                
                if target_button:
                    driver.execute_script("arguments[0].scrollIntoView(true);", target_button)
                    time.sleep(0.5)
                    driver.execute_script("arguments[0].click();", target_button)
                    time.sleep(2)
                
                # Extract shareholder rows
                shareholder_rows = driver.find_elements(
                    By.CSS_SELECTOR, 
                    "#quarterly-shp table tbody tr[data-person-url]"
                )
                
                if not shareholder_rows:
                    continue
                
                # Collect shareholder names
                for row in shareholder_rows:
                    try:
                        name_elem = row.find_element(By.CSS_SELECTOR, "td.text span")
                        shareholder_name = name_elem.text.strip()
                        
                        shareholders.append({
                            'Stock': company_ticker,
                            'Shareholder Name': shareholder_name,
                            'Category': category_name
                        })
                    except Exception as e:
                        continue
                
                print(f"    ✓ {category_name}: {len([s for s in shareholders if s['Category'] == category_name and s['Stock'] == company_ticker])} shareholders")
                
                # Collapse the section
                if target_button:
                    try:
                        driver.execute_script("arguments[0].click();", target_button)
                        time.sleep(0.5)
                    except:
                        pass
                        
            except Exception as e:
                print(f"    ⚠ Error in {category_name}: {e}")
                continue
    
    except Exception as e:
        print(f"  ❌ Error scraping {company_ticker}: {e}")
    
    return shareholders


def get_networth_from_trendlyne(driver, shareholder_name):
    """
    PHASE 2: Fetch net worth for a shareholder from Trendlyne
    
    Args:
        driver: Selenium webdriver instance
        shareholder_name: Name of the shareholder
        
    Returns:
        Net worth as string or None if not found
    """
    try:
        encoded_name = quote(shareholder_name)
        url = f"https://trendlyne.com/portfolio/superstar-shareholders/custom/?query={encoded_name}"
        
        driver.get(url)
        time.sleep(3)
        
        try:
            wait = WebDriverWait(driver, 5)
            networth_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "span.fw500"))
            )
            
            full_text = networth_element.text.strip()
            match = re.search(r'net worth of over\s*Rs\s*([\d,]+\.?\d*)\s*Cr', full_text)
            
            if match:
                networth = match.group(1)
                return f"Rs {networth} Cr"
            else:
                return None
                
        except TimeoutException:
            return None
        except Exception as e:
            return None
            
    except Exception as e:
        return None


def phase1_collect_all_shareholders(stock_tickers):
    """
    PHASE 1: Collect all shareholders from all stocks
    
    Args:
        stock_tickers: List of stock ticker symbols
        
    Returns:
        DataFrame with all shareholders (no net worth yet)
    """
    print("\n" + "="*70)
    print("🔍 PHASE 1: COLLECTING ALL SHAREHOLDERS FROM ALL STOCKS")
    print("="*70)
    
    options = Options()
    options.add_argument("--start-maximized")
    # Uncomment for headless mode
    # options.add_argument("--headless=new")
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(options=options)
    all_shareholders = []
    
    try:
        total_stocks = len(stock_tickers)
        
        for idx, ticker in enumerate(stock_tickers, 1):
            print(f"\n📈 [{idx}/{total_stocks}] Scraping shareholders from: {ticker}")
            shareholders = scrape_shareholders_only(driver, ticker)
            all_shareholders.extend(shareholders)
            print(f"  ✅ Collected {len(shareholders)} shareholders from {ticker}")
            print(f"  📊 Running total: {len(all_shareholders)} shareholders")
            
            if idx < total_stocks:
                time.sleep(2)
        
        df = pd.DataFrame(all_shareholders)
        
        # Save Phase 1 results
       
        phase1_file = f"phase1_all_shareholders.csv"
        df.to_csv(phase1_file, index=False, encoding="utf-8-sig")
        
        print(f"\n{'='*70}")
        print(f"✅ PHASE 1 COMPLETE!")
        print(f"📁 Saved to: {os.path.abspath(phase1_file)}")
        print(f"📊 Total shareholders collected: {len(all_shareholders)}")
        print(f"\n📈 Summary by Stock:")
        print(df['Stock'].value_counts())
        print(f"\n📈 Summary by Category:")
        print(df['Category'].value_counts())
        print(f"{'='*70}")
        
        return df, phase1_file, driver
        
    except Exception as e:
        print(f"❌ Error in Phase 1: {e}")
        import traceback
        traceback.print_exc()
        driver.quit()
        return None, None, None


def phase2_fetch_networth(df, phase1_file, driver):
    """
    PHASE 2: Fetch net worth for all shareholders and keep only those with data
    
    Args:
        df: DataFrame from Phase 1
        phase1_file: Filename from Phase 1
        driver: Selenium webdriver instance (reused)
    """
    print("\n" + "="*70)
    print("💰 PHASE 2: FETCHING NET WORTH FOR ALL SHAREHOLDERS")
    print("="*70)
    
    try:
        total_shareholders = len(df)
        shareholders_with_networth = []
        
        print(f"\n🔍 Processing {total_shareholders} shareholders...")
        print(f"⏱ Estimated time: ~{total_shareholders * 3 / 60:.1f} minutes\n")
        
        for idx, row in df.iterrows():
            shareholder_name = row['Shareholder Name']
            stock = row['Stock']
            category = row['Category']
            
            progress = f"[{idx+1}/{total_shareholders}]"
            print(f"{progress} Checking: {shareholder_name} ({stock})")
            
            # Fetch net worth
            networth = get_networth_from_trendlyne(driver, shareholder_name)
            
            if networth:
                shareholders_with_networth.append({
                    'Stock': stock,
                    'Shareholder Name': shareholder_name,
                    'Category': category,
                    'Net Worth': networth
                })
                print(f"  ✅ Found: {networth}")
            else:
                print(f"  ⏭ Skipped (no net worth data)")
            
            # Show progress every 10 shareholders
            if (idx + 1) % 10 == 0:
                print(f"\n📊 Progress: {idx+1}/{total_shareholders} checked | {len(shareholders_with_networth)} with net worth found\n")
        
        # Save Phase 2 results (final output)
        if shareholders_with_networth:
            final_df = pd.DataFrame(shareholders_with_networth)
            
            final_file = f"final_shareholders_with_networth.csv"
            final_df.to_csv(final_file, index=False, encoding="utf-8-sig")
            
            print(f"\n{'='*70}")
            print(f"✅ PHASE 2 COMPLETE!")
            print(f"📁 Final output saved to: {os.path.abspath(final_file)}")
            print(f"{'='*70}")
            print(f"📊 Statistics:")
            print(f"  - Total shareholders checked: {total_shareholders}")
            print(f"  - Shareholders with net worth: {len(shareholders_with_networth)}")
            print(f"  - Shareholders without net worth (removed): {total_shareholders - len(shareholders_with_networth)}")
            print(f"  - Success rate: {len(shareholders_with_networth)/total_shareholders*100:.1f}%")
            print(f"\n📈 Final Summary by Stock:")
            print(final_df['Stock'].value_counts())
            print(f"\n📈 Final Summary by Category:")
            print(final_df['Category'].value_counts())
            print(f"{'='*70}")
            
        else:
            print("\n⚠ No shareholders with net worth data found")
        
    except Exception as e:
        print(f"❌ Error in Phase 2: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n🔚 Closing browser...")
        driver.quit()


if __name__ == "__main__":
    print("="*70)
    print("🚀 TWO-PHASE SHAREHOLDER NET WORTH SCRAPER")
    print("="*70)
    print("\nThis script works in 2 phases:")
    print("  PHASE 1: Collect all shareholders from all stocks")
    print("  PHASE 2: Fetch net worth data and keep only valid entries")
    print("="*70)
    
    # Load stock tickers from market_data.json
    stock_tickers = load_stock_tickers_from_json("market_data.json")
    
    if not stock_tickers:
        print("❌ No stock tickers found. Exiting...")
    else:
        # PHASE 1: Collect all shareholders
        df, phase1_file, driver = phase1_collect_all_shareholders(stock_tickers)
        
        if df is not None and driver is not None:
            # PHASE 2: Fetch net worth and filter
            phase2_fetch_networth(df, phase1_file, driver)
        
    print("\n✅ Script completed!")