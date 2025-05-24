import pandas as pd
import os

def update_lummi_vocab(existing_csv, new_data_csv, output_csv=None):
    """
    Update the existing Lummi vocabulary CSV file with new entries.
    
    Parameters:
    existing_csv (str): Path to the existing Lummi vocabulary CSV
    new_data_csv (str): Path to the new data CSV to be merged
    output_csv (str, optional): Path to save the updated CSV file. 
                               If None, overwrites the existing file.
    
    Returns:
    pandas.DataFrame: The updated DataFrame
    """
    print(f"Loading existing vocabulary from {existing_csv}")
    existing_df = pd.read_csv(existing_csv)
    
    print(f"Loading new data from {new_data_csv}")
    new_df = pd.read_csv(new_data_csv)
    
    # Standardize column names to lowercase
    existing_df.columns = [col.lower() for col in existing_df.columns]
    new_df.columns = [col.lower() for col in new_df.columns]
    
    print(f"Existing vocabulary entries: {len(existing_df)}")
    print(f"New data entries: {len(new_df)}")
    
    # Create backup of existing file
    backup_path = existing_csv + '.backup'
    print(f"Creating backup of existing data at {backup_path}")
    existing_df.to_csv(backup_path, index=False)
    
    # Check for duplicates by converting English terms to lowercase for comparison
    existing_df['english_lower'] = existing_df['english'].str.lower()
    new_df['english_lower'] = new_df['english'].str.lower()
    
    # Find entries in the new data that don't exist in the original data
    duplicates = new_df[new_df['english_lower'].isin(existing_df['english_lower'])]
    unique_entries = new_df[~new_df['english_lower'].isin(existing_df['english_lower'])]
    
    print(f"Found {len(duplicates)} duplicate entries")
    print(f"Found {len(unique_entries)} unique new entries")
    
    if len(duplicates) > 0:
        print("\nDuplicate entries (not added):")
        for _, row in duplicates.iterrows():
            print(f"  - {row['english']}: {row['lummi']}")
    
    # Remove temporary columns used for comparison
    existing_df = existing_df.drop(columns=['english_lower'])
    unique_entries = unique_entries.drop(columns=['english_lower'])
    
    # Concatenate dataframes
    updated_df = pd.concat([existing_df, unique_entries], ignore_index=True)
    
    # Sort by English terms
    updated_df = updated_df.sort_values('english')
    
    # Save the updated vocabulary
    if output_csv is None:
        output_csv = existing_csv
    
    updated_df.to_csv(output_csv, index=False)
    print(f"\nUpdated vocabulary saved to {output_csv}")
    print(f"Total entries in updated vocabulary: {len(updated_df)}")
    
    return updated_df

def main():
    """
    Main function to run the update process.
    """
    # Define file paths
    existing_csv = '../raw_data/Lummi_vocab.csv'
    new_data_csv = '../processed_data/quizlet_lummi_cleaned.csv'
    
    # Update the vocabulary
    update_lummi_vocab(existing_csv, new_data_csv)

if __name__ == "__main__":
    main()