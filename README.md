# RTI-Knowledge-Pipeline

This project automates the extraction, processing, and embedding generation for Right to Information (RTI) data from various sources including websites and PDF documents.

## Project Structure

```
├── Cleaned_data/                  # Cleaned and processed data
├── embedding_gen/                 # Scripts for generating embeddings
├── Extracted_data/                # Raw extracted data
├── links/                         # Extracted links for scraping
├── logs/                          # Log files from pipeline runs
├── Misc/                          # Miscellaneous scripts
├── output_embeddings/             # Generated embeddings
├── pdfs/                          # Source PDF files
├── Scrapers/                      # Individual scraper scripts
│   ├── Link_Scraper.py            # Extracts case law links
│   ├── Content_Scraper.py         # Extracts content from links
│   ├── pdf_extracter.py           # Extracts text from RTI guide PDF
│   └── pdf_Q&Aextracter.py        # Extracts FAQs from PDF
├── requirements.txt               # Project dependencies
└── run_all_scrapers.py            # Main orchestrator script
```

## Workflow

The pipeline automates the following steps:

1. **Link Scraping**: Extract case law links from RTI Foundation of India website
2. **Content Scraping**: Extract detailed content from each link
3. **PDF Text Extraction**: Extract raw text from the RTI Guide PDF
4. **PDF Q&A Extraction**: Extract FAQs from the RTI FAQ PDF
5. **Embedding Generation**: Generate embeddings for all extracted text data

## Setup Instructions

1. Create and activate a Python virtual environment:
   ```
   python -m venv venv
   .\venv\Scripts\activate
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Running the Pipeline

### Running the Python Orchestrator Directly

To run the full pipeline in sequence:

```
python run_all_scrapers.py
```

### Running Individual Scripts

Each script can also be run individually if needed:

```
python Scrapers/Link_Scraper.py
python Scrapers/Content_Scraper.py
python Scrapers/pdf_extracter.py
python Scrapers/pdf_Q&Aextracter.py
python embedding_gen/embedding_gen.py
```

## Logs

All pipeline logs are saved in the `logs/` directory with timestamps for tracking and debugging.

## Output

- **case_law_data.csv**: Contains the extracted links and summaries
- **case_law_data_with_content.csv**: Contains the full extracted content from each link
- **rti_cases.jsonl**: Contains the extracted content in JSONL format
- **rti_faqs.csv**: Contains extracted FAQs from the PDF
- **cleaned_guide.txt**: Contains cleaned text from the RTI guide PDF
- **output_embeddings/**: Contains the generated embeddings for all processed data
