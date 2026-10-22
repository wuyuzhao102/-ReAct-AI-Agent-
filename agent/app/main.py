"""FastAPI 入口。

启动（在 agent/ 目录下）：
    uvicorn app.main:app --reload --port 8000
    # 或者 python -m app.main

接口：
    GET  /health       健康检查
    POST /agent/chat   ReAct 对话（当前为骨架占位，下一步接入循环）
"""

from fastapi import FastAPI

from app.config import get_settings
from app.schemas import ChatRequest, ChatResponse, TraceStep

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 ReAct 的课程学习助手 · 智能体服务",
)


@app.get("/", tags=["meta"])
def root() -> dict:
    """根路径，方便浏览器直接确认服务活着。"""
    return {
        "service": "coursemate-agent",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    """健康检查。

    注意：只回报"是否配置了 Key"，不返回 Key 本身，避免泄露。
    """
    return {
        "status": "ok",
        "env": settings.app_env,
        "llm_configured": settings.llm_configured,
        "llm_model": settings.llm_model,
        "max_react_steps": settings.max_react_steps,
    }


@app.post("/agent/chat", response_model=ChatResponse, tags=["agent"])
def chat(request: ChatRequest) -> ChatResponse:
    """ReAct 对话接口（骨架版）。

    ⚠️ 当前为占位实现：只把请求回显成 Markdown，不做任何推理。
       下一步会把这里替换成真正的 ReAct 循环：
       Thought → Action(工具) → Observation → ... → Final Answer
    """
    trace = [
        TraceStep(
            step=1,
            thought="骨架阶段：先确认 Java 业务层能正常把请求转发过来，ReAct 循环尚未接入。",
            action=None,
            observation=None,
        )
    ]
    answer = (
        f"### 收到你的问题\n\n"
        f"> {request.question}\n\n"
        f"当前是**服务骨架**，还没有接入大模型与工具。\n\n"
        f"- 用户 ID：`{request.user_id}`\n"
        f"- 会话 ID：`{request.session_id}`\n"
        f"- 课件 ID：`{request.courseware_id}`\n"
        f"- 已配置大模型：`{settings.llm_configured}`\n"
    )
    return ChatResponse(answer=answer, trace=trace, finished=True)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
