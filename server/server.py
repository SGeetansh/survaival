from __future__ import annotations
import socket
import threading
from utils import ChatMessage, send, recv
from common.logger import setup_logging
from common.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

HOST: str = "0.0.0.0"
PORT: int = 5555

clients: list[tuple[socket.socket, str]] = []  # (conn, name)


def handle_client(conn: socket.socket, addr: tuple[str, int]):
    logger.info(f"[NEW CONNECTION] {addr}")

    buffer = ""
    name: str | None = None

    try:
        while True:
            msgs, buffer = recv(conn, buffer)

            for msg in msgs:
                if msg["type"] == "join":

                    logger.info(f"[JOIN ATTEMPT] {addr} -> {msg}")

                    if name is not None:
                        logger.warning(
                            f"[ALREADY JOINED] {addr} tried to rejoin as {msg.get('name')}"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Already joined"},
                        )
                        continue

                    raw_name = msg.get("name")

                    if not raw_name or not raw_name.strip():
                        logger.warning(
                            f"[INVALID NAME] {addr} sent empty/invalid name"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Name is required"},
                        )
                        continue

                    candidate_name = raw_name.strip()
                    if any(n == candidate_name for _, n in clients):
                        logger.warning(
                            f"[DUPLICATE NAME] {candidate_name} from {addr}"
                        )
                        send(
                            conn,
                            {"type": "error", "message": "Name already taken"},
                        )
                        continue

                    name = candidate_name
                    clients.append((conn, name))
                    logger.info(
                        f"[JOIN SUCCESS] {name} ({addr}) | total_clients={len(clients)}"
                    )
                    send(
                        conn, {"type": "system", "message": f"Welcome {name}"}
                    )

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
                else:
                    logger.warning(f"[UNKNOWN MESSAGE] {addr} -> {msg}")
    except Exception as e:
        logger.error(f"[ERROR] {addr} -> {e}")

    finally:
        if name:
            logger.info(f"[DISCONNECT] {name} ({addr})")
        else:
            logger.info(f"[DISCONNECT] unknown ({addr})")

        clients[:] = [(c, n) for c, n in clients if c != conn]
        conn.close()


def broadcast(data: ChatMessage) -> None:
    logger.info(f"[BROADCAST] to {len(clients)} clients")
    for conn, _ in clients:
        send(conn, data)


def start_server() -> None:
    logger.info("Server is starting...")

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
