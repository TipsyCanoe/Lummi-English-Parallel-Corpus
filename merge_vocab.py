#!/usr/bin/env python3
"""
Lummi Vocabulary Merger

This script merges entries from a Quizlet CSV file into the Lummi vocabulary file.
It handles:
- Preserving context lines (lines starting with _)
- Removing duplicates (case-insensitive)
- Sorting entries alphabetically
- Maintaining the original format
"""

import csv
import argparse
from collections import defaultdict

def read_lummi_vocab(filepath):
    """
    Read the Lummi vocabulary file and extract entries with their context lines.
    
    Args:
        filepath: Path to the Lummi vocabulary CSV file
        
    Returns:
        tuple: (header, list of entry dictionaries)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract the header
    header = lines[0].strip()
    
    # Process the file line by line to extract entries and their context
    entries = []
    i = 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # If not a context line (doesn't start with _), it's a main entry
        if not line.startswith('_'):
            parts = line.split(',', 1)
            if len(parts) >= 2:
                english = parts[0].strip()
                lummi = parts[1].strip()
                
                # Collect context lines that follow this entry
                context_lines = []
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('_'):
                    context_lines.append(lines[j].strip())
                    j += 1
                
                # Create entry object
                entry = {
                    'english': english,
                    'lummi': lummi,
                    'context': context_lines,
                    'key': english.lower()  # Case-insensitive key
                }
                
                entries.append(entry)
                i = j  # Skip past the context lines
            else:
                i += 1
        else:
            # Skip orphaned context lines
            i += 1
    
    return header, entries

def read_quizlet_entries(filepath):
    """
    Read entries from the Quizlet CSV file.
    
    Args:
        filepath: Path to the Quizlet CSV file
        
    Returns:
        list: List of entry dictionaries
    """
    entries = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    # Process Quizlet entries (even lines are English, odd lines are Lummi)
    for i in range(0, len(lines)-1, 2):
        english = lines[i].strip()
        lummi = lines[i+1].strip()
        
        if english and lummi:
            entries.append({
                'english': english,
                'lummi': lummi,
                'context': [],
                'key': english.lower()
            })
    
    return entries

def merge_and_deduplicate(original_entries, new_entries):
    """
    Merge entries and remove duplicates, preferring uppercase entries.
    
    Args:
        original_entries: List of original entry dictionaries
        new_entries: List of new entry dictionaries
        
    Returns:
        list: List of merged and deduplicated entry dictionaries
    """
    # Combine all entries
    all_entries = original_entries + new_entries
    
    # Group entries by lowercase key
    entry_groups = defaultdict(list)
    for entry in all_entries:
        entry_groups[entry['key']].append(entry)
    
    # Process each group to handle duplicates
    final_entries = []
    
    for key, group in entry_groups.items():
        if len(group) == 1:
            # Only one entry with this key
            final_entries.append(group[0])
        else:
            # Multiple entries with same lowercase key
            # Prefer uppercase entries
            uppercase_entries = [e for e in group if e['english'].isupper()]
            
            if uppercase_entries:
                # Use the first uppercase entry as base
                merged_entry = uppercase_entries[0].copy()
            else:
                # No uppercase entries, use the first one
                merged_entry = group[0].copy()
            
            # Combine context lines from all entries in the group
            all_context = []
            for entry in group:
                all_context.extend(entry['context'])
            
            # Remove duplicate context lines (case-insensitive)
            seen = set()
            unique_context = []
            for line in all_context:
                if line.lower() not in seen:
                    seen.add(line.lower())
                    unique_context.append(line)
            
            merged_entry['context'] = unique_context
            final_entries.append(merged_entry)
    
    # Sort entries alphabetically by key
    return sorted(final_entries, key=lambda x: x['key'])

def write_vocab_file(filepath, header, entries):
    """
    Write the merged vocabulary to a CSV file.
    
    Args:
        filepath: Path to the output CSV file
        header: Header line for the CSV file
        entries: List of entry dictionaries to write
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        # Write header
        f.write(header + '\n')
        
        # Write each entry with its context
        for entry in entries:
            f.write(f"{entry['english']},{entry['lummi']}\n")
            for context in entry['context']:
                f.write(f"{context}\n")

def main():
    """Main function to merge vocabulary files."""
    parser = argparse.ArgumentParser(description='Merge Quizlet entries into Lummi vocabulary file')
    parser.add_argument('--vocab', default='raw_data/first_iteration_Lummi_vocab.csv',
                        help='Path to the Lummi vocabulary CSV file')
    parser.add_argument('--quizlet', default='raw_data/LUMMI_DICTIONARY_Quizlet.csv',
                        help='Path to the Quizlet CSV file')
    parser.add_argument('--output', default='raw_data/Lummi_vocab.csv',
                        help='Path to the output CSV file')
    args = parser.parse_args()
    
    # Read the original vocabulary file
    print(f"Reading original vocabulary from {args.vocab}...")
    header, original_entries = read_lummi_vocab(args.vocab)
    print(f"Read {len(original_entries)} original entries")
    
    # Read the Quizlet entries
    print(f"Reading Quizlet entries from {args.quizlet}...")
    quizlet_entries = read_quizlet_entries(args.quizlet)
    print(f"Read {len(quizlet_entries)} Quizlet entries")
    
    # Merge and deduplicate entries
    print("Merging and deduplicating entries...")
    merged_entries = merge_and_deduplicate(original_entries, quizlet_entries)
    
    # Write the output file
    print(f"Writing merged vocabulary to {args.output}...")
    write_vocab_file(args.output, header, merged_entries)
    
    # Print summary
    print("\nMerge complete!")
    print(f"Original entries: {len(original_entries)}")
    print(f"Quizlet entries: {len(quizlet_entries)}")
    print(f"Total entries before deduplication: {len(original_entries) + len(quizlet_entries)}")
    print(f"Total entries after deduplication: {len(merged_entries)}")
    print(f"Duplicates removed: {len(original_entries) + len(quizlet_entries) - len(merged_entries)}")

if __name__ == "__main__":
    main()
