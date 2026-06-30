"""Testes do Evidence Validator (regra determinística, sem LLM)."""

from app.evidence_validator import evidence_validator
from app.state import DadosEmpresa, RadarState


def _state(fontes, setor="Indústria", descricao="faz X", tentativas=0):
    return RadarState(
        conteudo_bruto=[{"texto": "t", "fonte": f} for f in fontes],
        dados_estruturados=DadosEmpresa(nome="X", setor=setor, descricao=descricao),
        tentativas=tentativas,
    )


def test_suficiente_com_3_dominios_e_campos():
    out = evidence_validator(_state(["https://a.com/x", "https://b.com/y", "https://c.com/z"]))
    assert out["evidencias_ok"] is True
    assert out["tentativas"] == 1  # incrementou


def test_insuficiente_com_2_dominios():
    out = evidence_validator(_state(["https://a.com/x", "https://b.com/y"]))
    assert out["evidencias_ok"] is False  # piso subiu para 3 domínios distintos


def test_insuficiente_sem_campos():
    out = evidence_validator(_state(["https://a.com/x", "https://b.com/y"], descricao=""))
    assert out["evidencias_ok"] is False
