"""ReAct 循环本体：Thought → Action → Observation，直到给出最终答案。

四条安全阀（对应项目文档「难点 2：Agent 无限循环」）：
1. 最大轮次上限 max_steps，超出强制收敛；
2. 相同「工具 + 参数」重复调用即打断；
3. 工具异常转为 Observation，不让整个请求 500；
4. 单步超时由上层（Java/网关）控制，这里只保证一定会返回。
"""

from __future__ import annotations

import json

from app.react.reasoner import Reasoner
from app.react.types import StepDecision
from app.schemas import ChatResponse, TraceStep
from app.tools.base import ToolError
from app.tools.box import ToolBox


class ReActAgent:
    def __init__(self, toolbox: ToolBox, reasoner: Reasoner, max_steps: int = 8) -> None:
        self.toolbox = toolbox
        self.reasoner = reasoner
        self.max_steps = max(1, int(max_steps))

    def run(self, question: str) -> ChatResponse:
        trace: list[TraceStep] = []
        seen: set[str] = set()

        for step in range(1, self.max_steps + 1):
            decision = self.reasoner.decide(
                step=step, question=question, trace=trace, toolbox=self.toolbox
            )

            # 结束：模型给出了最终答案
            if decision.is_final:
                trace.append(TraceStep(step=step, thought=decision.thought))
                return ChatResponse(
                    answer=decision.final_answer or "", trace=trace, finished=True
                )

            observation = self._execute(decision)
            trace.append(
                TraceStep(
                    step=step,
                    thought=decision.thought,
                    action=decision.action,
                    observation=observation,
                )
            )

            # 安全阀 2：同一个动作 + 同一套参数重复出现，说明卡住了
            key = self._signature(decision)
            if key in seen:
                return self._abort(
                    "检测到重复调用同一个工具，已中止以避免死循环。", trace
                )
            seen.add(key)

        # 安全阀 1：轮次用尽
        return self._abort(f"已达到最大思考轮次（{self.max_steps} 轮）。", trace)

    # ---------------- 内部方法 ----------------
    def _execute(self, decision: StepDecision) -> str:
        if not decision.action:
            return "（本步没有选择任何工具）"

        payload = dict(decision.action_input or {})
        # 请求里指定了课件时，自动补进检索参数（模型不需要知道这件事）
        if (
            decision.action == "search_courseware"
            and self.toolbox.courseware_id is not None
            and payload.get("courseware_id") is None
        ):
            payload["courseware_id"] = self.toolbox.courseware_id

        try:
            tool = self.toolbox.registry.get(decision.action)
            return tool.run(**payload)
        except ToolError as exc:  # 安全阀 3：错误也作为观察结果反馈
            return f"工具调用失败：{exc}"

    @staticmethod
    def _signature(decision: StepDecision) -> str:
        body = json.dumps(decision.action_input or {}, ensure_ascii=False, sort_keys=True)
        return f"{decision.action}::{body}"

    @staticmethod
    def _abort(reason: str, trace: list[TraceStep]) -> ChatResponse:
        collected = [t.observation for t in trace if t.observation and len(t.observation) > 20]
        body = "\n\n---\n\n".join(collected) if collected else "（没有可用的中间结果）"
        answer = f"### ⚠️ 本次回答未完成\n\n{reason}\n\n以下是已经拿到的内容：\n\n{body}"
        return ChatResponse(answer=answer, trace=trace, finished=False)
