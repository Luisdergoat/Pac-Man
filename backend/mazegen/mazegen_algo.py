#!/usr/bin/env python3
"""
Docstring for algo
"""

from __future__ import annotations

import random
from typing import Dict, List, Optional, Sequence, Tuple, Union

from .cell import Cell

try:
    import visualize_maze
except ImportError:
    pass

ConfigValue = Union[int, bool, str, Tuple[int, int]]
Config = Dict[str, ConfigValue]
Maze = Sequence[Sequence[Cell]]


steps: List[Tuple[int, int]] = []


def _require_int(config: Config, key: str) -> int:
    value = config.get(key)
    if isinstance(value, int):
        return value
    raise ValueError(f"Config key {key} must be int")


def _require_tuple(config: Config, key: str) -> Tuple[int, int]:
    value = config.get(key)
    if isinstance(value, tuple) and len(value) == 2:
        x_val, y_val = value
        return int(x_val), int(y_val)
    raise ValueError(f"Config key {key} must be a tuple of two ints")


def _require_bool(config: Config, key: str) -> bool:
    value = config.get(key)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() == "true"
    raise ValueError(f"Config key {key} must be bool")


def check_moves(
    maze: Maze,
    config: Config,
    x: int,
    y: int,
) -> Dict[str, bool]:
    """
    Docstring for check_moves
    :param maze: Description
    :param cell: Description
    """
    is_move_valid = {
        "N": False,
        "E": False,
        "S": False,
        "W": False
    }
    # Check North: y-1
    if y > 1:  # y > 1 to avoid frame at y=0
        cell = maze[y - 1][x]
        if not cell.is_visited() and not cell.frame:
            is_move_valid["N"] = True
    # Check South: y+1
    height_val = _require_int(config, "HEIGHT")
    if y < height_val:
        cell = maze[y + 1][x]
        if not cell.is_visited() and not cell.frame:
            is_move_valid["S"] = True
    # Check East: x+1
    width_val = _require_int(config, "WIDTH")
    if x < width_val:
        cell = maze[y][x + 1]
        if not cell.is_visited() and not cell.frame:
            is_move_valid["E"] = True
    # Check West: x-1
    if x > 1:  # x > 1 to avoid frame at x=0
        cell = maze[y][x - 1]
        if not cell.is_visited() and not cell.frame:
            is_move_valid["W"] = True
    return is_move_valid


def check_walls(
    maze: Maze,
    config: Config,
    x: int,
    y: int,
) -> Dict[str, bool]:
    """
    Docstring for check_moves
    :param maze: Description
    :param cell: Description
    """
    is_move_valid = {
        "N": False,
        "E": False,
        "S": False,
        "W": False
    }
    if maze[y][x].frame is True:
        return is_move_valid
    # Check North: y-1
    if y > 1:  # y > 1 to avoid frame at y=0
        cell = maze[y - 1][x]
        if not cell.frame:
            is_move_valid["N"] = True
    # Check South: y+1
    height_val = _require_int(config, "HEIGHT")
    if y < height_val:
        cell = maze[y + 1][x]
        if not cell.frame:
            is_move_valid["S"] = True
    # Check East: x+1
    width_val = _require_int(config, "WIDTH")
    if x < width_val:
        cell = maze[y][x + 1]
        if not cell.frame:
            is_move_valid["E"] = True
    # Check West: x-1
    if x > 1:  # x > 1 to avoid frame at x=0
        cell = maze[y][x - 1]
        if not cell.frame:
            is_move_valid["W"] = True
    return is_move_valid


def do_silent_next_move(
    maze: Maze,
    valid_moves: Dict[str, bool],
    x: int,
    y: int,
) -> Tuple[int, int]:
    """
    Docstring for do_next_move
    :param directions: Description
    """
    true_count = 0
    key: Optional[str] = None
    for key in valid_moves:
        if valid_moves[key] is True:
            true_count += 1
    if true_count == 0:
        return -1, -1
    while True:
        key = random.choice(list(valid_moves.keys()))
        if valid_moves[key] is True:
            break
    assert key is not None
    if key == "N":
        remove_wall_between(maze, x, y, "N")
        return x, y - 1
    if key == "E":
        remove_wall_between(maze, x, y, "E")
        return x + 1, y
    if key == "S":
        remove_wall_between(maze, x, y, "S")
        return x, y + 1
    if key == "W":
        remove_wall_between(maze, x, y, "W")
        return x - 1, y
    raise ValueError(f"Unknown direction: {key}")


def do_next_move(
    maze: Maze,
    valid_moves: Dict[str, bool],
    x: int,
    y: int,
) -> Tuple[int, int]:
    """
    Docstring for do_next_move
    :param directions: Description
    """
    true_count = 0
    key: Optional[str] = None
    for key in valid_moves:
        if valid_moves[key] is True:
            true_count += 1
    if true_count == 0:
        return -1, -1
    while True:
        key = random.choice(list(valid_moves.keys()))
        if valid_moves[key] is True:
            break
    assert key is not None
    if key == "N":
        remove_wall_between(maze, x, y, "N")
        new_x, new_y = x, y - 1
    elif key == "E":
        remove_wall_between(maze, x, y, "E")
        new_x, new_y = x + 1, y
    elif key == "S":
        remove_wall_between(maze, x, y, "S")
        new_x, new_y = x, y + 1
    elif key == "W":
        remove_wall_between(maze, x, y, "W")
        new_x, new_y = x - 1, y
    else:
        raise ValueError(f"Unknown direction: {key}")
    maze[new_y][new_x].mark_visited()
    steps.append((new_x, new_y))
    return new_x, new_y


def remove_wall_between(
    maze: Maze,
    x: int,
    y: int,
    direction: str,
) -> None:
    """
    Docstring for change_cell_and_bit
    :param maze: Description
    :param cell: Description
    """
    N = 7   # 0111
    E = 11  # 1011
    S = 13  # 1101
    W = 14  # 1110
    if direction == "N":
        maze[y][x].set_wall(N)
        maze[y - 1][x].set_wall(S)
    elif direction == "E":
        maze[y][x].set_wall(E)
        maze[y][x + 1].set_wall(W)
    elif direction == "S":
        maze[y][x].set_wall(S)
        maze[y + 1][x].set_wall(N)
    elif direction == "W":
        maze[y][x].set_wall(W)
        maze[y][x - 1].set_wall(E)
    else:
        raise ValueError(f"Unknown direction: {direction}")


def add_42_pattern(maze: Maze, config: Config) -> None:
    """
    Docstring for add_42_pattern
    :param maze: Description
    """
    height = _require_int(config, "HEIGHT") + 1
    width = _require_int(config, "WIDTH") + 1
    mid_x = int(height / 2)
    mid_y = int(width / 2)
    if height < 8 or width < 10:
        print("Maze is to small for 42 pattern")
        return
    # mark 4 as frame
    maze[mid_x][mid_y - 1].mark_as_frame()
    maze[mid_x + 1][mid_y - 1].mark_as_frame()
    maze[mid_x + 2][mid_y - 1].mark_as_frame()
    maze[mid_x][mid_y - 2].mark_as_frame()
    maze[mid_x][mid_y - 3].mark_as_frame()
    maze[mid_x - 1][mid_y - 3].mark_as_frame()
    maze[mid_x - 2][mid_y - 3].mark_as_frame()
    # mark 2 as frame
    maze[mid_x][mid_y + 1].mark_as_frame()
    maze[mid_x + 1][mid_y + 1].mark_as_frame()
    maze[mid_x + 2][mid_y + 1].mark_as_frame()
    maze[mid_x + 2][mid_y + 2].mark_as_frame()
    maze[mid_x + 2][mid_y + 3].mark_as_frame()
    maze[mid_x][mid_y + 2].mark_as_frame()
    maze[mid_x][mid_y + 3].mark_as_frame()
    maze[mid_x - 1][mid_y + 3].mark_as_frame()
    maze[mid_x - 2][mid_y + 3].mark_as_frame()
    maze[mid_x - 2][mid_y + 2].mark_as_frame()
    maze[mid_x - 2][mid_y + 1].mark_as_frame()


def check_42(maze: Maze, config: Config) -> bool:
    """checks if entry or exit is in 42 pattern"""
    entry_x, entry_y = _require_tuple(config, "ENTRY")
    exit_x, exit_y = _require_tuple(config, "EXIT")
    if maze[exit_y + 1][exit_x + 1].frame is True:
        return False
    if maze[entry_y + 1][entry_x + 1].frame is True:
        return False
    return True


def remove_extra_walls(maze: Maze, config: Config) -> None:
    """
    Docstring for remove_extra_walls
    :param maze: Description
    :param config: Description
    """
    height = _require_int(config, "HEIGHT")
    width = _require_int(config, "WIDTH")
    average_size = int(height + width / 2)
    for row in maze:
        for cell in row:
            rand = random.randint(1, average_size)
            if (cell.get_x() % rand == 0 or cell.get_y() % rand == 0):
                temp = cell.get_wall()
                moves = check_walls(maze, config, cell.get_x(), cell.get_y())
                do_silent_next_move(maze, moves, cell.get_x(), cell.get_y())
                wall_value = cell.get_wall()
                if wall_value == 0:
                    cell.set_wall(temp)


def generat_maze(
    maze: Maze,
    config: Config,
    animate: bool = False,
    delay: float = 0.01,
    color: str = "default",
) -> None:
    """
    Docstring for generat_maze
    :param config: Description
    :param animate: Wenn True, zeige Animation nach jedem Move
    :param delay: Verzögerung zwischen Frames (Sekunden)
    """
    import time

    if animate and visualize_maze is None:
        raise ImportError(
            "animate=True requires module 'visualize_maze' to be installed "
            "or available on PYTHONPATH"
        )

    #  macht das maze und erstellt den weg halt ha
    # Config coordinates are without frame, so add +1 offset
    entry_x, entry_y = _require_tuple(config, "ENTRY")
    exit_x, exit_y = _require_tuple(config, "EXIT")
    exit_x, exit_y = exit_x + 1, exit_y + 1  # Add frame
    x, y = entry_x + 1, entry_y + 1  # Add frame offset
    maze[y][x].mark_visited()
    maze[exit_y][exit_x].mark_visited()
    steps.append((x, y))

    # add 42 pattern
    if _require_bool(config, "42PATTERN") is True:
        add_42_pattern(maze, config)

    if check_42(maze, config) is False:
        return

    # Start Live-Visualisierung
    if animate and color == "default":
        visualize_maze.start_live_visualization(
            maze,
            config,
            current_pos=(x, y),
        )
    elif animate and color == "changed":
        visualize_maze.start_live_visualization_different_color(
            maze,
            config,
            current_pos=(x, y),
        )

    # handle seeds
    seed_val = config["SEED"]
    seed_int: int
    if isinstance(seed_val, int):
        seed_int = seed_val
    elif isinstance(seed_val, str):
        try:
            seed_int = int(seed_val)
        except ValueError:
            seed_int = random.randint(-2147483648, 2147483647)
    else:
        seed_int = random.randint(-2147483648, 2147483647)
    random.seed(seed_int)

    exit_moves = check_moves(
        maze,
        config,
        exit_x,
        exit_y,
    )  # open Exit Wall
    exit_x, exit_y = do_silent_next_move(
        maze,
        exit_moves,
        exit_x,
        exit_y,
    )
    perfect_maze = _require_bool(config, "PERFECT")
    while True:
        valid_moves = check_moves(maze, config, x, y)
        x, y = do_next_move(
            maze,
            valid_moves,
            x,
            y,
        )

        animated = False

        if x == -1:
            if len(steps) > 0:
                x, y = steps.pop()
                # Aktualisiere Live-Visualisierung für jeden Move
                if animate and animated is False:
                    animated = True
                    if color == "default":
                        visualize_maze.update_live_visualization(
                            maze,
                            config,
                            current_pos=(x, y),
                        )
                    elif color == "changed":
                        visualize_maze.update_live_visualization_diff_color(
                            maze,
                            config,
                            current_pos=(x, y),
                        )
                time.sleep(delay)
            else:
                break

        # Aktualisiere Live-Visualisierung für jeden Move
        if animate and animated is False:
            if color == "default":
                visualize_maze.update_live_visualization(
                    maze,
                    config,
                    current_pos=(x, y),
                )
            elif color == "changed":
                visualize_maze.update_live_visualization_diff_color(
                    maze,
                    config,
                    current_pos=(x, y),
                )
            time.sleep(delay)
        animated = False

    if not perfect_maze:
        remove_extra_walls(maze, config)

    # Stoppe Live-Visualisierung
    if animate:
        visualize_maze.stop_live_visualization()
