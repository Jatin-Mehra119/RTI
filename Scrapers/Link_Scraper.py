import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm

def extract_case_law_details(start_page=0, end_page=10, output_file="case_law_data.xlsx", append_mode=False):
    # Define the base URL
    base_url = "https://www.rtifoundationofindia.com"
    
    # Create a list to store all extracted data
    all_data = []
    
    # Load existing data if in append mode
    if append_mode and output_file:
        try:
            existing_df = pd.read_excel(output_file)
            all_data = existing_df.to_dict('records')
            print(f"Loaded {len(all_data)} existing records from {output_file}")
        except FileNotFoundError:
            print(f"No existing file found at {output_file}. Will create a new file.")
        except Exception as e:
            print(f"Error loading existing data: {str(e)}")
    
    # Loop through all pages
    for page_num in tqdm(range(start_page, end_page + 1), desc="Scraping pages"):
        # Construct the pagination URL
        page_url = f"{base_url}/?page=0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C0%2C{page_num}"
        
        # Fetch the webpage
        try:
            response = requests.get(page_url)
            if response.status_code != 200:
                print(f"Failed to fetch page {page_num}: {response.status_code}")
                continue
                
            # Parse the HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Locate the content block
            content_block = soup.find('div', id='content_listing_block')
            if not content_block:
                print(f"Content block not found on page {page_num}.")
                continue
            
            # Find the table
            table = content_block.find('table')
            if not table:
                print(f"Table not found on page {page_num}.")
                continue
            
            # Find all <td> elements containing case law entries
            td_elements = table.select('td:has(span.date_cls)')
            if not td_elements:
                print(f"No case law entries found on page {page_num}.")
                continue
            
            # Extract details from each <td>
            page_entries = 0
            for td in td_elements:
                # Extract date
                date_tag = td.select_one('span.date_cls')
                date = date_tag.get_text(strip=True) if date_tag else "No date"
                
                # Extract summary and link
                summary_tag = td.select_one('span.display1_teaser > a')
                summary = summary_tag.get_text(strip=True) if summary_tag else "No summary"
                link = base_url + summary_tag['href'] if summary_tag and summary_tag.has_attr('href') else "No link"
                
                # Add to data list
                all_data.append({
                    'Date': date,
                    'Summary': summary,
                    'Link': link,
                    'Page': page_num
                })
                page_entries += 1
            
            print(f"Processed page {page_num}: Found {page_entries} entries")
            
            # Add a small delay to be respectful to the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error processing page {page_num}: {str(e)}")
    
    if all_data:
        # Create DataFrame from collected data
        df = pd.DataFrame(all_data)
        
        # Save to csv
        df.to_csv(output_file, index=False)
        print(f"\nScraped {len(all_data)} case law entries.")
        print(f"Data saved to {output_file}")
    else:
        print("No data was collected.")
    
    return all_data

def main():
    # Set up argument parser
    start = 0
    end = 750
    output_file = "links/case_law_data.csv"
    append_mode = False
    
    return extract_case_law_details(
        start_page=start, 
        end_page=end,
        output_file=output_file,
        append_mode=append_mode
    )

if __name__ == "__main__":
    main()