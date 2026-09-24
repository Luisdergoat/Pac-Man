from dataclasses import dataclass, field


@dataclass
class Ghost:
    row: int
    col: int
    color: str
    start_row: int = 0
    start_col: int = 0


# MARK: Gamestate
@dataclass
class GameState:
    grid: list[list[int]]
    player_row: int = 0
    player_col: int = 0
    ghosts: list[Ghost] = field(default_factory=list)
    lives: int = 3
    score: int = 0
    started: bool = False
    gums: set[tuple[int, int]] = field(default_factory=set)
    super_gums: set[tuple[int, int]] = field(default_factory=set)
    game_over: bool = False
    paused: bool = False
    level: int = 1
    level_completed: bool = False
    edible_until: float = 0.0
    round_id: int = 0

    def init_lives(self, lives: int) -> None:
        self.lives = lives
