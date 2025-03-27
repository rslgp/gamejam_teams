import pandas as pd
import glob
from collections import defaultdict

def find_duplicate_authors(csv_files):
    """
    Find author IDs that appear in more than one CSV file.
    
    Args:
        csv_files (list): List of CSV file paths to process
        
    Returns:
        dict: {author: list_of_dataframes} containing duplicates
        list: All unique duplicate author IDs
    """
    author_files = defaultdict(list)
    
    for file in csv_files:
        df = pd.read_csv(file)

        df["file_name"] = file  # Add the file name as a new column
        # Rename column if needed        
        for author in df['author'].unique():
            author_files[author].append(df[df['author'] == author])
    
    # Filter only authors that appear in more than one file
    duplicate_authors = {k: v for k, v in author_files.items() if len(v) > 1}
    
    return duplicate_authors, list(duplicate_authors.keys())

def extract_duplicates_to_csv(csv_files, output_file):
    """
    Process multiple CSVs and save duplicate authors to a new CSV.
    
    Args:
        csv_files (list): List of CSV file paths
        output_file (str): Path for output CSV
    """
    # Find duplicate authors
    duplicates, authors = find_duplicate_authors(csv_files)
    
    if not duplicates:
        print("No duplicate authors found across files.")
        return
    
    print(f"Found {len(authors)} duplicate authors: {authors}")
    
    # Combine all records for duplicate authors
    dfs_to_combine = []
    for author in authors:
        for df in duplicates[author]:
            dfs_to_combine.append(df)
    
    # Concatenate all records
    combined_df = pd.concat(dfs_to_combine, ignore_index=True)
    
    # Select and order the desired columns
    desired_columns = [
        "author", "ludum_dare_version", "cool", "feedback", "given", "grade", 
        "grade-01-average", "grade-01-result", "grade-02-average", "grade-02-result",
        "grade-03-average", "grade-03-result", "grade-04-average", "grade-04-result",
        "grade-05-average", "grade-05-result", "grade-06-average", "grade-06-result",
        "grade-07-average", "grade-07-result", "grade-08-average", "grade-08-result", "smart"
    ]
    
    # Filter only the columns that exist in the data
    available_columns = [col for col in desired_columns if col in combined_df.columns]
    combined_df = combined_df[available_columns]
    
    # Save to CSV
    combined_df.to_csv(output_file, index=False)
    print(f"Saved duplicate author records to {output_file}")

# Example usage
if __name__ == "__main__":
    # Find all CSV files in the current directory
    csv_files = glob.glob("ludum_dare_games_*.csv")
    
    if not csv_files:
        print("No CSV files found in current directory.")
    else:
        print(f"Processing {len(csv_files)} CSV files...")
        extract_duplicates_to_csv(csv_files, "duplicate_authors_teams.csv")