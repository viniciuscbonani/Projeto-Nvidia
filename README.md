# NVIDIA Startup AI Radar

> Liga de IA do Inteli × NVIDIA — plataforma multiagente para **mapear, qualificar e priorizar startups brasileiras de IA**.

## Resumo

O **NVIDIA Startup AI Radar** é um sistema de inteligência de mercado para a gerência de **Startups & VCs da NVIDIA**. Dado um tema ou uma lista de empresas, ele:

1. **Descobre e coleta** dados públicos de startups brasileiras de IA;
2. **Classifica** a maturidade técnica de cada uma (eixo *AI-native*);
3. **Recomenda** tecnologias NVIDIA com base no *gap* técnico real da empresa;
4. **Calcula um score composto** (ponderado e ajustável) para ranquear o portfólio;
5. **Redige um briefing executivo** em linguagem de negócio para o *founder* — custo por token, latência, defensibilidade — e não como catálogo de produto.

É um **sistema multiagente orquestrado em LangGraph**, com desvio condicional (descarta *non-AI*) e loop com teto de tentativas (re-coleta quando falta evidência) — o tipo de fluxo que uma cadeia linear de prompts não permite.

A recomendação raciocina sobre o **"bolo de 5 camadas" da NVIDIA** (Energia → Chips → Infra → Models → Applications): identifica em qual camada está o gap da startup e sugere a tecnologia correspondente (ex.: gap em *serving* de modelos → NIM / Triton / TensorRT-LLM; robótica → Isaac / Omniverse). Para não alucinar specs, as recomendações vêm ancoradas em um **RAG** sobre a documentação técnica oficial da NVIDIA.

## Arquitetura

### Pipeline de 8 agentes (nós do LangGraph)

Todos os nós compartilham um **State Pydantic** (`RadarState`) — a "ficha" que viaja pelo fluxo. Cada nó lê campos, preenche outros e retorna **só o que atualizou** (dict parcial; o LangGraph mescla no State).

```
START → Search Planner → Scraper → Extractor → Classifier
        → [non-ai?  → END]                              (aresta condicional: descarta)
        → Evidence Validator
        → [evidência insuficiente? → volta ao Scraper]  (loop, com teto max_tentativas)
        → NVIDIA RAG → Recommendation → Briefing → END
```

| Agente | Papel |
|---|---|
| **Search Planner** | Transforma a consulta do usuário em plano de busca (termos + fontes). |
| **Scraper** | Coleta conteúdo público; guarda a fonte de cada trecho (rastreabilidade). |
| **Extractor** | *Structured output* (Pydantic) → preenche o schema da empresa. |
| **Classifier** | Aplica os 3 eixos *AI-native*; ponto do desvio condicional. |
| **Evidence Validator** | Checa se há fonte suficiente; ponto do loop (volta ao Scraper). |
| **NVIDIA RAG** | Recupera contexto técnico da base de conhecimento NVIDIA (híbrida + rerank). |
| **Recommendation** | Cruza gaps × portfólio NVIDIA, calcula o score, monta a recomendação. |
| **Briefing** | Redige o relatório executivo final. |

### Os dois bancos

- **Relacional** — dados estruturados das empresas (raspados + resultado da análise). SQLite (`radar.db`) por padrão; **PostgreSQL** via Docker quando configurado. Tipos portáveis (sem `JSONB`/`ARRAY`), então a migração é só trocar a `DATABASE_URL`.
- **Vetorial (Qdrant)** — base de conhecimento NVIDIA (embeddings). Modo **local embarcado** (`QDRANT_PATH=./qdrant`, sem servidor) ou **Qdrant-servidor** via Docker (`QDRANT_URL`). Escolhido em vez do Chroma pela **busca híbrida nativa** (denso + esparso/BM25).

### RAG em duas fases

- **Offline (ingestão, roda uma vez):** docs NVIDIA → *chunking* por seção → embeddings → Qdrant, guardando a fonte de cada chunk. Entrypoint: `python -m app.ingest`.
- **Online (a cada pergunta):** retrieve híbrido (vetorial + BM25) traz ~50 candidatos (recall) → **Cohere Rerank** reordena para o top-5 (precisão) → contexto enxuto + citações → LLM gera.

### Score composto

Não é rótulo binário; é uma soma ponderada com pesos **ajustáveis na UI** (re-rank ao vivo):

```
Score = w1·AI-Native + w2·NVIDIA-Fit (tamanho do gap/uplift) + w3·Tração/VC + w4·Time de IA
```

## Stack técnica

- **Python 3.11+** (desenvolvido em 3.13, na `.venv`).
- **LangGraph 1.x** (orquestração) + **LangChain** (utilidades).
- **Pydantic 2** — State e schemas de extração.
- **LLM:** **Groq** (`gpt-oss-20b`, grátis) via `GROQ_API_KEY`; *fallback* para OpenAI.
- **Embeddings:** **Gemini** (`gemini-embedding-001`, multilíngue, grátis) via `GEMINI_API_KEY`. Alternativas: `EMBEDDING_PROVIDER=openai` ou `=local` (fastembed, offline).
- **Rerank:** **Cohere** (`rerank-v3.5`).
- **Vetorial:** Qdrant (`qdrant-client[fastembed]`).
- **Relacional:** SQLAlchemy 2 → SQLite / PostgreSQL (`psycopg`).
- **Scraping:** trafilatura + BeautifulSoup + ddgs (busca multi-backend).
- **Frontend:** Streamlit.

## Pré-requisitos

- Python 3.11+
- Chaves de API no `.env` (copie de `.env.example`): `GROQ_API_KEY`, `GEMINI_API_KEY`, `COHERE_API_KEY`. `OPENAI_API_KEY` é opcional (fallback de LLM / embeddings).
- (Opcional) Docker, para subir PostgreSQL + Qdrant-servidor.

## Como rodar

### 1. Ambiente e dependências

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .            # instala o app + deps do pyproject.toml
# (dev) pip install -e ".[dev]"
```

### 2. Configuração

```bash
cp .env.example .env        # preencha as chaves de API
```

Por padrão o `.env.example` aponta para os bancos via Docker. Para rodar **sem servidor** (mais simples), use no `.env`:

```env
DATABASE_URL=sqlite:///radar.db
# QDRANT_URL vazio e:
QDRANT_PATH=./qdrant
```

### 3. (Opcional) Subir os bancos via Docker

```bash
docker compose up -d        # PostgreSQL (5432) + Qdrant-servidor (6333)
```

### 4. Popular a base NVIDIA no Qdrant (roda UMA vez, offline)

```bash
python -m app.ingest        # embeddings Gemini (grátis). ~3min pelo throttle do tier free.
# ou: EMBEDDING_PROVIDER=local python -m app.ingest   (offline, sem chave)
```

### 5. Usar

```bash
# descobrir startups brasileiras de IA por tema (gera a lista de nomes)
python -m app.discovery "startups brasileiras de IA em saúde"
python -m app.discovery "<tema>" --analisar      # encadeia direto para o batch

# analisar empresas em lote — roda o grafo por empresa e PERSISTE no banco
python -m app.batch "Tractian" "Gupy"

# interface web (ranking + detalhe + export + sliders de pesos + avaliar RAG)
streamlit run app/ui.py

# avaliar a qualidade do RAG (hit@k sobre perguntas-âncora)
python -m app.eval_rag

# rodar 1 empresa sem persistir (debug): imprime classificação / score / briefing
python -m app.graph
```

> ⚠️ O schema do `radar.db` evoluiu sem Alembic. Se vier de uma versão antiga em SQLite, apague antes: `rm -f radar.db`.

### Testes

Offline — busca, rede, LLM e Qdrant são *monkeypatchados* (sem custo, sem chaves).

```bash
python -m pytest -q
python -m pytest tests/test_db.py::test_salvar_resultado_faz_upsert    # um único teste
```

## Estrutura de pastas

```
ProjetoNvidia/
├── README.md / CLAUDE.md
├── .env / .env.example
├── pyproject.toml
├── docker-compose.yml          # PostgreSQL + Qdrant-servidor (opcional)
├── app/
│   ├── config.py               # settings (lê o .env): chaves, bancos, RAG, pesos do score
│   ├── state.py                # RadarState + DadosEmpresa + Classificacao + Recomendacao + Score
│   ├── sources.py              # fontes de busca + domínios + NVIDIA_DOCS (18 URLs)
│   ├── db.py                   # SQLAlchemy: modelo Empresa + salvar_resultado (upsert por nome)
│   ├── llm.py                  # chat(): cliente LLM apontado para a Groq
│   ├── rag.py                  # infra RAG: Qdrant + chunk + embed + híbrida + rerank
│   ├── ingest.py               # entrypoint OFFLINE: popula o Qdrant
│   ├── score.py                # compor(notas, pesos): soma ponderada do score
│   ├── eval_rag.py             # avaliação de RAG (hit@k)
│   ├── graph.py                # fiação dos 8 nós + arestas condicionais (desvio/loop)
│   ├── batch.py                # runner: analisar(consulta) = invoke + persistência
│   ├── discovery.py            # descoberta autônoma de startups por tema
│   ├── ui.py                   # Streamlit
│   ├── search_planner.py · scraper.py · extractor.py · classifier.py
│   ├── evidence_validator.py · nvidia_rag.py · recommendation.py · briefing.py
└── tests/                      # offline (rede/LLM/Qdrant monkeypatchados)
```

## Conceitos de domínio

**"AI-native"** — medido em 3 eixos pelo Classifier:

1. **Produto:** a IA é o core do valor, não um feature. Teste: se remove a IA, sobra produto?
2. **Dados e modelo:** tem dado proprietário e/ou treina/serve modelo próprio, em vez de só chamar API de terceiro.
3. **Stack técnica:** controla custo/latência da própria inferência (sinal forte: GPU/infra própria).

Rótulos: `ai-native`, `ai-enabled`, `non-ai`. **Tractian** é o caso de referência "nota 10" e a empresa de teste ponta a ponta.

## Os 6 entregáveis

1. Pipeline de scraping multiplataforma.
2. Sistema multiagente em LangGraph.
3. RAG da base NVIDIA com reranking.
4. Motor de recomendação (score + briefing).
5. Interface web.
6. Diferencial: pesos de ranking configuráveis ("modo caça-Tractian") + avaliação de qualidade do RAG.

**Status:** os 6 entregáveis estão completos. Evolução futura: mais empresas no lote, refinamento contínuo do RAG/briefing, migração plena para PostgreSQL/Qdrant-servidor.

## Princípios de construção

- **Esqueleto andante primeiro:** rodar de ponta a ponta com stubs, depois aprofundar cada nó.
- **Uma empresa antes de muitas:** validar o fluxo com a Tractian antes de escalar.
- **Um grafo por empresa:** para escala, rodar o mesmo grafo por empresa em lote — não um grafo gigante.
- **Loop sempre com teto** (`max_tentativas`), para nunca rodar infinito.
- **Tipos portáveis no banco relacional** (SQLite ↔ PostgreSQL).
- **Rastreabilidade de fonte:** toda afirmação e toda recomendação citam a origem; não inventar specs nem nomes de produto NVIDIA — daí o RAG.
- **Respeitar ToU e robots.txt** na coleta (atenção ao LinkedIn).
