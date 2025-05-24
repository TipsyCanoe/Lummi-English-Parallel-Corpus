import os
from clean_quizlet_data import clean_quizlet_data
from update_lummi_vocab import update_lummi_vocab

def process_lummi_corpus():
    """
    Full pipeline to process Lummi corpus data:
    1. Clean and format the quizlet data
    2. Update the Lummi vocabulary with new entries
    """
    print("=" * 50)
    print("LUMMI CORPUS PROCESSING PIPELINE")
    print("=" * 50)
    
    # Create processed_data directory if it doesn't exist
    os.makedirs('../processed_data', exist_ok=True)
    
    # Define file paths
    quizlet_raw = '../raw_data/quizlet_dictionary_lummi.txt'
    quizlet_cleaned = '../processed_data/quizlet_lummi_cleaned.csv'
    lummi_vocab = '../raw_data/Lummi_vocab.csv'
    
    # Step 1: Clean quizlet data
    print("\nSTEP 1: Cleaning Quizlet dictionary data")
    print("-" * 50)
    clean_quizlet_data(quizlet_raw, quizlet_cleaned)
    
    # Step 2: Update Lummi vocabulary
    print("\nSTEP 2: Updating Lummi vocabulary")
    print("-" * 50)
    update_lummi_vocab(lummi_vocab, quizlet_cleaned)
    
    print("\nProcessing complete!")

if __name__ == "__main__":
    process_lummi_corpus()