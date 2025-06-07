import pandas as pd
import re
from langdetect import detect, DetectorFactory
import logging
import os

DetectorFactory.seed = 0

# Configure logging
logging.basicConfig(level=logging.INFO)

# Directory containing the CSV files
input_dir = "processed_data/processed_pdfs"
output_dir = "processed_data/cleaned_pdfs"
os.makedirs(output_dir, exist_ok=True)

# Function to detect language with fallback
def detect_language_safe(text):
    try:
        return detect(text)
    except Exception as e:
        logging.info(f"Language detection failed for text: {text} | Error: {e}")
        return "unknown"

# Process each CSV file in the directory
for file_name in os.listdir(input_dir):
    if file_name.endswith(".csv"):
        file_path = os.path.join(input_dir, file_name)
        logging.info(f"Processing file: {file_path}")
        
        # Load the CSV
        df = pd.read_csv(file_path)

        # Apply language detection
        df['lummi_lang'] = df['lummi_sentence'].apply(detect_language_safe)
        df['english_lang'] = df['english_sentence'].apply(detect_language_safe)

        # Filter out rows where languages are incorrect or unknown
        clean_df = df[
            (df['lummi_lang'] != 'en') & 
            (df['english_lang'] == 'en') & 
            (df['lummi_lang'] != 'unknown') & 
            (df['english_lang'] != 'unknown')
        ]

        # Drop language columns for the final output
        clean_df = clean_df[['lummi_sentence', 'english_sentence']]

        # Save cleaned dataset
        output_file_path = os.path.join(output_dir, f"cleaned_{file_name}")
        clean_df.to_csv(output_file_path, index=False)
        logging.info(f"Cleaned file saved to: {output_file_path}")

import ace_tools as tools; tools.display_dataframe_to_user(name="Last Processed Cleaned Dataset", dataframe=clean_df)
