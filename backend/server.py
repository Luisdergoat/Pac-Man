from pathlib import Path

import asyncio
import json
import os
import signal

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from game_logic import GameState
from mazegen.maze_parser import parse_maze_config
from mazegen.mazegen_algo import generat_maze


TICK_RATE = 0.3

app = FastAPI()
config_path = Path(__file__).with_name("config.txt")
parsed = parse_maze_config(str(config_path))

if parsed is None:
    raise RuntimeError(f"Failed to load maze config from {config_path}")

maze, config = parsed
generat_maze(maze, config)


BASE_DIR = Path(__file__).resolve().parent


def cells_to_grid(maze, config):
    """
    Wandelt das Corridor-Maze (2D Liste von Cell-Objekten mit einer
    N/E/S/W Wand-Bitmaske) in ein einfaches Block-Grid um, wie es das
    Frontend erwartet: eine 2D-Liste aus 0 (begehbar) und 1 (Wand) in
    doppelter Aufloesung (jede Zelle wird zu einem 2x2 Block, damit die
    Waende zwischen den Zellen als eigene Grid-Felder dargestellt werden
    koennen).
    """
    width = config["WIDTH"]
    height = config["HEIGHT"]

    NORTH, EAST, SOUTH, WEST = 8, 4, 2, 1

    rows = height * 2 + 1
    cols = width * 2 + 1
    grid = [[1] * cols for _ in range(rows)]

    for y in range(1, height + 1):
        for x in range(1, width + 1):
            cell = maze[y][x]
            wall = cell.get_wall()
            gr = 2 * (y - 1) + 1
            gc = 2 * (x - 1) + 1
            grid[gr][gc] = 0
            if not wall & NORTH:
                grid[gr - 1][gc] = 0
            if not wall & EAST:
                grid[gr][gc + 1] = 0
            if not wall & SOUTH:
                grid[gr + 1][gc] = 0
            if not wall & WEST:
                grid[gr][gc - 1] = 0

    return grid


def regenerate_maze() -> list:
    """
    Generiert ein neues Maze und gibt das Block-Grid zurück.
    """
    global maze, config
    paresed_new = parse_maze_config(str(config_path))
    if paresed_new is None:
        return cells_to_grid(maze, config)  # Return the old maze if failed
    maze, config = paresed_new
    generat_maze(maze, config)
    return cells_to_grid(maze, config)


game_state = GameState(cells_to_grid(maze, config))
clients: set[WebSocket] = set()


async def broadcast_state() -> None:
    payload = json.dumps(game_state.to_dict())
    dead = []
    for client in clients:
        try:
            await client.send_text(payload)
        except Exception:
            dead.append(client)
    for client in dead:
        clients.remove(client)


async def game_loop() -> None:
    while True:
        await asyncio.sleep(TICK_RATE)
        game_state.tick()
        await broadcast_state()


@app.on_event("startup")
async def start_game_loop() -> None:
    asyncio.create_task(game_loop())


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    clients.add(websocket)
    await websocket.send_json(game_state.to_dict())
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "move":
                game_state.move_player(data.get("direction", ""))
                await broadcast_state()
            elif data.get("action") == "submit_name":
                game_state.recorde_highscore(
                    data.get("name", ""), "highscores.json")
                await broadcast_state()
            elif data.get("action") == "restart":
                game_state.reset(regenerate_maze())
                await broadcast_state()
    except WebSocketDisconnect:
        clients.discard(websocket)


@app.get("/")
def index():
    return FileResponse(BASE_DIR / ".." / "frontend" / "src" / "index.html")


@app.get("/maze")
def get_maze():
    return cells_to_grid(maze, config)


@app.post("/shutdown")
async def shutdown():
    """
    Beendet den Server. Dies ist nützlich für Tests,
    um den Server nach dem Testen zu stoppen.
    """
    async def _kill():
        await asyncio.sleep(0.2)
        os.kill(os.getpgrid(0), signal.SIGTERM)

    asyncio.create_task(_kill())
    return {"status": "Server is shutting down..."}


app.mount("/static", StaticFiles(directory="../frontend/src"), name="static")
