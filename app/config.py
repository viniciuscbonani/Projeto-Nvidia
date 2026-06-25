"""Configuração central do projeto, lida do .env uma única vez.

Use `from app.config import settings` em qualquer lugar — nunca leia variáveis
de ambiente espalhadas pelo código. Isso mantém a troca SQLite→Postgres e
Chroma-embarcado→servidor num só lugar.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Chaves de API
    openai_api_key: str = ""
    cohere_api_key: str = ""

    # Banco relacional (SQLite embarcado por enquanto)
    database_url: str = "sqlite:///radar.db"

    # Banco vetorial (Chroma embarcado por enquanto)
    chroma_path: str = "./chroma"


settings = Settings()
