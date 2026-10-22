"""ReAct 循环与四条安全阀的测试。

用「脚本化决策者」替代大模型，循环逻辑可以完全离线验证。
"""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from app.react.agent import ReActAgent
from app.react.reasoner import RuleBasedReasoner
from app.react.types import StepDecision
from app.store.memory import DEMO_COURSEWARE, store
from app.tools.box import ToolBox


class ScriptedReasoner:
    """按预设脚本依次返回决策；用完后重复最后一条。"""

    def __init__(self, decisions: list[StepDecision]) -> None:
        self.decisions = decisions
        self.calls = 0

    def decide(self, **_: object) -> StepDecision:
        idx = min(self.calls, len(self.decisions) - 1)
        self.calls += 1
        return self.decisions[idx]


@pytest.fixture(autouse=True)
def _seed():
    store.clear()
    store.add_courseware(1, "高等数学 · 极限", DEMO_COURSEWARE)
    yield
    store.clear()


def _agent(reasoner, max_steps: int = 8) -> ReActAgent:
    return ReActAgent(
        toolbox=ToolBox(user_id=1, session_id="sess-1"),
        reasoner=reasoner,
        max_steps=max_steps,
    )


# ---------------- 正常流程 ----------------
def test_rule_reasoner_completes_full_chain():
    result = _agent(RuleBasedReasoner()).run("高数极限怎么复习")

    assert result.finished is True
    actions = [t.action for t in result.trace if t.action]
    assert actions == ["search_courseware", "generate_exercises", "archive_note"]
    assert len(result.trace) == 4  # 3 次工具 + 1 次收尾
    assert "课件里的依据" in result.answer
    assert "配套练习" in result.answer


def test_rule_reasoner_adds_plan_when_exam_date_given():
    exam = (date.today() + timedelta(days=14)).isoformat()
    result = _agent(RuleBasedReasoner()).run(f"我 {exam} 要考试，帮我安排复习计划")

    actions = [t.action for t in result.trace if t.action]
    assert "generate_study_plan" in actions
    assert result.finished is True
    assert "备考计划" in result.answer


# ---------------- 安全阀 1：轮次上限 ----------------
def test_stops_at_max_steps():
    reasoner = ScriptedReasoner(
        [StepDecision(thought="一直检索", action="search_courseware", action_input={"keyword": "极限"})]
    )
    result = _agent(reasoner, max_steps=1).run("极限")

    assert result.finished is False
    assert len(result.trace) == 1
    assert "最大思考轮次" in result.answer


# ---------------- 安全阀 2：重复调用 ----------------
def test_aborts_on_repeated_identical_action():
    same = StepDecision(thought="重复", action="search_courseware", action_input={"keyword": "极限"})
    result = _agent(ScriptedReasoner([same, same, same])).run("极限")

    assert result.finished is False
    assert "重复调用" in result.answer
    assert len(result.trace) == 2


# ---------------- 安全阀 3：工具异常 ----------------
def test_unknown_tool_becomes_observation():
    reasoner = ScriptedReasoner(
        [
            StepDecision(thought="调一个不存在的工具", action="no_such_tool"),
            StepDecision(thought="收尾", final_answer="好的"),
        ]
    )
    result = _agent(reasoner).run("测试")

    assert result.finished is True
    assert "工具调用失败" in result.trace[0].observation
    assert "不存在名为 no_such_tool 的工具" in result.trace[0].observation


def test_wrong_arguments_become_observation():
    reasoner = ScriptedReasoner(
        [
            StepDecision(thought="少传参数", action="archive_note", action_input={}),
            StepDecision(thought="收尾", final_answer="好的"),
        ]
    )
    result = _agent(reasoner).run("测试")

    assert "参数错误" in result.trace[0].observation


# ---------------- 其它 ----------------
def test_courseware_id_is_auto_injected():
    """请求里指定了课件，检索时应自动限定范围，而不是让模型自己填。"""

    class SpyReasoner:
        def decide(self, **_: object) -> StepDecision:
            return StepDecision(thought="检索", action="search_courseware", action_input={"keyword": "极限"})

    box = ToolBox(user_id=1, session_id="s", courseware_id=999)
    agent = ReActAgent(toolbox=box, reasoner=SpyReasoner(), max_steps=1)
    result = agent.run("极限")

    # 课件 999 不存在 → 检索不到，说明 courseware_id 确实被带进参数了
    assert "未在课件中找到" in result.trace[0].observation


def test_trace_steps_are_numbered_from_one():
    result = _agent(RuleBasedReasoner()).run("高数极限怎么复习")
    assert [t.step for t in result.trace] == list(range(1, len(result.trace) + 1))
