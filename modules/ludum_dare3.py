import requests
import csv
import time
import re

def extract_unique_links(text):
    # Regex pattern to match URLs
    url_pattern = r'https?://[^\s)"]+'
    links = re.findall(url_pattern, text)
    
    # Return unique links
    return list(set(links))

def fetch_json(url):
    """Fetch JSON data from a given URL."""
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def get_game_results(event_id, limit):
    """Fetch game results for the given Ludum Dare event ID."""
    results_url = f"https://api.ldjam.com/vx/node2/walk/1/events/ludum-dare/{event_id}/results/overall/jam?node&parent&_superparent&author"
    results_data = fetch_json(results_url)
    node_id = results_data['node_id']  # Extract node_id
    
    games_url = f"https://api.ldjam.com/vx/node/feed/{node_id}/grade-01-result+reverse+parent/item/game/jam?limit={limit}"
    games_data = fetch_json(games_url)
    
    return [(game['id'], game['value']) for game in games_data['feed']]

def get_game_details(game_ids):
    """Fetch details for a list of game IDs."""
    ids_str = '+'.join(map(str, game_ids))
    details_url = f"https://api.ldjam.com/vx/node2/get/{ids_str}"
    return fetch_json(details_url)['node']

def save_to_csv(filename, game_data, magic_keys):
    # print(game_data)
      # Sort game data by game_position before saving
    game_data.sort(key=lambda x: x["game_position"])

    """Save game data to a CSV file."""
    headers = [
        "id", "name", "author", "team_size", "slug", "published", "created", "modified", "path", "comments",
        "game_position", "ludum_dare_version", "data_authors", "game_link", "links_body"
    ] + magic_keys
    
    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        for game in game_data:
            writer.writerow(game)

def main(event_id=48, limit=200, output_file="ludum_dare_games"):
    """Main function to fetch and save Ludum Dare game data."""
    print(f"Fetching top {limit} games for Ludum Dare event {event_id}...")
    game_results = get_game_results(event_id, limit)
    game_ids = [game_feed[0] for game_feed in game_results]
    game_positions = {game_feed[0]: game_feed[1] for game_feed in game_results}  # Store positions in a dict

    
    print("Fetching game details...")
    game_details = get_game_details(game_ids)
    
    processed_data = []


    magic_keys = set()
    for game in game_details:
        magic_data = game.get("magic", {})
        magic_keys.update(magic_data.keys())
        authors = game.get("meta", "").get("author", "")

        game_id = game.get("id", "")
        processed_data.append({
            "id": game.get("id", ""),
            "name": game.get("name", ""),
            "author": authors,
            "team_size": len(authors),

            "game_position": game_positions.get(game_id, ""),  # Append game position
            
            "slug": game.get("slug", ""),
            "published": game.get("published", ""),
            "created": game.get("created", ""),
            "modified": game.get("modified", ""),
            "path": game.get("path", ""),
            "comments": game.get("comments", ""),
            "ludum_dare_version": event_id,
            **magic_data,
            "data_authors": f"https://api.ldjam.com/vx/node2/get/{'+'.join(map(str, authors))}",
            "game_link": f"https://ldjam.com/events/ludum-dare/{event_id}/{game.get("slug", "")}",
            "links_body": extract_unique_links(game.get("body", "")),
        })
        time.sleep(0.2)  # Rate limiting
    
    print(f"Saving data to {output_file}...")

    magic_keys = sorted(magic_keys)  # Ensure consistent column order
    save_to_csv(f"{output_file}_{event_id}.csv", processed_data, magic_keys)
    print("Done!")

if __name__ == "__main__":
    main()