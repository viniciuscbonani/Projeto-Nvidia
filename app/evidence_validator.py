"""Evidence Validator (Fase 3 — real, regra determinística).

Decide se há fonte suficiente para sustentar as afirmações sobre a empresa, sem
LLM (previsível e testável). Regra: ≥2 domínios de fonte distintos E campos-chave
preenchidos (`setor` e `descricao`). É o ponto do loop: se insuficiente, o grafo
volta ao Search Planner (com teto em `tentativas`). Incrementa `tentativas` a cada
checagem.
"""

from urllib.parse import urlparse

from app.state import RadarState

MIN_DOMINIOS = 2


def _dominio(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def evidencia_suficiente(state: RadarState) -> bool:
    dominios = {_dominio(t.get("fonte", "")) for t in state.conteudo_bruto}
    dominios.discard("")
    dados = state.dados_estruturados
    campos_ok = bool(dados and dados.setor and dados.descricao)
    return len(dominios) >= MIN_DOMINIOS and campos_ok


def evidence_validator(state: RadarState) -> dict:
    return {
        "evidencias_ok": evidencia_suficiente(state),
        "tentativas": state.tentativas + 1,
    }
