"""Recommendation (Fase 5 — real).

Cruza o perfil/gaps da empresa × portfólio NVIDIA usando o `contexto_rag` (trechos
recuperados, com fonte) e produz a `Recomendacao` (7 campos do brief §5.5) + as 4
notas do score (0–10, julgadas pelo LLM). O código calcula o `composto` (pesos
configuráveis). LLM = Groq (via app.llm). Estrutura plana no structured output
(mais robusto no json_schema da Groq); mapeada para Recomendacao + Score.
"""

from typing import Optional

from pydantic import BaseModel, Field

from app.llm import chat
from app.score import compor
from app.state import Classificacao, DadosEmpresa, RadarState, Recomendacao, Score


class _SaidaLLM(BaseModel):
    # 7 campos da recomendação (brief §5.5)
    tecnologias: list[str] = Field(default_factory=list)
    justificativa_tecnica: str = ""
    justificativa_negocio: str = ""
    prioridade: Optional[str] = None
    complexidade: Optional[str] = None
    proxima_acao: str = ""
    evidencias: list[str] = Field(default_factory=list)
    # 4 notas do score (0–10)
    nota_ai_native: float = 0.0
    nota_nvidia_fit: float = 0.0
    nota_tracao: float = 0.0
    nota_time_ia: float = 0.0


_INSTRUCAO = (
    "Você recomenda tecnologias NVIDIA para uma startup, para o gerente de Startups & VCs.\n"
    "O campo `tecnologias` deve conter SÓ produtos NVIDIA a ADOTAR (ex.: Triton, TensorRT-LLM, "
    "NIM, NeMo, RAPIDS) — NÃO liste o stack atual da empresa nem ferramentas de terceiros "
    "(PyTorch, ONNX, AWS, etc.).\n"
    "Use APENAS produtos que aparecem no CONTEXTO NVIDIA fornecido — não invente specs nem nomes "
    "de produto. Para cada afirmação técnica, cite a fonte (URL) no campo evidencias.\n"
    "Raciocine sobre o gap: em qual camada a startup trava e qual tecnologia NVIDIA destrava.\n"
    "justificativa_negocio em linguagem de negócio (custo por token, latência, defensibilidade).\n"
    "Dê também 4 notas de 0 a 10: nota_ai_native (quão AI-native), nota_nvidia_fit (tamanho do "
    "gap/uplift que a NVIDIA destrava), nota_tracao (tração/funding), nota_time_ia (força do time)."
)


def recomendar(
    dados: DadosEmpresa, classificacao: Optional[Classificacao], contexto_rag: list[str]
) -> tuple[Recomendacao, Score]:
    contexto = "\n".join(contexto_rag) or "(sem contexto recuperado)"
    classif = classificacao.model_dump_json() if classificacao else "{}"
    prompt = (
        f"{_INSTRUCAO}\n\n"
        f"PERFIL DA EMPRESA:\n{dados.model_dump_json(indent=2)}\n\n"
        f"CLASSIFICAÇÃO AI-NATIVE:\n{classif}\n\n"
        f"CONTEXTO NVIDIA (trechos com fonte):\n{contexto}"
    )
    structured = chat().with_structured_output(_SaidaLLM, method="json_schema")
    s: _SaidaLLM = structured.invoke(prompt)

    rec = Recomendacao(
        tecnologias=s.tecnologias,
        justificativa_tecnica=s.justificativa_tecnica,
        justificativa_negocio=s.justificativa_negocio,
        prioridade=s.prioridade,
        complexidade=s.complexidade,
        proxima_acao=s.proxima_acao,
        evidencias=s.evidencias,
    )
    notas = Score(
        ai_native=s.nota_ai_native,
        nvidia_fit=s.nota_nvidia_fit,
        tracao=s.nota_tracao,
        time_ia=s.nota_time_ia,
    )
    return rec, notas


def recommendation(state: RadarState) -> dict:
    dados = state.dados_estruturados or DadosEmpresa(nome=state.consulta)
    rec, notas = recomendar(dados, state.classificacao_detalhe, state.contexto_rag)
    notas.composto = compor(notas)
    return {"recomendacao": rec, "score": notas}
