from pathlib import Path

import asyncio
import json
import os
import signal
import random

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from config_loader import load_highscores
from game_logic import GameState
from mazegenerator.mazegenerator import MazeGenerator


TICK_RATE = 0.3

app = FastAPI()
BASE_DIR = Path(__file__).resolve().parent


# MARK: cells_to_grid
def cells_to_grid(maze):
    """
    Wandelt das Corridor-Maze (2D Liste von Cell-Objekten mit einer
    N/E/S/W Wand-Bitmaske) in ein einfaches Block-Grid um, wie es das
    Frontend erwartet: eine 2D-Liste aus 0 (begehbar) und 1 (Wand) in
    doppelter Aufloesung (jede Zelle wird zu einem 2x2 Block, damit die
    Waende zwischen den Zellen als eigene Grid-Felder dargestellt werden
    koennen).
    """
    height = len(maze)
    width = len(maze[0])

    NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

    rows = height * 2 + 1
    cols = width * 2 + 1
    grid = [[1] * cols for _ in range(rows)]

    for y in range(height):
        for x in range(width):
            wall = maze[y][x]
            gr = 2 * y + 1
            gc = 2 * x + 1
            grid[gr][gc] = 0  # Zelle selbst ist begehbar
            if not wall & NORTH:
                grid[gr - 1][gc] = 0  # Nordwand ist offen
            if not wall & EAST:
                grid[gr][gc + 1] = 0  # Ostwand ist offen
            if not wall & SOUTH:
                grid[gr + 1][gc] = 0  # Südwand ist offen
            if not wall & WEST:
                grid[gr][gc - 1] = 0  # Westwand ist offen

    return grid


MAZE_WIDTH = 20
MAZE_HEIGHT = 20


# MARK: build_maze
def build_maze(seed: int = 0) -> list:
    """
    Generiert ein neues Maze mit den gegebenen Dimensionen und dem
    angegebenen Seed. Gibt das Maze als 2D-Liste von Cell-Objekten zurück.
    """
    generator = MazeGenerator(
        size=(MAZE_WIDTH, MAZE_HEIGHT),
        entry_cell=(0, 0),
        exit_cell=(MAZE_WIDTH - 1, MAZE_HEIGHT - 1),
        perfect=False,
        seed=seed,
    )
    return cells_to_grid(generator.maze)


game_state = GameState(build_maze(seed=42))
clients: set[WebSocket] = set()


# MARK: broadcast_state
async def broadcast_state() -> None:
    payload = json.dumps(game_state.to_dict())
    dead = []

    async def send_to_client(client: WebSocket) -> None:
        try:
            await asyncio.wait_for(client.send_text(payload), timeout=1.0)
        except Exception:
            dead.append(client)

    await asyncio.gather(*(send_to_client(client) for client in list(clients)))
    for client in dead:
        clients.discard(client)


# MARK: game_loop
async def game_loop() -> None:
    while True:
        await asyncio.sleep(TICK_RATE)
        game_state.tick()
        await broadcast_state()


# MARK: start_game_loop
@app.on_event("startup")
async def start_game_loop() -> None:
    asyncio.create_task(game_loop())


# MARK: websocket_endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "move":
                game_state.move_player(data.get("direction", ""))
                if game_state.level_completed:
                    new_grid = await asyncio.to_thread(
                        build_maze, seed=random.randint(0, 999999))
                    game_state.next_level(new_grid)
                await broadcast_state()
            elif data.get("action") == "submit_name":
                game_state.record_highscore(
                    data.get("name", ""), "highscores.json")
                await broadcast_state()
            elif data.get("action") == "restart":
                new_grid = await asyncio.to_thread(build_maze, seed=42)
                game_state.reset(new_grid)
                await broadcast_state()
            elif data.get("action") == "pause_toggle":
                game_state.toggle_pause()
                await broadcast_state()
            elif data.get("action") == "leave_to_menu":
                game_state.leave_to_menu()
                await broadcast_state()

    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        clients.discard(websocket)


# MARK: index
@app.get("/")
def index():
    return FileResponse(BASE_DIR / ".." / "frontend" / "src" / "index.html")


# MARK: get_maze
@app.get("/maze")
def get_maze():
    return game_state.grid


# MARK: get_highscores
@app.get("/highscores")
def get_highscores():
    scores = load_highscores("highscores.json")
    scores.sort(key=lambda entry: entry.get("score", 0), reverse=True)
    return scores


# MARK: shutdown
@app.post("/shutdown")
async def shutdown():
    """
    Beendet den Server. Dies ist nützlich für Tests,
    um den Server nach dem Testen zu stoppen.
    """
    # MARK: _kill
    async def _kill():
        await asyncio.sleep(0.2)
        os.killpg(os.getpgid(0), signal.SIGTERM)

    asyncio.create_task(_kill())
    return {"status": "Server is shutting down..."}


app.mount("/static", StaticFiles(directory="../frontend/src"), name="static")
