"""工具层：四个可被 ReAct 智能体调用的工具。

| 工具 | 作用 | 是否需要大模型 |
| :--- | :--- | :--- |
| search_courseware | 在学生课件中检索知识点 | 否 |
| generate_exercises | 基于课件原文出题 | 规则版不需要 / LLM 版需要 |
| generate_study_plan | 按考试日期排备考计划 | 否 |
| archive_note | 归档到个人学习档案 | 否 |
"""

from app.tools.base import Tool, ToolError, ToolRegistry
from app.tools.box import ToolBox

__all__ = ["Tool", "ToolError", "ToolRegistry", "ToolBox"]
