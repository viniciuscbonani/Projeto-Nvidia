"""Olá-mundo do grafo (Fase 0).

Dois nós stub em linha reta — só para provar que o LangGraph orquestra o
RadarState de ponta a ponta. As fases seguintes substituem estes stubs pelos
8 agentes reais e adicionam a aresta condicional e o loop.

    START → search_planner → briefing → END
"""

from langgraph.graph import END, START, StateGraph

from app.state import RadarState


def search_planner(state: RadarState) -> dict:
    """Stub: por enquanto só transforma a consulta num único alvo."""
    alvo = state.consulta.strip() or "Tractian"
    return {"alvos": [alvo]}


def briefing(state: RadarState) -> dict:
    """Stub: monta um briefing-placeholder a partir do alvo."""
    alvo = state.alvos[0] if state.alvos else "(sem alvo)"
    texto = (
        f"Briefing (stub) — {alvo}\n"
        "Pipeline ainda não implementado: este é o esqueleto andante da Fase 0."
    )
    return {"briefing": texto}


def build_graph():
    builder = StateGraph(RadarState)
    builder.add_node("search_planner", search_planner)
    builder.add_node("briefing", briefing)
    builder.add_edge(START, "search_planner")
    builder.add_edge("search_planner", "briefing")
    builder.add_edge("briefing", END)
    return builder.compile()


graph = build_graph()


if __name__ == "__main__":
    final = graph.invoke(RadarState(consulta="Tractian"))
    # invoke devolve os valores do State como dict
    briefing_text = final["briefing"] if isinstance(final, dict) else final.briefing
    print(briefing_text)
