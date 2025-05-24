import pandas as pd
import re
import os

def extract_phrases_from_quizlet(quizlet_file):
    """
    Extract full phrases and sentences from the quizlet file.
    These are likely to be more useful for a parallel corpus than individual words.
    """
    with open(quizlet_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to separate entries
    entries = re.split(r'\n\n+', content.strip())
    
    # Create lists to store phrases
    english_phrases = []
    lummi_phrases = []
    
    # Process each entry
    for i in range(0, len(entries), 2):
        if i+1 < len(entries):
            english = entries[i].strip()
            lummi = entries[i+1].strip()
            
            # Skip entries that don't have both parts
            if not english or not lummi:
                continue
            
            # Keep only entries with more than one word (likely phrases)
            if len(english.split()) > 1 or ',' in english:
                english_phrases.append(english)
                lummi_phrases.append(lummi)
    
    # Create a DataFrame
    df = pd.DataFrame({
        'english': english_phrases,
        'lummi': lummi_phrases
    })
    
    return df

def extract_phrases_from_vocab_csv(vocab_file):
    """
    Extract phrases and example sentences from the vocabulary CSV file.
    """
    df = pd.read_csv(vocab_file)
    english_phrases = []
    lummi_phrases = []
    
    for _, row in df.iterrows():
        english = str(row['english'])
        lummi = str(row['lummi'])
        
        # Extract phrases in italics (indicated by _underscores_)
        eng_phrases = re.findall(r'_([^_]+)_', english)
        
        for phrase in eng_phrases:
            # Find the corresponding Lummi phrase if possible
            pattern = re.escape(phrase)
            if re.search(pattern, english, re.IGNORECASE):
                # Try to find the Lummi equivalent in the same position
                english_phrases.append(phrase)
                lummi_phrases.append(lummi)  # This is approximate, might need manual cleanup
    
    phrase_df = pd.DataFrame({
        'english': english_phrases,
        'lummi': lummi_phrases
    })
    
    return phrase_df

def build_parallel_corpus():
    """
    Build a parallel corpus from various sources.
    """
    # Define file paths
    quizlet_file = '../raw_data/quizlet_dictionary_lummi.txt'
    vocab_file = '../raw_data/Lummi_vocab.csv'
    output_file = '../processed_data/lummi_english_parallel_corpus.csv'
    
    # Create processed_data directory if it doesn't exist
    os.makedirs('../processed_data', exist_ok=True)
    
    # Extract phrases from each source
    print("Extracting phrases from quizlet file...")
    quizlet_phrases = extract_phrases_from_quizlet(quizlet_file)
    
    print("Extracting phrases from vocabulary file...")
    vocab_phrases = extract_phrases_from_vocab_csv(vocab_file)
    
    # Combine all sources
    parallel_corpus = pd.concat([quizlet_phrases, vocab_phrases], ignore_index=True)
    
    # Remove duplicates
    parallel_corpus = parallel_corpus.drop_duplicates(subset=['english'])
    
    # Sort by English phrase
    parallel_corpus = parallel_corpus.sort_values('english')
    
    # Add a source column (optional)
    parallel_corpus['source'] = 'combined'
    
    # Save to CSV
    parallel_corpus.to_csv(output_file, index=False)
    print(f"Parallel corpus saved to {output_file} with {len(parallel_corpus)} entries")
    
    return parallel_corpus

if __name__ == "__main__":
    build_parallel_corpus()