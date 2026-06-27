"""Camada relacional (SQLAlchemy + SQLite por enquanto).

Reusa `settings.database_url` de app/config.py — trocar SQLite por PostgreSQL é
só mudar a `DATABASE_URL`. Tipos **portáveis** (String/Text/JSON/DateTime), sem
JSONB/ARRAY (convenção do CLAUDE.md), para a migração ser config, não reescrita.
"""

from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

from app.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class Empresa(Base):
    __tablename__ = "empresas"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nome: Mapped[str] = mapped_column(String(255), index=True)
    setor: Mapped[str | None] = mapped_column(String(255), nullable=True)
    descricao: Mapped[str] = mapped_column(Text, default="")
    dados: Mapped[dict] = mapped_column(JSON, default=dict)   # dump do DadosEmpresa
    fontes: Mapped[list] = mapped_column(JSON, default=list)  # URLs usadas
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )


def init_db() -> None:
    """Cria as tabelas (idempotente). Chamado antes do primeiro uso."""
    Base.metadata.create_all(engine)
