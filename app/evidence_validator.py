"""Evidence Validator — grounding (faithfulness check) dos fatos da empresa.

Antes de seguir para o RAG, checa se as afirmações que o Extractor produziu
(`dados_estruturados`) estão de fato sustentadas pelos trechos coletados
(`conteudo_bruto`) — não apenas se há fontes suficientes. Conceito:
Chain-of-Verification / grounding.

Duas camadas:
  1. `estrutura_suficiente` — pré-gate barato, sem LLM (≥ 3 domínios de fonte
     distintos E `setor`/`descricao` preenchidos). Rodadas magras nem chamam o LLM.
  2. `verificar_afirmacoes` — o faithfulness check por LLM: para cada campo não-vazio,
     diz se algum trecho o sustenta e qual a fonte. Campos de ALTO RISCO sem lastro
     (funding/founders/clientes) são removidos de `dados_estruturados`; o veredito de
     cada afirmação é registrado em `afirmacoes_verificadas` (rastreabilidade).

É o ponto do loop: se a evidência for insuficiente e ainda houver tentativas, o grafo
volta ao Search Planner (teto em `tentativas`). Incrementa `tentativas` a cada checagem.
Sem chave LLM / `grounding_habilitado=False` cai para a regra mecânica (só a camada 1).
"""

from typing import Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field

from app.config import settings
from app.llm import chat
from app.state import DadosEmpresa, RadarState, VerificacaoAfirmacao

MIN_DOMINIOS = 3   # piso de fontes distintas; rodadas magras voltam ao Scraper (loop)

# Campos factuais que mais machucam se alucinados: removidos quando sem lastro.
CAMPOS_ALTO_RISCO = ("funding", "founders", "clientes")

# teto de contexto enviado ao LLM (evita estourar tokens com páginas longas)
MAX_CONTEXTO = 12000


def _dominio(url: str) -> str:
    host = urlparse(url).netloc.lower()
    return host[4:] if host.startswith("www.") else host


def estrutura_suficiente(state: RadarState) -> bool:
    """Pré-gate mecânico (sem LLM): ≥ MIN_DOMINIOS fontes distintas E campos-chave."""
    dominios = {_dominio(t.get("fonte", "")) for t in state.conteudo_bruto}
    dominios.discard("")
    dados = state.dados_estruturados
    campos_ok = bool(dados and dados.setor and dados.descricao)
    return len(dominios) >= MIN_DOMINIOS and campos_ok


class _Veredito(BaseModel):
    campo: str
    sustentada: bool = False
    fonte: Optional[str] = None


class _SaidaGrounding(BaseModel):
    vereditos: list[_Veredito] = Field(default_factory=list)


_INSTRUCAO = (
    "Você audita afirmações sobre uma startup contra os TRECHOS coletados de páginas web. "
    "Para CADA afirmação listada, decida se algum trecho a sustenta explicitamente. "
    "Se sim, marque sustentada=true e informe a URL (fonte) do trecho que a sustenta. "
    "Se nenhum trecho a sustenta, marque sustentada=false e deixe fonte vazia. "
    "Não use conhecimento externo nem infira; julgue SÓ pelos trechos. Responda no schema pedido."
)


def _afirmacoes(dados: DadosEmpresa) -> list[tuple[str, str]]:
    """Extrai pares (campo, valor) dos campos não-vazios a verificar."""
    pares: list[tuple[str, str]] = []
    if dados.setor:
        pares.append(("setor", dados.setor))
    if dados.descricao:
        pares.append(("descricao", dados.descricao))
    if dados.funding:
        pares.append(("funding", dados.funding))
    for f in dados.founders:
        pares.append(("founders", f))
    for c in dados.clientes:
        pares.append(("clientes", c))
    for t in dados.tecnologias:
        pares.append(("tecnologias", t))
    return pares


def verificar_afirmacoes(
    dados: DadosEmpresa, conteudo_bruto: list[dict]
) -> list[VerificacaoAfirmacao]:
    """Faithfulness check por LLM: cada afirmação × trechos → veredito + fonte."""
    pares = _afirmacoes(dados)
    if not pares:
        return []

    trechos = "\n\n---\n\n".join(
        f"[fonte: {t.get('fonte', '')}]\n{t.get('texto', '')}" for t in conteudo_bruto
    )[:MAX_CONTEXTO]
    lista = "\n".join(f"- {campo}: {valor}" for campo, valor in pares)
    prompt = (
        f"{_INSTRUCAO}\n\n"
        f"EMPRESA-ALVO: {dados.nome}\n\n"
        f"AFIRMAÇÕES A VERIFICAR:\n{lista}\n\n"
        f"TRECHOS COLETADOS:\n{trechos}"
    )
    structured = chat().with_structured_output(_SaidaGrounding, method="json_schema")
    saida: _SaidaGrounding = structured.invoke(prompt)

    # casa cada par (na ordem) com o veredito de mesmo campo; default = não sustentada
    vereditos_por_campo: dict[str, list[_Veredito]] = {}
    for v in saida.vereditos:
        vereditos_por_campo.setdefault(v.campo, []).append(v)

    resultado: list[VerificacaoAfirmacao] = []
    consumidos: dict[str, int] = {}
    for campo, valor in pares:
        fila = vereditos_por_campo.get(campo, [])
        i = consumidos.get(campo, 0)
        v = fila[i] if i < len(fila) else None
        consumidos[campo] = i + 1
        resultado.append(
            VerificacaoAfirmacao(
                campo=campo,
                valor=valor,
                sustentada=bool(v and v.sustentada),
                fonte=(v.fonte if v and v.sustentada else None),
            )
        )
    return resultado


def _campo_sustentado(vereditos: list[VerificacaoAfirmacao], campo: str) -> bool:
    """True se o campo aparece e todas as suas afirmações estão sustentadas."""
    do_campo = [v for v in vereditos if v.campo == campo]
    return bool(do_campo) and all(v.sustentada for v in do_campo)


def _limpar_alto_risco(
    dados: DadosEmpresa, vereditos: list[VerificacaoAfirmacao]
) -> DadosEmpresa:
    """Remove de uma cópia dos dados os campos de alto risco sem lastro."""
    limpo = dados.model_copy(deep=True)
    nao_sustentados = {
        (v.campo, v.valor) for v in vereditos if not v.sustentada
    }
    if ("funding", limpo.funding or "") in nao_sustentados:
        limpo.funding = None
    limpo.founders = [f for f in limpo.founders if ("founders", f) not in nao_sustentados]
    limpo.clientes = [c for c in limpo.clientes if ("clientes", c) not in nao_sustentados]
    return limpo


def evidence_validator(state: RadarState) -> dict:
    tentativas = state.tentativas + 1
    dados = state.dados_estruturados

    # Fallback mecânico: sem grounding, sem chave LLM, ou nada para verificar.
    if (
        not settings.grounding_habilitado
        or not settings.llm_api_key
        or not dados
        or not state.conteudo_bruto
    ):
        return {"evidencias_ok": estrutura_suficiente(state), "tentativas": tentativas}

    vereditos = verificar_afirmacoes(dados, state.conteudo_bruto)
    dados_limpo = _limpar_alto_risco(dados, vereditos)

    # gate estrito: estrutura OK E os campos-chave de fato ancorados nas fontes
    evidencias_ok = (
        estrutura_suficiente(state)
        and _campo_sustentado(vereditos, "setor")
        and _campo_sustentado(vereditos, "descricao")
    )
    return {
        "evidencias_ok": evidencias_ok,
        "afirmacoes_verificadas": vereditos,
        "dados_estruturados": dados_limpo,
        "tentativas": tentativas,
    }
