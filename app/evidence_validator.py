"""Evidence Validator (stub — Fase 1).

Checa se há fonte suficiente para as afirmações. É o ponto do loop (Fase 3): se a
evidência for insuficiente, volta ao Scraper, com teto em `tentativas`. Stub:
aprova se houver qualquer conteúdo coletado e incrementa `tentativas`.
"""

from app.state import RadarState


def evidence_validator(state: RadarState) -> dict:
    return {
        "evidencias_ok": len(state.conteudo_bruto) > 0,
        "tentativas": state.tentativas + 1,
    }
