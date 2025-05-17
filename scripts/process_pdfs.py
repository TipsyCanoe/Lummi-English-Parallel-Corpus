import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import os

PDF_FOLDER = 'pdfs/'
OUTPUT_FOLDER = 'raw_data/'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def process_pdf(pdf_path):
    print(f"Processing: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)

    data = []
    for image in images:
        text = pytesseract.image_to_string(image)
        lines = text.split("\n")
        
        for i in range(0, len(lines) - 1, 2):
            lummi_text = lines[i].strip()
            english_text = lines[i + 1].strip()
            if lummi_text and english_text:
                data.append({'lummi_sentence': lummi_text, 'english_sentence': english_text})

    output_file = os.path.join(OUTPUT_FOLDER, os.path.basename(pdf_path).replace('.pdf', '.csv'))
    pd.DataFrame(data).to_csv(output_file, index=False)
    print(f"Saved to {output_file}")
