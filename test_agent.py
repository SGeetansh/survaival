import time
from ai.agent import Agent
from ai.memory import MemoryStore
from ai.llm import LocalLLM
from ai.prompt import build_prompt


# ----------------------------
# Setup AI Judge
# ----------------------------

llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")
memory = MemoryStore()
agent = Agent(llm, memory)


# ----------------------------
# Game Data
# ----------------------------

scenario = """
You are inside a subway train stopped in a tunnel.
Smoke is filling the carriage.
The emergency doors are jammed.
Visibility is low and conditions are worsening.
"""

players = ["Alice", "Bob", "Charlie"]

player_responses = {
    "Alice": "I stay low to avoid smoke, use my phone light, and try to find emergency equipment.",
    "Bob": "I stay calm, sit down, and wait for authorities to rescue us.",
    "Charlie": "I cover my face with my shirt and follow the wall to look for a maintenance exit."
}


# ----------------------------
# Helper functions
# ----------------------------

def divider():
    print("\n" + "=" * 40 + "\n")


# ----------------------------
# Simulation Begins
# ----------------------------

divider()
print("🧠 DEATH BY AI")
divider()

print("SITUATION:")
print(scenario.strip())

divider()
print("⏳ Players have 60 seconds to respond...")
time.sleep(2)  # simulate wait
print("🔒 Responses locked.")
divider()


print("🤖 AI JUDGEMENT PHASE")
divider()

results = {}

for player in players:
    print(f"👤 Player: {player}\n")
    print("📄 Response:")
    print(f"\"{player_responses[player]}\"\n")

    # Judge ONLY this player (important)
    verdict_text = agent.judge(
        scenario=scenario,
        player_responses={player: player_responses[player]}
    )

    print("⚖️ AI JUDGEMENT:")
    print(verdict_text.strip())

    # Store raw result for summary
    results[player] = verdict_text

    divider()
    time.sleep(2)  # dramatic pause


# ----------------------------
# Summary
# ----------------------------

print("🏁 ROUND SUMMARY")
divider()

for player, verdict in results.items():
    status = "SURVIVED" if "SURVIVE" in verdict else "DIED"
    emoji = "🟢" if status == "SURVIVED" else "🔴"
    print(f"{emoji} {player} → {status}")

divider()
print("End of round.")
