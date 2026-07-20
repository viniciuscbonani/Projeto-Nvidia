"""API HTTP do Radar — expõe o banco/pipeline para o frontend React.

    uvicorn app.api:app --reload

FastAPI é fino: lê o que já existe (db) e devolve JSON. O front (Next, :3000) consome.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app import db
from app.db import Empresa, SessionLocal

from pydantic import BaseModel
from app import batch
from app import discovery


app = FastAPI(title="NVIDIA Startup AI Radar API")

class AnalisarRequest(BaseModel):
    consulta: str


class DescobrirRequest(BaseModel):
    tema: str


# libera o front (Next em :3000) a chamar esta API (:8000) pelo navegador.
# Só vai importar no Passo 2, mas já deixamos pronto pra não esbarrar depois.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/empresas")
def listar_empresas() -> list[dict]:
    db.init_db()
    with SessionLocal() as sessao:
        empresas = sessao.query(Empresa).all()
        return [
            {
                "nome":e.nome,
                "setor": e.setor,
                "classificacao": e.classificacao,
                "score": e.score,
                "notas": e.notas,
            }
            for e in empresas
        ]

@app.get("/empresas/{nome}")
def detalhe_empresa(nome: str) -> dict:
    db.init_db()
    with SessionLocal() as sessao:
        e = sessao.query(Empresa).filter_by(nome=nome).first()
        if e is None:
            raise HTTPException(status_code=404, detail=f"Empresa '{nome}' não encontrada")
        return {
            "nome": e.nome,
            "setor": e.setor,
            "descricao": e.descricao,
            "dados": e.dados,  # dump do DadosEmpresa: founders, funding, clientes, tecnologias
            "classificacao": e.classificacao,
            "score": e.score,
            "notas": e.notas,
            "recomendacao": e.recomendacao,
            "briefing": e.briefing,
            "fontes": e.fontes,
        }

@app.post("/analisar")
def analisar_empresa(req: AnalisarRequest) -> dict:
    batch.analisar(req.consulta)  # roda o grafo e persiste (~1-2 min)
    return {"ok": True, "consulta": req.consulta}


@app.post("/descobrir")
def descobrir_startups(req: DescobrirRequest) -> dict:
    """Tema → lista de nomes de startups (busca web + LLM; lento, como /analisar).

    Só descobre NOMES; não analisa nem grava nada no banco. Erros de
    busca/LLM viram lista vazia (o front trata como 'nada encontrado').
    """
    try:
        nomes = discovery.descobrir(req.tema)
    except Exception:
        # loga no console do uvicorn (para diagnóstico) e devolve vazio,
        # que o front apresenta como "nada encontrado"
        import traceback

        traceback.print_exc()
        nomes = []
    return {"tema": req.tema, "nomes": nomes}
