import pandas as pd
import re

def clean_quizlet_data(input_file, output_file):
    """
    Clean and format the quizlet dictionary text file into a structured CSV.
    
    Parameters:
    input_file (str): Path to the raw quizlet dictionary text file
    output_file (str): Path to save the cleaned CSV file
    """
    # Read the raw text file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by double newlines to separate entries
    entries = re.split(r'\n\n+', content.strip())
    
    # Create lists to store cleaned data
    english_terms = []
    lummi_terms = []
    
    # Process each entry
    for i in range(0, len(entries), 2):
        if i+1 < len(entries):
            english = entries[i].strip()
            lummi = entries[i+1].strip()
            
            # Skip entries that don't have both parts
            if not english or not lummi:
                continue
                
            english_terms.append(english)
            lummi_terms.append(lummi)
    
    # Create a DataFrame
    df = pd.DataFrame({
        'english': english_terms,
        'lummi': lummi_terms
    })
    
    # Clean up the data
    # Remove leading/trailing whitespace
    df['english'] = df['english'].str.strip()
    df['lummi'] = df['lummi'].str.strip()
    
    # Sort by English term alphabetically
    df = df.sort_values('english')
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")
    return df

if __name__ == "__main__":
    input_file = '../raw_data/quizlet_dictionary_lummi.txt'
    output_file = '../processed_data/quizlet_lummi_cleaned.csv'
    
    # Create the processed_data directory if it doesn't exist
    import os
    os.makedirs('../processed_data', exist_ok=True)
    
    # Clean and save the data
    clean_quizlet_data(input_file, output_file)