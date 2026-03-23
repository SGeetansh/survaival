import socket
import threading
import json

HOST = "127.0.0.1"
PORT = 5555


def receive_messages(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024).decode()
            if not data:
                break

            buffer += data

            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                message = json.loads(msg)

                # Only print non-system join confirmations here
                if message["type"] != "system":
                    print(message)

        except:
            break


def join_server(client):
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
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    # Step 1: Join properly
    join_server(client)

    # Step 2: Start async receiver
    threading.Thread(
        target=receive_messages, args=(client,), daemon=True
    ).start()

    # Step 3: Chat loop
    while True:
        msg = input()

        if not msg.strip():
            continue

        client.send(
            (json.dumps({"type": "chat", "message": msg}) + "\n").encode()
        )


if __name__ == "__main__":
    start_client()
