import pandas as pd
import numpy as np

def calculate_author_rank(df):
    """
    Calculate author rankings with:
    - Tiered position weighting (top 15, top 25, top 50, others)
    - Custom category weights (Fun > Overall > Mood > Graphics)
    - Team size as neutral factor
    """
    
    # SCORING LEGEND
    scoring_legend = {
        'position_tiers': {
            'top_15': {'threshold': 15, 'weight_multiplier': 1.5},
            'top_25': {'threshold': 25, 'weight_multiplier': 1.3},
            'top_50': {'threshold': 50, 'weight_multiplier': 1.1},
            'others': {'weight_multiplier': 1.0}
        },
        'category_weights': {
            'Fun': 0.35,      # Highest priority
            'Overall': 0.30,   # Second priority
            'Mood': 0.12,     # Third priority
            'Graphics': 0.10,  # Fourth priority
            'Innovation': 0.05,
            'Audio': 0.04,
            'Theme': 0.03,
            'Humor': 0.01
        },
        'scoring_notes': [
            'Position tiers multiply the base category scores',
            'Top 15 positions get 3x multiplier',
            'Top 25 positions get 1.3x multiplier',
            'Top 50 positions get 1.1x multiplier',
            'Top 100 positions get 1.0x multiplier',
            'Top others positions get 0.7x multiplier'
        ]
    }
    
    # Make a copy of the dataframe
    ranked_df = df.copy()
    
    # Convert numeric columns
    numeric_cols = [
        'cool', 'feedback', 'given', 'grade', 'smart',
        'grade-01-average', 'grade-02-average', 'grade-03-average',
        'grade-04-average', 'grade-05-average', 'grade-06-average',
        'grade-07-average', 'grade-08-average',
        'grade-01-result', 'grade-02-result', 'grade-03-result',
        'grade-04-result', 'grade-05-result', 'grade-06-result',
        'grade-07-result', 'grade-08-result'
    ]
    
    for col in numeric_cols:
        if col in ranked_df.columns:
            ranked_df[col] = pd.to_numeric(ranked_df[col], errors='coerce')
    
    # Create game_position array from all result columns
    result_columns = [
        'grade-01-result', 'grade-02-result'
    ]
    
    ranked_df['game_position'] = ranked_df[result_columns].values.tolist()
    
    # Component weights
    weights = {
        'participation': 0.10,
        'community': 0.10,
        'performance': 0.80  # Increased weight for performance
    }
    
    # 1. Participation Score (team_size neutral)
    ranked_df['participation_score'] = ranked_df['count'].fillna(1).clip(0, 5)
    
    # 2. Community Engagement Score
    community_cols = ['cool', 'given']
    available_community = [c for c in community_cols if c in ranked_df.columns]
    ranked_df['community_score'] = (
        ranked_df[available_community].mean(axis=1).fillna(0) if available_community else 0
    )
    
    # 3. Performance Score with tiered position weighting
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
    
    # Calculate base scores for each category
    for prefix, category in category_mapping.items():
        avg_col = f'{prefix}-average'
        
        if avg_col in ranked_df.columns:
            # Normalize average score (0-5 → 0-1)
            ranked_df[f'{category}_avg_score'] = ranked_df[avg_col].fillna(0) / 5
            
            # Get position from game_position array
            pos_idx = list(category_mapping.keys()).index(prefix)
            ranked_df[f'{category}_rank'] = ranked_df['game_position'].apply(
                lambda x: x[pos_idx] if isinstance(x, list) and len(x) > pos_idx else np.nan
            )
            
            # Apply tiered position multipliers
            conditions = [
                (ranked_df[f'{category}_rank'] <= 15),
                (ranked_df[f'{category}_rank'] <= 25),
                (ranked_df[f'{category}_rank'] <= 50),
                (ranked_df[f'{category}_rank'] <= 100),
                (ranked_df[f'{category}_rank'] > 100) | (ranked_df[f'{category}_rank'].isna())
            ]
            multipliers = [12, 9, 3, 1.0, 0.7]
            ranked_df[f'{category}_position_multiplier'] = np.select(conditions, multipliers)
            
            # Combined score (base average × position multiplier)
            ranked_df[f'{category}_score'] = (
                ranked_df[f'{category}_avg_score'] * 
                ranked_df[f'{category}_position_multiplier']
            )
    
    # Calculate weighted performance score
    performance_score = 0
    total_weight = 0
    for category, weight in scoring_legend['category_weights'].items():
        performance_score += ranked_df.get(f'{category}_score', 0) * weight
        total_weight += weight
    
    ranked_df['performance_score'] = (performance_score / total_weight if total_weight > 0 else 0)
    
    # Final composite score (0-100)
    ranked_df['composite_score'] = (
        weights['participation'] * ranked_df['participation_score'] +
        weights['community'] * ranked_df['community_score'] +
        weights['performance'] * ranked_df['performance_score']
    ) * 100
    
    # Add rank column
    ranked_df['rank'] = ranked_df['composite_score'].rank(ascending=False, method='min').astype(int)
    
    # Sort and prepare output
    ranked_df = ranked_df.sort_values('rank')
    
    # Prepare output columns
    output_columns = [
        'rank', 'author', 'composite_score', 'count', 'team_size',
        'grade', 'game_position', 'performance_score', 'game_link'
    ]
    
    # Add all category scores and positions
    for category in scoring_legend['category_weights'].keys():
        output_columns.extend([
            f'{category}_score',
            f'{category}_rank',
            f'grade-{list(category_mapping.keys())[list(category_mapping.values()).index(category)]}-average'
        ])
    
    # Select available columns
    available_columns = [col for col in output_columns if col in ranked_df.columns]
    
    return ranked_df[available_columns], scoring_legend

# Example usage:
if __name__ == "__main__":
    # Load your data
    df = pd.read_csv("merged_authors_with_files.csv")
    
    # Calculate rankings
    ranked_authors, legend = calculate_author_rank(df)
    
    # Save results
    ranked_authors.to_csv("ranked_authors_tiered_weighting.csv", index=False)
    
    # Save legend
    with open("ranking_legend.txt", "w") as f:
        f.write("POSITION TIERS:\n")
        for tier, spec in legend['position_tiers'].items():
            if tier != 'others':
                f.write(f"{tier.replace('_', ' ').title()}: Top {spec['threshold']} positions get {spec['weight_multiplier']}x multiplier\n")
            else:
                f.write(f"Others: Standard weighting ({spec['weight_multiplier']}x)\n")
        
        f.write("\nCATEGORY WEIGHTS:\n")
        for cat, weight in legend['category_weights'].items():
            f.write(f"{cat}: {weight*100:.1f}%\n")
    
    print("Top 10 Authors:")
    print(ranked_authors.head(10)[['rank', 'author', 'composite_score', 'Fun_rank', 'Overall_rank']])
    print("\nScoring legend saved to ranking_legend.txt")