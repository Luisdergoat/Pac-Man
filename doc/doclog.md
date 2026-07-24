# Pac-Man – Dev Diary

Projekt-Tagebuch für die 42 Pac-Man-Aufgabe. Neue Einträge einfach unten anhängen
(neuestes Datum zuunterst), Format ist bewusst simpel gehalten:

```
## YYYY-MM-DD
### Was gemacht wurde
### Probleme / Bugs
### Naechste Schritte
```

---

## 2026-07-23

### Was gemacht wurde
- Maze-Generator (`A-Maze-ing`-Package `mazegen`) ans Backend angebunden: `server.py`
  parst die `config.txt`, erzeugt das Maze über `mazegen_algo.generat_maze` und
  wandelt das Corridor-Maze (Cell-Objekte mit N/E/S/W-Wand-Bitmaske) in ein
  einfaches 0/1-Block-Grid um (`cells_to_grid`), das sich einfach rendern lässt.
- Frontend (`frontend/src/game.js`, `index.html`, `style.css`) zeichnet das Maze
  auf einem `<canvas>`, skaliert dynamisch auf die Fenstergröße (`fitCanvasToWindow`)
  und zentriert Titel + Canvas per Flexbox.
- Architektur umgestellt: Spiellogik (Spieler-Bewegung, Geister-KI, Kollision)
  läuft jetzt komplett in Python (`backend/game_logic.py`), nicht mehr im JS.
  Kommunikation läuft über WebSocket (`/ws`): Server hält den `GameState`,
  pusht alle 300ms ein Tick-Update, Client schickt nur Tastendrücke.
- Geister-Grundgerüst steht: 4 Geister spawnen an den 4 Ecken des Maze
  (rot, pink, cyan, orange – wie im Screen-Recording zu sehen), einfache
  Chase-KI (bewegt sich pro Tick in die Richtung, die die Distanz zum Spieler
  am meisten verkleinert), Kollision kostet ein Leben und respawnt den Spieler
  in der Maze-Mitte.
- Im hochgeladenen Screen-Recording (`IMG_1435.mp4`) ist der aktuelle Stand zu
  sehen: Maze wird korrekt gerendert (blaue Wände, weiße Gänge), Titel "Pac-Man",
  alle 4 Geister stehen an ihren Spawn-Punkten in den Ecken. Spieler (schwarzes
  Quadrat) sitzt im Video an einer Zelle in der linken Maze-Hälfte – im Video
  bewegt sich nichts, ist also vermutlich nur ein kurzer Zustands-Schnappschuss,
  keine Bewegung sichtbar. Das Video hatte Ton (nicht transkribiert – sag
  Bescheid falls das noch gebraucht wird).

### Probleme / Bugs (im Laufe des Tages gefixt)
- `/maze`-Endpoint gab rohe `Cell`-Objekte zurück statt einem sauberen Grid ->
  gefixt mit `cells_to_grid`.
- `style.css` 404 wegen falschem Pfad (`href="style.css"` statt
  `href="static/style.css"`) – StaticFiles ist unter `/static` gemounted.
- Canvas war fix auf 800x600 bzw. später fälschlich auf 2000x2000 gesetzt,
  während das Maze-Grid nur ~1150px brauchte -> Maze hing in der Ecke der
  Canvas, sah "nicht zentriert" aus. Gefixt durch dynamische
  `fitCanvasToWindow()`.
- Body-Flexbox ohne `flex-direction: column` -> Titel/Text lagen nebeneinander
  statt übereinander zentriert.
- Beim Umstieg auf Python-Logik: `DIRECTIONS: Dict[...] = {...}` wurde beim
  Abtippen zu `DIRECTIONS = Dict[...] = {...}` (Doppelpunkt zu `=` vertippt) ->
  TypeError beim Start.
- `websockets`-Package war in Python 3.9 (System-Python) installiert statt in
  der `.venv` (Python 3.12), die uvicorn tatsächlich nutzt -> "No supported
  WebSocket library" Warnung, `/ws` gab 404.
- `GameState.__post_init__` war zu `position()` umbenannt und wurde nirgends
  aufgerufen -> Spieler/Geister-Startpositionen wurden nie gesetzt.
- `to_dict()` schickt das Grid unter dem Key `"grid"`, JS hat aber `data.maze`
  geprüft -> Mismatch, Maze kam nie im Frontend an.
- `draw()` im JS hat noch alte lokale `x`/`y` (fix auf 100) für den Spieler und
  `g.x`/`g.y` für Geister benutzt statt der vom Server kommenden
  `player.row/col` bzw. `ghost.row/col` -> Spieler unsichtbar (weit außerhalb
  der Canvas), Geister unsichtbar (`NaN`-Koordinaten).

### Naechste Schritte
- Pacgums (kleine Punkte) + Super-Pacgums (4 Ecken) einbauen, inkl. Scoring.
- Edible-Ghost-Modus nach Super-Pacgum (Geister fliehen statt jagen, zeitlich
  begrenzt, respawn nach X Sekunden wenn gefressen).
- Lives/Score im HUD anzeigen (aktuell nur im State, noch nicht im UI).
- Config-System auf JSON mit Kommentaren umstellen (Subject verlangt JSON,
  aktuell `config.txt` im eigenen Format).
- Level-Progression (mind. 10 Level, erstes mit festem Seed 42, Rest random).
- Highscore-System (Top 10, Name-Eingabe, persistiert als JSON).
- Main Menu / Pause Menu / Game Over / Victory Screen.
- Cheat Mode für die Review (Invincibility, Level Skip, Ghost Freeze, etc.).

---

## 2026-07-24

### Was gemacht wurde
- Geister-KI von naivem Greedy-Verhalten (nur direkte Nachbarzellen, Luftlinie
  zum Spieler) auf echtes Pathfinding umgestellt: `bfs_next_step()` in
  `game_logic.py` sucht per Breitensuche den tatsächlich kürzesten Weg durchs
  Maze und die Geister laufen nur noch den ersten Schritt davon – kein
  Anrennen gegen Wände/Sackgassen mehr.
- Ghost-Ghost-Kollision: pro Tick wird eine `occupied`-Menge aus den aktuellen
  Geisterpositionen gebaut, jeder Geist bekommt sie als `blocked`-Set fürs
  Pathfinding mit, damit nie zwei Geister auf demselben Feld landen.
- "Nichts bewegt sich, bis der Spieler den ersten Schritt macht": neues
  `started`-Flag in `GameState`, `tick()` bricht ab solange `started == False`,
  `move_player()` setzt es beim ersten Tastendruck.
- Pacgums + Super-Pacgums + Scoring eingebaut: `_place_gums()` verteilt kleine
  Gums auf allen freien Feldern und Super-Gums in den 4 Ecken, `_collect_gums()`
  sammelt sie ein und vergibt Punkte (`POINTS_PER_GUM`, `POINTS_PER_SUPER_GUM`).
- Edible-Ghost-Modus: Super-Gum setzt `edible_until` (Timer über
  `time.monotonic()`), Geister fliehen währenddessen (`_move_ghost_away_from_player`,
  greedy – maximiert statt minimiert die Distanz), Treffer auf einen fressbaren
  Geist zählt als "gefressen" (`Ghost.eaten`), gibt Punkte
  (`POINTS_PER_GHOST`) und der Geist respawnt nach `GHOST_RESPAWN_DELAY`
  Sekunden an seiner Startecke.
- Highscore-System in `config_loader.py`: `load_highscores()`/`add_highscore()`
  lesen/schreiben eine JSON-Liste, validieren Name (max. 10 Zeichen) und Score
  (nicht-negativer Int), halten Top 10, robust gegen fehlende/kaputte Datei.
  `GameState.game_over`-Flag informiert das Frontend, wenn Game Over ist.
- Eigenes Config-System (`config_loader.py`, `config.json`): JSON mit
  Kommentar-Zeilen (`#`/`//`), eigene Keys getrennt von der `mazegen`
  `config.txt` (Lives, Punkte pro Gum/Geist, `level_max_time`, Highscore-Datei).
- Neustart-Feature: Taste "R" (bzw. Button) sendet `restart`-Action über den
  WebSocket, `GameState.reset()` setzt Score/Leben/Flags zurück und platziert
  Spieler/Geister/Gums neu. `regenerate_maze()` in `server.py` parst die
  `config.txt` erneut und ruft `generat_maze()` frisch auf (eigenes `Cell`-Grid
  noetig, da alte Zellen schon "besucht"-Status haben) – dank `SEED=random`
  in der config.txt gibt's dabei jedes Mal ein komplett neues Maze.
- Kompletter UI-Umbau: Start-Screen ("Game Start"/"Settings"), Settings-Screen,
  Ladebildschirm und Game-Over-Overlay als eigene "Screens" mit gemeinsamer
  `showScreen()`/`hideAllScreens()`-Logik. Ladebalken ist ein bewusst gefaktes
  "Indeterminate Progress"-Element: waechst per CSS-Transition langsam
  (abbremsend, `cubic-bezier`) bis 92% und bleibt dort haengen, bis die echten
  Maze-Daten da sind – dann Klassenwechsel auf `.complete`, Breite springt ohne
  Transition sofort auf 100% ("Snap"). Game-Over-Overlay hat jetzt ein
  Namensfeld + "Save Score"/"Play Again" statt hässlichem `prompt()`.
- Exit-Game-Button auf Start-Screen und Game-Over-Overlay: sendet
  `POST /shutdown`, Server killt sich selbst nach kurzer Verzoegerung per
  `os.killpg(os.getpgid(0), signal.SIGTERM)` (killt Prozessgruppe, damit bei
  `uvicorn --reload` auch der Watcher-Prozess mit stirbt, nicht nur der Worker).
- `Makefile` im Projekt-Root: `install` baut venv per `uv venv` + installiert
  Requirements, `run`/`make` (Default-Target) öffnet automatisch ein neues
  Terminal-Fenster (`osascript`/AppleScript unter macOS), startet den Server
  darin und öffnet danach Chrome auf `localhost`. Dazu `debug` (pdb),
  `lint`/`lint-strict` (exakt die vom Subject geforderten flake8/mypy-Flags),
  `clean` (Caches), `fclean` (zusätzlich venv löschen), `re`.

### Probleme / Bugs (im Laufe des Tages gefixt)
- Geister "zuckten" gegen Wände: Greedy-Distanz-Bewegung ohne echtes
  Pathfinding lief in Sackgassen fest -> ersetzt durch BFS.
- `_strip_coments()` in `config_loader.py` nutzte
  `line.strip().startswith("#", "//")` – zweites Argument von `startswith` ist
  ein Start-Index (int), kein zweiter Praefix-String -> TypeError, Kommentare
  wurden nie entfernt. Fix: `startswith(("#", "//"))` mit Tupel.
- `save_highscore`-Methode war nur halb geschrieben (brach mitten in einem
  `if` ab) -> SyntaxError beim Start, Server lief gar nicht.
- Highscore "wurde nicht gespeichert" war kein Bug – es gab zwei Dateien
  (`highscore.json` leer im Root als toter Default-Wert, `backend/highscores.json`
  tatsaechlich befuellt), nur an der falschen Stelle nachgeschaut.
- `game.js`: `document.getElementById("name-submit")` – Button heisst aber
  `submit-name-btn`, Tippfehler crashte die `onmessage`-Funktion mitten drin.
- "R"-Taste hat `gameOverHandled = false` sofort beim Tastendruck gesetzt,
  noch bevor die Server-Antwort da war -> die State-gesteuerte Logik zum
  Ausblenden des Overlays hat nie gefeuert, Game-Over-Screen blieb haengen.
  Gefixt durch zentrales `showScreen()`/`hideAllScreens()`-Prinzip statt
  verstreuter Klassen-Toggles.
- `style.css` hatte doppelte, sich widersprechende Regeln fuer `.screen` und
  `#loading-bar-fill`/`#loading-bar-track` (alte Version wurde angehaengt statt
  ersetzt) -> Ladebalken hatte effektiv `width: 0%`, war unsichtbar.
- Makefile: `osascript`-Aufruf fuer `run` wurde falsch aufgeteilt (Anfuehrungszeichen
  nicht geschlossen, `unexpected EOF`) und faelschlich in `install` einsortiert;
  Befehle, die im neu geoeffneten Terminal laufen sollen, muessen alle als
  EIN String in `do script "..."` stehen (mit `&&` verkettet) – jede separate
  Rezept-Zeile im Makefile laeuft sonst in der Makefile-eigenen Shell, nicht im
  neuen Fenster.
- `game.js`: unvollstaendiger Funktionsaufruf `finish` statt
  `finishLoadingAnimation();` -> ReferenceError bei jedem Rundenstart, brach
  `onmessage` ab, Spiel blieb im Ladebildschirm haengen.
- Exit-Button im Start-Screen lag ausserhalb von `#start-screen`/`.screen-box`
  im HTML -> war permanent sichtbar statt nur auf dem Start-Screen.

### Naechste Schritte
- Level-Progression (mind. 10 Level, erstes mit festem Seed 42, Rest random) –
  Config-System steht, muss jetzt noch mit `server.py`/Level-Wechsel verdrahtet
  werden.
- Pause-Menü.
- Victory-Screen (aktuell nur Game-Over-Screen vorhanden).
- Cheat Mode für die Review (Invincibility, Level Skip, Ghost Freeze, etc.).
- README nach Subject-Vorgaben schreiben (Description, Instructions, Resources,
  Configuration, Highscore, Maze Generation, Implementation, Architecture,
  Project Management).
