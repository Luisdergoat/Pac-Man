from collections import deque
from typing import List, Tuple


# MARK: find_nearest_open_cell
def find_nearest_open_cell(grid: List[List[int]], row: int, col: int) -> Tuple[int, int]:
    """
    Findet die naechste begehbare Zelle (0) im Grid,
    beginnend von der Startposition.
    Verwendet eine Breitensuche (BFS), um die naechste offene Zelle zu finden.
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


# MARK: bfs_next_step
def bfs_next_step(
    grid: List[List[int]], start: Tuple[int, int],
    target: Tuple[int, int],
    blocked: set[Tuple[int, int]] = None
) -> Tuple[int, int]:
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
    parent: Dict[Tuple[int, int], Tuple[int, int]] = {}
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
