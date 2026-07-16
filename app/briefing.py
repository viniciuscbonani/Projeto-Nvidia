"""Briefing — relatório executivo final.

Redige o relatório executivo final para o gerente de Startups & VCs da NVIDIA, a
partir de tudo que o pipeline produziu (perfil, classificação, recomendação, score)
e citando as fontes do `contexto_rag`. Linguagem de negócio, não catálogo de produto.
LLM = Groq (via app.llm). `redigir` separado do nó para ser testável.
"""

from app.llm import chat
from app.state import RadarState

_INSTRUCAO = (
    "Você redige um briefing executivo (markdown) para o gerente de Startups & VCs da NVIDIA "
    "sobre uma startup, apoiando a abordagem comercial/técnica do programa NVIDIA Inception.\n"
    "Seja conciso e use linguagem de negócio (custo, latência, defensibilidade), não catálogo de produto.\n"
    "Estruture: visão geral da empresa, diagnóstico AI-native, tecnologias NVIDIA recomendadas com o "
    "porquê, prioridade/próxima ação, e o score.\n"
    "REGRA DE RIGOR (crítica): use SOMENTE informação presente no PERFIL, na RECOMENDAÇÃO ou no "
    "CONTEXTO NVIDIA. TODO número, percentual ou métrica — ex.: 'reduz latência 50%', 'corta custo 30%', "
    "'3x throughput', latência em ms, custo por token, benchmarks, nomes de chip/modelo — só pode aparecer "
    "se estiver LITERALMENTE em uma das fontes. Caso contrário é PROIBIDO citá-lo: escreva o benefício de "
    "forma qualitativa (ex.: 'menor latência de inferência', 'redução de custo de serving') ou use "
    "'não quantificado'. Nunca estime, arredonde nem invente ganhos percentuais. Ao citar uma spec real, "
    "inclua a URL da fonte."
)


def redigir(state: RadarState) -> str:
    dados = state.dados_estruturados.model_dump_json(indent=2) if state.dados_estruturados else "{}"
    rec = state.recomendacao.model_dump_json(indent=2) if state.recomendacao else "{}"
    score = state.score.model_dump_json() if state.score else "{}"
    contexto = "\n".join(state.contexto_rag) or "(sem contexto)"
    prompt = (
        f"{_INSTRUCAO}\n\n"
        f"EMPRESA:\n{dados}\n\n"
        f"CLASSIFICAÇÃO: {state.classificacao}\n\n"
        f"RECOMENDAÇÃO:\n{rec}\n\n"
        f"SCORE:\n{score}\n\n"
        f"CONTEXTO NVIDIA (fontes para citar):\n{contexto}"
    )
    resp = chat(temperature=0.3).invoke(prompt)
    return getattr(resp, "content", str(resp))


def briefing(state: RadarState) -> dict:
    return {"briefing": redigir(state)}
