import streamlit as st
import pandas as pd
import os, datetime, tempfile

st.set_page_config(
    page_title="Foundation Frame Studios — Análise de Filmes",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils import injetar_css, load_and_merge, load_single, load_sample

injetar_css()

LOGO_PATH = "assets/logo.png"

@st.cache_data(show_spinner="Carregando e processando a base de dados…")
def carregar_unico(caminho):
    return load_single(caminho)

@st.cache_data(show_spinner="Carregando e processando a base de dados…")
def carregar_duplo(c1, c2):
    return load_and_merge(c1, c2)

with st.sidebar:
    if os.path.exists(LOGO_PATH):
        st.image(LOGO_PATH, use_container_width=True)
    else:
        st.title("🎬 Foundation Frame Studios")

    st.markdown("---")
    st.subheader("📂 Base de Dados")

    modo = st.radio(
        "Formato do arquivo",
        ["📄 Um único CSV (novo formato TMDB+IMDb)",
         "📑 Dois CSVs (formato TMDB 5000 antigo)",
         "🔬 Usar dados de demonstração"],
        index=0,
    )

    caminho1 = caminho2 = tmp_unico = None

    if modo.startswith("📄"):
        arq = st.file_uploader(
            "Arquivo CSV unificado",
            type="csv",
            help="Novo dataset com ~400k filmes (tmdb_imdb_merged...csv)",
        )
        if arq:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            tmp.write(arq.read()); tmp.close()
            tmp_unico = tmp.name
            st.success(f"✅ **{arq.name}** carregado!")
        elif os.path.exists("data/tmdb_imdb_merged.csv"):
            tmp_unico = "data/tmdb_imdb_merged.csv"
            st.success("✅ Base detectada em `data/`")
        else:
            st.info(
                "Faça o download em:\n"
                "**kaggle.com/datasets/ggtejas/tmdb-imdb-merged-movies-dataset**\n\n"
                "e arraste o CSV aqui."
            )

    elif modo.startswith("📑"):
        arq1 = st.file_uploader("Arquivo de filmes (tmdb_5000_movies.csv)",  type="csv", key="f1")
        arq2 = st.file_uploader("Arquivo de créditos (tmdb_5000_credits.csv)", type="csv", key="f2")
        if arq1 and arq2:
            t1 = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            t2 = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
            t1.write(arq1.read()); t1.close()
            t2.write(arq2.read()); t2.close()
            caminho1, caminho2 = t1.name, t2.name
            st.success("✅ Dois arquivos carregados!")
        elif os.path.exists("data/tmdb_5000_movies.csv") and os.path.exists("data/tmdb_5000_credits.csv"):
            caminho1 = "data/tmdb_5000_movies.csv"
            caminho2 = "data/tmdb_5000_credits.csv"
            st.success("✅ Base TMDB 5000 detectada em `data/`")
        else:
            st.info("Aguardando os dois arquivos CSV…")

    st.markdown("---")
    st.subheader("🔧 Filtros Globais")
    slot_ano    = st.empty()
    slot_rating = st.empty()
    st.markdown("---")
    st.caption("Foundation Frame Studios © 2025")

if modo.startswith("🔬"):
    df_bruto = load_sample()
elif modo.startswith("📄") and tmp_unico:
    df_bruto = carregar_unico(tmp_unico)
elif modo.startswith("📑") and caminho1 and caminho2:
    df_bruto = carregar_duplo(caminho1, caminho2)
else:
    df_bruto = load_sample()

col_ano    = next((c for c in ("year","ano") if c in df_bruto.columns), None)
col_rating = next((c for c in ("rating","avaliacao","vote_average") if c in df_bruto.columns), None)

with slot_ano:
    if col_ano:
        anos = df_bruto[col_ano].dropna()
        a_min, a_max = int(anos.min()), int(anos.max())
        intervalo_ano = st.slider("Período (ano de lançamento)", a_min, a_max, (a_min, a_max))
    else:
        intervalo_ano = None

with slot_rating:
    if col_rating:
        avaliacao_min = st.slider("Avaliação mínima (0–10)", 0.0, 10.0, 0.0, 0.5)
    else:
        avaliacao_min = 0.0

df = df_bruto.copy()
if intervalo_ano and col_ano:
    df = df[(df[col_ano] >= intervalo_ano[0]) & (df[col_ano] <= intervalo_ano[1])]
if col_rating:
    df = df[df[col_rating] >= avaliacao_min]

if os.path.exists(LOGO_PATH):
    c1, c2 = st.columns([1, 4])
    with c1:
        st.image(LOGO_PATH, width=160)
    with c2:
        st.markdown(
            "<h1 style='margin-top:20px;color:#E50914;'>Análise de Filmes</h1>"
            "<p style='color:#CCCCCC;margin-top:-8px;'>"
            "Base de dados TMDB+IMDb — Insights para produtores de cinema</p>",
            unsafe_allow_html=True,
        )
else:
    st.title("🎬 Análise de Filmes — Foundation Frame Studios")

n_fmt = f"{len(df):,}"
st.markdown(f"**{n_fmt} filmes** carregados com os filtros aplicados.")
st.markdown("---")

abas = st.tabs(["🏠 Visão Geral","🎭 Gêneros","💰 Financeiro","🎬 Diretores"])

from pages.overview  import render as pg_overview
from pages.genres    import render as pg_genres
from pages.financial import render as pg_financial
from pages.directors import render as pg_directors

with abas[0]: pg_overview(df)
with abas[1]: pg_genres(df)
with abas[2]: pg_financial(df)
with abas[3]: pg_directors(df)

with st.sidebar:
    st.subheader("📄 Relatório em PDF")
    st.caption("Exporta todas as análises com gráficos e recomendações.")
    if st.button("📥 Gerar Relatório PDF", use_container_width=True, type="primary"):
        with st.spinner("Gerando relatório… aguarde."):
            from utils import gerar_relatorio_pdf
            try:
                pdf   = gerar_relatorio_pdf(df)
                nome  = f"relatorio_ffs_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
                st.sidebar.download_button("⬇️ Baixar PDF", pdf, nome,
                                           "application/pdf", use_container_width=True)
                st.sidebar.success("✅ Relatório pronto!")
            except Exception as e:
                st.sidebar.error(f"Erro: {e}")
