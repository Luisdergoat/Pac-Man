from dataclasses import dataclass, field
from enum import IntEnum


@dataclass
class Ghost:
    row: int
    col: int
    color: str
    start_row: int = 0
    start_col: int = 0
    on_cooldown: bool = False


class State(IntEnum):
    ALIVE = 0
    DEAD = 1,
    TIMEDOUT = 2


# MARK: Gamestate
@dataclass
class GameState:
    grid: list[list[int]]
    player_row: int = 0
    level_max_time: float = 90.0
    player_col: int = 0
    ghosts: list[Ghost] = field(default_factory=list)
    lives: int = 3
    score: int = 0
    started: bool = False
    gums: set[tuple[int, int]] = field(default_factory=set)
    super_gums: set[tuple[int, int]] = field(default_factory=set)
    state: State = State.ALIVE
    paused: bool = False
    level: int = 1
    level_completed: bool = False
    edible_until: float = 0.0
    round_id: int = 0
    cheats_enabled: bool = False
