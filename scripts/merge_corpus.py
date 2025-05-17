import pandas as pd
import os

NORMALIZED_DATA = 'normalized_data.csv'
MAIN_CORPUS = 'main_corpus.csv'

# Load data
normalized_df = pd.read_csv(NORMALIZED_DATA)
if os.path.exists(MAIN_CORPUS):
    main_corpus_df = pd.read_csv(MAIN_CORPUS)
else:
    main_corpus_df = pd.DataFrame(columns=['id', 'lummi_sentence', 'english_sentence'])

# Merge and remove duplicates
merged_df = pd.concat([main_corpus_df, normalized_df]).drop_duplicates()
merged_df.to_csv(MAIN_CORPUS, index=False)
print(f"Merged data saved to {MAIN_CORPUS}")
