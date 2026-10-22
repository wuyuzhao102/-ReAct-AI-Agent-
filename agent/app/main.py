"""FastAPI 入口。

启动（在 agent/ 目录下）：
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --port 8000

接口：
    GET  /              服务信息
    GET  /health        健康检查
    GET  /agent/tools   当前可用工具清单（调试用）
    POST /agent/chat    ReAct 对话
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings
from app.react.agent import ReActAgent
from app.react.reasoner import RuleBasedReasoner
from app.schemas import ChatRequest, ChatResponse
from app.store.memory import boot_demo_data
from app.tools.box import ToolBox

settings = get_settings()


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 开发期灌一份样例课件，方便前后端联调；接入真实上传后去掉
    if settings.app_env == "dev":
        boot_demo_data()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="基于 ReAct 的课程学习助手 · 智能体服务",
    lifespan=lifespan,
)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "service": "coursemate-agent",
        "version": settings.app_version,
        "docs": "/docs",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    """健康检查。只回报"是否配置了 Key"，不返回 Key 本身。"""
    return {
        "status": "ok",
        "env": settings.app_env,
        "llm_configured": settings.llm_configured,
        "llm_model": settings.llm_model,
        "max_react_steps": settings.max_react_steps,
        "reasoner": "llm" if settings.llm_configured else "rule-based",
    }


@app.get("/agent/tools", tags=["agent"])
def list_tools() -> dict:
    """列出当前可用工具（前端调试、答辩演示都能用）。"""
    box = ToolBox(user_id=0, session_id="inspect")
    return {
        "count": len(box.names),
        "tools": [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters,
            }
            for tool in box.registry.all()
        ],
    }


@app.post("/agent/chat", response_model=ChatResponse, tags=["agent"])
def chat(request: ChatRequest) -> ChatResponse:
    """ReAct 对话。

    当前用规则引擎驱动（不依赖大模型），整条链路 —— 检索 → 出题 →（排计划）→ 归档 —— 都能走通。
    接入大模型后，这里只需把 RuleBasedReasoner 换成 LLMReasoner。
    """
    toolbox = ToolBox(
        user_id=request.user_id,
        session_id=request.session_id,
        courseware_id=request.courseware_id,
    )
    agent = ReActAgent(
        toolbox=toolbox,
        reasoner=RuleBasedReasoner(),
        max_steps=settings.max_react_steps,
    )
    return agent.run(request.question)


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
