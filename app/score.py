"""Score composto (brief §"Score composto").

`composto = w1·AI-Native + w2·NVIDIA-Fit + w3·Tração/VC + w4·Time-de-IA`, com as 4
notas (0–10) julgadas pelo LLM e os pesos vindos de `settings` (configuráveis = o
gancho do diferencial da Fase 7). Função pura e determinística.
"""

from app.config import settings
from app.state import Score


def compor(notas: Score) -> float:
    s = settings
    composto = (
        s.w_ai_native * notas.ai_native
        + s.w_nvidia_fit * notas.nvidia_fit
        + s.w_tracao * notas.tracao
        + s.w_time_ia * notas.time_ia
    )
    return round(composto, 2)
