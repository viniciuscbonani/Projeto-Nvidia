"""Teste do nó briefing (offline — LLM monkeypatchado)."""

from app import briefing as brf_mod
from app.state import RadarState


def test_briefing_preenche(monkeypatch):
    monkeypatch.setattr(brf_mod, "redigir", lambda state: "## Briefing — Tractian\nClassificação: ai-native")
    out = brf_mod.briefing(RadarState(consulta="Tractian"))
    assert out["briefing"].startswith("## Briefing")
