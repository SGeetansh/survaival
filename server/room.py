class Room:
    def __init__(self):
        self.players: list = []
        self.state = "WAITING"
        self.situation_id = None

    def add_player(self, player):
        self.players.append(player)

    def remove_player(self, conn):
        self.players = [p for p in self.players if p.conn != conn]

    def all_ready(self):
        return len(self.players) > 0 and all(p.ready for p in self.players)
