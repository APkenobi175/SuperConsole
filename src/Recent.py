# src/recent.py
import json
import os

RECENT_FILE = "recent.json"
MAX_RECENT = 10
FAVORITES_FILE = "favorites.json"

def load_recent():
    if os.path.exists(RECENT_FILE):
        try:
            with open(RECENT_FILE, 'r') as f:
                recent = json.load(f)
                # Validate structure
                if isinstance(recent, list):
                    return [
                        g for g in recent
                        if isinstance(g, dict) and
                        all(k in g for k in ("title", "platform", "rom_path", "cover_path"))
                    ]
        except json.JSONDecodeError:
            print("Error: recent.json is corrupted. Resetting.")
    return []


def save_recent(game_info):
    recent = load_recent()

    # Remove if already exists
    recent = [g for g in recent if g['title'] != game_info['title'] or g['platform'] != game_info['platform']]

    # Add to front
    recent.insert(0, game_info)

    # Trim list
    recent = recent[:MAX_RECENT]

    with open(RECENT_FILE, 'w') as f:
        json.dump(recent, f, indent=2)

def load_favorites():
    if os.path.exists(FAVORITES_FILE):
        with open(FAVORITES_FILE, 'r') as f:
            return json.load(f)
    return []
