import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
import csv
import json
import os

# Set up logging
logging.basicConfig(filename='scraper_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# URL to scrape (for testing; script uses URLs from Excel)
url = "https://www.rtifoundationofindia.com/respondent-leave-accounts-employees-recruited-secr"

def extract_rti_case_content(url):
    print(f"Scraping URL: {url}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        h1_tag = soup.find('h1', style=lambda x: x and 'background-color:#FFCC00' in x)
        if not h1_tag:
            raise ValueError("Could not find content heading.")

        content_lines = []
        content_lines.append(f"# {h1_tag.get_text(strip=True)}")

        date_span = h1_tag.find_next('span', class_='innerArticle_span', style=lambda x: x and 'background-color:#FFCC00' in x)
        if date_span:
            content_lines.append(f"**Date**: {date_span.get_text(strip=True)}")

        current_element = date_span.find_next() if date_span else h1_tag.find_next()
        while current_element and current_element.get('id') != 'article-end':
            if current_element.name == 'p':
                text = current_element.get_text(strip=True)
                if not text:
                    current_element = current_element.find_next()
                    continue

                span = current_element.find('span', style=lambda x: x and 'color:#ff0000' in x)
                if span:
                    content_lines.append(f"## {span.get_text(strip=True)}")
                    remaining_text = current_element.get_text(strip=True).replace(span.get_text(strip=True), '').strip()
                    if remaining_text:
                        content_lines.append(remaining_text)
                else:
                    if current_element.get('style', '').startswith('margin-left'):
                        content_lines.append(f"  {text}")
                    else:
                        content_lines.append(text)

            elif current_element.name == 'span' and 'color:#0000ff' in current_element.get('style', ''):
                content_lines.append(f"**{current_element.get_text(strip=True)}**")

            current_element = current_element.find_next()

        content_text = '\n\n'.join(line for line in content_lines if line.strip())
        content_text = content_text.replace('\r', '').replace('\t', ' ')
        return content_text

    except (requests.exceptions.RequestException, ValueError) as e:
        logging.error(f"Failed to scrape {url}: {str(e)}")
        print(f"Error occurred for {url}: {e}")
        return None

def main():
    try:
        df = pd.read_csv('links/case_law_data.csv')
        df['Content'] = df['Link'].apply(lambda x: extract_rti_case_content(x) if pd.notna(x) else None)
        df['Content_Length'] = df['Content'].apply(lambda x: len(x) if pd.notna(x) else 0)
        df['Scrape_Status'] = df['Content'].apply(lambda x: "Success" if pd.notna(x) else "Failed")

        # Create output directory if it doesn't exist
        os.makedirs('Extracted_data', exist_ok=True)

        # Save full content (markdown format) into CSV
        df.to_csv('Extracted_data/case_law_data_with_content.csv', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_NONNUMERIC)

        # Save full content into JSONL (one JSON object per line)
        with open('Extracted_data/rti_cases.jsonl', 'w', encoding='utf-8') as f:
            for _, row in df.iterrows():
                if pd.notna(row['Content']):
                    json.dump({"text": row["Content"]}, f)
                    f.write('\n')

        print("Scraping complete. Data saved to CSV and JSONL.")
        return True
    except Exception as e:
        print(f"Error in content scraping: {str(e)}")
        logging.error(f"Error in content scraping: {str(e)}")
        return False

if __name__ == "__main__":
    main()