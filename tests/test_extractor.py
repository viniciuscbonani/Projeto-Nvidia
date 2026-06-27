"""Testes do Extractor (offline — LLM e persistência monkeypatchados)."""

from app import extractor
from app.state import DadosEmpresa, RadarState


def test_extractor_preenche_dados_e_salva(monkeypatch):
    fake = DadosEmpresa(nome="Tractian", setor="Indústria", tecnologias=["IoT", "ML"])
    monkeypatch.setattr(extractor, "extract_dados", lambda textos, nome, fontes: fake)

    salvos = []
    monkeypatch.setattr(extractor, "salvar_empresa", lambda dados: salvos.append(dados))

    state = RadarState(
        alvos=["Tractian"],
        conteudo_bruto=[{"texto": "trecho", "fonte": "https://x.com"}],
    )
    out = extractor.extractor(state)

    assert out["dados_estruturados"].nome == "Tractian"
    assert out["dados_estruturados"].tecnologias == ["IoT", "ML"]
    assert len(salvos) == 1  # persistência foi chamada


def test_extractor_sem_conteudo_nao_chama_llm(monkeypatch):
    def nao_deveria(*a, **k):
        raise AssertionError("extract_dados não deveria ser chamado sem conteúdo")

    monkeypatch.setattr(extractor, "extract_dados", nao_deveria)
    monkeypatch.setattr(extractor, "salvar_empresa", lambda dados: None)

    out = extractor.extractor(RadarState(alvos=["Tractian"], conteudo_bruto=[]))
    assert out["dados_estruturados"].nome == "Tractian"
