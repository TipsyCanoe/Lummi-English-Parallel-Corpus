import csv
import re
import os

def process_quizlet_file(input_file, output_file):
    """
    Process the quizlet text file into a CSV format with better handling of multi-line entries.
    """
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split content by double newlines which separate entries
    raw_entries = re.split(r'\n\s*\n', content)
    
    # Prepare data for CSV
    data = []
    for entry in raw_entries:
        lines = entry.strip().split('\n')
        if len(lines) < 2:
            continue  # Skip entries without both Lummi and English
        
        lummi = lines[0].strip()
        
        # If there are multiple lines, join the remaining lines as the English translation
        english = ' / '.join([line.strip() for line in lines[1:]])
        
        # Skip entries that are likely headers or formatting issues
        if (lummi and english and 
            not lummi.endswith(':') and 
            not english.endswith(':') and
            not lummi.startswith('//') and
            not english.startswith('//')):
            data.append([lummi, english])
    
    # Write to CSV
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Lummi', 'English'])  # Header
        writer.writerows(data)
    
    print(f"Processed {len(data)} entries into {output_file}")

# Process the file
input_file = "raw_data/quizlet_large.txt"
output_file = "processed_data/lummi_english_pairs.csv"

# Create output directory if it doesn't exist
os.makedirs(os.path.dirname(output_file), exist_ok=True)

process_quizlet_file(input_file, output_file)