from __future__ import annotations

import time

from config_loader import add_highscore
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional
from .private_gamestate import collect_gums, setup, move_ghost_towards_player, check_collision


Grid = List[List[int]]
GHOST_CHASE_CHANCE = 0.7  # Wahrscheinlichkeit, dass der Geist den Spieler jagt
POINTS_PER_GUM = 10
POINTS_PER_SUPER_GUM = 50
POINTS_PER_GHOST = 200
EDIBLE_DURATION = 8  # Dauer, für die Geister essbar sind (in Sekunden)

DIRECTIONS: Dict[str, Tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}

GHOST_COLORS = ["red", "pink", "cyan", "orange"]


# MARK: Gamestate
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
    paused: bool = False
    level: int = 1
    level_completed: bool = False
    edible_until: float = 0.0  # Zeit, bis die Geister nicht mehr essbar sind
    round_id: int = 0  # ID der aktuellen Runde, um alte Ticks zu ignorieren

    # MARK: __post_init__
    def __post_init__(self) -> None:
        """
        Setzt die Startposition des Spielers und der Geiste.
        """
        setup(self, GHOST_COLORS)

    # MARK: is_wall

    def is_wall(self, row: int, col: int) -> bool:
        """
        Checkt, ob die angegebene Position eine Wand ist.
        """
        rows, cols = len(self.grid), len(self.grid[0])
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return True
        return self.grid[row][col] == 1

    # MARK: move_player

    def move_player(self, direction: str) -> None:
        """
        Bewegt den Spieler in die angegebene Richtung, falls möglich.
        """
        if self.paused:
            return
        self.started = True
        if direction not in DIRECTIONS:
            return
        dr, dc = DIRECTIONS[direction]
        nr, nc = self.player_row + dr, self.player_col + dc
        if not self.is_wall(nr, nc):
            self.player_row, self.player_col = nr, nc
            collect_gums(self, POINTS_PER_GUM, POINTS_PER_SUPER_GUM, EDIBLE_DURATION)
        check_collision(self, POINTS_PER_GHOST)

    # MARK: is_edible
    def is_edible(self) -> bool:
        """
        Gibt zurück, ob die Geister essbar sind.
        """
        return time.monotonic() < self.edible_until

    # MARK: tick
    def tick(self) -> None:
        """
        Führt einen Tick des Spiels aus: bewegt die Geister und prüft Kontakte.
        """
        if not self.started:
            return
        if self.paused:
            return
        if self.lives <= 0:
            self.game_over = True
            return
        occupied = {(ghost.row, ghost.col) for ghost in self.ghosts}
        for ghost in self.ghosts:
            occupied.discard((ghost.row, ghost.col))  # Geiter entfernen
            move_ghost_towards_player(self, ghost, GHOST_CHASE_CHANCE, blocked=occupied)
            occupied.add((ghost.row, ghost.col))
        check_collision(self, POINTS_PER_GHOST)

    # MARK: to_dict
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
            "level": self.level,
            "edible": self.is_edible(),
            "gums": list(self.gums),
            "super_gums": list(self.super_gums),
            "game_over": self.game_over,
            "paused": self.paused,
            "round_id": self.round_id,
        }

    # MARK: record_highscore
    def record_highscore(
        self, name: str, filename: str
    ) -> list[Dict[str, Any]]:
        """
        Fügt den aktuellen Score zur Highscore-Liste hinzu.
        """
        return add_highscore(filename, name, self.score, self.level)

    # MARK: reset
    def reset(self, grid: Optional[Grid] = None) -> None:
        """
        Setzt den Spielzustand zurück, um ein neues Spiel zu starten.
        """
        self.round_id += 1
        if grid is not None:
            self.grid = grid
        self.lives = 3
        self.score = 0
        self.level = 1
        self.level_completed = False
        self.edible_until = 0.0
        self.started = False
        self.game_over = False
        setup(self, GHOST_COLORS)

    # MARK: next_level
    def next_level(self, grid: Grid) -> None:
        """
        Setzt den Spielzustand zurück, um das nächste Level zu starten.
        """
        self.level += 1
        self.level_completed = False
        self.grid = grid
        self.edible_until = 0.0
        setup(self, GHOST_COLORS)

    # MARK: toggle_pause
    def toggle_pause(self) -> None:
        """
        Pausiert oder setzt das Spiel fort.
        """
        self.paused = not self.paused

    # MARK: leave_to_menu
    def leave_to_menu(self) -> None:
        """
        Setzt das Spiel zurück und kehrt zum Startbildschirm zurück.
        """
        self.paused = False
        self.started = False
