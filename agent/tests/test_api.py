"""接口契约测试：保证 Java 业务层按约定调过来时能正常工作。

运行（在 agent/ 目录下）：
    .venv\\Scripts\\python.exe -m pytest
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_returns_service_info():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "coursemate-agent"


def test_health_reports_ok_and_hides_key():
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert "llm_configured" in body
    # 健康检查不能把密钥吐出来
    assert "llm_api_key" not in body


def test_chat_accepts_java_camel_case_contract():
    """Java 侧传的是 userId / sessionId / coursewareId（camelCase）。"""
    payload = {
        "userId": 1,
        "sessionId": "sess-0001",
        "coursewareId": 12,
        "question": "下周要考高数极限，帮我复习",
    }
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 200

    body = resp.json()
    assert body["finished"] is True
    assert body["answer"].startswith("###")
    assert len(body["trace"]) == 1
    assert body["trace"][0]["step"] == 1


def test_chat_works_without_courseware_id():
    """coursewareId 可为空：表示在用户全部课件里检索。"""
    payload = {"userId": 2, "sessionId": "sess-0002", "question": "概率论怎么复习"}
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 200


def test_chat_rejects_empty_question():
    payload = {"userId": 1, "sessionId": "s", "question": ""}
    resp = client.post("/agent/chat", json=payload)
    assert resp.status_code == 422
