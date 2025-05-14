import os
import sys
import json
from datetime import datetime, timedelta
from atproto import Client
from openai import OpenAI
import requests

# ---------------------------
# Game Window Check Function
# ---------------------------

def should_run_now(schedule_path="schedule.json"):
    """
    Check if WADE should be running now, based on today's Giants schedule.
    Only runs from first pitch to 4 hours after.
    """
    now = datetime.utcnow()

    if not os.path.exists(schedule_path):
        print("⚠️ schedule.json not found. Running anyway.")
        return True  # fail-safe to prevent total shutdown

    try:
        with open(schedule_path, "r", encoding="utf-8") as f:
            schedule = json.load(f)
    except Exception as e:
        print(f"⚠️ Failed to load schedule: {e}")
        return True  # fail-safe

   for game in schedule:
    try:
        game_time = parser.isoparse(game["start_time_utc"])
            end = start + timedelta(hours=4)

            if start.date() == now.date() and start <= now <= end:
                print(f"✅ Game in progress ({start.isoformat()}–{end.isoformat()}). Proceeding.")
                return True
        except Exception as e:
            print(f"⚠️ Error parsing game time: {e}")
            continue

    print("🛑 Not in a valid game window. Exiting.")
    return False

# ---------------------------
# Main WADE Posting Script
# ---------------------------

if not should_run_now():
    sys.exit()

# Simulated logic — replace with actual WADE logic below

print("🎯 Game ID: 777916 (start: 2025-05-14T19:45:00Z)")
print("✅ WADE check complete.")
