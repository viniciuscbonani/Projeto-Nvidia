"""Testes do Classifier (offline — LLM monkeypatchado)."""

from app import classifier as clf
from app.state import Classificacao, DadosEmpresa, RadarState


def test_classifier_preenche_rotulo_e_detalhe(monkeypatch):
    fake = Classificacao(
        rotulo="ai-native",
        eixo_produto="IA é o core",
        eixo_dados_modelo="modelo próprio",
        eixo_stack="infra própria",
        justificativa="3 eixos atendidos",
    )
    monkeypatch.setattr(clf, "classificar", lambda dados: fake)

    state = RadarState(dados_estruturados=DadosEmpresa(nome="Tractian", setor="Indústria"))
    out = clf.classifier(state)

    assert out["classificacao"] == "ai-native"
    assert out["classificacao_detalhe"].rotulo == "ai-native"
    assert out["classificacao_detalhe"].justificativa


def test_classifier_sem_dados_nao_chama_llm(monkeypatch):
    def nao_deveria(dados):
        raise AssertionError("não deveria classificar sem dados coletados")

    monkeypatch.setattr(clf, "classificar", nao_deveria)
    # dados vazios (busca/scraping não trouxe nada) → rótulo honesto "sem-dados"
    out = clf.classifier(RadarState(dados_estruturados=DadosEmpresa(nome="X")))
    assert out["classificacao"] == "sem-dados"
