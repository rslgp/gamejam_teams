import pandas as pd
from collections import defaultdict

def calculate_author_rankings(csv_path):
    # Load the CSV data
    df = pd.read_csv(csv_path)
    
    # Define category mapping and weights
    category_mapping = {
        'grade-01': 'Overall',
        'grade-02': 'Fun',
        'grade-03': 'Innovation',
        'grade-04': 'Theme',
        'grade-05': 'Graphics',
        'grade-06': 'Audio',
        'grade-07': 'Humor',
        'grade-08': 'Mood'
    }
    
    category_weights = {
        'Fun': 0.35,
        'Overall': 0.30,
        'Mood': 0.12,
        'Graphics': 0.10,
        'Innovation': 0.05,
        'Audio': 0.04,
        'Theme': 0.03,
        'Humor': 0.01
    }
    
    # Prepare data structures to store aggregated author data
    author_data = defaultdict(lambda: {
        'total_score': 0,
        'entries': 0,
        'average_scores': defaultdict(float),
        'average_ranks': defaultdict(float),
        'team_sizes': [],
        'participations': 0,
        'game_links': set(),
        'ludum_dare_versions': set()
    })
    
    # Process each row in the dataframe
    for _, row in df.iterrows():
        author = row['author']
        author_info = author_data[author]
        
        # Calculate weighted score for this entry
        entry_score = 0
        entry_ranks = {}
        
        for grade_key, category in category_mapping.items():
            avg_key = f"{grade_key}-average"
            result_key = f"{grade_key}-result"
            
            if avg_key in row and pd.notna(row[avg_key]):
                weight = category_weights[category]
                entry_score += row[avg_key] * weight
                
                # Track average scores and ranks per category
                author_info['average_scores'][category] += row[avg_key]
                if result_key in row and pd.notna(row[result_key]):
                    author_info['average_ranks'][category] += row[result_key]
        
        # Update author aggregates
        author_info['total_score'] += entry_score
        author_info['entries'] += 1
        
        # Track other metadata
        if pd.notna(row['team_size']):
            author_info['team_sizes'].append(row['team_size'])
        if pd.notna(row['game_link']):
            author_info['game_links'].add(row['game_link'])
        if pd.notna(row['ludum_dare_version']):
            author_info['ludum_dare_versions'].add(row['ludum_dare_version'])
    
    # Calculate final averages and prepare results
    results = []
    for author, data in author_data.items():
        # Calculate average score across all entries
        avg_score = data['total_score'] / data['entries']
        
        # Calculate average team size
        avg_team_size = (sum(data['team_sizes']) / len(data['team_sizes'])) if data['team_sizes'] else 0
        
        # Calculate average scores and ranks per category
        category_scores = {}
        category_ranks = {}
        for category in category_mapping.values():
            if data['average_scores'][category] > 0:
                category_scores[f"{category}_score"] = data['average_scores'][category] / data['entries']
                category_ranks[f"{category}_rank"] = data['average_ranks'][category] / data['entries']
        
        # Prepare result entry
        result = {
            'author': author,
            'overall_score': avg_score,
            'total_entries': data['entries'],
            'average_team_size': avg_team_size,
            'unique_events': len(data['ludum_dare_versions']),
            'unique_games': len(data['game_links']),
            **category_scores,
            **category_ranks,
            'game_link':data['game_links'],
            'ludum_events':data['ludum_dare_versions'],
        }
        results.append(result)
    
    # Convert to DataFrame and sort by overall score
    results_df = pd.DataFrame(results)
    results_df['rank'] = results_df['overall_score'].rank(ascending=False, method='min').astype(int)
    results_df = results_df.sort_values('rank')
    
    return results_df

# Example usage
if __name__ == "__main__":
    ranked_authors = calculate_author_rankings('merged_authors_with_files.csv')
    
    # Save results to a new CSV
    ranked_authors.to_csv('author_rankings1.csv', index=False)
    
    # Display top authors
    print(ranked_authors.head(10))