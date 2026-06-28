"""Testes de roteamento do grafo (desvio condicional + loop), offline."""

import pytest

from app import briefing, classifier, extractor, rag, recommendation, scraper, search_planner
from app.graph import graph
from app.state import Classificacao, DadosEmpresa, RadarState, Recomendacao, Score

HTML = "<html><body><article><p>" + ("texto " * 20) + "</p></article></body></html>"


def _base_offline(monkeypatch, rotulo, descricao):
    """Monkeypatcha busca/rede/LLM. `descricao` vazio força evidência insuficiente."""
    monkeypatch.setattr(
        search_planner, "buscar_urls",
        lambda consulta, top_n=None: ["https://a.com/x", "https://b.com/y"],
    )
    monkeypatch.setattr(scraper, "permitido_por_robots", lambda url: True)
    monkeypatch.setattr(scraper, "fetch_url", lambda url: HTML)
    monkeypatch.setattr(
        extractor, "extract_dados",
        lambda textos, nome, fontes: DadosEmpresa(nome=nome, setor="Indústria", descricao=descricao, fontes=fontes),
    )
    monkeypatch.setattr(classifier, "classificar", lambda dados: Classificacao(rotulo=rotulo))
    monkeypatch.setattr(rag, "recuperar", lambda q: [{"texto": "ctx", "fonte": "https://docs.nvidia.com/x"}])
    monkeypatch.setattr(
        recommendation, "recomendar",
        lambda dados, classificacao, contexto_rag: (Recomendacao(tecnologias=["Triton"]), Score()),
    )
    monkeypatch.setattr(briefing, "redigir", lambda state: "## Briefing (fake)")


def test_non_ai_encerra_cedo(monkeypatch):
    _base_offline(monkeypatch, rotulo="non-ai", descricao="faz X")
    final = graph.invoke(RadarState(consulta="Padaria do Zé"))

    assert final["classificacao"] == "non-ai"
    # nós depois do desvio NÃO rodaram → seus campos nem aparecem na saída
    # (o LangGraph só retorna os canais que foram escritos durante a execução)
    assert not final.get("recomendacao")
    assert not final.get("briefing")
    assert not final.get("evidencias_ok")  # validator nem rodou


def test_loop_respeita_o_teto(monkeypatch):
    # descricao vazia => evidência sempre insuficiente => loop até o teto
    _base_offline(monkeypatch, rotulo="ai-native", descricao="")
    final = graph.invoke(RadarState(consulta="Tractian"))

    from app.config import settings
    assert final["evidencias_ok"] is False
    assert final["tentativas"] == settings.max_tentativas  # parou no teto, não travou
    assert final["briefing"]  # após o teto, seguiu o fluxo até o fim
