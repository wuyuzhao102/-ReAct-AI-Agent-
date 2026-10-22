"""与 Java 业务层之间的数据契约。

字段命名同时兼容两种风格：
- Java 侧传 camelCase（userId / sessionId / coursewareId），对应 alias；
- Python 内部用 snake_case，便于阅读。

契约来源：docs/03-开发环境与接口约定.md · 3.4 Java ⇄ Python 的契约
"""

from pydantic import BaseModel, ConfigDict, Field


class TraceStep(BaseModel):
    """ReAct 循环的一步：思考 → 行动 → 观察。

    这是本项目的亮点字段：前端可以把整个过程展开给学生看，
    体现"可解释的智能体"。
    """

    step: int = Field(description="第几轮思考，从 1 开始")
    thought: str = Field(default="", description="Thought：模型这一轮在想什么")
    action: str | None = Field(default=None, description="Action：调用了哪个工具")
    observation: str | None = Field(default=None, description="Observation：工具返回了什么")


class ChatRequest(BaseModel):
    """学生的一轮提问。"""

    model_config = ConfigDict(populate_by_name=True)

    user_id: int = Field(alias="userId", description="用户 ID，用于隔离数据")
    session_id: str = Field(alias="sessionId", description="会话 ID，用于串联多轮对话")
    courseware_id: int | None = Field(
        default=None, alias="coursewareId", description="指定课件；为空表示在该用户全部课件中检索"
    )
    question: str = Field(min_length=1, description="学生的自然语言问题")


class ChatResponse(BaseModel):
    """智能体的回复。answer 为 Markdown 文本，前端负责渲染富文本与公式。"""

    answer: str = Field(description="Markdown 格式的回答")
    trace: list[TraceStep] = Field(default_factory=list, description="ReAct 思考轨迹")
    finished: bool = Field(default=True, description="本轮任务是否已完成")
