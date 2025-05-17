import pandas as pd

MAIN_CORPUS = 'main_corpus.csv'
main_corpus_df = pd.read_csv(MAIN_CORPUS)

def search_lummi(lummi_word):
    results = main_corpus_df[main_corpus_df['lummi_sentence'] == lummi_word]
    if not results.empty:
        print(f"\n🌐 Translations for '{lummi_word}':")
        for _, row in results.iterrows():
            print(f" - {row['english_sentence']}")

def search_english(english_word):
    results = main_corpus_df[main_corpus_df['english_sentence'] == english_word]
    if not results.empty:
        print(f"\n🌐 Translations for '{english_word}':")
        for _, row in results.iterrows():
            print(f" - {row['lummi_sentence']}")

while True:
    print("\n1. Search Lummi → English\n2. Search English → Lummi\n3. Exit")
    choice = input("Select an option: ")
    if choice == '1':
        word = input("Enter Lummi word: ").strip()
        search_lummi(word)
    elif choice == '2':
        word = input("Enter English word: ").strip()
        search_english(word)
    elif choice == '3':
        break
