"""Briefing (stub — Fase 1).

Redige o relatório executivo final a partir de tudo que os nós anteriores
preencheram no State. Stub: monta um briefing-placeholder com os campos-chave.
"""

from app.state import RadarState


def briefing(state: RadarState) -> dict:
    alvo = state.alvos[0] if state.alvos else "(sem alvo)"
    classificacao = state.classificacao or "(sem classificação)"
    techs = (
        ", ".join(state.recomendacao.tecnologias)
        if state.recomendacao
        else "(nenhuma)"
    )
    texto = (
        f"Briefing (stub) — {alvo}\n"
        f"Classificação: {classificacao}\n"
        f"Tecnologias recomendadas: {techs}\n"
        "Pipeline ainda em stubs: este é o esqueleto andante da Fase 1."
    )
    return {"briefing": texto}
