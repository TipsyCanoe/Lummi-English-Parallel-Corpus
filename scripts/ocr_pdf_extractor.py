import os
import pytesseract
from pdf2image import convert_from_path

# Ensure this matches your install path if using Windows
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def ocr_scanned_pdf(pdf_path, output_txt="ocr_output.txt", dpi=300):
    # Convert PDF pages to images
    print("📄 Converting PDF pages to images...")
    images = convert_from_path(pdf_path, dpi=dpi)

    extracted_text = ""
    for i, image in enumerate(images):
        print(f"🔍 OCR processing page {i + 1}/{len(images)}...")
        text = pytesseract.image_to_string(image, lang="eng")
        extracted_text += f"\n--- Page {i+1} ---\n{text.strip()}\n"

    # Save to text file
    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(extracted_text)

    print(f"✅ OCR complete. Output saved to: {output_txt}")

# Example usage:
# ocr_scanned_pdf("my_scanned_doc.pdf", "clean_text.txt")
if __name__ == "__main__":
    # Example usage
    pdf_path = "my_scanned_doc.pdf"  # Replace with your PDF file path
    output_txt = "clean_text.txt"     # Output text file
    ocr_scanned_pdf(pdf_path, output_txt)