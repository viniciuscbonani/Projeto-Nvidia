"""Smoke test do fluxo completo (offline).

Roda o grafo de ponta a ponta sem tocar rede nem API: a busca, o fetch HTTP, a
extração por LLM e a persistência são monkeypatchados. Verifica que o State viaja
e é preenchido pelos nós (3 reais + 5 stubs).
"""

import pytest

from app import extractor, scraper, search_planner
from app.graph import graph
from app.state import DadosEmpresa, RadarState

HTML = "<html><body><article><p>" + ("Tractian faz IA industrial. " * 10) + "</p></article></body></html>"


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(search_planner, "buscar_urls", lambda consulta, top_n=None: ["https://exemplo.com/a"])
    monkeypatch.setattr(scraper, "permitido_por_robots", lambda url: True)
    monkeypatch.setattr(scraper, "fetch_url", lambda url: HTML)
    monkeypatch.setattr(
        extractor, "extract_dados",
        lambda textos, nome, fontes: DadosEmpresa(nome=nome, setor="Indústria", tecnologias=["IoT"], fontes=fontes),
    )
    monkeypatch.setattr(extractor, "salvar_empresa", lambda dados: None)


def test_pipeline_preenche_todos_os_campos(offline):
    final = graph.invoke(RadarState(consulta="Tractian"))

    assert final["alvos"] == ["Tractian"]
    assert final["urls_busca"]
    assert final["conteudo_bruto"]
    assert final["dados_estruturados"].nome == "Tractian"
    assert final["classificacao"] == "ai-native"
    assert final["evidencias_ok"] is True
    assert final["contexto_rag"]
    assert final["recomendacao"] is not None
    assert final["recomendacao"].tecnologias
    assert final["briefing"]
