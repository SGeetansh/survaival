from __future__ import annotations
import socket
import threading
from utils import ChatMessage, send, recv


HOST: str = "0.0.0.0"
PORT: int = 5555

clients: list[tuple[socket.socket, str]] = []  # (conn, name)


def handle_client(conn: socket.socket, addr: tuple[str, int]):
    print(f"[NEW CONNECTION] {addr}")

    buffer = ""
    name: str | None = None

    try:
        while True:
            msgs, buffer = recv(conn, buffer)

            for msg in msgs:
                if msg["type"] == "join":

                    if name is not None:
                        send(
                            conn,
                            {"type": "error", "message": "Already joined"},
                        )
                        continue

                    raw_name = msg.get("name")

                    if not raw_name or not raw_name.strip():
                        send(
                            conn,
                            {"type": "error", "message": "Name is required"},
                        )
                        continue

                    name = raw_name.strip()

                    if any(n == name for _, n in clients):
                        send(
                            conn,
                            {"type": "error", "message": "Name already taken"},
                        )
                        name = None
                        continue

                    clients.append((conn, name))
                    print(f"{name} joined")

                    send(
                        conn, {"type": "system", "message": f"Welcome {name}"}
                    )

                elif msg["type"] == "chat":

                    if name is None:
                        send(
                            conn,
                            {
                                "type": "error",
                                "message": "You must join first",
                            },
                        )
                        continue

                    broadcast(
                        {
                            "type": "chat",
                            "name": name,
                            "message": msg["message"],
                        }
                    )

    finally:
        if name:
            print(f"{name} disconnected")

        clients[:] = [(c, n) for c, n in clients if c != conn]
        conn.close()


def broadcast(data: ChatMessage) -> None:
    for conn, _ in clients:
        send(conn, data)


def start_server() -> None:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(f"[SERVER STARTED] {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()


if __name__ == "__main__":
    start_server()
