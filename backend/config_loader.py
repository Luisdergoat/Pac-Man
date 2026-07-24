from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_CONFIG = {
    "highscore_file": "highscore.json",
    "lives": 3,
    "points_per_gum": 10,
    "points_per_super_gum": 50,
    "points_per_ghost": 200,
    "level_max_time": 90,
}
MAX_HIGHSCORES = 10
NAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{1,20}$")  # Nur Buchstaben, Zahlen und Unterstriche, max. 20 Zeichen


def _strip_coments(raw_text: str) -> str:
    """
    Entfernt Kommentare aus dem Text. Kommentare beginnen mit '#' und gehen bis zum Ende der Zeile.
    """
    try:
        lines = [
            line
            for line in raw_text.splitlines()
            if not line.strip().startswith("#", "//")
        ]
    except Exception as e:
        print(f"Error while stripping comments: {e}")
        return raw_text  # Fallback
    return "\n".join(lines)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Lädt die Konfiguration aus einer JSON-Datei. Wenn die Datei nicht existiert,
    wird die Standardkonfiguration verwendet.
    """
    default_config = dict(DEFAULT_CONFIG)  # Kopie der Standardkonfiguration
    try:
        with open(config_path, "r") as f:
            raw_text = f.read()
            stripped_text = _strip_coments(raw_text)
            loaded_config = json.loads(stripped_text)
            default_config.update(loaded_config)  # Überschreibt Standardwerte mit geladenen Werten
    except FileNotFoundError:
        print(f"Config file {config_path} not found. Using default configuration.")
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {config_path}: {e}. Using default configuration.")
    return default_config


def _sanitize_name(name: str) -> str:
    """
    Überprüft, ob der Name den Anforderungen entspricht. 
    Wenn nicht, wird ein Standardname zurückgegeben.
    """
    name = (name or "").strip()
    if not NAME_PATTERN.match(name):
        name = "Player"
    return name


def load_highscores(filename: str) -> List[Dict[str, Any]]:
    """
    Lädt die Highscores aus einer JSON-Datei. Wenn die Datei nicht existiert,
    wird eine leere Liste zurückgegeben.
    """
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Highscore file {filename} not found. Returning empty list.")
        return []
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Warning: Highscore file {filename} is corrupted or unreadable: {exc}. Returning empty list.")
        return []

    if not isinstance(data, list):
        print(f"Warning: Highscore file {filename} does not contain a list. Returning empty list.")
        return []

    return [
        {
            "name": entry["name"],
            "score": entry["score"],
        }
        for entry in data
        if isinstance(entry, dict)
        and isinstance(entry.get("name"), str)
        and isinstance(entry.get("score"), int)
        and entry.get("score") >= 0
    ]


def add_highscore(filename: str, name: str, score: int) -> None:
    """
    Fügt einen neuen Highscore hinzu und speichert die aktualisierte Liste in der Datei.
    Die Liste wird nach Score absteigend sortiert und auf MAX_HIGHSCORES Einträge begrenzt.
    """
    name = _sanitize_name(name)
    score = max(0, int(score)) if isinstance(score, (int, float)) else 0

    scores = load_highscores(filename)
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:MAX_HIGHSCORES]

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=2)
    except OSError as exc:
        print(f"Error writing to highscore file {filename}: {exc}")

    return scores
