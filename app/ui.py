"""Interface web (Streamlit) — dashboard rankeado + analisar nova + exportar.

    streamlit run app/ui.py

Lê o banco (resultados persistidos pelo runner) e permite analisar uma empresa
nova on-demand (roda o grafo na hora).
"""

import sys
from pathlib import Path

# `streamlit run app/ui.py` executa o arquivo direto e não põe a raiz do projeto
# no sys.path → garante que `app` seja importável.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import streamlit as st

from app import batch, db
from app.db import Empresa, SessionLocal

st.set_page_config(page_title="NVIDIA Startup AI Radar", layout="wide")
st.title("🟢 NVIDIA Startup AI Radar")

db.init_db()

# --- analisar nova empresa (on-demand) ---
with st.sidebar:
    st.header("Analisar nova empresa")
    nome = st.text_input("Empresa ou consulta")
    if st.button("Analisar", type="primary") and nome.strip():
        with st.spinner(f"Rodando o pipeline para '{nome}'… (~1–2 min)"):
            batch.analisar(nome.strip())
        st.success("Análise concluída.")
        st.rerun()

# --- carregar resultados ---
with SessionLocal() as sessao:
    empresas = sessao.query(Empresa).all()
empresas.sort(key=lambda e: e.score if e.score is not None else -1, reverse=True)

if not empresas:
    st.info("Nenhuma empresa analisada ainda. Use a barra lateral para analisar uma.")
    st.stop()

# --- ranking ---
st.subheader("Ranking por score")
st.dataframe(
    [{"Empresa": e.nome, "Score": e.score, "Classificação": e.classificacao} for e in empresas],
    width="stretch",
    hide_index=True,
)

# --- detalhe ---
sel = st.selectbox("Ver detalhe de:", [e.nome for e in empresas])
e = next(x for x in empresas if x.nome == sel)

col1, col2 = st.columns([1, 2])
with col1:
    st.metric("Score composto", e.score if e.score is not None else "—")
    st.write(f"**Classificação:** {e.classificacao or '—'}")
    st.write(f"**Setor:** {e.setor or '—'}")
    if e.notas:
        st.write("**Notas (0–10):**")
        st.json({k: e.notas[k] for k in ("ai_native", "nvidia_fit", "tracao", "time_ia") if k in e.notas})
    if e.recomendacao:
        st.write("**Tecnologias NVIDIA:** " + ", ".join(e.recomendacao.get("tecnologias", [])))
        if e.recomendacao.get("evidencias"):
            st.write("**Evidências:**")
            for u in e.recomendacao["evidencias"]:
                st.write(f"- {u}")
with col2:
    st.markdown("### Briefing executivo")
    st.markdown(e.briefing or "_(sem briefing — empresa non-ai ou não analisada)_")
    if e.briefing:
        st.download_button("⬇️ Exportar briefing (.md)", e.briefing, file_name=f"briefing_{e.nome}.md")
