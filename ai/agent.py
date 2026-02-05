from ai.rag import SituationRAG
from ai.prompt import build_story_prompt, build_verdict_prompt
import re

class Agent:
    def __init__(self, llm, memory, rag):
        self.llm = llm
        self.memory = memory
        self.rag = rag

    def judge(self, situation_id, player, response):
        situation = self.rag.get(situation_id)

        # Phase 1: Verdict
        verdict_prompt = build_verdict_prompt(
            situation,
            {player: response}
        )
        verdict_text = self.llm.generate(
            verdict_prompt,
            max_tokens=20,
            temperature=0.0
        )
        print("++++++++++++++++++++++")
        print(verdict_text)
        print("++++++++++++++++++++++")
        # verdict_text_lower = verdict_text.lower()
        verdict_text_tokens = re.findall(r"[a-z]+", verdict_text.lower())


        verdict = "SURVIVE" if "survive" in verdict_text_tokens else "DIE"

        # Phase 2: Story
        story_prompt = build_story_prompt(
            situation,
            player,
            verdict,
            response
        )
        story = self.llm.generate(story_prompt)

        # 🔒 HARD CONSISTENCY ENFORCEMENT
        if verdict == "DIE" and any(word in story.lower() for word in ["escape", "survive", "safe", "rescues"]):
            # Regenerate with extreme constraint
            story_prompt += "\nREMINDER: The player dies. Describe death only."
            story = self.llm.generate(story_prompt)

        if verdict == "SURVIVE" and any(word in story.lower() for word in ["dies", "death", "suffocates"]):
            story_prompt += "\nREMINDER: The player survives. Describe survival only."
            story = self.llm.generate(story_prompt)

        return {
            "player": player,
            "verdict": verdict,
            "story": story.strip()
        }
