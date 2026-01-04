from __future__ import annotations

from typing import Iterable, Optional

from .models import CBSNode, Conflict


class RLPolicyHook:
    """
    强化学习策略接口占位。

    若需要引入 RL，用于高层节点/冲突选择，可继承并实现以下方法。
    """

    def select_node(self, open_list: Iterable[CBSNode]) -> Optional[CBSNode]:
        """
        从开放列表中选择一个节点进行扩展。默认返回 None，表示使用算法内置策略。
        """
        return None

    def select_conflict(self, conflicts: Iterable[Conflict]) -> Optional[Conflict]:
        """
        从冲突集合中选择一个冲突用于分支。默认返回 None，表示采用默认冲突选择策略。
        """
        return None





