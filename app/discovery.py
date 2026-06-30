"""Descoberta autônoma de startups (fecha o "encontrar" do TAPI §2).

A partir de um TEMA, descobre uma LISTA de nomes de startups brasileiras de IA —
reusando a busca, o scraper e o LLM. NÃO faz a análise completa: produz a lista
para revisão humana, que então alimenta o `batch`.

    fluxo:  tema → busca → raspa listas/notícias → LLM extrai nomes → lista
    uso:    python -m app.discovery "startups brasileiras de IA em saúde"
            python -m app.discovery "fintechs de IA" --analisar   # encadeia o batch
"""

import sys

from app.llm import chat
from app.scraper import extract_text, fetch_url, permitido_por_robots
from app.search_planner import _buscar
from app.state import ListaEmpresas

MAX_CONTEXTO = 14000

_INSTRUCAO = (
    "Extraia uma lista de nomes de STARTUPS BRASILEIRAS de IA mencionadas no texto.\n"
    "Inclua apenas startups (empresas jovens) brasileiras cujo core envolve inteligência artificial.\n"
    "NÃO inclua: big techs (Google, Microsoft...), fundos/VCs, aceleradoras, universidades, "
    "veículos de notícia, nem empresas estrangeiras.\n"
    "Devolva só os nomes próprios das empresas, limpos e sem duplicar."
)


def _coletar_texto(tema: str, top_n: int = 5) -> str:
    """Busca listas/notícias sobre o tema e devolve o texto raspado concatenado."""
    queries = [
        f"melhores startups brasileiras de IA {tema}",
        f"startups de inteligência artificial {tema} Brasil",
        f"site:startups.com.br {tema}",
    ]
    vistos: set[str] = set()
    partes: list[str] = []
    for q in queries:
        for hit in _buscar(q, top_n):
            url = hit.get("href") or hit.get("url") or ""
            if not url or url in vistos:
                continue
            vistos.add(url)
            if not permitido_por_robots(url):
                continue
            html = fetch_url(url)
            if not html:
                continue
            texto = extract_text(html)
            if texto.strip():
                partes.append(texto)
    return "\n\n---\n\n".join(partes)[:MAX_CONTEXTO]


def extrair_nomes(texto: str) -> list[str]:
    """LLM extrai os nomes de startups brasileiras de IA do texto (structured output)."""
    if not texto.strip():
        return []
    structured = chat().with_structured_output(ListaEmpresas, method="json_schema")
    resultado: ListaEmpresas = structured.invoke(f"{_INSTRUCAO}\n\nTEXTO:\n{texto}")
    return resultado.empresas


def descobrir(tema: str, n: int = 10) -> list[str]:
    """Tema → lista de até `n` nomes de startups brasileiras de IA (deduplicada)."""
    nomes = extrair_nomes(_coletar_texto(tema))
    vistos: set[str] = set()
    limpos: list[str] = []
    for nome in nomes:
        chave = nome.strip().lower()
        if not chave or chave in vistos:
            continue
        vistos.add(chave)
        limpos.append(nome.strip())
    return limpos[:n]


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--analisar"]
    analisar = "--analisar" in sys.argv
    tema = " ".join(args) or "startups brasileiras de IA"

    print(f"Descobrindo startups para: '{tema}'…\n")
    nomes = descobrir(tema)
    if not nomes:
        print("Nenhuma startup encontrada (busca pode ter falhado ou tema muito restrito).")
        return
    for i, nome in enumerate(nomes, 1):
        print(f"  {i:>2}. {nome}")

    if analisar:
        from app import batch
        print(f"\nAnalisando as {len(nomes)} empresas…")
        batch.analisar_lote(nomes)


if __name__ == "__main__":
    main()
