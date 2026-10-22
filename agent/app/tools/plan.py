"""工具 3：备考计划生成。

纯日期计算 + 阶段划分，结果确定、可测试，不依赖大模型。
接入 LLM 后可以让模型根据薄弱点细化每日任务，这里保留为骨架与兜底。
"""

from __future__ import annotations

from datetime import date, datetime

from app.tools.base import tool

DATE_FORMATS = ("%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d", "%Y年%m月%d日")

PHASES = [
    ("构建知识框架", 0.40, "通读课件，整理公式与定义，形成章节骨架"),
    ("专题强化", 0.30, "按薄弱点做专项练习，错题即时归因"),
    ("真题模拟", 0.20, "限时套卷，训练速度与取舍"),
    ("查漏补缺", 0.10, "只看错题本与高频考点，保持手感"),
]


def _parse_date(text: str) -> date | None:
    text = (text or "").strip()
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


@tool(
    name="generate_study_plan",
    description="根据考试日期和薄弱知识点，生成按天划分的备考计划。",
    parameters={
        "type": "object",
        "properties": {
            "exam_date": {
                "type": "string",
                "description": "考试日期，格式 YYYY-MM-DD，例如 2026-12-20",
            },
            "weak_points": {
                "type": "string",
                "description": "薄弱知识点，逗号分隔，例如「洛必达法则,等价无穷小」",
            },
            "daily_minutes": {
                "type": "integer",
                "description": "每天可投入的分钟数，默认 90",
                "default": 90,
            },
        },
        "required": ["exam_date"],
    },
)
def generate_study_plan(
    exam_date: str, weak_points: str = "", daily_minutes: int = 90
) -> str:
    exam = _parse_date(exam_date)
    if exam is None:
        return f"无法识别考试日期「{exam_date}」，请使用 YYYY-MM-DD 格式。"

    today = date.today()
    if exam < today:
        return f"考试日期 {exam} 已经过去了，请确认是否填错年份。"

    total_days = (exam - today).days + 1
    points = [p.strip() for p in (weak_points or "").replace("，", ",").split(",") if p.strip()]

    lines = [
        f"## 备考计划（今天 {today} → 考试 {exam}，共 {total_days} 天）",
        "",
        f"- 每日投入：约 {int(daily_minutes)} 分钟",
        f"- 薄弱点：{'、'.join(points) if points else '未指定，按章节顺序推进'}",
        "",
        "| 阶段 | 时间 | 天数 | 重点任务 |",
        "| :--- | :--- | :-: | :--- |",
    ]

    cursor = 0
    for name, ratio, task in PHASES:
        days = max(1, round(total_days * ratio))
        if cursor + days > total_days:
            days = max(0, total_days - cursor)
        if days == 0:
            continue
        start = today.toordinal() + cursor
        end = start + days - 1
        span = f"{date.fromordinal(start)} ~ {date.fromordinal(end)}"
        if points:
            task = f"{task}（重点关注：{'、'.join(points[:2])}）"
        lines.append(f"| {name} | {span} | {days} | {task} |")
        cursor += days

    lines += [
        "",
        "**每天的执行模板**",
        "1. 复盘昨天错题（10 min）",
        "2. 按阶段任务学习（70% 时间）",
        "3. 做 3~5 道对应练习，错题记入错题本（30% 时间）",
    ]
    return "\n".join(lines)


GENERATE_STUDY_PLAN = generate_study_plan
