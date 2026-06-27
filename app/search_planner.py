"""Search Planner (Fase 2 — real).

Transforma a consulta do usuário num plano de busca: descobre, por **busca web**
(DuckDuckGo via ddgs), as URLs públicas a coletar. Generaliza para qualquer
empresa (sem cadastro manual). Prioriza domínios confiáveis do registro do
projeto (TAPI §7) e descarta fontes restritivas (LinkedIn/redes).
"""

from urllib.parse import urlparse

from ddgs import DDGS

from app.config import settings
from app.sources import DOMINIOS_BLOQUEADOS, DOMINIOS_CONFIAVEIS
from app.state import RadarState


def _dominio(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def _bloqueado(url: str) -> bool:
    dom = _dominio(url)
    if url.lower().endswith(".pdf"):
        return True
    return any(dom == b or dom.endswith("." + b) for b in DOMINIOS_BLOQUEADOS)


def _confiavel(url: str) -> bool:
    dom = _dominio(url)
    return any(dom == c or dom.endswith("." + c) for c in DOMINIOS_CONFIAVEIS)


def buscar_urls(consulta: str, top_n: int | None = None) -> list[str]:
    """Pesquisa a empresa/consulta e devolve as URLs a coletar.

    Faz uma busca geral e uma de notícias, filtra bloqueados, dedup, e ordena
    pondo os domínios confiáveis (TAPI §7) na frente.
    """
    top_n = top_n or settings.busca_top_n
    queries = [f"{consulta} startup", f"{consulta} startup notícias"]

    vistos: set[str] = set()
    resultados: list[str] = []
    with DDGS() as ddgs:
        for q in queries:
            for hit in ddgs.text(q, max_results=top_n):
                url = hit.get("href") or hit.get("url") or ""
                if not url or url in vistos or _bloqueado(url):
                    continue
                vistos.add(url)
                resultados.append(url)

    # confiáveis primeiro, preservando a ordem de descoberta
    resultados.sort(key=lambda u: not _confiavel(u))
    return resultados[:top_n]


def search_planner(state: RadarState) -> dict:
    consulta = state.consulta.strip() or "Tractian"
    # no retry do loop (tentativas > 0), amplia a cobertura para juntar evidência nova
    top_n = settings.busca_top_n + state.tentativas * settings.busca_top_n
    urls = buscar_urls(consulta, top_n=top_n)
    return {"alvos": [consulta], "urls_busca": urls}
