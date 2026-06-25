"""RadarState — o contrato central que viaja por todo o grafo.

Cada nó lê os campos de que precisa e retorna apenas um dict parcial com o
que atualizou; o LangGraph mescla esse dict no State.
"""

from typing import Optional

from pydantic import BaseModel, Field


class RadarState(BaseModel):
    consulta: str = ""                                  # entrada do usuário
    alvos: list[str] = Field(default_factory=list)      # empresas a investigar
    conteudo_bruto: list[dict] = Field(default_factory=list)   # trechos + fonte
    dados_estruturados: dict = Field(default_factory=dict)     # schema extraído
    classificacao: Optional[str] = None                 # "ai-native" | "ai-enabled" | "non-ai"
    evidencias_ok: bool = False                         # gate do Evidence Validator
    tentativas: int = 0                                 # teto do loop do Validator
    contexto_rag: list[str] = Field(default_factory=list)      # trechos NVIDIA recuperados
    recomendacao: dict = Field(default_factory=dict)    # gaps × portfólio + score
    briefing: str = ""                                  # relatório executivo final
