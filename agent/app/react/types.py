"""ReAct 循环的数据结构。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class StepDecision:
    """模型（或规则兜底）对「下一步做什么」的决定。"""

    thought: str
    action: str | None = None
    action_input: dict[str, Any] = field(default_factory=dict)
    final_answer: str | None = None

    @property
    def is_final(self) -> bool:
        return bool(self.final_answer)
