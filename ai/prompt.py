def build_prompt(memory, scenario, player_responses):
    responses_text = "\n".join(
        f"{player}: {response}"
        for player, response in player_responses.items()
    )

    players = list(player_responses.keys())
    num_players = len(players)

    return f"""
You are the AI judge in a game similar to Death by AI.

Scenario:
{scenario.strip()}

Players ({num_players} total):
{', '.join(players)}

Player responses:
{responses_text.strip()}

Task:
- You MUST judge EVERY player listed above
- You MUST output EXACTLY {num_players} verdict blocks
- Do NOT stop early

Output format (repeat exactly {num_players} times):

Player: <name>
VERDICT: SURVIVE or DIE
REASON: <one sentence>

Begin now.
"""
