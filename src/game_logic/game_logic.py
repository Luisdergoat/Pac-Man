from src.loader import add_highscore, load_config
from src.game_logic.objects import Ghost, GameState, State
from src.game_logic.game_logic_helper import LogicHelper as lhelp
from src.game_logic.maze import build_maze
from typing import Optional, Any
from random import randint

Grid = list[list[int]]

GHOST_CHASE_CHANCE = 0.7
EDIBLE_DURATION = 8
GHOST_COLORS = ["red", "pink", "cyan", "orange"]
DIRECTIONS: dict[str, tuple[int, int]] = {
    "up": (-1, 0),
    "down": (1, 0),
    "left": (0, -1),
    "right": (0, 1),
}


# MARK: GameLogic
class GameLogic:
    def __init__(self, config_name: str) -> None:
        self.g_state = GameState(build_maze(randint(0, 1000)))
        self.config = load_config(config_name)

    # MARK: __post_init__
    def __post_init__(self) -> None:
        """
        Sets up the start state of the game
        """
        self._setup(GHOST_COLORS)

    # MARK: setup
    def _setup(self, GHOST_COLORS: list[str]) -> None:
        """
        Setzt den Spielzustand zurück, falls das Spiel neu gestartet wird.
        """
        rows, cols = len(self.g_state.grid), len(self.g_state.grid[0])
        row, col = lhelp.find_nearest_open_cell(
            self.g_state.grid, rows // 2, cols // 2)

        self.g_state.player_row, self.g_state.player_col = row, col
        corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
        self.g_state.ghosts = [
            Ghost(*lhelp.find_nearest_open_cell(
                self.g_state.grid, row, col), color)
            for (row, col), color in zip(corners, GHOST_COLORS)
        ]
        for ghost in self.g_state.ghosts:
            ghost.start_row, ghost.start_col = ghost.row, ghost.col
        lhelp.place_gums(self.g_state)

    # MARK: move_player
    def move_player(self, direction: str) -> None:
        """
        Moves the player in the given direction, if possible
        """
        if self.g_state.paused:
            return
        self.g_state.started = True
        if direction not in DIRECTIONS:
            return
        dr, dc = DIRECTIONS[direction]
        nr = self.g_state.player_row + dr
        nc = self.g_state.player_col + dc
        if not lhelp.is_wall(self.g_state, nr, nc):
            self.g_state.player_row, self.g_state.player_col = nr, nc
            lhelp.collect_gums(
                self.g_state,
                self.config["points_per_pacgum"],
                self.config["points_per_super_pacgum"],
                EDIBLE_DURATION
            )
        lhelp.check_collision(self.g_state, self.config["points_per_ghost"])

    # MARK: tick
    def tick(self) -> None:
        """
        Start a tick of the game and checks for collisions
        """
        if not self.g_state.started:
            return
        if self.g_state.paused:
            return
        if self.g_state.lives <= 0:
            self.g_state.state = State.DEAD
            return
        if self.g_state.level_max_time <= 0:
            self.g_state.state = State.TIMEDOUT
        self.g_state.level_max_time -= 0.5
        occupied = {
            (ghost.row, ghost.col) for ghost in self.g_state.ghosts
            if not ghost.on_cooldown}
        for ghost in self.g_state.ghosts:
            occupied.discard((ghost.row, ghost.col))
            lhelp.move_ghost_towards_player(
                self.g_state,
                ghost,
                GHOST_CHASE_CHANCE,
                blocked=occupied
            )
            occupied.add((ghost.row, ghost.col))
        lhelp.check_collision(self.g_state, self.config["points_per_ghost"])

    # MARK: cheat_mode
    def cheat_mode(self) -> None:
        self.g_state.cheats_enabled = not self.g_state.cheats_enabled
        if self.g_state.cheats_enabled is True:
            self.g_state.edible_until = float('inf')
        else:
            self.g_state.edible_until = 0.0

    # MARK: check_cheat
    def check_cheat(self) -> bool:
        return self.g_state.cheats_enabled

    # MARK: skip_level
    def skip_level(self) -> None:
        if self.g_state.cheats_enabled:
            new_grid = build_maze(randint(0, 999999))
            self.next_level(new_grid)

    # MARK: record_highscore
    def record_highscore(
        self, name: str, filename: str
    ) -> list[dict[str, Any]] | None:
        """
        Puts the current score into the highscore list
        """
        return add_highscore(
            filename, name, self.g_state.score, self.g_state.level)

    # MARK: reset
    def reset(self, grid: Optional[Grid] = None) -> None:
        """
        resets the game state for a new round
        """
        # config = load_config()
        self.g_state.round_id += 1
        if grid is not None:
            self.g_state.grid = grid
        self.g_state.lives = self.config["lives"]
        self.g_state.score = 0
        self.g_state.level = 1
        self.g_state.level_max_time = self.config["level_max_time"]
        self.g_state.level_completed = False
        self.g_state.edible_until = 0.0
        self.g_state.started = False
        self.g_state.state = State.ALIVE
        self.g_state.cheats_enabled = False
        self._setup(GHOST_COLORS)

    # MARK: next_level
    def next_level(self, grid: Grid) -> None:
        """
        sets up the next level with a new grid and resets the level state
        """
        self.g_state.level += 1
        self.g_state.level_completed = False
        self.g_state.grid = grid
        if self.g_state.edible_until != float("inf"):
            self.g_state.edible_until = 0.0
        self.g_state.level_max_time = self.config["level_max_time"]
        self._setup(GHOST_COLORS)

    # MARK: toggle_pause
    def toggle_pause(self) -> None:
        """
        Pauses or unpauses the game
        """
        self.g_state.paused = not self.g_state.paused

    # MARK: leave_to_menu
    def leave_to_menu(self) -> None:
        """
        Resets the game state and returns to the main menu
        """
        self.g_state.paused = False
        self.g_state.started = False

    # MARK: to_dict
    def to_dict(self) -> dict[str, Any]:
        """
        Converts the game state to a dictionary for sending to the frontend
        """
        return {
            "grid": self.g_state.grid,
            "player": {
                "row": self.g_state.player_row,
                "col": self.g_state.player_col
                },
            "ghosts": [
                {
                    "row": g.row,
                    "col": g.col,
                    "color": g.color,
                    "on_cooldown": g.on_cooldown
                    } for g in self.g_state.ghosts],
            "lives": self.g_state.lives,
            "score": self.g_state.score,
            "level": self.g_state.level,
            "edible": lhelp.is_edible(self.g_state),
            "gums": list(self.g_state.gums),
            "super_gums": list(self.g_state.super_gums),
            "game_over": self.g_state.state,
            "paused": self.g_state.paused,
            "round_id": self.g_state.round_id,
            "level_max_time": self.g_state.level_max_time,
            "time": self.g_state.level_max_time,
        }
