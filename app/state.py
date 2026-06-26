"""RadarState — o contrato central que viaja por todo o grafo.

Cada nó lê os campos de que precisa e retorna apenas um dict parcial com o
que atualizou; o LangGraph mescla esse dict no State.
"""

from typing import Optional

from pydantic import BaseModel, Field


class Recomendacao(BaseModel):
    """Saída estruturada do Recommendation Agent.

    Os 7 campos são exigidos pelo brief do projeto (§5.5). O agente deve
    produzir isto como structured output (não texto solto) e toda recomendação
    precisa citar a origem (campo `evidencias`).
    """

    tecnologias: list[str] = Field(default_factory=list)        # 1. tecnologias NVIDIA recomendadas
    justificativa_tecnica: str = ""                             # 2. por que tecnicamente
    justificativa_negocio: str = ""                             # 3. por que para o negócio (custo, latência, defensibilidade)
    prioridade: Optional[str] = None                            # 4. nível de prioridade (ex.: alta/média/baixa)
    complexidade: Optional[str] = None                          # 5. complexidade de implementação
    proxima_acao: str = ""                                      # 6. próxima ação sugerida para o time NVIDIA
    evidencias: list[str] = Field(default_factory=list)         # 7. evidências/fontes usadas


class RadarState(BaseModel):
    consulta: str = ""                                  # entrada do usuário
    alvos: list[str] = Field(default_factory=list)      # empresas a investigar
    conteudo_bruto: list[dict] = Field(default_factory=list)   # trechos + fonte
    dados_estruturados: dict = Field(default_factory=dict)     # schema extraído
    classificacao: Optional[str] = None                 # "ai-native" | "ai-enabled" | "non-ai"
    evidencias_ok: bool = False                         # gate do Evidence Validator
    tentativas: int = 0                                 # teto do loop do Validator
    contexto_rag: list[str] = Field(default_factory=list)      # trechos NVIDIA recuperados
    recomendacao: Optional[Recomendacao] = None         # saída estruturada (7 campos do brief §5.5)
    briefing: str = ""                                  # relatório executivo final
