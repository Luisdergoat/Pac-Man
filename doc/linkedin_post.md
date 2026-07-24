🟡 Pac-Man, neu gebaut — als Web-Game

Aktuell arbeite ich im Rahmen meines 42-Projekts an einer eigenen Version des Arcade-Klassikers Pac-Man. Early state, aber der Kern läuft schon: Maze-Generierung, Bewegung, 4 Geister mit eigener KI (Pathfinding via BFS, Flucht-Verhalten bei Super-Pacgums), Pacgums sammeln, Scoring.

Der Tech-Stack:
– Backend: Python, komplette Spiellogik (Bewegung, Geister-KI, Kollisionen, Scoring) läuft serverseitig
– FastAPI + WebSocket für Echtzeit-Kommunikation zwischen Server und Browser
– Frontend: HTML5 Canvas + JavaScript rendert nur, was der Server an Zustand schickt — keine Spiellogik im Client

Mehr Updates folgen, sobald Levels, Highscores und Menüs dazukommen. Waka-waka! 👻

#python #fastapi #webdev #gamedev #42school
