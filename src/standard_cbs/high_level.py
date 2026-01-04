from __future__ import annotations

import heapq
from dataclasses import replace
from typing import Dict, Iterable, List, Optional

from .low_level import NoPathError, a_star_search
from .map_grid import GridMap
from .models import Agent, CBSNode, Conflict, Constraint, Path, Position, ProblemInstance, Solution
from .rl_interface import RLPolicyHook


class CBS:
    """标准冲突基搜索（CBS）求解器。"""

    def __init__(self, grid_map: GridMap, rl_hook: Optional[RLPolicyHook] = None) -> None:
        self.grid_map = grid_map
        self.rl_hook = rl_hook or RLPolicyHook()
        self._node_counter = 0

    def solve(self, problem: ProblemInstance, max_iterations: int = 10000) -> Solution:
        root = CBSNode(priority=(0, 0), id=self._next_node_id())
        root.paths = {}
        root.constraints = []

        for agent in problem.agents:
            root.paths[agent.name] = self._plan_for_agent(agent, root.constraints)

        root.cost = compute_total_cost(root.paths)
        root.conflicts = detect_conflicts(root.paths)
        root.priority = (root.cost, len(root.conflicts))

        open_list: List[CBSNode] = [root]
        heapq.heapify(open_list)

        iterations = 0

        while open_list and iterations < max_iterations:
            node = self._pop_node(open_list)
            if node.conflicts:
                conflict = self._choose_conflict(node.conflicts)
                if conflict is None:
                    # 如果 RL 接口返回 None，则回退到最早冲突
                    conflict = node.conflicts[0]
            else:
                return Solution(paths=node.paths, cost=node.cost)

            for agent_name in [conflict.agent1, conflict.agent2]:
                constraint = build_constraint_from_conflict(conflict, agent_name)
                child = self._generate_child(node, constraint, agent_name, problem)
                if child is not None:
                    heapq.heappush(open_list, child)

            iterations += 1

        raise RuntimeError("CBS 搜索未能在迭代限制内找到可行解。")

    def _pop_node(self, open_list: List[CBSNode]) -> CBSNode:
        candidate = self.rl_hook.select_node(open_list)
        if candidate is not None:
            # 根据节点 id 定位并移除
            for idx, node in enumerate(open_list):
                if node.id == candidate.id:
                    open_list[idx] = open_list[-1]
                    open_list.pop()
                    heapq.heapify(open_list)
                    return node
        return heapq.heappop(open_list)

    def _choose_conflict(self, conflicts: Iterable[Conflict]) -> Optional[Conflict]:
        conflict = self.rl_hook.select_conflict(conflicts)
        if conflict is not None:
            return conflict

        sorted_conflicts = sorted(
            conflicts,
            key=lambda c: (c.time, 0 if c.conflict_type == "vertex" else 1),
        )
        return sorted_conflicts[0] if sorted_conflicts else None

    def _generate_child(
        self,
        node: CBSNode,
        constraint: Constraint,
        agent_name: str,
        problem: ProblemInstance,
    ) -> Optional[CBSNode]:
        child = CBSNode(
            priority=node.priority,
            id=self._next_node_id(),
            constraints=list(node.constraints) + [constraint],
            paths={name: list(path) for name, path in node.paths.items()},
            conflicts=[],
            cost=0,
        )

        agent = problem.agent_by_name(agent_name)

        try:
            child.paths[agent_name] = self._plan_for_agent(agent, child.constraints)
        except NoPathError:
            return None

        child.cost = compute_total_cost(child.paths)
        child.conflicts = detect_conflicts(child.paths)
        child.priority = (child.cost, len(child.conflicts))
        return child

    def _plan_for_agent(self, agent: Agent, constraints: List[Constraint]) -> Path:
        return a_star_search(self.grid_map, agent, constraints)

    def _next_node_id(self) -> int:
        self._node_counter += 1
        return self._node_counter


def detect_conflicts(paths: Dict[str, Path]) -> List[Conflict]:
    conflicts: List[Conflict] = []
    if not paths:
        return conflicts

    max_length = max(len(path) for path in paths.values())

    def position_at(path: Path, time: int) -> Position:
        if time < len(path):
            return path[time]
        return path[-1]

    for time in range(max_length):
        occupancy: Dict[tuple, str] = {}
        for agent_name, path in paths.items():
            pos = position_at(path, time)
            if pos in occupancy:
                conflicts.append(
                    Conflict(
                        agent1=occupancy[pos],
                        agent2=agent_name,
                        time=time,
                        position=pos,
                        conflict_type="vertex",
                    )
                )
            else:
                occupancy[pos] = agent_name

        # Edge conflicts
        if time + 1 >= max_length:
            continue
        for agent_a, path_a in paths.items():
            pos_a_curr = position_at(path_a, time)
            pos_a_next = position_at(path_a, time + 1)
            for agent_b, path_b in paths.items():
                if agent_a >= agent_b:
                    continue
                pos_b_curr = position_at(path_b, time)
                pos_b_next = position_at(path_b, time + 1)
                if pos_a_curr == pos_b_next and pos_b_curr == pos_a_next and pos_a_next != pos_a_curr:
                    conflicts.append(
                        Conflict(
                            agent1=agent_a,
                            agent2=agent_b,
                            time=time + 1,
                            position=pos_a_curr,
                            next_position=pos_a_next,
                            conflict_type="edge",
                        )
                    )
    return conflicts


def compute_total_cost(paths: Dict[str, Path]) -> int:
    return sum(max(len(path) - 1, 0) for path in paths.values())


def build_constraint_from_conflict(conflict: Conflict, agent_name: str) -> Constraint:
    if conflict.conflict_type == "vertex":
        return Constraint(
            agent=agent_name,
            time=conflict.time,
            position=conflict.position,
        )
    return Constraint(
        agent=agent_name,
        time=conflict.time,
        position=conflict.position,
        next_position=conflict.next_position,
    )

