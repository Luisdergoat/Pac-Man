from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Any

DEFAULT_CONFIG = {
    "highscore_file": "highscore.json",
    "lives": 3,
    "points_per_gum": 10,
    "points_per_super_gum": 50,
    "points_per_ghost": 200,
    "level_max_time": 90,
}
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"
MAX_HIGHSCORES = 10

# Only allow alphanum charactes min 1 max 20.
NAME_PATTERN = re.compile(r"^[A-Za-z0-9]{1,20}$")


# MARK: _strip_coments
def _strip_comments(raw_text: str) -> str:
    """Remove comments out of raw text.
    Comments are marked by either '#' or '//'.

    Args:
        raw_text (str): Raw text string containing string to be stripped.

    Returns:
        str: Stripped string.
    """
    try:
        lines = [
            line
            for line in raw_text.splitlines()
            if not line.strip().startswith(("#", "//"))
        ]
    except Exception as e:
        print(f"Error while stripping comments: {e}")
        return raw_text  # Fallback
    return "\n".join(lines)


# MARK: config_parser
def _config_parser(config: dict[Any, Any]) -> dict[str, int | str]:
    """Parses raw config file and returns only valid entries.

    Args:
        config (dict[Any, Any]): Raw config dict.

    Returns:
        dict[str, int | str]: Dict with valid entries.
    """
    allowed_keys = {
        "highscore_filename",
        "lives",
        "points_per_pacgum",
        "points_per_super_pacgum",
        "points_per_ghost", "level_max_time"
    }

    res: dict[str, int | str] = {}
    for k, v in config.items():
        if k not in allowed_keys:
            print(f"Error unknown key in config: {repr(k)}, ignoring.")
            continue

        if k == "highscore_filename":
            if not isinstance(v, str) or not v:
                print(f"Error {k} invalid value {v}")
                continue
        elif not isinstance(v, int) or v < 0:
            print(f"Error {k} invalid value {repr(v)}")
            continue
        res.update({k: v})
    return res


# MARK: load_config
def load_config() -> dict[str, Any]:
    """Loads config from json file.
    If an error accours while reading use default values.

    Args:
        CONFIG_PATH (str): File path to json file.

    Returns:
        dict[str, Any]: Returns parsed json data or fallback data.
    """
    default_config = DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            raw_text = f.read()
            stripped_text = _strip_comments(raw_text)
            loaded_config = json.loads(stripped_text)
            if isinstance(loaded_config, dict):
                default_config.update(_config_parser(loaded_config))
    except FileNotFoundError:
        print(f"Config file {CONFIG_PATH} not found. "
              f"Using default configuration.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {CONFIG_PATH}: {e}. "
              f"Using default configuration.")
    except PermissionError:
        print(f"No permission to open config file {CONFIG_PATH}. "
              f"Using default configuration.")
    return default_config


# MARK: _sanitize_name
def _sanitize_name(name: str) -> str:
    """Checks if name is alpanum and max 20.
    If not return 'Player' as fallback.

    Args:
        name (str): Name to check.

    Returns:
        str: If valid returns name unchanged if unvalid returns fallback.
    """
    name = name.strip()
    if not NAME_PATTERN.match(name):
        name = "Player"
    return name


# MARK: parse_highscores
def _parse_highscores(
        highscores: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Parses loaded highscore to ensure valid entry.
    If entry is not valid it gets removed.

    Args:
        highscores (list[dict[str, Any]]): Raw loaded highscore list.

    Returns:
        list[dict[str, Any]]: Valid highscore entrys.
    """
    res = []
    for entry in highscores:
        if not isinstance(entry, dict):
            print("Error loading highscores, only dicts are allowed.")
            continue

        if not {"name", "score", "level"}.issubset(set(entry.keys())):
            print("Error loading highscores, key is missing.")
            continue

        if not isinstance(entry["name"], str) \
                or not NAME_PATTERN.match(entry["name"]):
            print("Error loading highscores, name not valid.")
            continue

        if not isinstance(entry["score"], int) or entry["score"] < 0:
            print("Error loading highscores, score not valid.")
            continue

        if not isinstance(entry["level"], int) or entry["level"] < 0:
            print("Error loading highscores, level not valid.")
            continue

        if len(entry) > 3:
            print("Error loading highscores, additional keys added.")
            continue

        # Fix order.
        res.append(
            {"name": entry["name"],
             "score": entry["score"],
             "level": entry["level"]
             })
    return res


# MARK: load_highscores
def load_highscores(filename: str) -> list[dict[str, Any]]:
    """Loads highscore json file.

    Args:
        filename (str): Filename of json highscore file.

    Returns:
        list[dict[str, Any]]: Returns loaded and parsed json file.
            If file not found or file is malformed returns empty list.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Highscore file {filename} not found. Returning empty list.")
        return []
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: Highscore file {filename} is corrupted or unreadable:"
              f" {exc}. Returning empty list.")
        return []
    except PermissionError:
        print(f"No permission to open highscore file {filename}. "
              "Returning empty list.")
        return []

    if not isinstance(data, list):
        print(f"Warning: Highscore file {filename} does not contain a list. "
              "Returning empty list.")
        return []

    return _parse_highscores(data)


# MARK: add_highscore
def add_highscore(
        filename: str,
        name: str,
        score: int,
        level: int = 1
) -> list[dict[str, Any]] | None:
    """Add new highscore to highscore file in biggest highscore at the top.
    If MAX_HIGHSCORES is overstepped then the lowest entry will be overwritten.

    Args:
        filename (str): Filename of highscore json file.
        name (str): Name of player.
        score (int): Score of player.
        level (int, optional): Level that player reached. Defaults to 1.

    Returns:
        list[dict[str, Any]] | None: Returns updated highscore list
            or None if OSError accured.
    """
    name = _sanitize_name(name)
    score = max(0, int(score)) if isinstance(score, (int, float)) else 0
    level = max(1, int(level)) if isinstance(level, (int, float)) else 1

    scores = load_highscores(filename)
    scores.append({"name": name, "score": score, "level": level})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:MAX_HIGHSCORES]

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError as exc:
        print(f"Error writing to highscore file {filename}: {exc}")
        return None
    return scores
