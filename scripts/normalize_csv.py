import pandas as pd
import uuid
import os

RAW_FOLDER = 'raw_data/'
OUTPUT_FILE = 'normalized_data.csv'
os.makedirs('raw_data', exist_ok=True)

data = pd.concat([pd.read_csv(f"{RAW_FOLDER}{file}") for file in os.listdir(RAW_FOLDER) if file.endswith('.csv')])

unique_ids = {}
rows = []

for _, row in data.iterrows():
    lummi_sentence = row['lummi_sentence'].strip()
    english_sentence = row['english_sentence'].strip()
    lummi_id = unique_ids.get(lummi_sentence) or uuid.uuid4().hex[:8]
    english_id = unique_ids.get(english_sentence) or uuid.uuid4().hex[:8]
    unique_ids[lummi_sentence] = lummi_id
    unique_ids[english_sentence] = english_id
    
    rows.append({'id': lummi_id, 'lummi_sentence': lummi_sentence, 'english_sentence': english_sentence})

df = pd.DataFrame(rows)
df.to_csv(OUTPUT_FILE, index=False)
print(f"Data normalized and saved to {OUTPUT_FILE}")
