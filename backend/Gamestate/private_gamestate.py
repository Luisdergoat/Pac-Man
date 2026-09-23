import random
import time
from collections import deque
from .ghost import Ghost
from typing import Tuple, List, TYPE_CHECKING
from .ghost_movement import bfs_next_step, find_nearest_open_cell
if TYPE_CHECKING:
    from .gamestate import GameState


# MARK: collect_gums
def collect_gums(gamestate, POINTS_PER_GUM: int, POINTS_PER_SUPER_GUM: int, EDIBLE_DURATION: int) -> None:
    """
    Zum einsammeln der gums.
    """
    pos = (gamestate.player_row, gamestate.player_col)
    if pos in gamestate.gums:
        gamestate.gums.discard(pos)
        gamestate.score += POINTS_PER_GUM
    elif pos in gamestate.super_gums:
        gamestate.super_gums.discard(pos)
        gamestate.score += POINTS_PER_SUPER_GUM
        gamestate.edible_until = time.monotonic() + EDIBLE_DURATION

    if not gamestate.gums and not gamestate.super_gums:
        gamestate.level_completed = True


# MARK: random_valid_step
def random_valid_step(
    gamestate, ghost: Ghost, blocked: set[Tuple[int, int]] = None
) -> Tuple[int, int]:
    """
    Gibt einen zufälligen gültigen Schritt für den Geist zurück.
    """
    blocked = blocked or set()
    rows, cols = len(gamestate.grid), len(gamestate.grid[0])
    valid_steps = []
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = ghost.row + dr, ghost.col + dc
        if (0 <= nr < rows and 0 <= nc < cols
                and gamestate.grid[nr][nc] == 0
                and (nr, nc) not in blocked):
            valid_steps.append((nr, nc))
    return random.choice(valid_steps) if valid_steps else (
        ghost.row, ghost.col)


# MARK: flee_step
def flee_step(
    gamestate, ghost: Ghost, blocked: set[Tuple[int, int]] = None
) -> Tuple[int, int]:
    """
    Gibt einen Schritt zurück, der den Geist vom Spieler wegführt.
    """
    blocked = blocked or set()
    best, best_dist = None, -1
    rows, cols = len(gamestate.grid), len(gamestate.grid[0])
    for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nr, nc = ghost.row + dr, ghost.col + dc
        if (0 <= nr < rows and 0 <= nc < cols
                and gamestate.grid[nr][nc] == 0
                and (nr, nc) not in blocked):
            dist = abs(nr - gamestate.player_row) + abs(nc - gamestate.player_col)
            if dist > best_dist:
                best_dist, best = dist, (nr, nc)
    return best or (ghost.row, ghost.col)


# MARK: move_ghost_towards_player
def move_ghost_towards_player(
    gamestate,
    ghost: Ghost,
    GHOST_CHASE_CHANCE: float,
    blocked: set[tuple[int, int]] = None
) -> None:
    if gamestate.is_edible():
        ghost.row, ghost.col = flee_step(gamestate, ghost, blocked)
        return
    if random.random() < GHOST_CHASE_CHANCE:
        next_step = bfs_next_step(
            gamestate.grid, (ghost.row, ghost.col),
            (gamestate.player_row, gamestate.player_col), blocked)
        if next_step:
            ghost.row, ghost.col = next_step
            return
    ghost.row, ghost.col = random_valid_step(gamestate, ghost, blocked)


# MARK: respawn_after_hit
def respawn_after_hit(gamestate) -> str:
    """
    Respawnt den Spieler an der Startposition und reduziert die Leben.
    """
    gamestate.lives -= 1
    if gamestate.lives > 0:
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        gamestate.player_row, gamestate.player_col = find_nearest_open_cell(
            gamestate.grid, rows // 2, cols // 2)
        for ghost in gamestate.ghosts:
            ghost.row, ghost.col = find_nearest_open_cell(
                gamestate.grid, ghost.start_row, ghost.start_col)
    else:
        return "Game Over"


# MARK: check_collision
def check_collision(gamestate, POINTS_PER_GHOST: int) -> None:
    """
    Checkt, ob der Spieler ein Geist berührt.
    """
    for ghost in gamestate.ghosts:
        if ghost.row == gamestate.player_row and ghost.col == gamestate.player_col:
            if gamestate.is_edible():
                gamestate.score += POINTS_PER_GHOST
                ghost.row, ghost.col = find_nearest_open_cell(
                    gamestate.grid, ghost.start_row, ghost.start_col)
            else:
                result = respawn_after_hit(gamestate)
                if result == "Game Over":
                    gamestate.game_over = True


# MARK: reachable_cells
def reachable_cells(gamestate, start: Tuple[int, int]) -> set[Tuple[int, int]]:
    """
    Gibt die Menge der erreichbaren Zellen,
    von der Startposition aus zurück.
    """
    rows, cols = len(gamestate.grid), len(gamestate.grid[0])
    visited = set()
    queue = deque([start])
    while queue:
        row, col = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = row + dr, col + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and gamestate.grid[nr][nc] == 0
                    and (nr, nc) not in visited):
                visited.add((nr, nc))
                queue.append((nr, nc))
    return visited


# MARK: place_gums
def place_gums(gamestate) -> None:
    """
    Platziert die Gums und Super-Gums im Grid.
    """
    rows, cols = len(gamestate.grid), len(gamestate.grid[0])
    reachable = reachable_cells(gamestate, (gamestate.player_row, gamestate.player_col))
    ocupied = {(gamestate.player_row, gamestate.player_col)} | {
        (ghost.row, ghost.col) for ghost in gamestate.ghosts}
    corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    gamestate.super_gums = {
        find_nearest_open_cell(gamestate.grid, row, col) for row, col in corners
        } & reachable
    gamestate.gums = {
        (r, c)
        for r in range(rows)
        for c in range(cols)
        if (gamestate.grid[r][c] == 0
            and (r, c) not in ocupied
            and (r, c) not in gamestate.super_gums
            and (r, c) in reachable)
    }


# MARK: setup
def setup(gamestate, GHOST_COLORS: List[str]) -> None:
    """
    Setzt den Spielzustand zurück, falls das Spiel neu gestartet wird.
    """
    rows, cols = len(gamestate.grid), len(gamestate.grid[0])
    gamestate.player_row, gamestate.player_col = find_nearest_open_cell(
        gamestate.grid, rows // 2, cols // 2)
    corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
    gamestate.ghosts = [
        Ghost(*find_nearest_open_cell(gamestate.grid, row, col), color)
        for (row, col), color in zip(corners, GHOST_COLORS)
    ]
    for ghost in gamestate.ghosts:
        ghost.start_row, ghost.start_col = ghost.row, ghost.col
    place_gums(gamestate)
