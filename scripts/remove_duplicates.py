import csv
import os
import re
from collections import defaultdict

def normalize_text(text):
    """Normalize text for comparison to identify duplicates"""
    # Remove punctuation, convert to lowercase
    text = re.sub(r'[.,;:\'"\(\)_\-]', '', text.lower())
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    return text

def pick_best_entry(entries):
    """Select the best entry from a set of duplicates"""
    # Sort entries by quality heuristics
    sorted_entries = sorted(entries, key=lambda entry: (
        # Prefer entries without special formatting characters
        -len(re.findall(r'[\'"\(\)_]', entry[0])),
        # Prefer entries with proper capitalization
        -sum(1 for c in entry[0] if c.isupper()),
        # Prefer shorter entries (often cleaner)
        len(entry[0])
    ))
    return sorted_entries[0]

def clean_duplicates(input_file, output_file):
    """Remove duplicate entries while preserving the most accurate versions"""
    # Read all entries
    entries = []
    with open(input_file, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                entries.append((row[0], row[1]))
    
    # Group by normalized English translation
    english_dict = defaultdict(list)
    for lummi, english in entries:
        norm_english = normalize_text(english)
        if norm_english:  # Skip empty entries
            english_dict[norm_english].append((lummi, english))
    
    # Select best entry from each group
    unique_entries = []
    duplicate_count = 0
    for norm_english, entries_list in english_dict.items():
        if len(entries_list) > 1:
            duplicate_count += len(entries_list) - 1
            unique_entries.append(pick_best_entry(entries_list))
        else:
            unique_entries.append(entries_list[0])
    
    # Sort alphabetically by English
    unique_entries.sort(key=lambda x: x[1].lower())
    
    # Write the cleaned data
    with open(output_file, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(unique_entries)
    
    return len(entries), len(unique_entries), duplicate_count

# File paths
input_file = "processed_data/combined_lummi_english.csv"
output_file = "processed_data/unique_lummi_english.csv"

# Clean the duplicates
total_entries, unique_entries, duplicates_removed = clean_duplicates(input_file, output_file)

print(f"Original file: {total_entries} entries")
print(f"Cleaned file: {unique_entries} entries")
print(f"Removed {duplicates_removed} duplicates")
print(f"Saved cleaned data to {output_file}")