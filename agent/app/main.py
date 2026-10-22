"""FastAPI 入口。

启动（在 agent/ 目录下）：
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --port 8000

接口文档（全部中文）：http://localhost:8000/docs

    GET  /              服务信息
    GET  /health        健康检查
    GET  /agent/tools   当前可用工具清单（调试用）
    POST /agent/chat    ReAct 对话
"""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.config import get_settings
from app.react.agent import ReActAgent
from app.react.reasoner import RuleBasedReasoner
from app.schemas import ChatRequest, ChatResponse
from app.store.memory import boot_demo_data
from app.tools.box import ToolBox

settings = get_settings()

# ---- 接口文档里显示的标签（中文）----
标签 = [
    {"name": "基础信息", "description": "服务信息与健康检查"},
    {"name": "智能体", "description": "工具清单与 ReAct 对话"},
]

# ---- 数据模型在文档里的中文名 ----
模型中文名 = {
    "ChatRequest": "对话请求",
    "ChatResponse": "对话响应",
    "TraceStep": "思考轨迹",
    "HTTPValidationError": "参数校验失败",
    "ValidationError": "字段校验失败",
}


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 开发期灌一份样例课件，方便前后端联调；接入真实上传后去掉
    if settings.app_env == "dev":
        boot_demo_data()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "基于 ReAct 的课程学习助手 · 智能体服务。\n\n"
        "工作方式：先检索学生上传的课件原文，再基于原文出题、排计划并归档，"
        "全过程对外输出思考轨迹（思考 → 行动 → 观察）。"
    ),
    lifespan=lifespan,
    openapi_tags=标签,
)


@app.get("/", tags=["基础信息"], summary="服务信息", description="返回服务名称与版本，用于快速确认服务已启动。")
def root() -> dict:
    return {
        "服务": "课程学习助手-智能体",
        "版本": settings.app_version,
        "接口文档": "/docs",
    }


@app.get("/health", tags=["基础信息"], summary="健康检查", description="返回服务状态与配置情况；只回报是否配置了密钥，不返回密钥本身。")
def health() -> dict:
    """健康检查。只回报是否配置了 Key，不返回 Key 本身。"""
    return {
        "状态": "正常",
        "运行环境": settings.app_env,
        "已配置大模型": settings.llm_configured,
        "模型名称": settings.llm_model,
        "最大思考轮次": settings.max_react_steps,
        "决策方式": "大模型" if settings.llm_configured else "规则引擎",
    }


@app.get("/agent/tools", tags=["智能体"], summary="工具清单", description="列出智能体当前可调用的全部工具及其参数说明。")
def list_tools() -> dict:
    """列出当前可用工具（前端调试、答辩演示都能用）。"""
    box = ToolBox(user_id=0, session_id="inspect")
    return {
        "工具数量": len(box.names),
        "工具列表": [
            {
                "名称": tool.name,
                "说明": tool.description,
                "参数": tool.parameters,
            }
            for tool in box.registry.all()
        ],
    }


@app.post("/agent/chat", response_model=ChatResponse, tags=["智能体"], summary="发起对话", description="执行一次完整的 ReAct 循环：检索课件 → 生成练习 →（有考试日期则）排计划 → 归档，并返回思考轨迹。")
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


def 生成中文接口文档() -> dict:
    """把自动生成的 OpenAPI 里的模型名替换成中文，让 /docs 页面全中文显示。"""
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        tags=标签,
    )

    # 先把所有 $ref 指向改成新名字，再改 components 里的键
    text = json.dumps(schema, ensure_ascii=False)
    for old, new in 模型中文名.items():
        text = text.replace(f"#/components/schemas/{old}", f"#/components/schemas/{new}")
    schema = json.loads(text)

    components = schema.get("components", {}).get("schemas", {})
    for old, new in 模型中文名.items():
        if old in components:
            components[new] = components.pop(old)
            components[new]["title"] = new

    app.openapi_schema = schema
    return schema


app.openapi = 生成中文接口文档


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
