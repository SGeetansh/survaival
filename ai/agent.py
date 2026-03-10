from __future__ import annotations
from typing import TYPE_CHECKING

from ai.prompt import build_story_prompt, build_verdict_prompt
import re
from enum import Enum

if TYPE_CHECKING:
    from ai.llm import LocalLLM
    from ai.memory import MemoryStore
    from ai.rag import SituationRAG


class Verdict(Enum):
    SURVIVE = "SURVIVE"
    DIE = "DIE"


class Agent:
    def __init__(
        self,
        llm: LocalLLM,
        memory: MemoryStore,
        rag: SituationRAG,
    ):
        self.llm = llm
        self.memory = memory
        self.rag = rag

    def judge(
        self,
        situation_id: str,
        player: str,
        response: str,
    ) -> dict:
        situation = self.rag.get(situation_id)

        # Phase 1: Verdict
        verdict_prompt = build_verdict_prompt(situation, {player: response})
        verdict_text = self.llm.generate(
            verdict_prompt,
            max_tokens=20,
            temperature=0.0,
        )
        verdict_text_tokens = re.findall(r"[a-z]+", verdict_text.lower())

        verdict = (
            Verdict.SURVIVE
            if "survive" in verdict_text_tokens
            else Verdict.DIE
        )

        # Phase 2: Story
        story_prompt = build_story_prompt(
            situation=situation,
            player_name=player,
            verdict=verdict,
            player_response=response,
        )
        story = self.llm.generate(story_prompt)

        # CONSISTENCY ENFORCEMENT
        if verdict == Verdict.DIE and any(
            word in story.lower()
            for word in [
                "escape",
                "survive",
                "safe",
                "rescues",
            ]
        ):
            # Regenerate with extreme constraint
            story_prompt += "\nREMINDER: The player dies. Describe death only."
            story = self.llm.generate(story_prompt)

        if verdict == Verdict.SURVIVE and any(
            word in story.lower() for word in ["dies", "death", "suffocates"]
        ):
            story_prompt += (
                "\nREMINDER: The player survives. Describe survival only."
            )
            story = self.llm.generate(story_prompt)

        return {
            "player": player,
            "verdict": verdict.value,
            "story": story.strip(),
        }
