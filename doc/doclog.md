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
- Zugewiesenes A-Maze-ing Package erhalten (`mazegenerator-00001-py3-none-any.whl`
  im Projekt-Root) – ersetzt den bisherigen selbstgeschriebenen `mazegen`-Ordner.
  Wheel entpackt und Quellcode direkt geprüft (nicht nur README vertraut):
  Klasse `MazeGenerator`, Konstruktor `size=(w,h), entry_cell, exit_cell,
  perfect, seed` (seed=0 heisst voll zufaellig), Property `.maze` liefert
  `maze[y][x]`-Grid ohne extra Rahmen (Aussenkanten sind fest in den
  Randzellen-Bits kodiert), Wand-Bits **N=1, E=2, S=4, W=8** (anders als beim
  alten Package: N=8, E=4, S=2, W=1). `cells_to_grid()` in `server.py` dafuer
  umgeschrieben (kein `+1`-Offset mehr fuers Ausblenden eines Rahmens noetig).
  Maze-Erzeugung laeuft jetzt direkt ueber Konstruktor-Parameter in Python,
  kein `config.txt`/`parse_maze_config`-Umweg mehr fuer den Maze-Teil noetig.
  Package als lokale Wheel-Datei in `requirements.txt` eingetragen
  (`../mazegenerator-00001-py3-none-any.whl`).

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
- Package-Wechsel: README-Quickstart des zugewiesenen `mazegenerator`-Wheels
  ist falsch/veraltet (`from mazegenerator import MazeGenerator` schlaegt fehl,
  `__init__.py` im Wheel ist leer und exportiert nichts). Tatsaechlich
  funktionierender Import: `from mazegenerator.mazegenerator import
  MazeGenerator`. Erst durch direktes Testen im Sandbox-Python gefunden, nicht
  aus der Doku ersichtlich.

### Naechste Schritte
- Umstellung auf das neue `mazegenerator`-Package in `server.py` einbauen
  (siehe oben) und alten `mazegen/`-Ordner + `config.txt` aufraeumen/loeschen,
  sobald das laeuft.
- Level-Progression (mind. 10 Level, erstes mit festem Seed 42, Rest random) –
  jetzt auf Basis von `build_maze(seed=...)` mit variabler Breite/Hoehe pro
  Level statt der alten `config.txt`.
- Pause-Menü.
- Victory-Screen (aktuell nur Game-Over-Screen vorhanden).
- Cheat Mode für die Review (Invincibility, Level Skip, Ghost Freeze, etc.).
- README nach Subject-Vorgaben schreiben (Description, Instructions, Resources,
  Configuration, Highscore, Maze Generation, Implementation, Architecture,
  Project Management).

**-> Hier Schluss gemacht für heute.** Weiter geht's mit dem Einbau des
`mazegenerator`-Packages, danach Level-Progression.

---

## 2026-08-26

### Was gemacht wurde
- Maze-Generator-Package-Wechsel fertig integriert: `build_maze()` in
  `server.py` nutzt jetzt die `.maze`-Property von `MazeGenerator` direkt
  (vorher fälschlich `.generate_maze()` aufgerufen, existiert nicht),
  `cells_to_grid()` verarbeitet das Bitmask-Grid des neuen Packages.
- Server-Shutdown-Bug gefixt: `os.getpgrid(0)` existiert nicht in Python,
  korrekt ist `os.killpg(os.getpgid(0), signal.SIGTERM)`.
- Makefile-Bug gefixt, der für den hartnäckigen "läuft trotzdem unter Python
  3.9"-Fehler verantwortlich war: `uv venv` überschreibt ein bestehendes
  venv-Verzeichnis nicht. `install`-Target löscht das alte venv jetzt vorher
  (`rm -rf $(VENV_NAME) &&`), bevor es mit `--python 3.12` neu angelegt wird.
  Damit läuft `mazegenerator` (nutzt `str | bool`-Syntax, braucht Python
  >=3.10) endlich im richtigen Interpreter.
- Pause-Feature eingebaut: Taste "P" toggelt `GameState.paused`,
  `move_player()`/`tick()` brechen früh ab wenn pausiert, neuer
  `#pause-screen` mit Resume-/Back-to-Main-Menu-Buttons in `index.html`.
- Bug beim "Back to Main Menu"-Button gefixt: Button hat vorher nur lokal den
  Screen gewechselt, ohne den Server zu informieren -> nächster periodischer
  Broadcast kam noch mit `paused: true` rein und hat den Pause-Screen wieder
  übergelegt. Fix: neue `leave_to_menu`-Action/Methode, die serverseitig
  `paused`/`started` zurücksetzt.
- Geister-KI "dümmer" gemacht: `GHOST_CHASE_CHANCE` (Default 0.6) – Geister
  jagen nur noch mit dieser Wahrscheinlichkeit gezielt per BFS, sonst laufen
  sie zufällig (`_random_valid_step`).
- Spieler-Speed-Cap: Bewegungstasten haben bei gehaltener Taste durch
  Browser-Keyrepeat zu schnell ausgelöst -> `MOVE_INTERVAL_MS`-Throttle in
  `game.js` (Standard 150ms) begrenzt die Bewegungsrate unabhängig vom
  Keyrepeat.
- Edible-Ghost-Modus vollständig eingebaut: Super-Gum setzt `edible_until`
  (`time.monotonic()`-Timer, `EDIBLE_DURATION` Sekunden), Geister fliehen
  währenddessen (`_flee_step`, maximiert statt minimiert die Distanz zum
  Spieler), Kollision mit fressbarem Geist gibt `POINTS_PER_GHOST` Punkte und
  respawnt nur den Geist an seiner Startecke statt ein Leben zu kosten.
- Level-Progression eingebaut: neues `level`-Feld in `GameState`,
  `level_complete` wird gesetzt sobald Gums und Super-Gums leer sind,
  `next_level()` erhöht das Level, lädt ein frisches Maze (neuer zufälliger
  Seed) und behält Score/Leben. `server.py` generiert nach jedem Zug bei
  Bedarf ein neues Maze und ruft `next_level()`.
- Highscore-System um Level erweitert: `config_loader.add_highscore()`/
  `load_highscores()` speichern/lesen jetzt zusätzlich `level` pro Eintrag,
  `GameState.recorde_highscore()` übergibt das aktuelle Level mit.
- Neuer `/highscores`-Endpoint + Highscore-Screen im Frontend (Button auf dem
  Start-Screen), zeigt Einträge als "Name - Stage X - Score Punkte".
- Live-HUD zeigt jetzt zusätzlich das aktuelle Level, Geister werden während
  des Edible-Modus blau eingefärbt.

### Probleme / Bugs (im Laufe der Session gefixt)
- `generator.generate_maze()` existiert nicht auf `MazeGenerator` (richtig:
  `.maze`-Property) -> `AttributeError` beim Serverstart nach dem
  Package-Wechsel.
- `os.getpgrid(0)` gibt es in Python nicht (richtig:
  `os.killpg(os.getpgid(0), ...)`) -> Shutdown-Endpoint crashte.
- `TypeError: unsupported operand type(s) for |: 'type' and 'type'` beim
  Start: Server lief unter Python 3.9 (Xcode-Bundled-Python) statt der
  3.12-venv, weil `uv venv` ein bestehendes (kaputtes) venv-Verzeichnis nicht
  überschreibt – die venv aus dem ersten fehlgeschlagenen Versuch blieb bei
  3.9 hängen, obwohl `--python 3.12` schon im Makefile stand.
- Pause-Feature: ursprüngliche Vermutung war ein falscher Tastencheck
  (Escape statt P) – tatsächlich war P von Anfang an korrekt so gewollt,
  kein echter Bug.
- "Back to Main Menu" zeigte kurz den Start-Screen und sprang dann wieder
  zurück: Server wusste nichts vom Menü-Wechsel, periodischer Broadcast mit
  `paused: true` hat den Pause-Screen reaktiviert. Gefixt mit expliziter
  `leave_to_menu`-Action.
- `_check_collision()` hat `"Game Over"` von `_respawn_after_hit()` nur
  geprintet statt `self.game_over` zu setzen -> Game-Over-Screen kam erst mit
  bis zu 300ms Verzögerung (nächster Tick). Beim Umbau für Edible-Ghosts
  direkt mitgefixt.

### Naechste Schritte
- Alten `backend/mazegen/`-Ordner und `config.txt` (fürs alte Maze-Package)
  endgültig aufräumen/löschen.
- Testen, dass `make fclean && make run` jetzt zuverlässig mit Python 3.12
  durchläuft und das neue Maze-Package/Level-Progression im echten Browser
  funktioniert.
- Victory-Screen (aktuell wird alles über das Game-Over-Overlay abgewickelt).
- Cheat Mode für die Review (Invincibility, Level Skip, Ghost Freeze, etc.).
- README nach Subject-Vorgaben schreiben (Description, Instructions,
  Resources inkl. AI-Nutzung, Configuration, Highscore, Maze Generation,
  Implementation, Architecture, Project Management).
- Projektmanagement-Doku (Zeitplan/Gantt/Kanban, Risikoanalyse,
  Team-Organisation, Abnahmetestplan) laut Subject Kapitel VIII – bisher nur
  dieses informelle Tagebuch.
- `mypy`/`flake8`-Durchlauf über den gesamten Code (u.a. `blocked: set[...]
  = None` ist nicht als `Optional` annotiert, würde unter `--strict`
  durchfallen).

**-> Hier Schluss gemacht für heute.**
