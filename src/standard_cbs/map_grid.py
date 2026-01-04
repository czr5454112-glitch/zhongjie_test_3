from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Set, Tuple

from .models import Position


@dataclass(frozen=True)
class GridMap:
    """简单网格地图封装，使用 4-邻接移动。"""

    width: int
    height: int
    obstacles: Set[Position]

    @classmethod
    def from_matrix(cls, matrix: Sequence[Sequence[int]]) -> "GridMap":
        height = len(matrix)
        width = len(matrix[0]) if height else 0
        obstacles: Set[Position] = {
            (x, y) for y, row in enumerate(matrix) for x, cell in enumerate(row) if cell
        }
        return cls(width=width, height=height, obstacles=obstacles)

    @classmethod
    def from_json(cls, path: Path | str) -> "GridMap":
        with Path(path).open("r", encoding="utf-8") as file:
            data = json.load(file)
        width = data["width"]
        height = data["height"]
        obstacles = {(x, y) for x, y in data.get("obstacles", [])}
        return cls(width=width, height=height, obstacles=obstacles)

    def to_json(self, path: Path | str) -> None:
        payload = {
            "width": self.width,
            "height": self.height,
            "obstacles": sorted(list(self.obstacles)),
        }
        with Path(path).open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def in_bounds(self, pos: Position) -> bool:
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, pos: Position) -> bool:
        return pos not in self.obstacles

    def neighbors(self, pos: Position) -> Iterable[Position]:
        x, y = pos
        deltas: List[Tuple[int, int]] = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in deltas:
            nxt = (x + dx, y + dy)
            if self.in_bounds(nxt) and self.passable(nxt):
                yield nxt

    def heuristic(self, a: Position, b: Position) -> int:
        """曼哈顿距离启发式。"""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])





