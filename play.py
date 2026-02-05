import time
from ai.agent import Agent
from ai.memory import MemoryStore
from ai.llm import LocalLLM
from ai.rag import SituationRAG


# ----------------------------
# Setup
# ----------------------------
rag = SituationRAG("data/situations.json")

llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")
memory = MemoryStore()
rag = SituationRAG("data/situations.json")
agent = Agent(llm, memory, rag)


# ----------------------------
# Helpers
# ----------------------------


def divider():
    print("\n" + "=" * 50 + "\n")


# ----------------------------
# Game Start
# ----------------------------

divider()
print("🧠 DEATH BY AI — SOLO MODE")
divider()

# Pick a situation (later: random)
situation_id = "subway_fire"
situation = rag.get(situation_id)

print("SITUATION:")
print(situation["description"])

divider()
print("⏳ You have 60 seconds to respond.")
print("(Type your plan and press Enter)")
divider()

# ----------------------------
# Player Input
# ----------------------------

player_name = input("Enter your name: ").strip() or "Player"

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

result = agent.judge(
    situation_id="subway_fire",
    player=player_name,
    response=response,
)


print(f"Player: {result['player']}")
print(f"VERDICT: {result['verdict']}")
print("OUTCOME:")
print(result["story"])

divider()
print("Game over.")
