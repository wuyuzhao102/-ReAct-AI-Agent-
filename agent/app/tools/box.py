"""把四个工具按「谁在问」组装成一套可用的工具箱。

为什么需要 ToolBox：
    四个工具里有需要用户上下文的（归档笔记要写进"你的"档案），
    这类信息绝不能交给大模型决定，所以在构造时绑定死。
"""

from __future__ import annotations

from app.tools.archive import make_archive_tool
from app.tools.base import ToolRegistry
from app.tools.courseware import SEARCH_COURSEWARE
from app.tools.exercise import GENERATE_EXERCISES
from app.tools.plan import GENERATE_STUDY_PLAN


class ToolBox:
    def __init__(
        self,
        user_id: int,
        session_id: str,
        courseware_id: int | None = None,
    ) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.courseware_id = courseware_id

        self.registry = ToolRegistry()
        self.registry.register(
            SEARCH_COURSEWARE,
            GENERATE_EXERCISES,
            GENERATE_STUDY_PLAN,
            make_archive_tool(user_id, session_id),
        )

    @property
    def names(self) -> list[str]:
        return self.registry.names()

    def describe(self) -> str:
        return self.registry.describe()
