"""NVIDIA RAG — lado online (stub — Fase 1).

Recupera contexto técnico da base de conhecimento NVIDIA (Qdrant). É o lado
*online* do RAG: assume a base já populada pela ingestão offline (app/ingest.py,
Fase 4) e NÃO faz ingestão aqui. Stub: devolve um trecho-placeholder com fonte.
"""

from app.state import RadarState


def nvidia_rag(state: RadarState) -> dict:
    contexto = [
        "(stub) Triton — serving eficiente de modelos [fonte: docs NVIDIA]",
    ]
    return {"contexto_rag": contexto}
