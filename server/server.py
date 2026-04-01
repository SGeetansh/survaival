from __future__ import annotations
import socket
import threading
from server.utils import ChatMessage, send, recv
from common.logger import setup_logging, get_logger
from server.player import Player
from server.room import Room

setup_logging()
logger = get_logger(__name__)

HOST: str = "0.0.0.0"
PORT: int = 5555

room = Room()
# clients: list[tuple[socket.socket, str]] = []  # (conn, name)


def handle_client(conn: socket.socket, addr: tuple[str, int]):
    logger.info(f"[NEW CONNECTION] {addr}")

    buffer = ""
    player: Player | None = None

    try:
        while True:
            msgs, buffer = recv(conn, buffer)

            for msg in msgs:
                # ---------------- JOIN ----------------
                if msg["type"] == "join":

                    logger.info(f"[JOIN ATTEMPT] {addr} -> {msg}")

                    if (
                        player is not None
                    ):  # if the same client sends another join request, name var would not be None. Hence, its another join request.
                        logger.warning(
                            f"[ALREADY JOINED] {addr} tried to rejoin as {msg.get('name')}"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Already joined"},
                        )
                        continue

                    raw_name = msg.get("name")

                    if (
                        not raw_name or not raw_name.strip()
                    ):  # name field is empty
                        logger.warning(
                            f"[INVALID NAME] {addr} sent empty/invalid name"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Name is required"},
                        )
                        continue

                    # check for duplicate name
                    candidate_name = raw_name.strip()
                    if any(p.name == candidate_name for p in room.players):
                        logger.warning(
                            f"[DUPLICATE NAME] {candidate_name} from {addr}"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Name already taken"},
                        )
                        continue

                    name = candidate_name
                    # create player
                    player = Player(conn, candidate_name)
                    room.add_player(player)
                    logger.info(
                        f"[JOIN SUCCESS] {name} ({addr}) | total_clients={len(room.players)}"
                    )
                    send(
                        conn, {"type": "system", "message": f"Welcome {name}"}
                    )

                # ---------------- CHAT ----------------
                elif msg["type"] == "chat":

                    if name is None:
                        logger.warning(
                            f"[CHAT BEFORE JOIN] {addr} tried to chat"
                        )
                        send(
                            conn,
                            {
                                "type": "error",
                                "message": "You must join first",
                            },
                        )
                        continue

                    message = msg.get("message", "")

                    logger.info(f"[CHAT] {name}: {message}")

                    broadcast(
                        {
                            "type": "chat",
                            "name": name,
                            "message": msg["message"],
                        }
                    )

                # ---------------- READY ----------------
                elif msg["type"] == "ready":

                    if player is None:
                        send(conn, {"type": "error", "message": "Join first"})
                        continue

                    player.ready = True
                    logger.info(f"[READY] {player.name}")

                    broadcast(
                        {
                            "type": "system",
                            "message": f"{player.name} is ready",
                        }
                    )

                    if room.all_ready():
                        start_game()

                else:
                    logger.warning(f"[UNKNOWN MESSAGE] {addr} -> {msg}")
    except Exception as e:
        logger.error(f"[ERROR] {addr} -> {e}")

    finally:
        if player:
            logger.info(f"[DISCONNECT] {name} ({addr})")
        else:
            logger.info(f"[DISCONNECT] unknown ({addr})")

        room.remove_player(conn)
        conn.close()


def broadcast(data: dict) -> None:
    logger.info(f"[BROADCAST] to {len(room.players)} clients")
    for p in room.players:
        send(p.conn, data)


def start_game():
    logger.info("[GAME START] All players ready")

    broadcast({"type": "system", "message": "Game starting..."})


def start_server() -> None:
    logger.info("[Server Start] Server is starting...")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))

    logger.info(f"[BIND] host={HOST} port={PORT}")

    server.listen()
    logger.info(f"[SERVER READY] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        logger.info(f"[ACCEPT] connection from {addr}")
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
