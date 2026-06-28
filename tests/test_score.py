"""Teste do score composto (função pura, pesos configuráveis)."""

from app.config import settings
from app.score import compor
from app.state import Score


def test_compor_pesos_iguais(monkeypatch):
    for w in ("w_ai_native", "w_nvidia_fit", "w_tracao", "w_time_ia"):
        monkeypatch.setattr(settings, w, 0.25)
    notas = Score(ai_native=8, nvidia_fit=8, tracao=4, time_ia=4)
    assert compor(notas) == 6.0  # média simples


def test_compor_respeita_pesos(monkeypatch):
    monkeypatch.setattr(settings, "w_ai_native", 1.0)
    monkeypatch.setattr(settings, "w_nvidia_fit", 0.0)
    monkeypatch.setattr(settings, "w_tracao", 0.0)
    monkeypatch.setattr(settings, "w_time_ia", 0.0)
    notas = Score(ai_native=9, nvidia_fit=1, tracao=1, time_ia=1)
    assert compor(notas) == 9.0  # só ai_native pesa
