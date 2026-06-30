"""Testes do Search Planner (offline — DDGS monkeypatchado)."""

from app import search_planner as sp


class FakeDDGS:
    def __init__(self, *a, **k):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def text(self, query, max_results=None, **kwargs):  # aceita backend=...
        return [
            {"href": "https://linkedin.com/company/tractian"},  # bloqueado
            {"href": "https://example.com/sobre"},              # normal
            {"href": "https://braziljournal.com/tractian"},     # confiável
            {"href": "https://exemplo.com/ficha.pdf"},          # pdf -> descartado
        ]


def test_buscar_urls_filtra_e_prioriza(monkeypatch):
    monkeypatch.setattr(sp, "DDGS", FakeDDGS)
    urls = sp.buscar_urls("Tractian", top_n=8)

    # LinkedIn e PDF foram descartados
    assert not any("linkedin.com" in u for u in urls)
    assert not any(u.endswith(".pdf") for u in urls)
    # domínio confiável vem antes do normal
    assert urls[0] == "https://braziljournal.com/tractian"
    assert "https://example.com/sobre" in urls
