import time
import json
from ai.agent import Agent
from ai.memory import MemoryStore
from ai.llm import LocalLLM
from ai.rag import SituationRAG
import random
from game.engine import GameEngine

# ----------------------------
# Setup
# ----------------------------
rag = SituationRAG("data/situations.json")

llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")
memory = MemoryStore()
rag = SituationRAG("data/situations.json")
agent = Agent(llm, memory, rag)
engine = GameEngine(agent, rag)

# ----------------------------
# Helpers
# ----------------------------


def divider():
    print("\n" + "=" * 50 + "\n")


situations = open("data/situations.json")
situations_dict = json.load(situations)

# ----------------------------
# Game Start
# ----------------------------

divider()
print("🧠 DEATH BY AI — SOLO MODE")
divider()

# Pick a situation (later: random)
situation_ids = list(situations_dict.keys())
random_situation_id = random.choice(situation_ids)
situation = rag.get(random_situation_id)

player_name = input("Enter your name: ").strip() or "Player"

print("SITUATION:")
print(situation["description"])

divider()
print("⏳ You have 60 seconds to respond.")
print("(Type your plan and press Enter)")
divider()

# ----------------------------
# Player Input
# ----------------------------


print("\nYour response:")
response = input("> ").strip()
divider()
print("🔒 Response locked.")
time.sleep(1)

# ----------------------------
# AI Judgement
# ----------------------------

print("🤖 AI JUDGEMENT")
divider()

results = engine.run_round(
    situation_id=situation["id"], player_responses={player_name: response}
)
result = results["results"][0]


print(f"Player: {result['player']}")
print(f"VERDICT: {result['verdict']}")
print("OUTCOME:")
print(result["story"])

divider()
print("Game over.")
