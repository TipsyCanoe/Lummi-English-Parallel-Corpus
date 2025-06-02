#!/usr/bin/env python3
"""
Lummi-English Parallel Corpus Evaluation Script

This script provides quantitative analysis of the better_format.csv corpus.
It calculates various statistics to evaluate the quality and coverage of the parallel corpus.
"""

import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns

# Set display options for better readability
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
pd.set_option('display.max_colwidth', 100)

def load_and_clean_data(filepath):
    """Load and clean the corpus data."""
    print("Loading corpus data...")
    df = pd.read_csv(filepath)
    
    # Basic cleaning
    df = df.dropna(how='all')
    for col in ['english', 'lummi']:
        df[col] = df[col].fillna('').astype(str).str.strip()
    
    return df

def calculate_basic_stats(df):
    """Calculate basic corpus statistics."""
    print("\n=== Basic Corpus Statistics ===")
    stats = {}
    
    # Total entries
    stats['total_entries'] = len(df)
    
    # Entry types distribution
    stats['category_dist'] = df['category'].value_counts().to_dict()
    
    # Source distribution
    if 'source' in df.columns:
        stats['source_dist'] = df['source'].value_counts().to_dict()
    
    return stats

def analyze_parallel_quality(df):
    """Analyze the quality of parallel entries."""
    print("\n=== Parallel Text Analysis ===")
    results = {}
    
    # Check for missing translations
    missing_eng = df[df['english'].str.strip() == '']
    missing_lummi = df[df['lummi'].str.strip() == '']
    
    results['missing_english'] = len(missing_eng)
    results['missing_lummi'] = len(missing_lummi)
    
    # Calculate token statistics
    df['eng_tokens'] = df['english'].str.split().str.len()
    df['lummi_tokens'] = df['lummi'].str.split().str.len()
    
    # Basic token stats
    results['avg_eng_tokens'] = df['eng_tokens'].mean()
    results['avg_lummi_tokens'] = df['lummi_tokens'].mean()
    results['token_ratio'] = results['avg_lummi_tokens'] / results['avg_eng_tokens']
    
    return results, df

def analyze_vocabulary(df):
    """Analyze vocabulary distribution and coverage."""
    print("\n=== Vocabulary Analysis ===")
    
    # Get all words (simple whitespace tokenization for now)
    eng_words = ' '.join(df['english'].dropna()).lower().split()
    lummi_words = ' '.join(df['lummi'].dropna()).split()
    
    # Basic counts
    eng_vocab = Counter(eng_words)
    lummi_vocab = Counter(lummi_words)
    
    # Calculate TTR (Type-Token Ratio)
    eng_ttr = len(eng_vocab) / len(eng_words) if eng_words else 0
    lummi_ttr = len(lummi_vocab) / len(lummi_words) if lummi_words else 0
    
    return {
        'eng_vocab_size': len(eng_vocab),
        'lummi_vocab_size': len(lummi_vocab),
        'eng_ttr': eng_ttr,
        'lummi_ttr': lummi_ttr,
        'top_eng_words': eng_vocab.most_common(20),
        'top_lummi_words': lummi_vocab.most_common(20)
    }

def analyze_context_notes(df):
    """Analyze the presence and quality of context notes."""
    print("\n=== Context Notes Analysis ===")
    
    if 'context_notes' not in df.columns:
        return {'has_context_notes': False}
    
    # Check for presence of context notes
    has_notes = df['context_notes'].notna() & (df['context_notes'] != 'N/A') & (df['context_notes'] != '')
    notes_coverage = has_notes.mean() * 100
    
    # Sample some context notes for review
    sample_notes = df[has_notes].sample(min(5, len(df[has_notes])), random_state=42)['context_notes'].tolist()
    
    return {
        'has_context_notes': True,
        'notes_coverage_pct': notes_coverage,
        'sample_notes': sample_notes
    }

def generate_report(stats, parallel_quality, vocab_stats, context_stats):
    """Generate a formatted report of the analysis."""
    print("\n" + "="*50)
    print("Lummi-English Parallel Corpus Evaluation Report")
    print("="*50 + "\n")
    
    # Basic stats
    print(f"Total entries: {stats['total_entries']:,}")
    print("\nCategory Distribution:")
    for cat, count in stats['category_dist'].items():
        print(f"  - {cat}: {count:,} ({count/stats['total_entries']*100:.1f}%)")
    
    if 'source_dist' in stats:
        print("\nSource Distribution:")
        for src, count in stats['source_dist'].items():
            print(f"  - {src}: {count:,} ({count/stats['total_entries']*100:.1f}%)")
    
    # Parallel quality
    print("\nParallel Text Quality:")
    print(f"  - Missing English translations: {parallel_quality['missing_english']}")
    print(f"  - Missing Lummi translations: {parallel_quality['missing_lummi']}")
    print(f"  - Avg. English tokens per entry: {parallel_quality['avg_eng_tokens']:.2f}")
    print(f"  - Avg. Lummi tokens per entry: {parallel_quality['avg_lummi_tokens']:.2f}")
    print(f"  - Token ratio (Lummi/English): {parallel_quality['token_ratio']:.2f}")
    
    # Vocabulary
    print("\nVocabulary Analysis:")
    print(f"  - English vocabulary size: {vocab_stats['eng_vocab_size']:,} unique words")
    print(f"  - Lummi vocabulary size: {vocab_stats['lummi_vocab_size']:,} unique words")
    print(f"  - English Type-Token Ratio: {vocab_stats['eng_ttr']:.3f}")
    print(f"  - Lummi Type-Token Ratio: {vocab_stats['lummi_ttr']:.3f}")
    
    # Context notes
    if context_stats['has_context_notes']:
        print(f"\nContext Notes Coverage: {context_stats['notes_coverage_pct']:.1f}%")
        print("\nSample Context Notes:")
        for i, note in enumerate(context_stats['sample_notes'], 1):
            print(f"  {i}. {note}")
    else:
        print("\nNo context notes found in the dataset.")

def main():
    """Main function to run the analysis."""
    # File path - update this if needed
    corpus_file = 'better_format.csv'
    
    try:
        # Load and clean data
        df = load_and_clean_data(corpus_file)
        
        # Calculate statistics
        stats = calculate_basic_stats(df)
        parallel_quality, df = analyze_parallel_quality(df)
        vocab_stats = analyze_vocabulary(df)
        context_stats = analyze_context_notes(df)
        
        # Generate and display report
        generate_report(stats, parallel_quality, vocab_stats, context_stats)
        
        # Save the enhanced dataframe for further analysis
        df.to_csv('analyzed_corpus.csv', index=False)
        print("\nAnalysis complete. Enhanced dataset saved as 'analyzed_corpus.csv'")
        
    except Exception as e:
        print(f"\nError during analysis: {str(e)}")
        raise

if __name__ == "__main__":
    main()
