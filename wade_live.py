# wade_live.py
import requests
import time
from datetime import datetime
from openai import OpenAI
import os

# Setup your client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def fetch_plays(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    response = requests.get(url)
    data = response.json()
    return data.get("liveData", {}).get("plays", {}).get("allPlays", [])

def filter_and_generate_post(play):
    # Placeholder filtering logic – update this based on your project criteria
    description = play.get("result", {}).get("description", "")
    if "San Francisco" in description:
        return f"🟠 WADE SYSTEM DETECTED: {description}"
    return None

def run_wade_bot(game_pk):
    print(f"🚨 WADE LIVE STARTED: gamePk={game_pk}")
    plays = fetch_plays(game_pk)
    print(f"📦 Total plays fetched: {len(plays)}")

    for play in plays[-5:]:  # For now, just show last 5
        post = filter_and_generate_post(play)
        if post:
            print(f"📤 POST: {post}")
        else:
            description = play.get("result", {}).get("description")
            if description:
                print(f"🤖 Ignored play: {description}")
            else:
                print("🤖 Ignored play with no description")

if __name__ == "__main__":
    # For quick testing
    test_pk = 746721  # Replace with a real past gamePk
    run_wade_bot(test_pk)
