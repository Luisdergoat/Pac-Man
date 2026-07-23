#!/usr/bin/env python3
"""
Hier wir die logik genommen aus der config.txt werden die regel eingesetzt
und in ein maze umgewandelt.
"""

from __future__ import annotations

import os
import sys
from typing import Dict, List, Optional, Tuple, Union

from mazegen.cell import Cell

ConfigValue = Union[int, bool, str, Tuple[int, int]]
Config = Dict[str, ConfigValue]


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


def read_out_config(
    file_path: str,
) -> Optional[Config]:
    """
    Nimmt die werte aus der Config.txt
    und gibt sie als dictionary zurueck
    die keys werden dann noch in integer und boolean umgewandelt.
    """
    config: Config = {}

    try:
        #  Versucht die config datei zu oeffnen und die werte in ein Dict macht
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue  # Skip empty lines and comments

                if "=" not in line:
                    continue  # Skip lines without '='

                value: str | int | bool | None | tuple[int, int] = None
                key, value = line.split("=", 1)
                if value.isdigit():
                    config[key] = int(value)
                elif value.lower() == "true":
                    config[key] = True
                elif value.lower() == "false":
                    config[key] = False
                else:
                    config[key] = value

        #  checked ob alle Werte auch gegeben wurden
        required_keys = [
            "WIDTH",
            "HEIGHT",
            "ENTRY",
            "EXIT",
            "OUTPUT_FILE",
            "PERFECT",
            "42PATTERN",
            "SEED",
        ]

        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key:{key}")

        #  checked ob die werte fuer die groesse des mazes passen
        width = _require_int(config, "WIDTH")
        height = _require_int(config, "HEIGHT")
        for key in ("ENTRY", "EXIT"):
            value = config[key]
            if isinstance(value, str):
                x_val, y_val = value.split(",", 1)
                config[key] = (int(x_val.strip()), int(y_val.strip()))

        if width < 3 or height < 3:
            raise ValueError(
                "The Maze turned out to small. "
                "At least 3x3 is required."
            )
        entry_x, entry_y = _require_tuple(config, "ENTRY")
        exit_x, exit_y = _require_tuple(config, "EXIT")
        if not -1 < entry_x < width:
            raise ValueError("The entry is out of bounds.")
        if not -1 < entry_y < height:
            raise ValueError("The entry is out of bounds.")
        if not -1 < exit_x < width:
            raise ValueError("The exit is out of bounds.")
        if not -1 < exit_y < height:
            raise ValueError("The exit is out of bounds.")
        if config['ENTRY'] == config['EXIT']:
            raise ValueError("The entry and exit points must be different.")

    except FileNotFoundError as e:
        print("ERROR: The config.txt file was not found ", e)
        return None
    except Exception as e:
        print(
            "ERROR: An error occurred while reading the config file: "
            f"{e}"
        )
        return None
    return config


def parse_maze_config(
    file_path: Optional[str] = None,
) -> Optional[Tuple[List[List[Cell]], Config]]:
    """
    Also die funktion macht die validierung der config werte,
    hier wird sich um die logik des Mazes auf Bit ebene gekuemmert.
    Das Maze wird erst einmal als 2D-Liste von Zellen dargestellt,
    ohne korrekten Weg zzwischen Entry und Exit.
    """

    project_root = os.path.dirname(os.path.dirname(__file__))
    try:
        if file_path is None:
            config_path = os.path.join(project_root, sys.argv[1])
        elif os.path.isabs(file_path):
            config_path = file_path
        else:
            config_path = os.path.join(project_root, file_path)
        config = read_out_config(config_path)
    except Exception:
        return None
    if config is None:
        return None

    #  Initialisiere das Maze mit cells anstadt ints
    # maze[y][x] mit y=0..HEIGHT+1, x=0..WIDTH+1
    # Der Frame ist bei x=0, x=WIDTH+1, y=0, y=HEIGHT+1
    width = _require_int(config, "WIDTH")
    height = _require_int(config, "HEIGHT")
    maze = [
        [Cell(x, y) for x in range(width + 2)]
        for y in range(height + 2)
    ]

    # Markiere Frame-Zellen (Rand)
    for y in range(height + 2):
        for x in range(width + 2):
            if (x == 0 or x == width + 1 or y == 0 or y == height + 1):
                maze[y][x].mark_as_frame()

    return maze, config
