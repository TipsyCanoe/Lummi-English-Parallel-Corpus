import requests
import re
import pandas as pd
import os

# Paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_PATH = os.path.join(ROOT_DIR, 'raw_data/gutenberg_vocabulary_v3.csv')
os.makedirs(os.path.join(ROOT_DIR, 'raw_data'), exist_ok=True)

# URL of the plain text version of the book
url = "https://www.gutenberg.org/files/22228/22228-0.txt"
response = requests.get(url)
text = response.text

# Define the section
start_marker = "VOCABULARY OF THE LUMMI."
end_marker = "Local Nomenclature of the Lummi Tribe"
start_index = text.find(start_marker)
end_index = text.find(end_marker, start_index)

# ✅ Check if the section was found
if start_index == -1 or end_index == -1:
    print("❌ Vocabulary section not found in the document.")
    exit(1)

lummi_section = text[start_index:end_index]
print("✅ Vocabulary section successfully extracted.")

# Extract vocabulary
vocabulary = []
for line in lummi_section.splitlines():
    line = line.strip()
    
    # Ignore lines that start with _ (they are descriptions, not vocabulary)
    if line.startswith("_"):
        continue
    
    if len(line) < 5:
        continue
    match = re.match(r'^(.+?),\s+(.+?)\.$', line)
    if match:
        english = match.group(1).strip()
        lummi = match.group(2).strip()
        vocabulary.append({'english': english, 'lummi': lummi})

# ✅ Debugging Information
print(f"✅ Total Entries Found: {len(vocabulary)}")
if len(vocabulary) > 0:
    print("🔍 First 5 entries:")
    for entry in vocabulary[:5]:
        print(entry)

# Save to CSV
df = pd.DataFrame(vocabulary)
df.to_csv(OUTPUT_PATH, index=False, encoding='utf-8')
print(f"✅ Vocabulary scraped and saved to {OUTPUT_PATH}")
