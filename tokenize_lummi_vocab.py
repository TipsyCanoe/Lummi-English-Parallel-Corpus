#!/usr/bin/env python3
"""
Tokenize Lummi third iteration vocabulary file.
- Tokenizes English and Lummi fields using whitespace or custom logic
- Keeps context lines as-is

Does NOT process the data yet; just defines the logic.
"""

import csv
import re

def tokenize_text(text, method='whitespace'):
    if method == 'whitespace':
        # Simple whitespace tokenization
        return ' '.join(text.strip().split())
    elif method == 'punct':
        # Tokenize on whitespace and punctuation
        return ' '.join(re.findall(r"\w+|[^\w\s]", text, re.UNICODE))
    else:
        raise ValueError(f"Unknown tokenization method: {method}")

def tokenize_vocab_file(input_path, output_path, method='whitespace'):
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if not row or row[0].startswith('_'):
                # Context or empty line, write as-is
                writer.writerow(row)
            else:
                # Tokenize both columns
                tok_row = [tokenize_text(col, method) for col in row]
                writer.writerow(tok_row)

if __name__ == "__main__":
    print("This script defines tokenization logic but does not process data yet.")
    # Example usage:
    # tokenize_vocab_file('raw_data/third_iteration_Lummi_vocab.csv', 'raw_data/third_iteration_Lummi_vocab_tokenized.csv')
