import csv
import os
import pandas as pd
import re

# Define input and output file paths
base_path = "/mnt/c/Users/richa/OneDrive/Desktop/school/Spring_2025/CSCI404/FinalProj/Lummi-English-Parallel-Corpus/processed_data"
vocab_file = os.path.join(base_path, "Lummi_vocab.csv")
pairs_file = os.path.join(base_path, "lummi_english_pairs.csv")
output_file = os.path.join(base_path, "merged_lummi_english_alphabetical.csv")

# Function to clean and standardize English entries for sorting
def standardize_english(text):
    if not isinstance(text, str):
        return text
    
    # Remove any formatting characters or indicators
    text = re.sub(r'_([^_]+)_', r'\1', text)  # Remove underscores around words
    
    # Extract the main term for sorting (ignore qualifiers in parentheses)
    main_term = re.sub(r'\s*\([^)]*\)', '', text)
    main_term = re.sub(r'\s*\"[^\"]*\"', '', main_term)
    
    # Remove any formatting or special characters for sorting
    main_term = re.sub(r'[^\w\s]', '', main_term)
    
    # Convert to lowercase for case-insensitive sorting
    return main_term.strip().lower()

# Read the first file (English, Lummi)
vocab_data = []
with open(vocab_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Skip header
    header = next(reader)
    for row in reader:
        if len(row) >= 2:
            english = row[0].strip()
            lummi = row[1].strip()
            
            # Skip rows where English is empty or appears to be a continuation
            if english and not english.startswith('_'):
                vocab_data.append({
                    'english': english,
                    'lummi': lummi,
                    'sort_key': standardize_english(english)
                })

# Read the second file (Lummi, English) - note the column swap
pairs_data = []
with open(pairs_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    # Skip header
    header = next(reader)
    for row in reader:
        if len(row) >= 2:
            lummi = row[0].strip()
            english = row[1].strip()
            pairs_data.append({
                'english': english,
                'lummi': lummi,
                'sort_key': standardize_english(english)
            })

# Combine the data
all_data = vocab_data + pairs_data

# Create DataFrame 
df = pd.DataFrame(all_data)

# Remove exact duplicates
df = df.drop_duplicates(subset=['english', 'lummi'])

# Sort alphabetically by the standardized English term
df = df.sort_values(by='sort_key')

# Remove the sort_key column before writing to CSV
df = df[['english', 'lummi']]

# Write the merged data to a new CSV
df.to_csv(output_file, index=False)

print(f"Merged data saved to {output_file}")
print(f"Total entries: {len(df)}")