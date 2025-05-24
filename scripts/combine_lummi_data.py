import csv
import os
import re

def clean_data(text):
    """Clean up the data entries to handle special formatting"""
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Handle footnotes or annotations in the vocab file
    text = re.sub(r'\^[0-9]', '', text)  # Remove superscript numbers
    
    # Handle other formatting issues
    text = re.sub(r'_([^_]+)_', r'\1', text)  # Remove underscores around text
    
    return text

def process_vocab_data(vocab_file):
    """Process the Lummi_vocab.csv file which has a different format"""
    data = []
    
    with open(vocab_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader, None)  # Skip header row
        
        for row in reader:
            if len(row) < 2:
                continue
                
            english = clean_data(row[0])
            lummi = clean_data(row[1])
            
            # Skip empty entries or column labels
            if not english or not lummi or english == 'english' or lummi == 'lummi':
                continue
                
            # Handle multi-part definitions
            if ',' in lummi:
                # Process entries with multiple translations
                lummi_parts = [part.strip() for part in lummi.split(',')]
                for part in lummi_parts:
                    if part and not part.startswith('_') and not part.startswith('('):
                        data.append((part, english))
            else:
                data.append((lummi, english))
    
    return data

def combine_lummi_data(pairs_file, vocab_file, output_file):
    """Combine data from both files and sort by English translation"""
    all_entries = []
    
    # Process the pairs file (simple format)
    with open(pairs_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader, None)  # Skip header row
        
        for row in reader:
            if len(row) < 2:
                continue
                
            lummi = clean_data(row[0])
            english = clean_data(row[1])
            
            # Skip file path or empty entries
            if lummi.startswith('//') or not english or not lummi:
                continue
                
            all_entries.append((lummi, english))
    
    # Process the vocab file (more complex format)
    vocab_entries = process_vocab_data(vocab_file)
    all_entries.extend(vocab_entries)
    
    # Remove duplicates (based on exact matches)
    unique_entries = []
    seen = set()
    
    for lummi, english in all_entries:
        # Create a key for deduplication
        entry_key = (lummi.lower(), english.lower())
        if entry_key not in seen:
            seen.add(entry_key)
            unique_entries.append((lummi, english))
    
    # Sort alphabetically by English translation
    sorted_entries = sorted(unique_entries, key=lambda x: x[1].lower())
    
    # Write to the output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Lummi', 'English'])
        writer.writerows(sorted_entries)
    
    print(f"Combined {len(sorted_entries)} unique entries into {output_file}")
    print(f"Original data had {len(all_entries)} entries (including duplicates)")

# File paths
pairs_file = "processed_data/lummi_english_pairs.csv"
vocab_file = "processed_data/Lummi_vocab.csv"
output_file = "processed_data/combined_lummi_english.csv"

# Combine the data
combine_lummi_data(pairs_file, vocab_file, output_file)