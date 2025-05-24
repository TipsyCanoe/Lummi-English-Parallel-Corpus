#!/usr/bin/env python3
"""
Comprehensive Lummi Vocabulary Merger

This script provides a unified solution for merging and fixing Lummi vocabulary files.
It can handle multiple input formats and operations:

1. Merging standard vocabulary files with context lines
2. Merging Quizlet-style files (alternating English/Lummi lines)
3. Merging CSV files with 'english' and 'lummi' columns
4. Fixing misplaced context lines using a reference file

Features:
- Preserves context lines (lines starting with _, (, or ")
- Removes duplicates (case-insensitive)
- Sorts entries alphabetically
- Maintains the original format
- Fixes misplaced context lines
"""

import csv
import argparse
import os
from collections import defaultdict
from typing import List, Dict, Tuple, Optional, Set


def read_vocab_file(filepath: str) -> Tuple[str, List[Dict]]:
    """
    Read a vocabulary file and extract entries with their context lines.
    
    Args:
        filepath: Path to the vocabulary CSV file
        
    Returns:
        tuple: (header, list of entry dictionaries)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Extract the header
    header = lines[0].strip() if lines else "English,Lummi"
    
    # Process the file line by line to extract entries and their context
    entries = []
    i = 1
    
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # If not a context line (doesn't start with _, (, or "), it's a main entry
        if not (line.startswith('_') or line.startswith('(') or line.startswith('"')):
            parts = line.split(',', 1)
            if len(parts) >= 2:
                english = parts[0].strip()
                lummi = parts[1].strip()
                
                # Collect context lines that follow this entry
                context_lines = []
                j = i + 1
                while j < len(lines) and (lines[j].strip().startswith('_') or 
                                         lines[j].strip().startswith('(') or 
                                         lines[j].strip().startswith('"')):
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


def read_quizlet_entries(filepath: str) -> List[Dict]:
    """
    Read entries from a Quizlet-style file (alternating English/Lummi lines).
    
    Args:
        filepath: Path to the Quizlet file
        
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


def read_pairs_file(filepath: str) -> List[Dict]:
    """
    Read entries from a CSV file with 'english' and 'lummi' columns.
    
    Args:
        filepath: Path to the pairs CSV file
        
    Returns:
        list: List of entry dictionaries
    """
    entries = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            english = row['english'].strip()
            lummi = row['lummi'].strip()
            
            if english and lummi:
                entries.append({
                    'english': english,
                    'lummi': lummi,
                    'context': [],
                    'key': english.lower()
                })
    
    return entries


def merge_and_deduplicate(original_entries: List[Dict], new_entries: List[Dict]) -> List[Dict]:
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


def write_vocab_file(filepath: str, header: str, entries: List[Dict]) -> None:
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


def create_context_mapping(entries: List[Dict]) -> Dict[str, str]:
    """
    Create a mapping of context lines to their main entries.
    
    Args:
        entries: List of entry dictionaries
        
    Returns:
        dict: Mapping of context lines to their main entry English terms
    """
    context_mapping = {}
    
    for entry in entries:
        english = entry['english']
        for context in entry['context']:
            context_mapping[context] = english
    
    return context_mapping


def fix_context_lines(entries: List[Dict], reference_entries: List[Dict], orphaned_contexts: List[str]) -> List[Dict]:
    """
    Fix misplaced context lines by assigning them to the correct entries.
    
    Args:
        entries: List of entry dictionaries to fix
        reference_entries: List of reference entry dictionaries
        orphaned_contexts: List of orphaned context lines
        
    Returns:
        list: List of fixed entry dictionaries
    """
    # Create a mapping of context lines to their main entries from the reference file
    context_mapping = create_context_mapping(reference_entries)
    
    # Create a dictionary of entries by English term for easy lookup
    entries_by_english = {entry['english']: entry for entry in entries}
    
    # Add orphaned context lines to their respective entries
    for context_line in orphaned_contexts:
        # Check if this context line is in our mapping
        for ref_context, ref_english in context_mapping.items():
            if context_line.lower() == ref_context.lower():
                # Find the entry in our entries
                if ref_english in entries_by_english:
                    entries_by_english[ref_english]['context'].append(context_line)
                    break
        
        # If the exact match wasn't found, try a more flexible approach
        if not any(context_line.lower() == ref_context.lower() for ref_context in context_mapping):
            # Try to match based on the beginning of the context line
            for ref_context, ref_english in context_mapping.items():
                # Check if the context line starts with the reference context (ignoring case)
                if context_line.lower().startswith(ref_context.split(',')[0].lower()):
                    if ref_english in entries_by_english:
                        entries_by_english[ref_english]['context'].append(context_line)
                        break
    
    # Convert back to a list of entries
    fixed_entries = list(entries_by_english.values())
    
    # Sort entries alphabetically by English term
    fixed_entries.sort(key=lambda x: x['key'])
    
    return fixed_entries


def collect_orphaned_contexts(filepath: str) -> List[str]:
    """
    Collect orphaned context lines from the beginning of a file.
    
    Args:
        filepath: Path to the vocabulary file
        
    Returns:
        list: List of orphaned context lines
    """
    orphaned_lines = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 1  # Skip header
    while i < len(lines) and (lines[i].strip().startswith('_') or 
                             lines[i].strip().startswith('(') or 
                             lines[i].strip().startswith('"')):
        orphaned_lines.append(lines[i].strip())
        i += 1
    
    return orphaned_lines


def merge_vocab_files(args):
    """
    Merge vocabulary files based on the specified mode.
    """
    if args.mode == 'quizlet':
        # Read the original vocabulary file
        print(f"Reading original vocabulary from {args.primary}...")
        header, original_entries = read_vocab_file(args.primary)
        print(f"Read {len(original_entries)} original entries")
        
        # Read the Quizlet entries
        print(f"Reading Quizlet entries from {args.secondary}...")
        quizlet_entries = read_quizlet_entries(args.secondary)
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
    
    elif args.mode == 'pairs':
        # Read the vocabulary file
        print(f"Reading vocabulary from {args.primary}...")
        header, vocab_entries = read_vocab_file(args.primary)
        print(f"Read {len(vocab_entries)} vocabulary entries")
        
        # Read the pairs file
        print(f"Reading pairs from {args.secondary}...")
        pairs_entries = read_pairs_file(args.secondary)
        print(f"Read {len(pairs_entries)} pairs entries")
        
        # Merge and deduplicate entries
        print("Merging and deduplicating entries...")
        merged_entries = merge_and_deduplicate(vocab_entries, pairs_entries)
        
        # Write the output file
        print(f"Writing merged vocabulary to {args.output}...")
        write_vocab_file(args.output, header, merged_entries)
        
        # Print summary
        print("\nMerge complete!")
        print(f"Vocabulary entries: {len(vocab_entries)}")
        print(f"Pairs entries: {len(pairs_entries)}")
        print(f"Total entries before deduplication: {len(vocab_entries) + len(pairs_entries)}")
        print(f"Total entries after deduplication: {len(merged_entries)}")
        print(f"Duplicates removed: {len(vocab_entries) + len(pairs_entries) - len(merged_entries)}")
    
    elif args.mode == 'fix':
        # Read the file to fix
        print(f"Reading file to fix: {args.primary}...")
        header, entries = read_vocab_file(args.primary)
        print(f"Read {len(entries)} entries")
        
        # Read the reference file
        print(f"Reading reference file: {args.secondary}...")
        _, reference_entries = read_vocab_file(args.secondary)
        print(f"Read {len(reference_entries)} reference entries")
        
        # Collect orphaned context lines
        print("Collecting orphaned context lines...")
        orphaned_contexts = collect_orphaned_contexts(args.primary)
        print(f"Found {len(orphaned_contexts)} orphaned context lines")
        
        # Fix context lines
        print("Fixing context lines...")
        fixed_entries = fix_context_lines(entries, reference_entries, orphaned_contexts)
        
        # Write the fixed file
        print(f"Writing fixed vocabulary to {args.output}...")
        write_vocab_file(args.output, header, fixed_entries)
        
        print("\nFix complete!")
        print(f"Entries processed: {len(entries)}")
        print(f"Orphaned contexts processed: {len(orphaned_contexts)}")
    
    else:
        print(f"Unknown mode: {args.mode}")
        print("Supported modes: quizlet, pairs, fix")


def main():
    """Main function to parse arguments and call the appropriate function."""
    parser = argparse.ArgumentParser(description='Comprehensive Lummi Vocabulary Merger')
    
    parser.add_argument('--mode', choices=['quizlet', 'pairs', 'fix'], required=True,
                        help='Operation mode: quizlet (merge Quizlet entries), pairs (merge pairs file), or fix (fix context lines)')
    
    parser.add_argument('--primary', required=True,
                        help='Path to the primary input file (vocabulary file for quizlet/pairs modes, file to fix for fix mode)')
    
    parser.add_argument('--secondary', required=True,
                        help='Path to the secondary input file (Quizlet file for quizlet mode, pairs file for pairs mode, reference file for fix mode)')
    
    parser.add_argument('--output', required=True,
                        help='Path to the output file')
    
    args = parser.parse_args()
    
    merge_vocab_files(args)


if __name__ == "__main__":
    main()
