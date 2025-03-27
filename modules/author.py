import pandas as pd
import glob
import ast  # For safely evaluating string representations of lists

# Step 1: Read all CSV files
csv_files = glob.glob("ludum_dare_games_*.csv")  # Select all CSV files in the directory
df_list = [pd.read_csv(file) for file in csv_files]

# Step 2: Flatten and count unique authors across files
author_counts = {}  # Dictionary to store author ID occurrences
author_data = {}  # Store last seen author-related data

# Columns to keep
columns_to_keep = [
    "game_position", "team_size", "ludum_dare_version","game_link", "id","cool", "feedback", "given", "grade", "grade-01-average", "grade-01-result",
    "grade-02-average", "grade-02-result", "grade-03-average", "grade-03-result",
    "grade-04-average", "grade-04-result", "grade-05-average", "grade-05-result",
    "grade-06-average", "grade-06-result", "grade-07-average", "grade-07-result",
    "grade-08-average", "grade-08-result", "smart"
]

# Step 3: Process each CSV file and add file name
for file in csv_files:
    df = pd.read_csv(file)
    df = df.dropna(subset=["author"])  # Drop rows where "author" is empty
    for _, row in df.iterrows():
        # Safely convert the author string to a list if necessary
        try:
            # Convert author to a list if it is a string representation of a list (e.g., "[9110, 122697]")
            authors = ast.literal_eval(row["author"]) if isinstance(row["author"], str) else [row["author"]]
        except (ValueError, SyntaxError):
            authors = []  # In case the author field is not formatted correctly
        
        # Handle case where `author` might be a single integer (not a list)
        if isinstance(authors, int):
            authors = [authors]  # Wrap it in a list

        for author in authors:
            if author:  # Ensure there's a valid author ID
                # Increment the author count and store their data with file name
                if author not in author_data:
                    author_data[author] = []
                author_data[author].append({"file_name": file, **row[columns_to_keep].to_dict()})
                author_counts[author] = author_counts.get(author, 0) + 1

# Step 4: Create final DataFrame
result_data = []
for author, data_list in author_data.items():
    for data in data_list:
        row_data = {"author": author, "count": author_counts[author], "file_name": data["file_name"]}
        row_data.update({key: data[key] for key in columns_to_keep})
        result_data.append(row_data)

final_df = pd.DataFrame(result_data)

# Step 5: Save to CSV
final_df.to_csv("merged_authors_with_files.csv", index=False)

print("Merged CSV created: merged_authors_with_files.csv")
