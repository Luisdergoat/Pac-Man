from dataclasses import dataclass


@dataclass
class Ghost:
    row: int
    col: int
    color: str
    start_row: int = 0
    start_col: int = 0
