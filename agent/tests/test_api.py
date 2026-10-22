"""接口契约测试：保证 Java 业务层按约定调过来时能正常工作。"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store.memory import DEMO_COURSEWARE, store

client = TestClient(app)


@pytest.fixture(autouse=True)
def _seed():
    store.clear()
    store.add_courseware(1, "高等数学（上）· 第一章 极限", DEMO_COURSEWARE)
    yield
    store.clear()


def test_root_returns_service_info():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["服务"] == "课程学习助手-智能体"


def test_health_reports_ok_and_hides_key():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["状态"] == "正常"
    assert "已配置大模型" in body
    assert body["决策方式"] in {"规则引擎", "大模型"}
    # 健康检查不能把密钥吐出来
    assert "llm_api_key" not in body
    assert "sk-" not in str(body)


def test_tools_endpoint_lists_four_tools():
    resp = client.get("/agent/tools")
    assert resp.status_code == 200
    body = resp.json()
    assert body["工具数量"] == 4
    names = {t["名称"] for t in body["工具列表"]}
    assert names == {"课件检索", "习题生成", "备考计划", "笔记归档"}


def test_chat_accepts_java_camel_case_contract():
    """Java 侧传的是 userId / sessionId / coursewareId（camelCase）。"""
    payload = {
        "userId": 1,
        "sessionId": "sess-0001",
        "coursewareId": 1,
        "question": "下周要考高数极限，帮我复习",
    }
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["finished"] is True
    assert body["answer"]
    # 至少走过 检索 → 出题 → 归档
    actions = [t["action"] for t in body["trace"] if t["action"]]
    assert actions[:2] == ["课件检索", "习题生成"]
    assert "笔记归档" in actions
    assert body["trace"][0]["step"] == 1


def test_chat_works_without_courseware_id():
    """coursewareId 可为空：表示在用户全部课件里检索。"""
    payload = {"userId": 2, "sessionId": "sess-0002", "question": "概率论怎么复习"}
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 200
    assert resp.json()["answer"]


def test_chat_rejects_empty_question():
    payload = {"userId": 1, "sessionId": "s", "question": ""}
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 422


def test_openapi_is_chinese():
    """接口文档页面的标签、接口名、模型名都应是中文。"""
    schema = app.openapi()

    assert schema["info"]["title"] == "课程学习助手 · 智能体服务"
    tag_names = {t["name"] for t in schema["tags"]}
    assert tag_names == {"基础信息", "智能体"}

    summaries = {
        op.get("summary") for path in schema["paths"].values() for op in path.values()
    }
    assert {"服务信息", "健康检查", "工具清单", "发起对话"} <= summaries

    model_names = set(schema["components"]["schemas"])
    assert {"对话请求", "对话响应", "思考轨迹"} <= model_names
    # 自动生成的两个英文校验模型也要改名
    assert "HTTPValidationError" not in model_names
    assert "ValidationError" not in model_names

    # $ref 必须能对上改名后的模型，否则文档会渲染失败
    text = str(schema)
    assert "#/components/schemas/ChatRequest" not in text
    assert "#/components/schemas/对话请求" in text
