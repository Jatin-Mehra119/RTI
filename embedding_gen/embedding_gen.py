import os
import pandas as pd
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import numpy as np
import json
import logging
import torch

# Set up logging
log_file = 'logs/embedding_gen.log'
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename=log_file, filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def chunk_text(text, chunk_size=200, overlap=20):
    """
    Split text into overlapping chunks of words.
    """
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks


def create_embeddings(input_dir, output_dir, model_name='all-MiniLM-L6-v2'):
    """
    Create embeddings and metadata from text/csv files for RAG applications.
    """
    model = SentenceTransformer(model_name, trust_remote_code=True)
    os.makedirs(output_dir, exist_ok=True)

    all_embeddings = []
    all_metadata = []

    for filename in tqdm(os.listdir(input_dir)):
        file_path = os.path.join(input_dir, filename)
        
        if filename.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
            chunks = chunk_text(text)

        elif filename.endswith('.csv'):
            try:
                df = pd.read_csv(file_path)
                content_col = 'Content' if 'Content' in df.columns else 'content'
                chunks = []
                for idx, row in df.iterrows():
                    row_text = str(row[content_col])
                    row_chunks = chunk_text(row_text)
                    chunks.extend(row_chunks)
            except Exception as e:
                logger.warning(f"Skipping {filename} due to error: {e}")
                continue
        else:
            continue

        # Generate embeddings
        embeddings = model.encode(chunks, batch_size=4, show_progress_bar=True)

        # Collect embeddings and metadata
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            all_embeddings.append(emb)
            all_metadata.append({
                "source_file": filename,
                "chunk_index": i,
                "text": chunk
            })

        logger.info(f"Processed {filename}: {len(chunks)} chunks.")

        torch.cuda.empty_cache()

    # Save final embedding and metadata
    np.save(os.path.join(output_dir, 'embeddings.npy'), np.array(all_embeddings))
    with open(os.path.join(output_dir, 'metadata.json'), 'w', encoding='utf-8') as meta_file:
        json.dump(all_metadata, meta_file, indent=2, ensure_ascii=False)

    logger.info(f"Saved total {len(all_embeddings)} embeddings and metadata.")
    print(f"Saved {len(all_embeddings)} embeddings and metadata to {output_dir}")


def main():
    try:
        logger.info("Started creating RAG-ready embeddings.")
        input_directory = 'Cleaned_data/'
        output_directory = 'output_embeddings_rag/'
        model_name = 'nomic-ai/nomic-embed-text-v1.5'

        logger.info(f"Model: {model_name}")
        logger.info(f"Input directory: {input_directory}")
        logger.info(f"Output directory: {output_directory}")

        create_embeddings(input_directory, output_directory, model_name)

        logger.info("Completed RAG embedding generation.")
        print("RAG embeddings and metadata saved successfully.")
        return True
    except Exception as e:
        logger.error(f"Error generating RAG embeddings: {str(e)}")
        print(f"Error generating RAG embeddings: {str(e)}")
        return False


if __name__ == "__main__":
    main()