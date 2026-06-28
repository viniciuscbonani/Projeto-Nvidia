"""Testes do nó recommendation (offline — LLM monkeypatchado)."""

from app import recommendation as rec_mod
from app.state import DadosEmpresa, RadarState, Recomendacao, Score


def test_recommendation_monta_rec_e_score(monkeypatch):
    fake_rec = Recomendacao(tecnologias=["Triton", "TensorRT-LLM"], evidencias=["https://docs.nvidia.com/triton"])
    fake_notas = Score(ai_native=10, nvidia_fit=10, tracao=10, time_ia=10)
    monkeypatch.setattr(rec_mod, "recomendar", lambda dados, classificacao, contexto_rag: (fake_rec, fake_notas))

    state = RadarState(
        dados_estruturados=DadosEmpresa(nome="Tractian"),
        contexto_rag=["Triton serve modelos [fonte: https://docs.nvidia.com/triton]"],
    )
    out = rec_mod.recommendation(state)

    assert out["recomendacao"].tecnologias == ["Triton", "TensorRT-LLM"]
    assert out["recomendacao"].evidencias  # rastreabilidade
    assert out["score"].composto == 10.0   # todas 10, pesos somam 1.0
    assert out["score"].nvidia_fit == 10
