class MemoryStore:
    def __init__(self, max_items=50):
        self.entries = []
        self.max_items = max_items

    def add(self, text: str):
        self.entries.append(text)
        if len(self.entries) > self.max_items:
            self.entries.pop(0)

    def retrieve(self, k=5):
        return self.entries[-k:]

