"""工具 4：笔记归档。

把本次会话产出的复习资料写进个人学习档案。
注意 userId 由 ToolBox 绑定，**不作为工具参数暴露给大模型**（否则模型可能写别人的档案）。
"""

from __future__ import annotations

from app.tools.base import Tool, tool


def make_archive_tool(user_id: int, session_id: str) -> Tool:
    @tool(
        name="archive_note",
        description="把本次生成的复习提纲、练习题等资料归档到学生的个人学习档案，返回笔记编号。",
        parameters={
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "笔记标题，例如「高数极限复习提纲」"},
                "content": {"type": "string", "description": "要归档的 Markdown 内容"},
            },
            "required": ["title", "content"],
        },
    )
    def archive_note(title: str, content: str) -> str:
        from app.store.memory import store  # 延迟导入，便于测试替换

        title = (title or "").strip() or "未命名笔记"
        content = (content or "").strip()
        if not content:
            return "内容为空，未归档。"

        note = store.add_note(user_id=user_id, title=title, content=content)
        return f"已归档：笔记 #{note.id}《{note.title}》（用户 {user_id} / 会话 {session_id}）"

    return archive_note
