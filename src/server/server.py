from pathlib import Path

import asyncio
import json
import os
import signal
import random
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.loader import load_highscores
from src.game_logic import build_maze, GameLogic


app = FastAPI()
TICK_RATE = 0.3
BASE_DIR = Path(__file__).resolve().parent

clients: set[WebSocket] = set()
game_logic = GameLogic()


# MARK: start_game_loop
@app.on_event("startup")
async def start_game_loop() -> None:
    asyncio.create_task(game_loop())


# MARK: game_loop
async def game_loop() -> None:
    # game_state = GameState(build_maze(seed=42))
    # ! While true is most of the time not a good idea.
    while True:
        await asyncio.sleep(TICK_RATE)
        game_logic.tick()
        await broadcast_state()


# MARK: broadcast_state
async def broadcast_state() -> None:
    payload = json.dumps(game_logic.to_dict())
    dead = []

    async def send_to_client(client: WebSocket) -> None:
        try:
            await asyncio.wait_for(client.send_text(payload), timeout=1.0)
        except Exception:
            dead.append(client)

    await asyncio.gather(*(send_to_client(client) for client in list(clients)))
    for client in dead:
        clients.discard(client)


# MARK: websocket_endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Its the Websocket entrypoint for the frontend.

    Args:
        websocket (WebSocket): The Websocket connection to the frontend.
    """
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_json()

            match data.get("action"):
                case "move":
                    game_logic.move_player(data.get("direction", ""))
                    if game_logic.g_state.level_completed:
                        # Make function for that.
                        new_grid = await asyncio.to_thread(
                            build_maze, seed=random.randint(0, 999999))
                        game_logic.next_level(new_grid)
                    await broadcast_state()

                case "submit_name":
                    game_logic.record_highscore(
                        data.get("name", ""), "highscores.json")
                    await broadcast_state()

                case "restart":
                    # Make function for that.
                    new_grid = await asyncio.to_thread(build_maze, seed=42)
                    game_logic.reset(new_grid)
                    await broadcast_state()

                case "pause_toggle":
                    game_logic.toggle_pause()
                    await broadcast_state()

                case "leave_to_menu":
                    game_logic.leave_to_menu()
                    await broadcast_state()

    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        clients.discard(websocket)


# MARK: index
@app.get("/")
def index() -> FileResponse:
    return FileResponse("src/frontend/index.html")


# MARK: get_maze
@app.get("/maze")
def get_maze() -> list[list[int]]:
    return game_logic.g_state.grid


# MARK: get_highscores
@app.get("/highscores")
def get_highscores() -> list[dict[str, Any]]:
    scores = load_highscores("highscores.json")
    scores.sort(key=lambda entry: entry.get("score", 0), reverse=True)
    return scores


# MARK: shutdown
@app.post("/shutdown")
async def shutdown() -> dict[str, str]:
    """
    Beendet den Server. Dies ist nützlich für Tests,
    um den Server nach dem Testen zu stoppen.
    """
    # MARK: _kill
    async def _kill() -> None:
        await asyncio.sleep(0.2)
        os.killpg(os.getpgid(0), signal.SIGTERM)

    asyncio.create_task(_kill())
    return {"status": "Server is shutting down..."}


app.mount("/static", StaticFiles(directory="src/frontend"), name="static")
