"""运行期配置：全部来自环境变量 / .env 文件。

约定见 docs/03-开发环境与接口约定.md：
密钥类配置一律不写进代码，也不提交仓库。
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """服务配置。字段名会自动匹配同名大写环境变量（llm_api_key ← LLM_API_KEY）。"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ---------- 服务 ----------
    app_name: str = "课程学习助手 · 智能体服务"
    app_version: str = "0.1.0"
    app_env: str = "dev"
    log_level: str = "INFO"

    # ---------- 大模型 ----------
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com/v1"
    llm_model: str = "deepseek-chat"

    # ---------- ReAct 循环 ----------
    max_react_steps: int = 8
    agent_timeout_seconds: int = 120

    @property
    def llm_configured(self) -> bool:
        """是否已配置真实可用的 API Key（用于健康检查，不暴露密钥本身）。"""
        key = self.llm_api_key.strip()
        return bool(key) and not key.startswith("sk-your-key")


@lru_cache
def get_settings() -> Settings:
    """单例配置；测试里可用 get_settings.cache_clear() 重置。"""
    return Settings()
