import socket
import threading
import json
from common.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

HOST = "127.0.0.1"
PORT = 5555


def receive_messages(sock: socket.socket) -> None:
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                logger.warning("[RECEIVER] Server closed connection")
                break

            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                message = json.loads(msg)

                logger.info(f"[RECEIVED] {message}")

                # Only print non-system join confirmations here
                if message["type"] != "system":
                    print(message)

        except Exception as e:
            logger.error(f'"[RECEIVER ERROR] {e}"')
            break


def join_server(client: socket.socket) -> None:
    buffer = ""

    while True:
        name = input("Input your name: ").strip()

        if not name:
            print("Name cannot be empty")
            continue

        # send join request
        client.send(
            (json.dumps({"type": "join", "name": name}) + "\n").encode()
        )

        # wait for server response
        while True:
            data = client.recv(1024).decode()
            buffer += data

            if "\n" not in buffer:
                continue

            msg, buffer = buffer.split("\n", 1)
            response = json.loads(msg)

            if response["type"] == "system":
                print(response["message"])
                return  # success → exit join loop

            elif response["type"] == "error":
                print("Error:", response["message"])
                break  # retry name input


def start_client():
    logger.info(f"[Client Start] Starting client...")
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((HOST, PORT))
        logger.info(f"[CONNECTED] to {HOST}:{PORT}")
    except Exception as e:
        logger.error(f"[CONNECTION FAILED] {e}")
        return

    # Step 1: Join properly
    join_server(client)

    # Step 2: Start async receiver
    threading.Thread(
        target=receive_messages, args=(client,), daemon=True
    ).start()

    # Step 3: Chat loop
    logger.info("[CHAT LOOP] Ready to send messages")

    while True:
        try:
            msg = input()

            if not msg.strip():
                logger.warning("[CHAT] Empty message ignored")
                continue

            logger.info(f"[SENT] {msg}")

            client.send(
                (json.dumps({"type": "chat", "message": msg}) + "\n").encode()
            )

        except Exception as e:
            logger.error(f"[CHAT ERROR] {e}")
            break


if __name__ == "__main__":
    start_client()
