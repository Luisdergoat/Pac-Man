from __future__ import annotations

from config_loader import add_highscore
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional


Grid = List[List[int]]

POINTS_PER_GUM = 10
POINTS_PER_SUPER_GUM = 50
POINTS_PER_GHOST = 200

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

GHOST_COLORS = ["red", "pink", "cyan", "orange"]


def find_nearest_open_cell(grid: Grid, row: int, col: int) -> Tuple[int, int]:
    """
    Findet die naechste begehbare Zelle (0) im Grid,
    beginnend von der Startposition.
    Verwendet eine Breitensuche (BFS), um die naechste offene Zelle zu finden.
    """
    rows, cols = len(grid), len(grid[0])
    visited = {(row, col)}
    queue = deque([(row, col)])
    while queue:
        row, col = queue.popleft()
        if 0 <= row < rows and 0 <= col < cols and grid[row][col] == 0:
            return row, col
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            new_row, new_col = row + dr, col + dc
            if (0 <= new_row < rows
                and 0 <= new_col < cols
                    and (new_row, new_col)) not in visited:
                visited.add((new_row, new_col))
                queue.append((new_row, new_col))

    return 1, 1  # Fallback, falls keine offene Zelle gefunden wird


def bfs_next_step(
    grid: Grid, start: Tuple[int, int],
    target: Tuple[int, int],
    blocked: set[Tuple[int, int]] = None
) -> Tuple[int, int]:
    """
    Findet den naechsten Schritt auf dem kuerzesten
    Weg von start zu target im Grid.
    Verwendet eine Breitensuche (BFS), um den kuerzesten Weg zu finden.
    """
    if start == target:
        return start

    blocked = blocked or set()
    rows, cols = len(grid), len(grid[0])
    visited = {start}
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
    queue = deque([start])
    found = False

    while queue:
        current = queue.popleft()
        if current == target:
            found = True
            break
        row, col = current
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            neighbor = (row + dr, col + dc)
            nr, nc = neighbor
            if (
                0 <= nr < rows
                and 0 <= nc < cols
                and grid[nr][nc] == 0
                and neighbor not in visited
                and (neighbor == target or neighbor not in blocked)
            ):
                visited.add(neighbor)
                parent[neighbor] = current
                queue.append(neighbor)
    if not found:
        return None  # Kein Weg gefunden

    step = target
    while parent[step] != start:
        step = parent[step]
    return step


@dataclass
class Ghost:
    row: int
    col: int
    color: str
    start_row: int = 0
    start_col: int = 0


@dataclass
class GameState:
    grid: Grid
    player_row: int = 0
    player_col: int = 0
    ghosts: List[Ghost] = field(default_factory=list)
    lives: int = 3
    score: int = 0
    started: bool = False
    gums: set[Tuple[int, int]] = field(default_factory=set)
    super_gums: set[Tuple[int, int]] = field(default_factory=set)
    game_over: bool = False

    def __post_init__(self) -> None:
        """
        Setzt die Startposition des Spielers und der Geiste.
        """
        self._setup()

    def is_wall(self, row: int, col: int) -> bool:
        """
        Checkt, ob die angegebene Position eine Wand ist.
        """
        rows, cols = len(self.grid), len(self.grid[0])
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return True
        return self.grid[row][col] == 1

    def move_player(self, direction: str) -> None:
        """
        Bewegt den Spieler in die angegebene Richtung, falls möglich.
        """
        self.started = True
        if direction not in DIRECTIONS:
            return
        dr, dc = DIRECTIONS[direction]
        nr, nc = self.player_row + dr, self.player_col + dc
        if not self.is_wall(nr, nc):
            self.player_row, self.player_col = nr, nc
            self._collect_gums()
        self._check_collision()

    def _collect_gums(self) -> None:
        """
        Zum einsammeln der gums.
        """
        pos = (self.player_row, self.player_col)
        if pos in self.gums:
            self.gums.discard(pos)
            self.score += POINTS_PER_GUM
        elif pos in self.super_gums:
            self.super_gums.discard(pos)
            self.score += POINTS_PER_SUPER_GUM
            # Hier kommt noch dieser Ess modus hin

    def _move_ghost_towards_player(
        self,
        ghost: Ghost,
        blocked: set[tuple[int, int]] = None
    ) -> None:
        """
        Bewegt den Geist in Richtung des Spielers, falls möglich.
        """
        next_step = bfs_next_step(
            self.grid,
            (ghost.row, ghost.col),
            (self.player_row, self.player_col),
            blocked
        )
        if next_step:
            ghost.row, ghost.col = next_step

    def _respawn_after_hit(self) -> str:
        """
        Respawnt den Spieler an der Startposition und reduziert die Leben.
        """
        self.lives -= 1
        if self.lives > 0:
            rows, cols = len(self.grid), len(self.grid[0])
            self.player_row, self.player_col = find_nearest_open_cell(
                self.grid, rows // 2, cols // 2)
            for ghost in self.ghosts:
                ghost.row, ghost.col = find_nearest_open_cell(
                    self.grid, ghost.start_row, ghost.start_col)
        else:
            return "Game Over"

    def _check_collision(self) -> None:
        """
        Checkt, ob der Spieler ein Geist berührt.
        """
        for ghost in self.ghosts:
            if ghost.row == self.player_row and ghost.col == self.player_col:
                result = self._respawn_after_hit()
                if result == "Game Over":
                    print(result)  # Game Over printen, logic fehlt noch

    def _place_gums(self) -> None:
        """
        Platziert die Gums und Super-Gums im Grid.
        """
        rows, cols = len(self.grid), len(self.grid[0])
        ocupied = {(self.player_row, self.player_col)} | {
            (ghost.row, ghost.col) for ghost in self.ghosts}
        corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
        self.super_gums = {
            find_nearest_open_cell(self.grid, row, col) for row, col in corners
            }
        self.gums = {
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (self.grid[r][c] == 0
                and (r, c) not in ocupied
                and (r, c) not in self.super_gums)
        }

    def _setup(self) -> None:
        """
        Setzt den Spielzustand zurück, falls das Spiel neu gestartet wird.
        """
        rows, cols = len(self.grid), len(self.grid[0])
        self.player_row, self.player_col = find_nearest_open_cell(
            self.grid, rows // 2, cols // 2)
        corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
        self.ghosts = [
            Ghost(*find_nearest_open_cell(self.grid, row, col), color)
            for (row, col), color in zip(corners, GHOST_COLORS)
        ]
        for ghost in self.ghosts:
            ghost.start_row, ghost.start_col = ghost.row, ghost.col
        self._place_gums()

    def tick(self) -> None:
        """
        Führt einen Tick des Spiels aus: bewegt die Geister und prüft Kontakte.
        """
        if not self.started:
            return
        if self.lives <= 0:
            self.game_over = True
            return
        occupied = {(ghost.row, ghost.col) for ghost in self.ghosts}
        for ghost in self.ghosts:
            occupied.discard((ghost.row, ghost.col))  # Geiter entfernen
            self._move_ghost_towards_player(ghost, blocked=occupied)
            occupied.add((ghost.row, ghost.col))
        self._check_collision()

    def to_dict(self) -> Dict:
        """
        Gibt den aktuellen Spielzustand als Dict zurück,
        für die JS Kommunikation.
        """
        return {
            "grid": self.grid,
            "player": {"row": self.player_row, "col": self.player_col},
            "ghosts": [
                {
                    "row": g.row, "col": g.col, "color": g.color
                    } for g in self.ghosts],
            "lives": self.lives,
            "score": self.score,
            "gums": list(self.gums),
            "super_gums": list(self.super_gums),
            "game_over": self.game_over,
        }

    def recorde_highscore(
        self, name: str, filename: str
    ) -> list[Dict[str, Any]]:
        """
        Fügt den aktuellen Score zur Highscore-Liste hinzu.
        """
        return add_highscore(filename, name, self.score)

    def reset(self, grid: Optional[Grid] = None) -> None:
        """
        Setzt den Spielzustand zurück, um ein neues Spiel zu starten.
        """
        if grid is not None:
            self.grid = grid
        self.lives = 3
        self.score = 0
        self.started = False
        self.game_over = False
        self._setup()
