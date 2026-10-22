"""工具 2：习题生成（规则版）。

为什么不做"挖空填空"：
    没有中文分词器的前提下，按 n-gram 挑出来的词会横跨词边界
    （例如把「两个重要极限」挖成「两____限」），题面直接变成错误文本。
    所以规则版改为**按课件小节出简答题**：题目问"这一节讲了什么"，
    参考答案就是课件原文 —— 不改编原文，也就不会出错的题。

接入大模型后，仍保留这个规则版作为兜底（断网/没配 Key 时也能出题）。
"""

from __future__ import annotations

import re

from app.tools.base import tool

# 检索工具返回的"包装行"，出题时要剔除
_WRAPPER_LINE = re.compile(r"^(【\d+】|找到以下课件原文|回答时请引用)")
_TITLE_LINE = re.compile(r"^《.*》")

# 小节标题特征：1.2 / 一、 / 第一章 / 第 3 部分
_HEADING_PREFIX = re.compile(
    r"^(\d+(\.\d+)*\s*|[一二三四五六七八九十]+[、.．]|第\s*[一二三四五六七八九十\d]+\s*[章节部分讲])"
)

DIFFICULTY_LABEL = {"easy": "基础", "medium": "中等", "hard": "较难"}
_ANSWER_MAX = 160


def _strip_retrieval_wrapper(context: str) -> str:
    """去掉检索结果里的编号、书名号标题和提示语，只留课件正文。"""
    kept: list[str] = []
    for line in context.split("\n"):
        stripped = line.strip()
        if not stripped:
            kept.append("")
            continue
        if _WRAPPER_LINE.match(stripped) or _TITLE_LINE.match(stripped) or stripped.startswith("#"):
            continue
        kept.append(stripped)
    return "\n".join(kept)


def _is_heading(line: str) -> bool:
    """短、不带句末标点 → 认为是一节的小标题。"""
    if len(line) > 24 or line.endswith(("。", "；", "！", "？")):
        return False
    return bool(_HEADING_PREFIX.match(line)) or len(line) <= 14


def _split_sections(text: str) -> list[tuple[str, str]]:
    """按小标题切分：[(标题, 正文), ...]。"""
    sections: list[tuple[str, str]] = []
    title = ""
    body: list[str] = []

    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if _is_heading(line):
            if body:
                sections.append((title or "本节", " ".join(body)))
            title, body = line, []
        else:
            body.append(line)
    if body:
        sections.append((title or "本节", " ".join(body)))

    return [(t, b) for t, b in sections if len(b) >= 20]


@tool(
    name="generate_exercises",
    description=(
        "基于给定的课件原文生成配套练习题与参考答案。"
        "调用前应先用 search_courseware 拿到可信的课件内容，把原文放进 context。"
    ),
    parameters={
        "type": "object",
        "properties": {
            "context": {"type": "string", "description": "课件原文（通常是上一步检索到的内容）"},
            "count": {"type": "integer", "description": "出题数量，默认 3", "default": 3},
            "difficulty": {
                "type": "string",
                "enum": ["easy", "medium", "hard"],
                "description": "难度，默认 medium",
                "default": "medium",
            },
        },
        "required": ["context"],
    },
)
def generate_exercises(context: str, count: int = 3, difficulty: str = "medium") -> str:
    context = _strip_retrieval_wrapper(context or "").strip()
    if not context:
        return "没有提供课件原文，无法出题。请先调用 search_courseware 取得内容。"

    try:
        count = max(1, min(int(count), 10))
    except (TypeError, ValueError):
        count = 3
    level = DIFFICULTY_LABEL.get(str(difficulty), "中等")

    sections = _split_sections(context)
    if not sections:
        return "课件原文内容过短或缺少小节标题，暂无法生成题目。"

    lines = [f"## 练习题（{level} · 共 {count} 题）", ""]
    for i in range(count):
        title, body = sections[i % len(sections)]
        answer = body if len(body) <= _ANSWER_MAX else body[:_ANSWER_MAX] + "…"
        lines += [
            f"**第 {i + 1} 题（简答）** 课件的「{title}」这一节讲了什么？请结合课件原文说明。",
            "",
            f"> 参考答案：{answer}",
            "",
        ]

    lines.append("> 📌 当前为**规则版出题**（不依赖大模型）；接入后在此补充计算题、变式题与详细解析。")
    return "\n".join(lines)


GENERATE_EXERCISES = generate_exercises
