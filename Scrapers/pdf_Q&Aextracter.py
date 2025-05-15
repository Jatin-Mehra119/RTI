import PyPDF2
import pandas as pd
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_faqs(text):
    """Extract FAQs from the text."""
    faqs = []
    current_question = None
    current_answer = []
    
    # Split text into lines and remove empty lines/page separators
    lines = [line.strip() for line in text.split('\n') 
             if line.strip() and not re.match(r'=+ Page \d+ =+', line)]
    
    for line in lines:
        # Check for section headers (e.g., "1. General Questions")
        if re.match(r'^\d+\.\s+[A-Za-z]', line):
            continue
        
        # Check for question pattern (e.g., "1.1.", "2.3.")
        question_match = re.match(r'^(\d+\.\d+\.)\s+(.*)', line)
        if question_match:
            if current_question:
                # Save previous Q&A
                faqs.append((current_question, ' '.join(current_answer)))
                current_answer = []
            
            current_question = question_match.group(2).strip()
            answer_start = line[len(question_match.group(0)):].strip()
            if answer_start:
                current_answer.append(answer_start)
        else:
            if current_question is not None:
                current_answer.append(line)
    
    # Add the last Q&A pair
    if current_question:
        faqs.append((current_question, ' '.join(current_answer)))
    
    return faqs

def save_faqs_to_csv(faqs, output_path):
    """Save FAQs to a CSV file."""
    df = pd.DataFrame(faqs, columns=['Question', 'Answer'])
    df.to_csv(output_path, index=False, encoding='utf-8')

def main():
    try:
        import os
        # Ensure the output directory exists
        os.makedirs('Extracted_data', exist_ok=True)
        
        pdf_path = 'pdfs/RTI FAQs INCOIS.pdf'
        output_csv = 'Extracted_data/rti_faqs.csv'

        # Extract and save FAQs
        text = extract_text_from_pdf(pdf_path)
        faqs = extract_faqs(text)
        save_faqs_to_csv(faqs, output_csv)

        print(f"Successfully extracted {len(faqs)} FAQs to {output_csv}")
        return True
    except Exception as e:
        print(f"Error extracting FAQs from PDF: {str(e)}")
        return False

if __name__ == "__main__":
    main()