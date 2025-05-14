# gha_main.py
import os
from datetime import datetime, timedelta
from dateutil import parser
from pytz import utc
from wade_live import run_wade_bot


def get_most_recent_game():
    import requests

    team_id = 137  # Giants
    url = f"https://statsapi.mlb.com/api/v1/schedule?sportId=1&teamId={team_id}&date={datetime.utcnow().date()}"

    response = requests.get(url)
    data = response.json()
    dates = data.get("dates", [])
    if not dates:
        return None
    games = dates[0].get("games", [])
    if not games:
        return None

    game = games[0]
    game_time = parser.isoparse(game["gameDate"]).replace(tzinfo=utc)  # ✅ correct timezone handling
    return {
        "gamePk": game["gamePk"],
        "start_time_utc": game_time,
    }

def in_valid_game_window(game_time):
    now = datetime.utcnow().replace(tzinfo=utc)
    return game_time - timedelta(hours=1) <= now <= game_time + timedelta(hours=5)

def main():
    game = get_most_recent_game()
    if not game:
        print("🛑 No game found for today. Exiting.")
        return

    game_time = game["start_time_utc"]
    print(f"📅 Found game time: {game_time} (UTC)")
    now = datetime.utcnow().replace(tzinfo=utc)
    print(f"🕒 Current time:     {now} (UTC)")
    print(f"✅ Valid window:     {game_time - timedelta(hours=1)} → {game_time + timedelta(hours=5)} (UTC)")

    if not in_valid_game_window(game_time):
        print("🛑 Not in a valid game window. Exiting.")
        return

    # Run WADE
    run_wade_bot(game["gamePk"])

if __name__ == "__main__":
    main()
