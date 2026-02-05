from ai.agent import Agent
from ai.memory import MemoryStore
from ai.llm import LocalLLM

# Load local model
llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")

# Memory for consistency across rounds
memory = MemoryStore()

# Create judge agent
agent = Agent(llm, memory)

# Scenario
scenario = """
You are trapped in a burning building.
Smoke is filling the room and the exit is blocked.
"""

# Player responses
player_responses = {
    "Alice": "I cover my face with a cloth and crawl low to find an exit.",
    "Bob": "I wait calmly and hope the fire dies down on its own."
}

# Judge
verdicts = agent.judge(scenario, player_responses)

print(verdicts)
