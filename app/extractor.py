"""Extractor (Fase 2 — real).

Transforma o conteúdo bruto coletado em dados estruturados (structured output via
LLM OpenAI, schema DadosEmpresa) e grava no banco relacional (SQLite). A extração
e a persistência são funções separadas do nó, para serem testáveis sem LLM/banco.
"""

from langchain_openai import ChatOpenAI

from app.config import settings
from app.db import Empresa, SessionLocal, init_db
from app.state import DadosEmpresa, RadarState

# teto de contexto enviado ao LLM (evita estourar tokens com páginas longas)
MAX_CONTEXTO = 12000

_INSTRUCAO = (
    "Você extrai dados públicos de uma startup a partir de trechos de páginas web. "
    "Preencha apenas com o que estiver no texto; não invente. Deixe campos vazios "
    "quando não houver informação. Responda no schema pedido."
)


def extract_dados(textos: list[str], nome: str, fontes: list[str]) -> DadosEmpresa:
    """Chama o LLM com structured output e devolve um DadosEmpresa."""
    contexto = "\n\n---\n\n".join(textos)[:MAX_CONTEXTO]
    llm = ChatOpenAI(
        model=settings.llm_model,
        temperature=0,
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
    )
    # json_schema = saída estruturada nativa (Groq e OpenAI). Mais robusto que
    # function_calling, que na Groq às vezes prefixa a tool com "functions." e quebra.
    structured = llm.with_structured_output(DadosEmpresa, method="json_schema")
    prompt = f"{_INSTRUCAO}\n\nEmpresa-alvo: {nome}\n\nTrechos:\n{contexto}"
    dados: DadosEmpresa = structured.invoke(prompt)

    # garante rastreabilidade e identidade mínimas
    if not dados.nome:
        dados.nome = nome
    if not dados.fontes:
        dados.fontes = fontes
    return dados


def salvar_empresa(dados: DadosEmpresa) -> None:
    """Persiste o DadosEmpresa como uma linha em `empresas` (SQLite)."""
    init_db()
    with SessionLocal() as sessao:
        sessao.add(
            Empresa(
                nome=dados.nome,
                setor=dados.setor,
                descricao=dados.descricao,
                dados=dados.model_dump(),
                fontes=dados.fontes,
            )
        )
        sessao.commit()


def extractor(state: RadarState) -> dict:
    nome = state.alvos[0] if state.alvos else state.consulta
    textos = [t["texto"] for t in state.conteudo_bruto]
    fontes = [t["fonte"] for t in state.conteudo_bruto]

    if textos:
        dados = extract_dados(textos, nome=nome, fontes=fontes)
    else:
        dados = DadosEmpresa(nome=nome, fontes=fontes)

    salvar_empresa(dados)
    return {"dados_estruturados": dados}
