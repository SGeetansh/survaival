class Player:
    def __init__(self, conn, name: str):
        self.conn = conn
        self.name = name
        self.ready = False
        self.lives = 3
        self.response = None
        self.buffer = ""

    def __repr__(self):
        return f"Player(name={self.name}, ready={self.ready})"
