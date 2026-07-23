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
