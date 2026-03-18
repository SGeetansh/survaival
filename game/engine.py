from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ai.agent import Agent
    from ai.rag import SituationRAG


class GameEngine:
    def __init__(self, agent: Agent, rag: SituationRAG):
        self.agent = agent
        self.rag = rag

    def run_round(self, situation_id: str, player_responses: dict):
        situation = self.rag.get(situation_id)
        results = []

        for player, response in player_responses.items():
            result = self.agent.judge(
                situation_id=situation_id,
                player=player,
                response=response,
            )
            results.append(result)

        return {"situation": situation, "results": results}
