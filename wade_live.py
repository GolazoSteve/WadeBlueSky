# wade_live.py
import requests
import time
from datetime import datetime
from openai import OpenAI
import os

# Setup your client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Giants team ID
GIANTS_TEAM_ID = 137

# Events that count as batter reaching base
REACH_BASE_EVENTS = {
    "single", "double", "triple", "home_run",
    "walk", "hit_by_pitch", "field_error", "fielders_choice"
}

# Optional: Events for stolen base tracking
STOLEN_BASE_EVENTS = {
    "stolen_base", "caught_stealing", "pickoff"
}

def fetch_plays(game_pk):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live"
    response = requests.get(url)
    data = response.json()
    return data.get("liveData", {}).get("plays", {}).get("allPlays", [])

def filter_and_generate_post(play):
    result = play.get("result", {})
    matchup = play.get("matchup", {})
    runners = play.get("runners", [])
    description = result.get("description", "")
    event_type = result.get("eventType", "")
    rbi_count = result.get("rbi", 0)

    is_giants_batting = matchup.get("battingTeamId") == GIANTS_TEAM_ID

    if is_giants_batting:
        if event_type in REACH_BASE_EVENTS:
            tags = []
            if rbi_count > 0:
                tags.append(f"{rbi_count} RBI{'s' if rbi_count > 1 else ''}")
            return f"🟠 BASE REACHED: {description}" + (f" ({', '.join(tags)})" if tags else "")
        elif event_type in STOLEN_BASE_EVENTS:
            return f"🟠 BASERUNNING: {description}"

    return None

def run_wade_bot(game_pk):
    print(f"🚨 WADE LIVE STARTED: gamePk={game_pk}")
    plays = fetch_plays(game_pk)
    print(f"📦 Total plays fetched: {len(plays)}")

    for play in plays[-10:]:  # Adjust window as needed
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
