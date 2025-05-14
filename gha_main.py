# gha_main.py

import os
import json
import datetime
import requests
from dateutil import parser
from pytz import timezone, utc

def load_schedule():
    try:
        with open("schedule.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️ schedule.json not found. Running anyway.")
        return []

def find_today_game(schedule):
    today = datetime.datetime.now(tz=utc).date()
    for game in schedule:
        try:
            game_time = parser.isoparse(game["start_time_utc"])  # This must match your schedule.json format
            game_date = game_time.date()
            if game_date == today:
                return game_time, game.get("game_id")
        except Exception as e:
            print(f"⚠️ Error parsing game time: {e}")
    return None, None

def in_valid_window(game_time):
    now = datetime.datetime.now(tz=utc)
    window_start = game_time - datetime.timedelta(hours=1)
    window_end = game_time + datetime.timedelta(hours=5)
    return window_start <= now <= window_end

def main():
    schedule = load_schedule()
    game_time, game_id = find_today_game(schedule)

    if not game_time:
        print("🛑 No Giants game scheduled today. Exiting.")
        return

    if not in_valid_window(game_time):
        print("🛑 Not in a valid game window. Exiting.")
        return

    print(f"🎯 Game ID: {game_id} (start: {game_time.isoformat()})")
    print("✅ WADE check complete.")
    # Your main bot logic would run here...

if __name__ == "__main__":
    main()
