import time
from ai.agent import Agent
from ai.memory import MemoryStore
from ai.llm import LocalLLM
from ai.rag import SituationRAG


# ----------------------------
# Setup AI Judge
# ----------------------------

llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")
memory = MemoryStore()
rag = SituationRAG("data/situations.json")
agent = Agent(llm, memory, rag)


# ----------------------------
# Game Data
# ----------------------------

player_responses = {

    "Alice": (
        "I immediately crouch to stay below the smoke layer and cover my nose "
        "and mouth with my jacket. I use the wall to guide my movement and "
        "search for emergency equipment or a service exit while avoiding panic."
    ),

    "Bob": (
        "I move away from the center of the carriage, stay low, and keep one hand "
        "on the wall to avoid getting lost. I look for any marked maintenance door "
        "or emergency access while limiting my breathing."
    ),

    "Charlie": (
        "I cover my face with cloth, get as low as possible, and carefully feel "
        "along the side of the train to maintain orientation. I look for emergency "
        "tools or a maintenance exit rather than waiting passively."
    ),

    "Diana": (
        "I stay low to reduce smoke inhalation, use my phone light only when needed, "
        "and follow the wall to avoid disorientation. I actively check doors and "
        "equipment instead of remaining seated."
    ),

    "Evan": (
        "I keep my breathing shallow, cover my mouth, and crawl along the carriage "
        "wall to maintain direction. I search for emergency exits or safety equipment "
        "while staying calm and deliberate."
    ),

    "Frank": (
        "I immediately get down low under the smoke, cover my face with my clothing, "
        "and follow the wall to avoid losing my bearings. I focus on finding a "
        "maintenance exit or emergency gear rather than waiting."
    ),

    "Grace": (
        "I lower myself to the floor to avoid smoke, cover my mouth, and move slowly "
        "along the wall to find any emergency exit or equipment. I avoid standing or "
        "waiting in one place."
    ),
}

# ✅ Automatically derive players
players = list(player_responses.keys())


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
print(rag.get("subway_fire")["description"])

divider()
print("⏳ Players have 60 seconds to respond...")
time.sleep(2)
print("🔒 Responses locked.")
divider()

print("🤖 AI JUDGEMENT PHASE")
divider()

results = {}

for player in players:
    print(f"👤 Player: {player}\n")
    print("📄 Response:")
    print(f"\"{player_responses[player]}\"\n")

    result = agent.judge(
        situation_id="subway_fire",
        player=player,
        response=player_responses[player]
    )

    print("⚖️ AI JUDGEMENT:")
    print(f"Player: {result['player']}")
    print(f"VERDICT: {result['verdict']}")
    print("OUTCOME:")
    print(result["story"])

    results[player] = result["verdict"]

    divider()
    time.sleep(2)


# ----------------------------
# Summary
# ----------------------------

print("🏁 ROUND SUMMARY")
divider()

for player, verdict in results.items():
    status = "SURVIVED" if verdict == "SURVIVE" else "DIED"
    emoji = "🟢" if status == "SURVIVED" else "🔴"
    print(f"{emoji} {player} → {status}")

divider()
print("End of round.")
