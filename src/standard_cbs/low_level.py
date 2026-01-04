from __future__ import annotations

import heapq
from collections import defaultdict
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .map_grid import GridMap
from .models import Agent, Constraint, Path, Position


class NoPathError(RuntimeError):
    """在给定约束下找不到路径。"""


def build_constraint_tables(constraints: Iterable[Constraint], agent: str) -> Tuple[
    Dict[int, Set[Position]],
    Dict[int, Set[Tuple[Position, Position]]],
    Dict[int, Set[Position]],
    Dict[int, Set[Tuple[Position, Position]]],
]:
    vertex_blockers: Dict[int, Set[Position]] = defaultdict(set)
    edge_blockers: Dict[int, Set[Tuple[Position, Position]]] = defaultdict(set)
    vertex_required: Dict[int, Set[Position]] = defaultdict(set)
    edge_required: Dict[int, Set[Tuple[Position, Position]]] = defaultdict(set)

    for constraint in constraints:
        if constraint.agent != agent:
            continue
        if constraint.is_positive:
            if constraint.next_position is None:
                vertex_required[constraint.time].add(constraint.position)
            else:
                edge_required[constraint.time].add((constraint.position, constraint.next_position))
        else:
            if constraint.next_position is None:
                vertex_blockers[constraint.time].add(constraint.position)
            else:
                edge_blockers[constraint.time].add((constraint.position, constraint.next_position))

    return vertex_blockers, edge_blockers, vertex_required, edge_required


def satisfies_positive_constraints(
    time: int,
    position: Position,
    next_position: Optional[Position],
    vertex_required: Dict[int, Set[Position]],
    edge_required: Dict[int, Set[Tuple[Position, Position]]],
) -> bool:
    if time in vertex_required and position not in vertex_required[time]:
        return False
    if next_position is not None and time in edge_required:
        return (position, next_position) in edge_required[time]
    return True


def wait_move(position: Position) -> Position:
    return position


def a_star_search(
    grid_map: GridMap,
    agent: Agent,
    constraints: Iterable[Constraint],
    safety_margin: int = 16,
) -> Path:
    """在 GridMap 上执行带约束的 A* 搜索。"""

    vertex_blockers, edge_blockers, vertex_required, edge_required = build_constraint_tables(constraints, agent.name)

    max_constraint_time = 0
    if vertex_blockers:
        max_constraint_time = max(max_constraint_time, max(vertex_blockers.keys()))
    if edge_blockers:
        max_constraint_time = max(max_constraint_time, max(edge_blockers.keys()))
    if vertex_required:
        max_constraint_time = max(max_constraint_time, max(vertex_required.keys()))
    if edge_required:
        max_constraint_time = max(max_constraint_time, max(edge_required.keys()))

    def is_blocked(position: Position, nxt: Position, time: int) -> bool:
        if time in vertex_blockers and nxt in vertex_blockers[time]:
            return True
        if time in edge_blockers and (position, nxt) in edge_blockers[time]:
            return True
        return False

    start = agent.start
    goal = agent.goal

    open_list: List[Tuple[int, int, Position]] = []
    heapq.heappush(open_list, (grid_map.heuristic(start, goal), 0, start))

    came_from: Dict[Tuple[Position, int], Tuple[Position, int]] = {}
    g_cost: Dict[Tuple[Position, int], int] = {(start, 0): 0}

    visited_goal_times: Set[int] = set()
    upper_time_bound = max_constraint_time + grid_map.heuristic(start, goal) + safety_margin

    while open_list:
        f_score, time, current = heapq.heappop(open_list)
        current_key = (current, time)

        if current == goal and time >= max_constraint_time:
            if satisfies_positive_constraints(time, current, None, vertex_required, edge_required):
                visited_goal_times.add(time)
                # 允许直接返回最早满足条件的路径
                return reconstruct_path(came_from, current_key)

        if time > upper_time_bound:
            continue

        for neighbor in list(grid_map.neighbors(current)) + [wait_move(current)]:
            next_time = time + 1
            transition = (current, neighbor)

            if next_time in vertex_required and neighbor not in vertex_required[next_time]:
                continue
            if next_time in edge_required and transition not in edge_required[next_time]:
                continue

            if is_blocked(current, neighbor, next_time):
                continue

            next_key = (neighbor, next_time)
            new_cost = g_cost[current_key] + 1

            if next_key not in g_cost or new_cost < g_cost[next_key]:
                g_cost[next_key] = new_cost
                priority = new_cost + grid_map.heuristic(neighbor, goal)
                heapq.heappush(open_list, (priority, next_time, neighbor))
                came_from[next_key] = current_key

    raise NoPathError(f"无法为智能体 {agent.name} 找到满足约束的路径。")


def reconstruct_path(
    came_from: Dict[Tuple[Position, int], Tuple[Position, int]],
    goal_key: Tuple[Position, int],
) -> Path:
    position, time = goal_key
    path: List[Position] = [position]
    current_key = goal_key
    while current_key in came_from:
        current_key = came_from[current_key]
        path.append(current_key[0])
    path.reverse()
    return path


def extend_path(path: Path, length: int) -> Path:
    if not path:
        return path
    extended = list(path)
    last = path[-1]
    while len(extended) < length:
        extended.append(last)
    return extended





