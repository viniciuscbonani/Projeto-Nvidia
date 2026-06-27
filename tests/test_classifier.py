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
