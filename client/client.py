import socket
import threading
import json
from common.logger import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

HOST = "127.0.0.1"
PORT = 5555

# This flag tells main thread:
# "next input should be treated as game response"
waiting_for_response = False


def receive_messages(sock: socket.socket) -> None:
    """
    Runs in a separate thread.
    Responsible ONLY for:
    - receiving messages
    - printing messages
    - updating flags (no input here!)
    """
    global waiting_for_response

    buffer = ""
    logger.info("[RECEIVER] Started listening")

    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                logger.warning("[RECEIVER] Server closed connection")
                break

            buffer += data

            # process complete messages
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                message = json.loads(msg)

                logger.info(f"[RECEIVED] {message}")

                msg_type = message.get("type")

                # ---------------- CHAT ----------------
                if msg_type == "chat":
                    print(f"{message['name']}: {message['message']}")

                # ---------------- SYSTEM ----------------
                elif msg_type == "system":
                    print(f"[SYSTEM] {message['message']}")

                # ---------------- SITUATION ----------------
                elif msg_type == "situation":
                    data = message.get("data")

                    if not data:
                        logger.error(f"[INVALID SITUATION MESSAGE] {message}")
                        continue

                    print("\n========== GAME START ==========")
                    print("SITUATION:")
                    print(message["data"])
                    print("\nYou have 60 seconds. Type your response:")

                    # Signal main thread to send response instead of chat
                    waiting_for_response = True

                # ---------------- AI RESULT ----------------
                elif msg_type == "ai_result":
                    print(f"\n{message['player']} → {message['verdict']}")
                    print(message["story"])

                # ---------------- FALLBACK ----------------
                else:
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
            if not data:
                logger.error("[JOIN] No response from server")
                continue

            buffer += data

            if "\n" not in buffer:
                continue

            msg, buffer = buffer.split("\n", 1)
            response = json.loads(msg)
            logger.info(f"[JOIN RESPONSE] {response}")

            if response["type"] == "system":
                print(response["message"])
                logger.info(f"[JOIN SUCCESS] {name}")
                return  # success → exit join loop

            elif response["type"] == "error":
                print("Error:", response["message"])
                logger.warning(f"[JOIN FAILED] {name}")
                break  # retry name input


def start_client():
    global waiting_for_response

    logger.info(f"[Client Start] Starting client...")

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # connection to server
    try:
        client.connect((HOST, PORT))
        logger.info(f"[CONNECTED] to {HOST}:{PORT}")
    except Exception as e:
        logger.error(f"[CONNECTION FAILED] {e}")
        return

    # Step 1: Join properly
    join_server(client)

    # Step 2: Start receiver
    threading.Thread(
        target=receive_messages, args=(client,), daemon=True
    ).start()

    # Step 3: Chat loop
    logger.info("[CHAT LOOP] Ready to send messages")

    while True:
        try:
            msg = input()

            if not msg.strip():
                logger.warning("[INPUT] Empty message ignored")
                continue

            logger.info(f"[SENT] {msg}")

            # ---------------- READY COMMAND ----------------
            if msg.lower() == "ready":
                logger.info("[READY SENT]")

                client.send((json.dumps({"type": "ready"}) + "\n").encode())
                continue

            # ---------------- RESPONSE MODE ----------------
            if waiting_for_response:
                logger.info(f"[RESPONSE SENT] {msg}")

                client.send(
                    (
                        json.dumps({"type": "response", "text": msg}) + "\n"
                    ).encode()
                )

                waiting_for_response = False

            # ---------------- CHAT MODE ----------------
            else:
                logger.info(f"[CHAT SENT] {msg}")

                client.send(
                    (
                        json.dumps({"type": "chat", "message": msg}) + "\n"
                    ).encode()
                )

        except Exception as e:
            logger.error(f"[MAIN LOOP ERROR] {e}")
            break


if __name__ == "__main__":
    start_client()
