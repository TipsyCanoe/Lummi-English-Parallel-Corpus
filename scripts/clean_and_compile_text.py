import os
import csv
from pathlib import Path

def clean_text(text):
    """
    Cleans the extracted text by removing unnecessary whitespace and formatting issues.
    
    Args:
        text (str): Raw text extracted from the PDF.
    
    Returns:
        str: Cleaned text.
    """
    # Remove extra whitespace, newlines, and normalize text
    cleaned_text = text.strip()
    cleaned_text = " ".join(cleaned_text.split())
    return cleaned_text

def compile_to_csv(input_dir, output_csv):
    """
    Reads cleaned text files, organizes them into a CSV with columns for id, English, and Lummi.
    
    Args:
        input_dir (str): Directory containing cleaned text files.
        output_csv (str): Path to save the compiled CSV file.
    
    Returns:
        None
    """
    input_dir = Path(input_dir)
    output_csv = Path(output_csv)
    
    if not input_dir.exists():
        print(f"Input directory {input_dir} does not exist.")
        return
    
    # Prepare CSV file
    with open(output_csv, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["id", "English", "Lummi"])  # Header row
        
        # Iterate through text files in the input directory
        for i, text_file in enumerate(input_dir.glob("*.txt"), start=1):
            print(f"Processing {text_file.name}...")
            
            # Read and clean the text
            with open(text_file, "r", encoding="utf-8") as f:
                raw_text = f.read()
                cleaned_text = clean_text(raw_text)
            
            # Split cleaned text into English and Lummi sections
            # Assuming the text alternates between English and Lummi lines
            lines = cleaned_text.split("\n")
            english_lines = []
            lummi_lines = []
            
            for idx, line in enumerate(lines):
                if idx % 2 == 0:  # Even lines are English
                    english_lines.append(line)
                else:  # Odd lines are Lummi
                    lummi_lines.append(line)
            
            # Combine English and Lummi lines into single strings
            english_text = " ".join(english_lines)
            lummi_text = " ".join(lummi_lines)
            
            # Write to CSV
            writer.writerow([i, english_text, lummi_text])
    
    print(f"Compiled CSV saved to {output_csv}")

if __name__ == "__main__":
    import argparse
    
    # Argument parser for command-line usage
    parser = argparse.ArgumentParser(description="Clean text files and compile them into a CSV.")
    parser.add_argument("input_dir", help="Directory containing cleaned text files.")
    parser.add_argument("output_csv", help="Path to save the compiled CSV file.")
    args = parser.parse_args()
    
    compile_to_csv(args.input_dir, args.output_csv)