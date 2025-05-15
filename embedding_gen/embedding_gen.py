# Create embeddings for the text files, csv files.

import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
import logging
import torch

# Set up logging and save logs to a file
log_file = 'logs/embedding_gen.log'
logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
# Create a logger
logger = logging.getLogger(__name__)

def create_embeddings(input_dir, output_dir, model_name='all-MiniLM-L6-v2'):
    """
    Create embeddings for text files and csv files in the input directory and save them to the output directory.
    
    Args:
        input_dir (str): Path to the input directory containing text and csv files.
        output_dir (str): Path to the output directory where embeddings will be saved.
        model_name (str): Name of the SentenceTransformer model to use for generating embeddings.
    """
    # Load the pre-trained model
    model = SentenceTransformer(model_name, trust_remote_code=True)

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over all files in the input directory
    for filename in tqdm(os.listdir(input_dir)):
        file_path = os.path.join(input_dir, filename)
        
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            sentences = text.split('\n')
        
        elif filename.endswith('.csv'):
            df = pd.read_csv(file_path)
            try:
                sentences = df['Content'].tolist()
            except:
                sentences = df['content'].tolist()
        
        else:
            continue  # Skip non-text and non-csv files

        # Generate embeddings
        embeddings = model.encode(sentences, batch_size=4, show_progress_bar=True)
        

        # Save embeddings to a file
        embedding_file_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_embeddings.npy")
        np.save(embedding_file_path, embeddings)  # Save as .npy file
        torch.cuda.empty_cache()


        # Log the completion of the file
        logger.info(f"Processed {filename}: {len(sentences)} sentences, saved embeddings to {embedding_file_path}")
        print(f"Processed {filename}: {len(sentences)} sentences, saved embeddings to {embedding_file_path}")

def main():
    try:
        # Create log directory if it doesn't exist
        os.makedirs('logs', exist_ok=True)
        
        # Log the start of the script
        logger.info("Started creating embeddings.")
        input_directory = 'Cleaned_data/'  # Directory containing text and csv files
        output_directory = 'output_embeddings'  # Directory to save embeddings
        model_name = 'nomic-ai/nomic-embed-text-v1.5'  # Pre-trained model 
        
        # Log the model being used, output directory, and input directory
        logger.info(f"Using model: {model_name}")
        logger.info(f"Input directory: {input_directory}")
        logger.info(f"Output directory: {output_directory}")

        create_embeddings(input_directory, output_directory, model_name)
        
        # Log the completion of the script
        logger.info("Completed creating embeddings.")
        print("Embeddings created and saved successfully.")
        return True
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        print(f"Error generating embeddings: {str(e)}")
        return False

if __name__ == "__main__":
    main()