from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

Position = Tuple[int, int]


@dataclass(frozen=True)
class Agent:
    """多智能体规划中的单个智能体描述。"""

    name: str
    start: Position
    goal: Position


@dataclass(frozen=True)
class Constraint:
    """CBS 约束，支持顶点和边两种形式。"""

    agent: str
    time: int
    position: Position
    next_position: Optional[Position] = None
    is_positive: bool = False

    def matches(self, agent: str, time: int, position: Position, next_position: Optional[Position]) -> bool:
        if agent != self.agent:
            return False
        if time != self.time:
            return False
        if self.next_position is None:
            return position == self.position
        return position == self.position and next_position == self.next_position


@dataclass(frozen=True)
class Conflict:
    """描述两个智能体之间的冲突。"""

    agent1: str
    agent2: str
    time: int
    position: Position
    next_position: Optional[Position] = None
    conflict_type: str = "vertex"  # vertex 或 edge


Path = List[Position]


@dataclass
class Solution:
    """保存求解结果。"""

    paths: Dict[str, Path] = field(default_factory=dict)
    cost: int = 0

    def makespan(self) -> int:
        return max((len(path) for path in self.paths.values()), default=0) - 1

    def as_dict(self) -> Dict[str, List[List[int]]]:
        return {agent: [list(pos) for pos in path] for agent, path in self.paths.items()}


@dataclass
class ProblemInstance:
    """包含地图与智能体集合的信息。"""

    agents: List[Agent]

    def agent_by_name(self, name: str) -> Agent:
        for agent in self.agents:
            if agent.name == name:
                return agent
        raise KeyError(f"Agent '{name}' not found.")

    def names(self) -> Iterable[str]:
        return (agent.name for agent in self.agents)


@dataclass(order=True)
class CBSNode:
    """CBS 高层搜索节点。"""

    priority: Tuple[int, int]  # (总代价, 冲突数)
    id: int
    constraints: List[Constraint] = field(default_factory=list, compare=False)
    paths: Dict[str, Path] = field(default_factory=dict, compare=False)
    conflicts: List[Conflict] = field(default_factory=list, compare=False)
    cost: int = field(default=0, compare=False)

    def add_constraint(self, constraint: Constraint) -> None:
        self.constraints.append(constraint)

    def clone_with_constraint(self, constraint: Constraint, node_id: int) -> "CBSNode":
        new_node = CBSNode(
            priority=self.priority,
            id=node_id,
            constraints=list(self.constraints),
            paths={agent: list(path) for agent, path in self.paths.items()},
            conflicts=list(self.conflicts),
            cost=self.cost,
        )
        new_node.constraints.append(constraint)
        return new_node





