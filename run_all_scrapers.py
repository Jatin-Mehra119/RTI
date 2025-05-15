#!/usr/bin/env python
# filepath: c:\Users\admin\Desktop\Jatin\RTI\run_all_scrapers.py
"""
RTI Data Processing Pipeline Orchestrator

This script runs all the scraper and data processing scripts in the correct sequence:
1. Link_Scraper.py - Extract case law links
2. Content_Scraper.py - Extract content from the links
3. pdf_extracter.py - Extract text from RTI guide PDF
4. pdf_Q&Aextracter.py - Extract FAQs from PDF
5. embedding_gen.py - Generate embeddings for the extracted data

Usage:
    python run_all_scrapers.py
"""

import os
import sys
import time
import importlib.util
import logging
from datetime import datetime

# Configure logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f'pipeline_run_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def import_script(script_path):
    """Dynamically import a Python script as a module."""
    module_name = os.path.basename(script_path).replace(".py", "")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def run_script(script_path, script_name):
    """Run a script and handle exceptions."""
    logger.info(f"Starting {script_name}...")
    start_time = time.time()
    
    try:
        # Create necessary directories if they don't exist
        for dir_path in ['Extracted_data', 'Cleaned_data', 'links', 'output_embeddings']:
            os.makedirs(dir_path, exist_ok=True)
        
        # Import and run the script
        script_module = import_script(script_path)
        
        # For scripts with main function, run it directly
        if hasattr(script_module, 'main'):
            script_module.main()
        # If not, the code will have executed during import
        
        elapsed_time = time.time() - start_time
        logger.info(f"Completed {script_name} in {elapsed_time:.2f} seconds")
        return True
        
    except Exception as e:
        logger.error(f"Error in {script_name}: {str(e)}", exc_info=True)
        return False

def main():
    """Run all scripts in sequence."""
    scripts = [
        ("Scrapers/Link_Scraper.py", "Link Scraper"),
        ("Scrapers/Content_Scraper.py", "Content Scraper"),
        ("Scrapers/pdf_extracter.py", "PDF Extractor"),
        ("Scrapers/pdf_Q&Aextracter.py", "PDF Q&A Extractor"),
        ("embedding_gen/embedding_gen.py", "Embedding Generator")
    ]
    
    logger.info("Starting RTI Data Processing Pipeline")
    print("\n" + "="*50)
    print(" RTI DATA PROCESSING PIPELINE STARTED ".center(50, "="))
    print("="*50 + "\n")
    
    start_time = time.time()
    successful_steps = 0
    failed_steps = 0
    
    for script_path, script_name in scripts:
        absolute_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script_path)
        
        if not os.path.exists(absolute_path):
            logger.error(f"Script not found: {absolute_path}")
            print(f"❌ ERROR: Script not found: {script_path}")
            failed_steps += 1
            continue
        
        print(f"\n[{successful_steps + failed_steps + 1}/{len(scripts)}] Running {script_name}...")
        success = run_script(absolute_path, script_name)
        
        if success:
            print(f"✅ {script_name} completed successfully")
            successful_steps += 1
        else:
            print(f"❌ {script_name} failed")
            failed_steps += 1
            user_input = input(f"\nPipeline encountered an error in {script_name}. Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                logger.error(f"Pipeline stopped at {script_name} due to errors (user requested)")
                break
    
    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    
    print("\n" + "="*50)
    print(" PIPELINE EXECUTION SUMMARY ".center(50, "="))
    print("="*50)
    print(f"Total steps: {len(scripts)}")
    print(f"Successful: {successful_steps}")
    print(f"Failed: {failed_steps}")
    print(f"Total time: {int(minutes)} minutes, {int(seconds)} seconds")
    print("="*50 + "\n")
    
    logger.info(f"RTI Data Processing Pipeline completed with {successful_steps} successful and {failed_steps} failed steps")

if __name__ == "__main__":
    main()
