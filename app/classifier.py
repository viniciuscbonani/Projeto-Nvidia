"""Startup Classifier — aplica os 3 eixos AI-native.

Aplica os 3 eixos AI-native (CLAUDE.md "Conceitos de domínio") sobre os dados
estruturados, via LLM com structured output. Devolve um rótulo
(ai-native | ai-enabled | non-ai) — usado pelo desvio condicional do grafo — e a
análise por eixo (rastreabilidade). Função de classificação separada do nó.
"""

from langchain_openai import ChatOpenAI

from app.config import settings
from app.state import Classificacao, DadosEmpresa, RadarState

_INSTRUCAO = (
    "Você classifica a maturidade 'AI-native' de uma startup em 3 eixos:\n"
    "1) Produto: a IA é o core do valor, não um feature? (teste: se remove a IA, sobra produto?)\n"
    "2) Dados e modelo: tem dado proprietário e/ou treina/serve modelo próprio, "
    "em vez de só chamar API de terceiro?\n"
    "3) Stack técnica: controla custo/latência da própria inferência (sinal forte: GPU/infra própria)?\n\n"
    "Rótulos: 'ai-native' (IA é o core nos 3 eixos), 'ai-enabled' (usa IA como "
    "feature/wrapper), 'non-ai' (não usa IA de forma relevante). Avalie só pelo "
    "texto; não invente. Responda no schema pedido."
)


def classificar(dados: DadosEmpresa) -> Classificacao:
    """Chama o LLM com structured output e devolve uma Classificacao."""
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    structured = llm.with_structured_output(Classificacao, method="json_schema")
    prompt = f"{_INSTRUCAO}\n\nDados da empresa:\n{dados.model_dump_json(indent=2)}"
    return structured.invoke(prompt)


def classifier(state: RadarState) -> dict:
    dados = state.dados_estruturados or DadosEmpresa(nome=state.consulta)
    # se nada foi coletado (ex.: busca bloqueada), não dá para classificar:
    # rotular honestamente como "sem-dados" em vez de chutar "non-ai".
    if not (dados.setor or dados.descricao or dados.tecnologias):
        return {"classificacao": "sem-dados"}
    c = classificar(dados)
    return {"classificacao": c.rotulo, "classificacao_detalhe": c}
