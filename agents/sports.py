from nba_api.stats.endpoints import playergamelog
from nba_api.stats.static import players
import anthropic
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
client = anthropic.Anthropic()

# The Israeli players we track
ISRAELI_PLAYERS = [
    {"name": "Deni Avdija", "team": "Portland Trail Blazers"},
    {"name": "Ben Saraf", "team": "Brooklyn Nets"},
    {"name": "Danny Wolf", "team": "Brooklyn Nets"},
]

def get_player_id(full_name: str):
    """Find player ID by name"""
    all_players = players.get_players()
    for p in all_players:
        if p["full_name"].lower() == full_name.lower():
            return p["id"]
    return None

def get_last_game_stats(player_name: str) -> dict:
    player_id = get_player_id(player_name)
    if not player_id:
        return {"player": player_name, "status": "Player not found"}

    gamelog = playergamelog.PlayerGameLog(
        player_id=player_id,
        season="2025-26"
    )

    df = gamelog.get_data_frames()[0]

    if df.empty:
        return {"player": player_name, "status": "No games found this season"}

    last_game = df.iloc[0]
    game_date_str = last_game["GAME_DATE"]

    # Check if the game was last night
    game_date = datetime.strptime(game_date_str, "%b %d, %Y")
    yesterday = datetime.now() - timedelta(days=1)

    if game_date.date() != yesterday.date():
        return {"player": player_name, "status": "Did not play last night"}

    return {
        "player": player_name,
        "date": game_date_str,
        "opponent": last_game["MATCHUP"],
        "points": int(last_game["PTS"]),
        "assists": int(last_game["AST"]),
        "rebounds": int(last_game["REB"]),
        "minutes": int(last_game["MIN"]),
        "result": last_game["WL"]
    }

def run(query: str = "") -> str:
    """Main function — fetch stats and return Hebrew summary"""

    print("  Fetching NBA stats for Israeli players...")

    stats = []
    for player in ISRAELI_PLAYERS:
        data = get_last_game_stats(player["name"])
        stats.append(data)
        print(f"  Got stats for {player['name']}")

    # Build a summary prompt
    stats_text = ""
    for s in stats:
        if "points" in s:
            stats_text += f"""
{s['player']} ({s['date']}):
- Game: {s['opponent']} | Result: {s['result']}
- Points: {s['points']} | Assists: {s['assists']} | Rebounds: {s['rebounds']}
- Minutes: {s['minutes']}
"""
        else:
            stats_text += f"\n{s['player']}: {s['status']}\n"

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=500,
        system="""You are a sports reporter covering Israeli NBA players.
        Present the stats in a clean, engaging format in Hebrew.
        If a player did not play, mention it clearly.""",
        messages=[
            {
                "role": "user",
                "content": f"Here are the latest stats for the Israeli NBA players:\n{stats_text}"
            }
        ]
    )

    return response.content[0].text