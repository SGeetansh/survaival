from ai.prompt import build_prompt

class Agent:
    def __init__(self, llm, memory):
        self.llm = llm
        self.memory = memory

    def observe(self, judgment: str):
        # Store past judgments for consistency (RAG)
        self.memory.add(judgment)

    def judge(self, scenario: str, player_responses: dict):
        prompt = build_prompt(
            memory=self.memory.retrieve(),
            scenario=scenario,
            player_responses=player_responses
        )
        return self.llm.generate(prompt)
