import random
import time
import asyncio
from collections import deque
from src.game_logic.objects import GameState, Ghost


class LogicHelper:
    # MARK: find_nearest_open_cell
    @staticmethod
    def find_nearest_open_cell(
            grid: list[list[int]], row: int, col: int) -> tuple[int, int]:
        """
        Findet die naechste begehbare Zelle (0) im Grid,
        beginnend von der Startposition.
        Verwendet eine Breitensuche (BFS), um die
        naechste offene Zelle zu finden.
        """
        rows, cols = len(grid), len(grid[0])
        visited = {(row, col)}
        queue = deque([(row, col)])
        while queue:
            row, col = queue.popleft()
            if 0 <= row < rows and 0 <= col < cols and grid[row][col] == 0:
                return row, col
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                new_row, new_col = row + dr, col + dc
                if (0 <= new_row < rows
                    and 0 <= new_col < cols
                        and (new_row, new_col)) not in visited:
                    visited.add((new_row, new_col))
                    queue.append((new_row, new_col))

        return 1, 1  # Fallback, falls keine offene Zelle gefunden wird

    # MARK: collect_gums
    @staticmethod
    def collect_gums(
        gamestate: GameState,
        POINTS_PER_GUM: int,
        POINTS_PER_SUPER_GUM: int,
        EDIBLE_DURATION: int
    ) -> None:
        """
        Zum einsammeln der gums.
        """
        pos = (gamestate.player_row, gamestate.player_col)
        if pos in gamestate.gums:
            gamestate.gums.discard(pos)
            gamestate.score += POINTS_PER_GUM
        elif pos in gamestate.super_gums:
            gamestate.super_gums.discard(pos)
            gamestate.score += POINTS_PER_SUPER_GUM
            gamestate.edible_until = time.monotonic() + EDIBLE_DURATION

        if not gamestate.gums and not gamestate.super_gums:
            gamestate.level_completed = True

    # MARK: random_valid_step
    @staticmethod
    def _random_valid_step(
        gamestate: GameState,
        ghost: Ghost,
        blocked: set[tuple[int, int]] | None = None
    ) -> tuple[int, int]:
        """
        Gibt einen zufälligen gültigen Schritt für den Geist zurück.
        """
        blocked = blocked or set()
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        valid_steps = []
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = ghost.row + dr, ghost.col + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and gamestate.grid[nr][nc] == 0
                    and (nr, nc) not in blocked):
                valid_steps.append((nr, nc))
        return random.choice(valid_steps) if valid_steps else (
            ghost.row, ghost.col)

    # MARK: flee_step
    @staticmethod
    def _flee_step(
        gamestate: GameState,
        ghost: Ghost,
        blocked: set[tuple[int, int]] | None = None
    ) -> tuple[int, int]:
        """
        Gibt einen Schritt zurück, der den Geist vom Spieler wegführt.
        """
        blocked = blocked or set()
        best, best_dist = None, -1
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = ghost.row + dr, ghost.col + dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and gamestate.grid[nr][nc] == 0
                    and (nr, nc) not in blocked):
                dist = abs(
                    nr - gamestate.player_row) + abs(nc - gamestate.player_col)
                if dist > best_dist:
                    best_dist, best = dist, (nr, nc)
        return best or (ghost.row, ghost.col)

    # MARK: respawn_after_hit
    @classmethod
    def respawn_after_hit(cls, gamestate: GameState) -> str:
        """
        Respawnt den Spieler an der Startposition und reduziert die Leben.
        """
        gamestate.lives -= 1
        if gamestate.lives > 0:
            rows, cols = len(gamestate.grid), len(gamestate.grid[0])
            rows, cols = cls.find_nearest_open_cell(
                gamestate.grid, rows // 2, cols // 2)

            gamestate.player_row, gamestate.player_col = rows, cols
            for ghost in gamestate.ghosts:
                ghost.row, ghost.col = cls.find_nearest_open_cell(
                    gamestate.grid, ghost.start_row, ghost.start_col)
        else:
            return "Game Over"
        return ""

    @staticmethod
    async def _ghost_respawn(ghost: Ghost, row: int, col: int) -> None:
        await asyncio.sleep(5)
        ghost.row, ghost.col = row, col
        ghost.on_cooldown = False

    # MARK: check_collision
    @classmethod
    def check_collision(
            cls, gamestate: GameState, POINTS_PER_GHOST: int) -> None:
        """
        Checkt, ob der Spieler ein Geist berührt.
        """
        for ghost in gamestate.ghosts:
            if ghost.on_cooldown:
                continue
            if ghost.row == gamestate.player_row \
                    and ghost.col == gamestate.player_col:
                if cls.is_edible(gamestate):
                    gamestate.score += POINTS_PER_GHOST
                    ghost.on_cooldown = True
                    row, col = cls.find_nearest_open_cell(
                        gamestate.grid, ghost.start_row, ghost.start_col)
                    asyncio.create_task(cls._ghost_respawn(ghost, row, col))
                else:
                    result = cls.respawn_after_hit(gamestate)
                    if result == "Game Over":
                        gamestate.game_over = True

    # MARK: reachable_cells
    @staticmethod
    def reachable_cells(
            gamestate: GameState,
            start: tuple[int, int]) -> set[tuple[int, int]]:
        """
        Gibt die Menge der erreichbaren Zellen,
        von der Startposition aus zurück.
        """
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        visited = set()
        queue = deque([start])
        while queue:
            row, col = queue.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = row + dr, col + dc
                if (0 <= nr < rows and 0 <= nc < cols
                        and gamestate.grid[nr][nc] == 0
                        and (nr, nc) not in visited):
                    visited.add((nr, nc))
                    queue.append((nr, nc))
        return visited

    # MARK: place_gums
    @classmethod
    def place_gums(cls, gamestate: GameState) -> None:
        """
        Platziert die Gums und Super-Gums im Grid.
        """
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        reachable = cls.reachable_cells(
            gamestate, (gamestate.player_row, gamestate.player_col))

        ocupied = {(gamestate.player_row, gamestate.player_col)} | {
            (ghost.row, ghost.col) for ghost in gamestate.ghosts}

        corners = [(1, 1), (1, cols - 2), (rows - 2, 1), (rows - 2, cols - 2)]
        gamestate.super_gums = {
            cls.find_nearest_open_cell(
                gamestate.grid, row, col) for row, col in corners
            } & reachable
        gamestate.gums = {
            (r, c)
            for r in range(rows)
            for c in range(cols)
            if (gamestate.grid[r][c] == 0
                and (r, c) not in ocupied
                and (r, c) not in gamestate.super_gums
                and (r, c) in reachable)
        }

    # MARK: is_wall
    @staticmethod
    def is_wall(gamestate: GameState, row: int, col: int) -> bool:
        """
        Checkt, ob die angegebene Position eine Wand ist.
        """
        rows, cols = len(gamestate.grid), len(gamestate.grid[0])
        if row < 0 or row >= rows or col < 0 or col >= cols:
            return True
        return gamestate.grid[row][col] == 1

    # MARK: is_edible
    @staticmethod
    def is_edible(gamestate: GameState) -> bool:
        """
        Gibt zurück, ob die Geister essbar sind.
        """
        return time.monotonic() < gamestate.edible_until

    # MARK: bfs_next_step
    @staticmethod
    def bfs_next_step(
        grid: list[list[int]], start: tuple[int, int],
        target: tuple[int, int],
        blocked: set[tuple[int, int]] | None = None
    ) -> tuple[int, int] | None:
        """
        Findet den naechsten Schritt auf dem kuerzesten
        Weg von start zu target im Grid.
        Verwendet eine Breitensuche (BFS), um den kuerzesten Weg zu finden.
        """
        if start == target:
            return start

        blocked = blocked or set()
        rows, cols = len(grid), len(grid[0])
        visited = {start}
        parent: dict[tuple[int, int], tuple[int, int]] = {}
        queue = deque([start])
        found = False

        while queue:
            current = queue.popleft()
            if current == target:
                found = True
                break
            row, col = current
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                neighbor = (row + dr, col + dc)
                nr, nc = neighbor
                if (
                    0 <= nr < rows
                    and 0 <= nc < cols
                    and grid[nr][nc] == 0
                    and neighbor not in visited
                    and (neighbor == target or neighbor not in blocked)
                ):
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        if not found:
            return None  # Kein Weg gefunden

        step = target
        while parent[step] != start:
            step = parent[step]
        return step

    # MARK: move_ghost_towards_player
    @classmethod
    def move_ghost_towards_player(
        cls,
        gamestate: GameState,
        ghost: Ghost,
        GHOST_CHASE_CHANCE: float,
        blocked: set[tuple[int, int]] | None = None
    ) -> None:
        if cls.is_edible(gamestate):
            ghost.row, ghost.col = cls._flee_step(gamestate, ghost, blocked)
            return
        if random.random() < GHOST_CHASE_CHANCE:
            next_step = cls.bfs_next_step(
                gamestate.grid, (ghost.row, ghost.col),
                (gamestate.player_row, gamestate.player_col), blocked)
            if next_step:
                ghost.row, ghost.col = next_step
                return
        ghost.row, ghost.col = cls._random_valid_step(
            gamestate, ghost, blocked)
