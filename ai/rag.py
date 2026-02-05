import json


class SituationRAG:
    def __init__(self, path="data/situations.json"):
        with open(path, "r") as f:
            self.situations = json.load(f)

    def get(self, situation_id: str):
        return self.situations[situation_id]
