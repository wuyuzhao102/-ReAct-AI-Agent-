"""工具层测试。"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.store.memory import InMemoryStore, store
from app.tools.archive import make_archive_tool
from app.tools.base import ToolError, ToolRegistry
from app.tools.box import ToolBox
from app.tools.courseware import SEARCH_COURSEWARE
from app.tools.exercise import GENERATE_EXERCISES
from app.tools.plan import GENERATE_STUDY_PLAN

DOC = """第一章 极限

1.1 极限的定义
设函数 f(x) 在点 x0 的某个去心邻域内有定义，当 x 无限趋近于 x0 时，函数值无限趋近于常数 A，则称 A 为极限。

1.2 两个重要极限
lim(x→0) sin x / x = 1；lim(x→∞) (1 + 1/x)^x = e。

1.3 洛必达法则
对于 0/0 型未定式，若分子分母可导且分母导数不为零，则可用洛必达法则。"""


@pytest.fixture(autouse=True)
def _fresh_store():
    store.clear()
    store.add_courseware(1, "高等数学 · 极限", DOC)
    yield
    store.clear()


# ---------------- 注册表 ----------------
def test_registry_raises_for_unknown_tool():
    registry = ToolRegistry()
    with pytest.raises(ToolError):
        registry.get("nope")


def test_toolbox_registers_four_tools():
    box = ToolBox(user_id=1, session_id="s")
    assert len(box.names) == 4
    assert set(box.names) == {
        "search_courseware",
        "generate_exercises",
        "generate_study_plan",
        "archive_note",
    }


def test_registry_describe_lists_tools_with_required_args():
    box = ToolBox(user_id=1, session_id="s")
    text = box.describe()
    assert "search_courseware(keyword)" in text
    assert "archive_note(title, content)" in text


# ---------------- 检索 ----------------
def test_search_returns_courseware_paragraph():
    out = SEARCH_COURSEWARE.run(keyword="极限")
    assert "课件原文" in out
    assert "当 x 无限趋近于 x0" in out


def test_search_miss_returns_hint():
    out = SEARCH_COURSEWARE.run(keyword="量子力学")
    assert "未在课件中找到" in out


def test_search_limits_to_courseware_id():
    out = SEARCH_COURSEWARE.run(keyword="极限", courseware_id=999)
    assert "未在课件中找到" in out


# ---------------- 出题 ----------------
def test_generate_exercises_produces_questions_and_answers():
    out = GENERATE_EXERCISES.run(context=DOC, count=2, difficulty="easy")
    assert out.startswith("## 练习题")
    assert "基础" in out
    assert out.count("参考答案") == 2


def test_generate_exercises_rejects_empty_context():
    assert "无法出题" in GENERATE_EXERCISES.run(context="")


def test_generate_exercises_ignores_retrieval_wrapper():
    """检索结果里的编号/书名号包装行不能被当成正文拿来出题。"""
    wrapped = (
        "找到以下课件原文（回答时请引用这里的依据）：\n\n"
        "【1】《高等数学 · 极限》· 课件 1\n"
        "第一个重要极限：lim(x→0) sin x / x = 1，这是课堂重点内容之一。\n"
    )
    out = GENERATE_EXERCISES.run(context=wrapped, count=1)
    assert "【1】" not in out
    assert "《高等数学" not in out
    assert "参考答案" in out


def test_generate_exercises_does_not_blank_out_text():
    """规则版按小节出简答题，不切词挖空，避免把词切坏。"""
    out = GENERATE_EXERCISES.run(context=DOC, count=3)
    assert "____" not in out
    assert "两个重要极限" in out


def test_generate_exercises_needs_enough_context():
    assert "无法生成题目" in GENERATE_EXERCISES.run(context="太短了", count=2)


# ---------------- 备考计划 ----------------
def test_study_plan_contains_phases():
    exam = (date.today() + timedelta(days=20)).isoformat()
    out = GENERATE_STUDY_PLAN.run(exam_date=exam, weak_points="洛必达法则,等价无穷小")
    assert "备考计划" in out
    assert "构建知识框架" in out
    assert "洛必达法则" in out


def test_study_plan_rejects_bad_date():
    assert "无法识别考试日期" in GENERATE_STUDY_PLAN.run(exam_date="下个月")


def test_study_plan_rejects_past_date():
    out = GENERATE_STUDY_PLAN.run(exam_date="2020-01-01")
    assert "已经过去" in out


# ---------------- 归档 ----------------
def test_archive_writes_note_to_store():
    tool = make_archive_tool(user_id=7, session_id="sess-1")
    out = tool.run(title="极限复习提纲", content="极限定义与两个重要极限")
    assert "已归档" in out
    notes = store.list_notes(7)
    assert len(notes) == 1
    assert notes[0].title == "极限复习提纲"
    # 只对本人可见
    assert store.list_notes(8) == []


def test_archive_rejects_empty_content():
    tool = make_archive_tool(user_id=7, session_id="s")
    assert "未归档" in tool.run(title="空", content="   ")


# ---------------- 检索分词 ----------------
def test_query_terms_splits_chinese_into_bigrams():
    from app.store.memory import query_terms

    terms = query_terms("下周要考高数极限")
    assert "极限" in terms
    assert "高数" in terms


def test_store_is_isolated_per_instance():
    other = InMemoryStore()
    assert other.list_courseware() == []
