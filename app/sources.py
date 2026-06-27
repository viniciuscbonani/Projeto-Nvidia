"""Registro canônico de fontes do projeto (TAPI §7).

Diretórios de startups (§7.1) e fontes de notícias (§7.2). Na Fase 2 essas listas
servem para **priorizar** resultados da busca web (domínios confiáveis) e
**descartar** fontes restritivas (LinkedIn). Não são seed por empresa — a
descoberta de URLs é feita por busca (ver app/search_planner.py).
"""

from urllib.parse import urlparse

# §7.1 — diretórios e aceleradoras
FONTES_DIRETORIOS = [
    "https://www.startse.com/",
    "https://distrito.me/",
    "https://www.latitud.com/",
    "https://cubo.network/",
    "https://acestartups.com.br/",
    "https://endeavor.org.br/",
    "https://abstartups.com.br/",
    "https://bossainvest.com/",
    "https://www.anjosdobrasil.net/",
    "https://www.darwinstartups.com/",
    "https://liga.ventures/",
    "https://www.wow.ac/",
    "https://www.inovativabrasil.com.br/",
    "https://www.openstartups.net/",
]

# §7.2 — notícias e sinais públicos
FONTES_NOTICIAS = [
    "https://braziljournal.com/",
    "https://neofeed.com.br/",
    "https://exame.com/bussola/startups/",
    "https://startups.com.br/",
    "https://revistapegn.globo.com/",
    "https://valor.globo.com/",
    "https://www.meioemensagem.com.br/",
    "https://www.mobiletime.com.br/",
]


def _dominio(url: str) -> str:
    """Extrai o domínio (sem www) de uma URL."""
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


# Domínios confiáveis (para priorizar resultados da busca)
DOMINIOS_CONFIAVEIS = {
    _dominio(u) for u in FONTES_DIRETORIOS + FONTES_NOTICIAS
}

# Domínios a descartar (restritivos ou de baixo sinal)
DOMINIOS_BLOQUEADOS = {
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "youtube.com",
    "tiktok.com",
}
