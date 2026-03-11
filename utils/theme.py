import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

CORES = {
    "primaria":  "#E50914",
    "secundaria":"#F5C518",
    "escuro":    "#141414",
    "superficie":"#1F1F1F",
    "texto":     "#FFFFFF",
    "suave":     "#CCCCCC",
    "positivo":  "#2ECC71",
    "negativo":  "#E74C3C",
    "destaque":  "#3498DB",
}

PALETA = [
    "#E50914", "#F5C518", "#3498DB", "#2ECC71",
    "#9B59B6", "#E67E22", "#1ABC9C", "#E91E63",
    "#00BCD4", "#FF5722",
]

COLORS  = CORES
PALETTE = PALETA


def aplicar_tema():
    plt.rcParams.update({
        "figure.facecolor":   CORES["escuro"],
        "axes.facecolor":     CORES["superficie"],
        "axes.edgecolor":     "#555555",
        "axes.labelcolor":    CORES["texto"],
        "axes.titlecolor":    CORES["texto"],
        "axes.titlesize":     15,
        "axes.titleweight":   "bold",
        "axes.labelsize":     13,
        "xtick.color":        CORES["texto"],
        "ytick.color":        CORES["texto"],
        "xtick.labelsize":    11,
        "ytick.labelsize":    11,
        "grid.color":         "#383838",
        "grid.linestyle":     "--",
        "grid.linewidth":     0.7,
        "text.color":         CORES["texto"],
        "legend.facecolor":   "#2A2A2A",
        "legend.edgecolor":   "#555555",
        "legend.labelcolor":  CORES["texto"],
        "legend.fontsize":    11,
        "font.family":        "DejaVu Sans",
    })
    sns.set_theme(style="darkgrid", palette=PALETA, rc={
        "figure.facecolor": CORES["escuro"],
        "axes.facecolor":   CORES["superficie"],
    })

apply_theme = aplicar_tema


def nova_figura(l=10, a=5):
    aplicar_tema()
    fig, ax = plt.subplots(figsize=(l, a), facecolor=CORES["escuro"])
    ax.set_facecolor(CORES["superficie"])
    return fig, ax

new_fig = nova_figura


def novas_figuras(linhas, colunas, l=14, a=6):
    aplicar_tema()
    fig, eixos = plt.subplots(linhas, colunas, figsize=(l, a), facecolor=CORES["escuro"])
    lista = eixos.flatten() if hasattr(eixos, "flatten") else [eixos]
    for ax in lista:
        ax.set_facecolor(CORES["superficie"])
    return fig, eixos

new_figs = novas_figuras


def formatar_eixo_milhoes(ax, eixo="y"):
    fmt = mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M")
    if eixo == "y":
        ax.yaxis.set_major_formatter(fmt)
    else:
        ax.xaxis.set_major_formatter(fmt)

fmt_millions = formatar_eixo_milhoes


def rotulos_nas_barras(ax, formato="{:.1f}", cor=None):
    cor = cor or CORES["texto"]
    for barra in ax.patches:
        h = barra.get_height()
        if h == 0:
            continue
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            h * 1.01,
            formato.format(h),
            ha="center", va="bottom",
            fontsize=9, color=cor, fontweight="bold",
        )

add_bar_labels = rotulos_nas_barras


CSS_STREAMLIT = """
<style>
.stApp { background-color: #141414; color: #FFFFFF; }

section[data-testid="stSidebar"] {
    background-color: #0A0A0A;
    border-right: 1px solid #2A2A2A;
}

div[data-testid="metric-container"] {
    background-color: #1F1F1F;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 14px 18px;
}
div[data-testid="metric-container"] label {
    color: #CCCCCC !important;
    font-size: 0.9rem !important;
}
div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
    color: #F5C518 !important;
    font-size: 1.7rem !important;
    font-weight: 700;
}

h1 { color: #E50914 !important; font-weight: 800; }
h2 { color: #F5C518 !important; }
h3 { color: #FFFFFF !important; }

.caixa-insight {
    background: linear-gradient(135deg, #1F1F1F 0%, #2A1A1A 100%);
    border-left: 4px solid #E50914;
    border-radius: 6px;
    padding: 14px 18px;
    margin: 10px 0;
    font-size: 0.95rem;
    line-height: 1.6;
    color: #FFFFFF;
}

div[data-baseweb="tab-list"] { background-color: #0A0A0A; }
button[data-baseweb="tab"] { color: #CCCCCC !important; font-size: 1rem !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #F5C518 !important; font-weight: 700 !important; }

div[data-baseweb="select"] > div { background-color: #1F1F1F !important; }
hr { border-color: #333333; }

div[data-testid="stDataFrame"] { border: 1px solid #333333; border-radius: 6px; }
</style>
"""


def injetar_css():
    st.markdown(CSS_STREAMLIT, unsafe_allow_html=True)

inject_css = injetar_css


def caixa_insight(texto):
    st.markdown(f'<div class="caixa-insight">💡 {texto}</div>', unsafe_allow_html=True)

insight_box = caixa_insight
