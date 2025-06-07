import pytesseract
from pdf2image import convert_from_path
import pandas as pd
import os
import re

PDF_FOLDER = 'pdf/'
OUTPUT_FOLDER = 'processed_data/processed_pdfs/'
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Optional: If needed, specify path to Tesseract binary
pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract'  # Adjust path if needed

def is_valid_line(line):
    # Filter out lines that are too short, numeric-only, or look like headers/footers
    if not line.strip():
        return False
    if line.strip().isdigit():
        return False
    if re.match(r'^(page\s*\d+|chapter|section)', line.lower()):
        return False
    return True

def process_pdf(pdf_path):
    print(f"🔍 Processing: {pdf_path}")
    images = convert_from_path(pdf_path, dpi=300)

    data = []
    for image in images:
        text = pytesseract.image_to_string(image, lang='eng')  # Or 'eng+lmn' if a Lummi model existed
        lines = [line.strip() for line in text.split("\n") if is_valid_line(line)]

        # Attempt to pair lines (imperfect but better than crashing)
        i = 0
        while i < len(lines) - 1:
            l1 = lines[i]
            l2 = lines[i + 1]
            # Add sanity check: skip if both are English (or both are gibberish)
            if len(l1.split()) < 8 and len(l2.split()) > 3:
                data.append({'lummi_sentence': l1, 'english_sentence': l2})
                i += 2
            else:
                i += 1  # Shift window and retry

    if data:
        output_file = os.path.join(OUTPUT_FOLDER, os.path.basename(pdf_path).replace('.pdf', '.csv'))
        pd.DataFrame(data).to_csv(output_file, index=False)
        print(f"✅ Saved to {output_file}")
    else:
        print("⚠️ No valid sentence pairs found.")

# Process all PDF files in the folder
for pdf_file in os.listdir(PDF_FOLDER):
    if pdf_file.endswith('.pdf'):
        process_pdf(os.path.join(PDF_FOLDER, pdf_file))
