import PyPDF2
import re

def extract_text_from_pdf(pdf_path):
    """Extract raw text from a PDF file."""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page in reader.pages:
            text += page.extract_text() + '\n'  # Ensure page separation
        return text

def clean_extracted_text(text):
    """Clean the extracted text by removing page markers, footers, and other noise."""
    cleaned_lines = []
    for line in text.split('\n'):
        line = line.strip()
        
        # Remove page markers (e.g., "===== Page 1 =====")
        if re.match(r'^===== Page \d+( \[text layer\])? =====$', line):
            continue
        
        # Remove footer lines (e.g., "6 Guide on Right to Information Act, 2005")
        if re.match(r'^\d+ Guide on Right to Information Act,? 2005$', line):
            continue
        
        # Remove standalone page numbers (e.g., "9")
        if re.match(r'^\d+$', line):
            continue
        
        # Remove trailing page numbers (e.g., "Part I - ... 7" → "Part I - ...")
        line = re.sub(r'\s+\d+$', '', line)
        
        cleaned_lines.append(line)
    
    # Join lines and remove excessive empty lines
    cleaned_text = '\n'.join([line for line in cleaned_lines if line])
    return cleaned_text

def main():
    try:
        # Make sure output directory exists
        import os
        os.makedirs("Cleaned_data", exist_ok=True)
        
        pdf_path = "pdfs/GuideonRTI.pdf"
        raw_text = extract_text_from_pdf(pdf_path)
        clean_text = clean_extracted_text(raw_text)

        # Save cleaned text to a file
        output_file = "Cleaned_data/cleaned_guide.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(clean_text)

        print(f"Cleaned text extracted and saved to '{output_file}'.")
        return True
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return False

if __name__ == "__main__":
    main()