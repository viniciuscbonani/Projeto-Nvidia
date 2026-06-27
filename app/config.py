"""Configuração central do projeto, lida do .env uma única vez.

Use `from app.config import settings` em qualquer lugar — nunca leia variáveis
de ambiente espalhadas pelo código. Isso mantém a troca SQLite→Postgres e
Qdrant-local→servidor num só lugar.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Chaves de API
    openai_api_key: str = ""
    groq_api_key: str = ""
    cohere_api_key: str = ""

    # Banco relacional (SQLite embarcado por enquanto)
    database_url: str = "sqlite:///radar.db"

    # Banco vetorial (Qdrant em modo local por enquanto; servidor depois)
    qdrant_path: str = "./qdrant"

    # LLM (extração estruturada no Extractor). Servido pela Groq (API compatível
    # com OpenAI) quando há GROQ_API_KEY; senão, OpenAI direto.
    llm_model: str = "openai/gpt-oss-20b"

    # Coleta web
    user_agent: str = "NVIDIA-Startup-Radar/0.1 (+pesquisa academica Inteli)"
    http_timeout: float = 15.0
    busca_top_n: int = 8

    @property
    def llm_base_url(self) -> str | None:
        """URL base do LLM: Groq se houver chave Groq; senão OpenAI (None)."""
        return "https://api.groq.com/openai/v1" if self.groq_api_key else None

    @property
    def llm_api_key(self) -> str:
        """Chave do LLM: prioriza Groq; cai para OpenAI."""
        return self.groq_api_key or self.openai_api_key


settings = Settings()
