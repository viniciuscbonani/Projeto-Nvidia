"""Grafo do pipeline (Fase 1 — esqueleto andante completo).

Os 8 nós (todos stubs) em linha reta, START → ... → END. Cada nó vive em seu
próprio arquivo; aqui só importamos e fazemos a fiação. As fases seguintes trocam
os stubs por lógica real e adicionam a aresta condicional e o loop (Fase 3).

    START → search_planner → scraper → extractor → classifier
          → evidence_validator → nvidia_rag → recommendation → briefing → END
"""

from langgraph.graph import END, START, StateGraph

from app.state import RadarState
from app.search_planner import search_planner
from app.scraper import scraper
from app.extractor import extractor
from app.classifier import classifier
from app.evidence_validator import evidence_validator
from app.nvidia_rag import nvidia_rag
from app.recommendation import recommendation
from app.briefing import briefing


# Ordem do pipeline (linha reta). Para mudar o fluxo, mexa só aqui.
NODES = [
    ("search_planner", search_planner),
    ("scraper", scraper),
    ("extractor", extractor),
    ("classifier", classifier),
    ("evidence_validator", evidence_validator),
    ("nvidia_rag", nvidia_rag),
    ("recommendation", recommendation),
    ("briefing", briefing),
]


def build_graph():
    builder = StateGraph(RadarState)
    for name, fn in NODES:
        builder.add_node(name, fn)
    builder.add_edge(START, NODES[0][0])
    for (origem, _), (destino, _) in zip(NODES, NODES[1:]):
        builder.add_edge(origem, destino)
    builder.add_edge(NODES[-1][0], END)
    return builder.compile()


graph = build_graph()


if __name__ == "__main__":
    final = graph.invoke(RadarState(consulta="Tractian"))
    # invoke devolve os valores do State como dict
    briefing_text = final["briefing"] if isinstance(final, dict) else final.briefing
    print(briefing_text)
