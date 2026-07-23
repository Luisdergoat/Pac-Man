#!/usr/bin/env python3
"""
Docstring for cell
"""

from __future__ import annotations


class Cell:
    """
    Class representing a cell in the maze.
    """
    def __init__(self, x: int, y: int) -> None:
        self.x: int = x
        self.y: int = y
        self.wall: int = 15
        self.visited: bool = False
        self.frame: bool = False
        self.solve_need: bool = False

    def __repr__(self) -> str:
        return (
            "Cell("
            f"x={self.x}, "
            f"y={self.y}, "
            f"is_visited={self.visited}"
            ")"
        )

    def mark_visited(self) -> None:
        self.visited = True

    def unvisit(self) -> None:
        self.visited = False

    def is_visited(self) -> bool:
        return self.visited

    def mark_need_to_solve(self) -> None:
        self.solve_need = True

    def unmark_need_to_solve(self) -> None:
        self.solve_need = False

    def get_x(self) -> int:
        return self.x

    def get_y(self) -> int:
        return self.y

    def set_wall(self, direction: int) -> None:
        self.wall = self.wall & direction

    def set_wall_value(self, wall: int) -> None:
        self.wall = wall

    def get_wall(self) -> int:
        return self.wall

    def mark_as_frame(self) -> None:
        self.frame = True
