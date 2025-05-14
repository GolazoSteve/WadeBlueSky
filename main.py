import os
import json
import requests
import datetime
from zoneinfo import ZoneInfo
from openai import OpenAI
from atproto import Client

# === CONFIGURATION ===
TEAM_ID = 137  # San Francisco Giants
POST_WINDOW_HOURS = 4

# Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BLUESKY_HANDLE = os.getenv("BLUESKY_HANDLE")
BLUESKY_PASSWORD = os.getenv("BLUESKY_PASSWORD")

client_ai = OpenAI(api_key=OPENAI_API_KEY)
client_bsky = Client()
client_bsky.login(BLUESKY_HANDLE, BLUESKY_PASSWORD)

# Load prompt
with open("wade_prompt.txt", "r", encoding="utf-8") as f:
    WADE_PROMPT = f.read()

# Load Giants schedule
with open("giants_schedule.json", "r", encoding="utf-8") as f:
    giants_schedule = json.load(f)

# === TIME CHECK ===
def is_within_game_window(schedule):
    now = datetime.datetime.now(ZoneInfo("UTC"))
    for game in schedule:
        try:
            start = datetime.datetime.fromisoformat(game["start_time_utc"].replace("Z", "+00:00"))
            end = start + datetime.timedelta(hours=POST_WINDOW_HOURS)
            if start <= now <= end:
                return True, game["start_time_utc"]
        except:
            continue
    return False, None

# === FETCH GAME ID ===
def get_game_id():
    today = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    url = f"https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={today}"
    response = requests.get(url).json()
    for date in response.get("dates", []):
        for game in date.get("games", []):
            if TEAM_ID in [game["teams"]["home"]["team"]["id"], game["teams"]["away"]["team"]["id"]]:
                return game["gamePk"]
    return None

# === FETCH PLAYS ===
def fetch_all_plays(game_id):
    url = f"https://statsapi.mlb.com/api/v1.1/game/{game_id}/feed/live"
    return requests.get(url).json().get("liveData", {}).get("plays", {}).get("allPlays", [])

# === POST LOGIC ===
def is_giants_pa(play):
    team_id = (
        play.get("team", {}).get("id") or
        play.get("matchup", {}).get("battingTeam", {}).get("id")
    )
    return team_id == TEAM_ID

def should_post(play):
    event = play.get("result", {}).get("event", "")
    rbi = play.get("result", {}).get("rbi", 0)
    batter = play.get("matchup", {}).get("batter", {}).get("fullName", "")

    if event == "Home Run" and is_giants_pa(play):
        return True, "Giants Home Run"
    if is_giants_pa(play) and rbi > 0:
        return True, "Giants RBI scoring play"
    if batter == "Jung Hoo Lee" and event in {"Single", "Double", "Triple", "Home Run", "Walk", "Hit By Pitch"}:
        return True, f"Priority: Jung Hoo Lee {event}"
    if batter == "Matt Chapman" and event in {"Double", "Triple", "Home Run"}:
        return True, f"Priority: Matt Chapman {event}"
    if batter == "Tyler Fitzgerald" and event in {"Single", "Double", "Triple", "Home Run"}:
        return True, f"Priority: Tyler Fitzgerald {event}"
    if batter == "Willy Adames" and event in {"Double", "Triple", "Home Run"}:
        return True, f"Priority: Willy Adames {event}"

    return False, "No trigger"

# === POST GENERATION ===
def generate_post(description):
    messages = [
        {"role": "system", "content": WADE_PROMPT},
        {"role": "user", "content": f"Write a Bluesky post reacting to this: {description}"}
    ]
    response = client_ai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.85,
        max_tokens=300
    )
    post = response.choices[0].message.content.strip()
    if "#SFGiants" not in post:
        post += " #SFGiants"
    return post[:300]

# === MAIN LOGIC ===
if __name__ == "__main__":
    active, start_time = is_within_game_window(giants_schedule)
    if not active:
        print("📴 Outside game window. Exiting.")
        exit()

    game_id = get_game_id()
    if not game_id:
        print("❌ No Giants game found today.")
        exit()

    print(f"🎯 Game ID: {game_id} (start: {start_time})")
    plays = fetch_all_plays(game_id)

    for play in reversed(plays[-5:]):  # Only check last few plays
        desc = play.get("result", {}).get("description", "")
        decision, reason = should_post(play)
        if decision:
            print(f"📣 Trigger matched: {reason}")
            post = generate_post(desc)
            print(f"📤 {post}")
            client_bsky.send_post(text=post)
            break  # Post once and exit

    print("✅ WADE check complete.")

