# First, install the necessary library if you haven't already:
# pip install PyMuPDF

import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    # Open the PDF file
    with fitz.open(pdf_path) as doc:
        text = ''
        # Extract text from each page
        for page in doc:
            text += page.get_text()
    return text

# Example usage
pdf_path = '3000 Yemek Tarifi.pdf'
pdf_text = extract_text_from_pdf(pdf_path)

# Print or save the extracted text
# print(pdf_text)

# Optionally, save it to a text file
with open('extracted_text.txt', 'w', encoding='utf-8') as file:
    file.write(pdf_text)
