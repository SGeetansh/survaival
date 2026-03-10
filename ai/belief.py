from __future__ import annotations


class BeliefState:
    def __init__(self):
        self.trust: dict = {}  # player -> score
        self.suspicion: dict = {}  # player -> score

    def update(
        self,
        player,
        delta_trust: float = 0.0,
        delta_suspicion: float = 0.0,
    ):
        self.trust[player] = self.trust.get(player, 0.0) + delta_trust
        self.suspicion[player] = (
            self.suspicion.get(player, 0.0) + delta_suspicion
        )

    def summary(self):
        return {"trust": self.trust, "suspicion": self.suspicion}
