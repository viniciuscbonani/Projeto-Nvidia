"""Smoke test do fluxo completo (offline, caminho feliz).

Roda o grafo de ponta a ponta sem tocar rede nem API: busca, fetch HTTP, extração
e classificação por LLM são monkeypatchados. A evidência é suficiente (2 domínios
+ campos), então NÃO entra no loop e segue até o briefing.
"""

import pytest

from app import classifier, extractor, scraper, search_planner
from app.graph import graph
from app.state import Classificacao, DadosEmpresa, RadarState

HTML = "<html><body><article><p>" + ("Tractian faz IA industrial. " * 10) + "</p></article></body></html>"


@pytest.fixture
def offline(monkeypatch):
    monkeypatch.setattr(
        search_planner, "buscar_urls",
        lambda consulta, top_n=None: ["https://a.com/x", "https://b.com/y"],
    )
    monkeypatch.setattr(scraper, "permitido_por_robots", lambda url: True)
    monkeypatch.setattr(scraper, "fetch_url", lambda url: HTML)
    monkeypatch.setattr(
        extractor, "extract_dados",
        lambda textos, nome, fontes: DadosEmpresa(
            nome=nome, setor="Indústria", descricao="manutenção preditiva", tecnologias=["IoT"], fontes=fontes
        ),
    )
    monkeypatch.setattr(extractor, "salvar_empresa", lambda dados: None)
    monkeypatch.setattr(
        classifier, "classificar",
        lambda dados: Classificacao(rotulo="ai-native", justificativa="core de IA"),
    )


def test_pipeline_preenche_todos_os_campos(offline):
    final = graph.invoke(RadarState(consulta="Tractian"))

    assert final["alvos"] == ["Tractian"]
    assert final["urls_busca"]
    assert final["conteudo_bruto"]
    assert final["dados_estruturados"].nome == "Tractian"
    assert final["classificacao"] == "ai-native"
    assert final["classificacao_detalhe"].rotulo == "ai-native"
    assert final["evidencias_ok"] is True
    assert final["tentativas"] == 1          # sem loop (evidência suficiente de 1ª)
    assert final["contexto_rag"]
    assert final["recomendacao"] is not None
    assert final["briefing"]
