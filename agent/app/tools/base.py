"""工具的基础设施：工具定义、注册表、装饰器。

设计要点：
- 每个工具 = 名字 + 描述 + 参数 JSON Schema + 可执行函数
- 描述和 Schema 是给大模型看的（它靠这些决定调不调、传什么参数）
- 四个工具由 ToolBox 绑定用户上下文后注册，避免把 userId 暴露给模型（安全问题）
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable


class ToolError(Exception):
    """工具执行失败。Agent 会把它转成一条 Observation 反馈给模型，而不是直接 500。"""


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    func: Callable[..., str]

    def run(self, **kwargs: Any) -> str:
        try:
            return self.func(**kwargs)
        except ToolError:
            raise
        except TypeError as exc:  # 参数名/类型不对
            raise ToolError(f"参数错误：{exc}") from exc
        except Exception as exc:  # noqa: BLE001 工具内部异常统一转为可观察的错误
            raise ToolError(f"工具内部错误：{exc}") from exc


def tool(name: str, description: str, parameters: dict[str, Any]) -> Callable[[Callable[..., str]], Tool]:
    """把普通函数装饰成 Tool。"""

    def deco(func: Callable[..., str]) -> Tool:
        return Tool(name=name, description=description, parameters=parameters, func=func)

    return deco


class ToolRegistry:
    """工具注册表。"""

    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, *items: Tool) -> None:
        for item in items:
            if item.name in self._tools:
                raise ValueError(f"工具重名：{item.name}")
            self._tools[item.name] = item

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolError(f"不存在名为 {name} 的工具") from exc

    def names(self) -> list[str]:
        return list(self._tools)

    def all(self) -> Iterable[Tool]:
        return self._tools.values()

    def describe(self) -> str:
        """生成给大模型看的工具清单（后续接 LLM 时塞进 system prompt）。"""
        lines = []
        for t in self._tools.values():
            required = ", ".join(t.parameters.get("required", []))
            lines.append(f"- {t.name}({required})：{t.description}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._tools)

    def __contains__(self, name: object) -> bool:
        return name in self._tools
