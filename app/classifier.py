"""Startup Classifier (stub — Fase 1).

Aplica os 3 eixos AI-native e rotula a empresa como ai-native | ai-enabled |
non-ai. É o ponto do desvio condicional (Fase 3). Stub: devolve rótulo fixo.
"""

from app.state import RadarState


def classifier(state: RadarState) -> dict:
    return {"classificacao": "ai-native"}
