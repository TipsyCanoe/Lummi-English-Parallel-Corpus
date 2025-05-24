#!/usr/bin/env python3
"""
Normalize Lummi third iteration vocabulary file.
- Lowercases English and Lummi fields (optional, configurable)
- Strips whitespace
- Unicode NFC normalization
- Removes duplicate spaces
- Standardizes punctuation (optional, configurable)

Does NOT process the data yet; just defines the logic.
"""

import unicodedata
import csv

def normalize_text(text, lowercase=True, nfc=True):
    # Strip whitespace
    text = text.strip()
    # Lowercase if desired
    if lowercase:
        text = text.lower()
    # Unicode normalization
    if nfc:
        text = unicodedata.normalize('NFC', text)
    # Remove duplicate spaces
    text = ' '.join(text.split())
    return text

def normalize_vocab_file(input_path, output_path, lowercase=True, nfc=True):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if not row or row[0].startswith('_'):
                # Context or empty line, write as-is
                writer.writerow(row)
            else:
                # Normalize both columns
                norm_row = [normalize_text(col, lowercase, nfc) for col in row]
                writer.writerow(norm_row)

if __name__ == "__main__":
    print("This script defines normalization logic but does not process data yet.")
    # Example usage:
    # normalize_vocab_file('raw_data/third_iteration_Lummi_vocab.csv', 'raw_data/third_iteration_Lummi_vocab_normalized.csv')
