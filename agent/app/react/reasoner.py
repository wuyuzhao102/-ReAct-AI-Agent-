"""ReAct 的"决策者"。

接口只有一个方法：根据问题 + 已有轨迹，决定下一步是「调工具」还是「给最终答案」。

两种实现：
· RuleBasedReasoner —— 不依赖大模型，按固定脚本推进；开发期兜底、也用于测试。
· (下一步) LLMReasoner —— 把工具清单塞进 prompt，让大模型输出 Thought/Action。

这样拆分的好处：循环逻辑与模型调用解耦，测试不需要网络和 API Key。
"""

from __future__ import annotations

import re
from typing import Protocol

from app.react.types import StepDecision
from app.schemas import TraceStep
from app.tools.box import ToolBox

_DATE_RE = re.compile(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})")


class Reasoner(Protocol):
    def decide(
        self,
        *,
        step: int,
        question: str,
        trace: list[TraceStep],
        toolbox: ToolBox,
    ) -> StepDecision: ...


def _last_observation(trace: list[TraceStep]) -> str:
    for item in reversed(trace):
        if item.observation:
            return item.observation
    return ""


class RuleBasedReasoner:
    """规则兜底：检索 → 出题 →（有日期则）排计划 → 归档 → 总结。

    它不做真正的"推理"，但把 ReAct 的每一环都走一遍，
    保证 Java 层/前端在不配 API Key 的情况下也能联调。
    """

    def decide(
        self,
        *,
        step: int,
        question: str,
        trace: list[TraceStep],
        toolbox: ToolBox,
    ) -> StepDecision:
        done = {t.action for t in trace if t.action}
        observation = _last_observation(trace)

        if "课件检索" not in done:
            return StepDecision(
                thought="用户问的是课程内容，先检索他自己的课件，拿到原文再作答。",
                action="课件检索",
                action_input={"keyword": question},
            )

        if "习题生成" not in done:
            return StepDecision(
                thought="已拿到课件原文，基于它出一组配套练习。",
                action="习题生成",
                action_input={"context": observation, "count": 3, "difficulty": "medium"},
            )

        exam_date = self._extract_date(question)
        # 只要提到考试日期，就补一份倒排计划
        if exam_date is not None and "备考计划" not in done:
            return StepDecision(
                thought=f"用户提到了考试时间 {exam_date}，补一份倒排复习计划。",
                action="备考计划",
                action_input={"exam_date": exam_date, "weak_points": question},
            )

        if "笔记归档" not in done:
            return StepDecision(
                thought="资料齐了，存进个人学习档案，方便考前回看。",
                action="笔记归档",
                action_input={
                    "title": f"复习资料：{question[:20]}",
                    "content": self._collect_content(trace),
                },
            )

        return StepDecision(
            thought="检索、出题、归档都完成了，整理成最终回答。",
            final_answer=self._final_answer(question, trace),
        )

    # ---------------- 内部工具 ----------------
    @staticmethod
    def _extract_date(text: str) -> str | None:
        m = _DATE_RE.search(text)
        if not m:
            return None
        y, mo, d = m.groups()
        return f"{y}-{int(mo):02d}-{int(d):02d}"

    @staticmethod
    def _collect_content(trace: list[TraceStep]) -> str:
        parts = [t.observation for t in trace if t.observation and len(t.observation) > 20]
        return "\n\n---\n\n".join(parts)

    def _final_answer(self, question: str, trace: list[TraceStep]) -> str:
        search_obs = next(
            (t.observation for t in trace if t.action == "课件检索"), ""
        )
        exercise_obs = next(
            (t.observation for t in trace if t.action == "习题生成"), ""
        )
        plan_obs = next(
            (t.observation for t in trace if t.action == "备考计划"), ""
        )
        archive_obs = next(
            (t.observation for t in trace if t.action == "笔记归档"), ""
        )

        blocks = [f"## 关于「{question[:40]}」的复习资料", ""]

        if search_obs:
            blocks += ["### 一、课件里的依据", search_obs, ""]
        if exercise_obs:
            blocks += ["### 二、配套练习", exercise_obs, ""]
        if plan_obs:
            blocks += ["### 三、备考计划", plan_obs, ""]
        if archive_obs:
            blocks += ["### 四、归档", f"> {archive_obs}", ""]

        blocks.append(
            "> 🤖 当前由**规则引擎**驱动（未接入大模型）。接入后会基于课件原文生成"
            "更完整的讲解、解析与个性化建议。"
        )
        return "\n".join(blocks)
