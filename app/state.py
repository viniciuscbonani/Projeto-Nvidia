"""RadarState — o contrato central que viaja por todo o grafo.

Cada nó lê os campos de que precisa e retorna apenas um dict parcial com o
que atualizou; o LangGraph mescla esse dict no State.
"""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class DadosEmpresa(BaseModel):
    """Saída estruturada do Extractor (structured output via LLM).

    Os campos vêm do brief (§2): dados públicos da empresa, produto, setor,
    clientes, funding, founders e tecnologias. `fontes` guarda as URLs usadas
    (rastreabilidade).
    """

    nome: str = ""
    setor: Optional[str] = None
    descricao: str = ""                                  # o que a empresa faz / produto
    founders: list[str] = Field(default_factory=list)
    funding: Optional[str] = None
    clientes: list[str] = Field(default_factory=list)
    tecnologias: list[str] = Field(default_factory=list)  # stack / sinais de IA
    fontes: list[str] = Field(default_factory=list)       # URLs usadas


class Classificacao(BaseModel):
    """Saída estruturada do Classifier — os 3 eixos AI-native (CLAUDE.md).

    `rotulo` é usado pelo desvio condicional do grafo; os 3 eixos e a
    justificativa dão rastreabilidade ao julgamento.
    """

    rotulo: Literal["ai-native", "ai-enabled", "non-ai"]
    eixo_produto: str = ""          # a IA é o core do valor? (se remove a IA, sobra produto?)
    eixo_dados_modelo: str = ""     # tem dado proprietário e/ou modelo próprio?
    eixo_stack: str = ""            # controla custo/latência da própria inferência?
    justificativa: str = ""


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
    urls_busca: list[str] = Field(default_factory=list)  # URLs a coletar (Search Planner)
    conteudo_bruto: list[dict] = Field(default_factory=list)   # trechos + fonte
    dados_estruturados: Optional[DadosEmpresa] = None   # schema extraído (structured output)
    classificacao: Optional[str] = None                 # rótulo: "ai-native" | "ai-enabled" | "non-ai"
    classificacao_detalhe: Optional[Classificacao] = None  # análise rica dos 3 eixos
    evidencias_ok: bool = False                         # gate do Evidence Validator
    tentativas: int = 0                                 # teto do loop do Validator
    contexto_rag: list[str] = Field(default_factory=list)      # trechos NVIDIA recuperados
    recomendacao: Optional[Recomendacao] = None         # saída estruturada (7 campos do brief §5.5)
    briefing: str = ""                                  # relatório executivo final
