from __future__ import annotations
import socket
import threading
from server.utils import ChatMessage, send, recv
from common.logger import setup_logging, get_logger
from server.player import Player
from server.room import Room
import time

import random
from ai.rag import SituationRAG
from ai.agent import Agent
from ai.llm import LocalLLM
from ai.memory import MemoryStore
from game.engine import GameEngine

setup_logging()

logger = get_logger(__name__)

rag = SituationRAG("data/situations.json")
llm = LocalLLM("models/qwen2.5-7b-instruct-q4_k_m.gguf")
memory = MemoryStore()
agent = Agent(llm, memory, rag)
engine = GameEngine(agent, rag)

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

                    if player is None:
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
                        threading.Thread(
                            target=start_game, daemon=True
                        ).start()

                elif msg["type"] == "response":

                    if player is None:
                        send(conn, {"type": "error", "message": "Join first"})
                        continue

                    player.response = msg.get("text")

                    logger.info(f"[RESPONSE RECEIVED] {player.name}")
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

    room.state = "IN_GAME"

    logger.info("[GAME START]")

    # pick situation
    situation_ids = list(rag.situations.keys())
    situation_id = random.choice(situation_ids)
    situation = rag.get(situation_id)

    room.situation_id = situation_id

    # send situation
    broadcast({"type": "situation", "data": situation["description"]})

    # collect responses
    responses = collect_responses(timeout=60)

    # run AI
    result_bundle = engine.run_round(situation_id, responses)

    results = result_bundle["results"]

    reveal_results(results)

    logger.info(f"[DEBUG RESULTS TYPE] {type(results)}")
    logger.info(f"[DEBUG RESULTS VALUE] {results}")

    # reveal results
    reveal_results(results)


def reveal_results(results):
    logger.info("[REVEAL RESULTS]")

    for r in results:

        # show response first
        broadcast(
            {
                "type": "reveal_response",
                "player": r["player"],
                "response": r.get("response", ""),
            }
        )

        time.sleep(2)

        # then AI result
        broadcast(
            {
                "type": "ai_result",
                "player": r["player"],
                "verdict": r["verdict"],
                "story": r["story"],
            }
        )

        time.sleep(2)


def collect_responses(timeout=60):
    logger.info("[COLLECTING RESPONSES]")

    start = time.time()

    for p in room.players:
        p.response = None

    while time.time() - start < timeout:

        responses = {
            p.name: p.response for p in room.players if p.response is not None
        }

        logger.info(f"[RESPONSES SO FAR] {len(responses)}/{len(room.players)}")

        if len(responses) == len(room.players):
            logger.info("[ALL RESPONSES RECEIVED]")
            return responses

        time.sleep(0.2)  # 🔥 IMPORTANT (gives time for thread sync)

    logger.warning("[TIMEOUT] Not all players responded")

    return {p.name: p.response for p in room.players if p.response is not None}


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
