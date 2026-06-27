"""Recommendation (stub — Fase 1).

Cruza gaps × portfólio NVIDIA, calcula o score e monta a recomendação estruturada
(os 7 campos do schema Recomendacao). Stub: preenche os 7 campos com placeholders,
exercitando o contrato estruturado da Fase 0.
"""

from app.state import RadarState, Recomendacao


def recommendation(state: RadarState) -> dict:
    rec = Recomendacao(
        tecnologias=["Triton", "TensorRT-LLM"],
        justificativa_tecnica="(stub) reduz latência de inferência",
        justificativa_negocio="(stub) menor custo por token servido",
        prioridade="alta",
        complexidade="média",
        proxima_acao="(stub) agendar conversa técnica com o time NVIDIA",
        evidencias=state.contexto_rag,
    )
    return {"recomendacao": rec}
