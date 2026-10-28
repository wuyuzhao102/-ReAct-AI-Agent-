"""工具层：四个可被 ReAct 智能体调用的工具。

| 工具 | 作用 | 是否需要大模型 |
| :--- | :--- | :--- |
| 课件检索 | 在学生课件中检索知识点 | 否 |
| 习题生成 | 基于课件原文出题 | 规则版不需要 / LLM 版需要 |
| 备考计划 | 按考试日期排备考计划 | 否 |
| 笔记归档 | 归档到个人学习档案 | 否 |
"""

from app.tools.base import Tool, ToolError, ToolRegistry
from app.tools.box import ToolBox

__all__ = ["Tool", "ToolError", "ToolRegistry", "ToolBox"]
