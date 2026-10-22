"""工具 1：课件检索。

这是整个项目的"反幻觉"关键 —— 强制 Agent 先查学生自己的课件，
再基于原文作答，而不是凭模型记忆编造。
"""

from __future__ import annotations

from app.store.memory import store
from app.tools.base import tool


@tool(
    name="search_courseware",
    description=(
        "在学生上传的课件原文中检索知识点，返回匹配到的课件段落。"
        "凡是涉及课程内容的问题，必须先调用本工具取得原文依据，禁止凭记忆直接作答。"
    ),
    parameters={
        "type": "object",
        "properties": {
            "keyword": {
                "type": "string",
                "description": "检索关键词或整句疑问，例如「极限」「洛必达法则的适用条件」",
            },
            "courseware_id": {
                "type": "integer",
                "description": "只在某一份课件里检索；不传表示在该用户全部课件中检索",
            },
            "top_k": {
                "type": "integer",
                "description": "返回最多几个段落，默认 3",
                "default": 3,
            },
        },
        "required": ["keyword"],
    },
)
def search_courseware(
    keyword: str, courseware_id: int | None = None, top_k: int = 3
) -> str:
    keyword = (keyword or "").strip()
    if not keyword:
        return "检索关键词为空，请提供一个具体的知识点名称。"

    hits = store.search(keyword, courseware_id=courseware_id, top_k=int(top_k or 3))
    if not hits:
        return (
            f"未在课件中找到与「{keyword}」相关的内容。"
            "可能是该学生尚未上传对应课件，或关键词不匹配。"
        )

    blocks = []
    for i, hit in enumerate(hits, start=1):
        para = hit.paragraph
        if len(para) > 400:
            para = para[:400] + "…"
        blocks.append(f"【{i}】《{hit.courseware_title}》· 课件 {hit.courseware_id}\n{para}")

    return "找到以下课件原文（回答时请引用这里的依据）：\n\n" + "\n\n".join(blocks)


# 供 ToolBox 注册使用的别名
SEARCH_COURSEWARE = search_courseware
