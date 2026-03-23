import json
from typing import TypedDict


class ChatMessage(TypedDict):
    type: str
    name: str
    message: str


def send(conn, data):
    msg = json.dumps(data) + "\n"
    conn.sendall(msg.encode())


def recv(conn, buffer):
    try:
        data = conn.recv(1024).decode()
        if not data:
            return [], buffer
        buffer += data
    except:
        return [], buffer

    messages = []
    while "\n" in buffer:
        msg, buffer = buffer.split("\n", 1)
        messages.append(json.loads(msg))

    return messages, buffer
