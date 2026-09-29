# Pac-Man – Dev Diary

Projekt-Tagebuch für die 42 Pac-Man-Aufgabe. Jeder Arbeitstag hat pro
Person eine eigene Datei im `doc/`-Ordner nach dem Muster:

```
<intra-login> YYYY-MM-DD.md
```

| Login      | Person             |
| ---------- | ------------------ |
| `lunsold`  | Luis Unsöld        |
| `ascheufe` | Achilles Scheufele |

Neuer Tag = neue Datei, mit dem gleichen simplen Format:

```
### Was gemacht wurde
### Probleme / Bugs
### Naechste Schritte
```

---

## Überblick nach Phasen

| Phase                  | Zeitraum            | Schwerpunkt                                                        |
| ---------------------- | ------------------- | ------------------------------------------------------------------ |
| 1. Prototyp            | 23.07. – 24.07.     | FastAPI, WebSocket, Canvas-Frontend, Ghost-AI, Gums, Highscores, UI |
| 2. Gameplay & Polish   | 26.08.              | Pause, Level, Power-Pellets, Ghost-Modi, Highscore-Screen           |
| 3. Config & Refactor   | 21.09. – 24.09.     | Config-Parser, `src/`-Struktur, Makefile/uv, Frontend-Module        |
| 4. Cheats & Finish     | 25.09. – 29.09.     | Cheat-Mode, Timer, Config per Argument, Exit-Flow, Cleanup, mypy    |

---

## Tage

### 2026-07-23 – Prototyp steht

**lunsold** – [Datei](lunsold%202026-07-23.md)
- Maze-Generator ans Backend angebunden (`cells_to_grid`, Wand-Bitmasken → 0/1-Grid)
- Canvas-Frontend: Maze zeichnen, dynamisch skalieren (`fitCanvasToWindow`)
- Architektur: Spiellogik komplett in Python, Kommunikation per WebSocket (`/ws`), Tick alle 300 ms
- 4 Geister (rot, pink, cyan, orange) mit einfacher Chase-AI, Kollision kostet ein Leben

### 2026-07-24 – Features, UI, Makefile

**lunsold** – [Datei](lunsold%202026-07-24.md)
- Ghost-AI: BFS-Pathfinding, Geister blockieren sich nicht gegenseitig
- Spiel startet erst nach dem ersten Schritt (`started`-Flag)
- Pac-Gums, Power-Pellets, Punktesystem, Edible-Ghost-Modus
- Highscore-System + eigenes Config-System (`config.json`, Kommentare erlaubt)
- Restart (R), neues Maze bei jedem Start
- Komplette UI: Startscreen, Settings, Loading-Bar, Game-Over-Overlay mit Namenseingabe
- Exit-Button (`POST /shutdown`), `Makefile` (install/run/debug/lint/clean/fclean/re)
- Neues `mazegenerator`-Wheel eingebunden (Wand-Bits N=1, E=2, S=4, W=8)

### 2026-08-26 – Gameplay-Feinschliff

**lunsold** – [Datei](lunsold%202026-08-26.md)
- Maze-Paketwechsel abgeschlossen (`.maze`-Property statt `generate_maze()`)
- Makefile-Fix: altes venv wird gelöscht → Python 3.12 statt 3.9
- Pause-Feature (P), `leave_to_menu`-Action, Movement-Throttle (150 ms)
- Dümmere Ghost-AI (`GHOST_CHASE_CHANCE`), Flee-Modus, Level-Progression
- Highscores mit Level, `/highscores`-Endpoint + Highscore-Screen, HUD mit Level
- Bugfix-Plan für das unerreichbare „42“-Logo (`_reachable_cells()`)

### 2026-09-21 – Erste Bestandsaufnahme

**ascheufe** – [Datei](ascheufe%202026-09-21.md)
- Code gelesen, Probleme per Kommentar markiert
- Gefunden: mypy-Fehler, Permission-Bug im Config-Loader, fehlende Highscore-Validierung

### 2026-09-22 – Loader & Übersetzung

**ascheufe** – [Datei](ascheufe%202026-09-22.md)
- `config_loader.py` → `loader.py` refactored
- Permission-Crash gefixt, Highscore-Parsing mit Validierung
- Config-Parser hinzugefügt, Doku auf Englisch

**lunsold** – [Datei](lunsold%202026-09-22.md)
- Kommentare/Docstrings im Backend auf Englisch
- `pac_man.py` als plattformübergreifender Launcher (macOS/Linux)
- Erster Linux-Test

### 2026-09-23 – Großer Refactor

**ascheufe** – [Datei](ascheufe%202026-09-23.md)
- Neue `src/`-Struktur: `frontend`, `game_logic`, `loader`, `server`
- Makefile neu, `pyproject.toml` für `uv`, mypy-Konfiguration
- `pac_man.py` startet uvicorn + Browser direkt aus Python
- Alte `backend/`- und `frontend/`-Ordner entfernt

**lunsold** – [Datei](lunsold%202026-09-23.md)
- Launcher-Fix für Linux/venv, Chrome öffnet automatisch
- `GameState`/Game-Logic in mehrere Dateien aufgeteilt
- HTML auf Englisch, Pfeiltasten + Shift-Bewegung
- Konami-Code-Erkennung im Frontend (`cheat_activate`)
- `uv.lock` und `__pycache__` aus Git entfernt

### 2026-09-24 – Ghost-Respawn & Frontend-Module

**ascheufe** – [Datei](ascheufe%202026-09-24.md)
- Geist wartet nach dem Fressen 5 s bis zum Respawn (`on_cooldown`, async Task)
- Browser öffnet erst, wenn der Server bereit ist

**lunsold** – [Datei](lunsold%202026-09-24.md)
- WebSocket-Endpoint-Fix
- `game.js` in `scripts/`-Module aufgeteilt (state, rendering, screens, controls, …)
- Config lädt korrekt (`lives` aus `config.json`)

### 2026-09-25 – Cheat-Mode & Config-Refactor

**ascheufe** – [Datei](ascheufe%202026-09-25.md)
- Toter Geist wird nicht mehr gezeichnet
- Hardcodierte Config-Werte entfernt: `GameLogic(config_name)`, `create_app()`-Factory
- Config-Datei als Kommandozeilenargument
- Merge-Fix in `server.py`

**lunsold** – [Datei](lunsold%202026-09-25.md)
- Bugfix: „R“ im Namensfeld startete die Runde neu
- Cheat-Mode (Unverwundbarkeit) + Level-Skip mit Space
- UI-Cleanup (HOME-Button, Übersetzungen, Settings-Hinweise)
- Altes `config.txt` entfernt

### 2026-09-28 – Timer & Config-Argument

**ascheufe** – [Datei](ascheufe%202026-09-28.md)
- Timer per `level_max_time`, `State`-Enum (`ALIVE`/`DEAD`/`TIMEDOUT`)
- Config-Keys vereinheitlicht, Defaults als Fallback
- Spielername max. 10 Zeichen

**lunsold** – [Datei](lunsold%202026-09-28.md)
- Cheat-Combo-Bug („zweimal eingeben“) gefixt
- Timer im HUD, passende Game-Over-Meldung (keine Leben / Zeit abgelaufen)
- Config-Pfad per Argument: `make run config.json`
- Pause-Menü-HOME räumt Canvas/Scoreboard auf

### 2026-09-29 – Cleanup & Exit-Flow

**ascheufe** – [Datei](ascheufe%202026-09-29.md)
- mypy-Fixes, globaler `CONFIG_PATH` entfernt, `pac_man.py` → `pac-man.py`
- Makefile: `debug` mit `python3 -m pdb`
- Highscore-Dateiname aus der Config statt hardcodiert
- Cheat-Mode-Reset beim Neustart, Power-Pellet-Bug im Cheat-Mode
- Bool-Werte werden in Config/Highscores abgelehnt

**lunsold** – [Datei](lunsold%202026-09-29.md)
- Escape-Menü mit RESUME/EXIT, `exit_game`-Action fährt den Server herunter
- „GAME CLOSED“-Screen, Eingaben danach ignoriert
- Zentrierung der Overlay-Screens, Timer nie negativ
