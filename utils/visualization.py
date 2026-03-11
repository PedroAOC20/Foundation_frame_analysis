import io
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

from .theme import CORES, PALETA, nova_figura, novas_figuras, aplicar_tema
from .analysis import (
    expandir_generos, popularidade_por_genero, quantidade_por_genero,
    financeiro_por_genero, faixas_orcamento, filmes_lucrativos,
    analise_duracao, estatisticas_diretores,
)


def _fig_para_bytes(fig) -> bytes:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight",
                facecolor=fig.get_facecolor())
    buf.seek(0)
    dados = buf.read()
    plt.close(fig)
    return dados


def grafico_producao_por_ano(df: pd.DataFrame) -> bytes:
    if "year" not in df.columns:
        return b""
    por_ano = df.groupby("year").agg(
        quantidade=("title", "count"),
        media_rating=("rating", "mean"),
    ).reset_index()

    fig, ax1 = plt.subplots(figsize=(12, 4), facecolor=CORES["escuro"])
    ax1.set_facecolor(CORES["superficie"])
    ax2 = ax1.twinx()

    ax1.fill_between(por_ano["year"], por_ano["quantidade"], alpha=0.35, color=CORES["primaria"])
    ax1.plot(por_ano["year"], por_ano["quantidade"], color=CORES["primaria"], linewidth=2.5)
    ax1.set_ylabel("Número de Filmes", color=CORES["primaria"], fontsize=13)
    ax1.tick_params(axis="y", colors=CORES["primaria"], labelsize=11)
    ax1.tick_params(axis="x", colors=CORES["texto"],   labelsize=11)
    ax1.set_xlabel("Ano", color=CORES["texto"], fontsize=13)

    ax2.plot(por_ano["year"], por_ano["media_rating"],
             color=CORES["secundaria"], linewidth=2.5, linestyle="--",
             marker="o", markersize=3)
    ax2.set_ylabel("Rating Médio", color=CORES["secundaria"], fontsize=13)
    ax2.tick_params(axis="y", colors=CORES["secundaria"], labelsize=11)
    ax2.set_ylim(0, 10)

    ax1.set_title("Volume de Produção × Rating Médio por Ano",
                  color=CORES["texto"], fontsize=15, fontweight="bold", pad=12)
    ax1.grid(color="#383838", linestyle="--", linewidth=0.6)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_distribuicao_ratings(df: pd.DataFrame) -> bytes:
    if "rating" not in df.columns:
        return b""
    fig, ax = nova_figura(11, 5)
    sns.histplot(df["rating"].dropna(), bins=40, kde=True, ax=ax,
                 color=CORES["secundaria"], edgecolor="none", alpha=0.85)
    media   = df["rating"].mean()
    mediana = df["rating"].median()
    ax.axvline(media,   color=CORES["primaria"], linestyle="--",
               linewidth=2.5, label=f"Média: {media:.2f}")
    ax.axvline(mediana, color=CORES["destaque"], linestyle=":",
               linewidth=2.5, label=f"Mediana: {mediana:.2f}")
    ax.set_xlabel("Rating IMDb", fontsize=13)
    ax.set_ylabel("Frequência",  fontsize=13)
    ax.set_title("Distribuição de Ratings dos Filmes", fontsize=15, fontweight="bold")
    leg = ax.legend(fontsize=12, framealpha=0.8)
    for t in leg.get_texts():
        t.set_color(CORES["texto"])
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_correlacao(df: pd.DataFrame) -> bytes:
    colunas = [c for c in ["rating", "budget", "gross", "profit", "runtime", "votes"]
               if c in df.columns]
    if len(colunas) < 3:
        return b""
    corr = df[colunas].corr()
    nomes_pt = {"rating": "Rating", "budget": "Orçamento", "gross": "Receita",
                "profit": "Lucro",  "runtime": "Duração",  "votes": "Votos"}
    corr.index   = [nomes_pt.get(c, c) for c in corr.index]
    corr.columns = [nomes_pt.get(c, c) for c in corr.columns]
    fig, ax = nova_figura(9, 6)
    mascara = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mascara, annot=True, fmt=".2f", cmap="RdYlGn",
                ax=ax, linewidths=0.6, linecolor="#1A1A1A",
                annot_kws={"size": 11, "weight": "bold", "color": "white"},
                vmin=-1, vmax=1)
    ax.set_title("Mapa de Correlação entre Variáveis", fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_adesao_generos(df: pd.DataFrame) -> bytes:
    pop = popularidade_por_genero(df)
    top = pop.head(10)
    fig, ax = nova_figura(12, 6)
    barras = ax.barh(top["genre"][::-1], top["popularity_score"][::-1],
                     color=PALETA[:len(top)], height=0.65)
    for b, s in zip(barras, top["popularity_score"][::-1]):
        ax.text(b.get_width() + 0.5, b.get_y() + b.get_height() / 2,
                f"{s:.1f}", va="center", fontsize=12, color=CORES["texto"], fontweight="bold")
    ax.set_xlabel("Pontuação de Popularidade", fontsize=13)
    ax.set_title("Top 10 Gêneros — Adesão do Público", fontsize=15, fontweight="bold")
    ax.set_xlim(0, top["popularity_score"].max() * 1.14)
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_generos_produzidos(df: pd.DataFrame) -> bytes:
    prod = quantidade_por_genero(df).head(10)
    fig, ax = nova_figura(12, 5)
    cores = [CORES["primaria"] if i == 0 else CORES["destaque"] for i in range(len(prod))]
    barras = ax.bar(prod["genre"], prod["count"], color=cores, edgecolor="none", width=0.65)
    for b in barras:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 8, f"{int(h):,}",
                ha="center", fontsize=11, color=CORES["texto"], fontweight="bold")
    ax.set_xlabel("Gênero", fontsize=13)
    ax.set_ylabel("Número de Filmes", fontsize=13)
    ax.set_title("Volume de Produção por Gênero", fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_rating_por_genero(df: pd.DataFrame) -> bytes:
    pop = popularidade_por_genero(df).sort_values("avg_rating", ascending=False).head(12)
    fig, ax = nova_figura(12, 5)
    paleta = sns.color_palette("YlOrRd", len(pop))[::-1]
    barras = ax.bar(pop["genre"], pop["avg_rating"], color=paleta, edgecolor="none", width=0.65)
    media = pop["avg_rating"].mean()
    ax.axhline(media, color=CORES["suave"], linestyle="--", linewidth=2,
               label=f"Média: {media:.2f}")
    for b in barras:
        h = b.get_height()
        ax.text(b.get_x() + b.get_width() / 2, h + 0.05, f"{h:.2f}",
                ha="center", fontsize=10, color=CORES["texto"], fontweight="bold")
    ax.set_ylim(0, 10)
    ax.set_ylabel("Rating Médio IMDb", fontsize=13)
    ax.set_title("Rating Médio por Gênero", fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    leg = ax.legend(fontsize=11)
    for t in leg.get_texts():
        t.set_color(CORES["texto"])
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_lucro_por_genero(df: pd.DataFrame) -> bytes:
    fin = financeiro_por_genero(df).head(10)
    if fin.empty or "avg_profit" not in fin.columns:
        return b""
    fig, (ax1, ax2) = novas_figuras(1, 2, l=15, a=6)

    cores_l = [CORES["positivo"] if v > 0 else CORES["negativo"] for v in fin["avg_profit"]]
    ax1.bar(fin["genre"], fin["avg_profit"] / 1e6, color=cores_l, edgecolor="none", width=0.65)
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax1.set_title("Lucro Médio por Gênero", fontsize=14, fontweight="bold")
    ax1.set_ylabel("Lucro Médio (USD)", fontsize=12)
    ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    plt.setp(ax1.get_xticklabels(), rotation=30, ha="right", fontsize=10)

    if "avg_roi" in fin.columns:
        cores_r = [CORES["positivo"] if v > 0 else CORES["negativo"] for v in fin["avg_roi"]]
        ax2.bar(fin["genre"], fin["avg_roi"] * 100, color=cores_r, edgecolor="none", width=0.65)
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
        ax2.set_title("ROI Médio por Gênero", fontsize=14, fontweight="bold")
        ax2.set_ylabel("ROI Médio (%)", fontsize=12)
        ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        plt.setp(ax2.get_xticklabels(), rotation=30, ha="right", fontsize=10)

    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_faixas_orcamento(df: pd.DataFrame) -> bytes:
    faixas = faixas_orcamento(df)
    if faixas.empty:
        return b""
    fig, (ax1, ax2, ax3) = novas_figuras(1, 3, l=16, a=6)

    ax1.bar(faixas["budget_range"].astype(str), faixas["count"],
            color=CORES["destaque"], edgecolor="none", width=0.65)
    ax1.set_title("Filmes por Faixa de Orçamento", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Quantidade", fontsize=12)
    ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=10)
    plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")

    cores_l = [CORES["positivo"] if v > 0 else CORES["negativo"] for v in faixas["avg_profit"]]
    ax2.bar(faixas["budget_range"].astype(str), faixas["avg_profit"] / 1e6,
            color=cores_l, edgecolor="none", width=0.65)
    ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax2.set_title("Lucro Médio por Faixa", fontsize=13, fontweight="bold")
    ax2.set_ylabel("Lucro Médio (USD)", fontsize=12)
    ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=10)
    plt.setp(ax2.get_xticklabels(), rotation=30, ha="right")

    ax3.bar(faixas["budget_range"].astype(str), faixas["avg_roi"] * 100,
            color=CORES["secundaria"], edgecolor="none", width=0.65)
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax3.set_title("ROI Médio por Faixa", fontsize=13, fontweight="bold")
    ax3.set_ylabel("ROI Médio (%)", fontsize=12)
    ax3.tick_params(axis="both", colors=CORES["texto"], labelsize=10)
    plt.setp(ax3.get_xticklabels(), rotation=30, ha="right")

    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_orcamento_lucro(df: pd.DataFrame) -> bytes:
    df_fin = df.dropna(subset=["budget", "gross", "profit", "roi"])
    if df_fin.empty:
        return b""
    amostra = df_fin.sample(min(len(df_fin), 800), random_state=42)
    fig, ax = nova_figura(11, 5)
    disp = ax.scatter(amostra["budget"] / 1e6, amostra["profit"] / 1e6,
                      c=amostra["roi"].clip(-1, 5), cmap="RdYlGn",
                      alpha=0.65, s=25, vmin=-1, vmax=3)
    ax.axhline(0, color=CORES["suave"], linestyle="--", linewidth=1.5)
    cb = fig.colorbar(disp, ax=ax)
    cb.set_label("ROI", color=CORES["texto"], fontsize=12)
    cb.ax.yaxis.set_tick_params(color=CORES["texto"], labelsize=11)
    plt.setp(cb.ax.yaxis.get_ticklabels(), color=CORES["texto"])
    ax.set_xlabel("Orçamento ($M)", fontsize=13)
    ax.set_ylabel("Lucro ($M)", fontsize=13)
    ax.set_title("Relação entre Orçamento e Lucro  (cor = ROI)",
                 fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_duracao(df: pd.DataFrame) -> bytes:
    if "runtime" not in df.columns:
        return b""
    rt = analise_duracao(df)
    fig, (ax1, ax2) = novas_figuras(1, 2, l=14, a=6)

    ax1.bar(rt["runtime_range"].astype(str), rt["avg_rating"],
            color=PALETA[:len(rt)], edgecolor="none", width=0.65)
    for b in ax1.patches:
        h = b.get_height()
        ax1.text(b.get_x() + b.get_width() / 2, h + 0.05, f"{h:.2f}",
                 ha="center", fontsize=10, color=CORES["texto"], fontweight="bold")
    ax1.set_title("Rating Médio por Duração", fontsize=13, fontweight="bold")
    ax1.set_ylabel("Rating Médio", fontsize=12)
    ax1.set_ylim(0, 10)
    ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    plt.setp(ax1.get_xticklabels(), rotation=20, ha="right")

    if "avg_profit" in rt.columns:
        cores_d = [CORES["positivo"] if v > 0 else CORES["negativo"]
                   for v in rt["avg_profit"].fillna(0)]
        ax2.bar(rt["runtime_range"].astype(str), rt["avg_profit"].fillna(0) / 1e6,
                color=cores_d, edgecolor="none", width=0.65)
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
        ax2.set_title("Lucro Médio por Duração", fontsize=13, fontweight="bold")
        ax2.set_ylabel("Lucro Médio (USD)", fontsize=12)
        ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        plt.setp(ax2.get_xticklabels(), rotation=20, ha="right")

    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_top_diretores(df: pd.DataFrame, min_filmes: int = 3) -> bytes:
    stats = estatisticas_diretores(df, min_filmes=min_filmes)
    if stats.empty or "total_profit" not in stats.columns:
        return b""
    top10 = stats.head(10)
    fig, ax = nova_figura(12, 6)
    cores_d = [CORES["primaria"] if i == 0 else CORES["destaque"] for i in range(len(top10))]
    barras = ax.barh(top10["director"][::-1], top10["total_profit"][::-1] / 1e6,
                     color=cores_d[::-1], edgecolor="none", height=0.65)
    for b, v in zip(barras, top10["total_profit"][::-1]):
        label = f"${v/1e6:.0f}M"
        ax.text(b.get_width() + 5, b.get_y() + b.get_height() / 2,
                label, va="center", fontsize=11, color=CORES["texto"], fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    ax.set_xlabel("Lucro Total (USD)", fontsize=13)
    ax.set_title("Top 10 Diretores — Maior Lucro Acumulado", fontsize=15, fontweight="bold")
    ax.set_xlim(0, top10["total_profit"].max() / 1e6 * 1.2)
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
    fig.tight_layout()
    return _fig_para_bytes(fig)


def grafico_roi_diretores(df: pd.DataFrame, min_filmes: int = 3) -> bytes:
    stats = estatisticas_diretores(df, min_filmes=min_filmes)
    if stats.empty or "avg_roi" not in stats.columns:
        return b""
    top_roi = stats.dropna(subset=["avg_roi"]).sort_values("avg_roi", ascending=False).head(10)
    fig, ax = nova_figura(12, 6)
    cores_r = [CORES["positivo"] if v > 0 else CORES["negativo"] for v in top_roi["avg_roi"]]
    barras = ax.barh(top_roi["director"][::-1], top_roi["avg_roi"][::-1] * 100,
                     color=cores_r[::-1], edgecolor="none", height=0.65)
    for b, v in zip(barras, top_roi["avg_roi"][::-1]):
        ax.text(b.get_width() + 1, b.get_y() + b.get_height() / 2,
                f"{v*100:.0f}%", va="center", fontsize=12, color=CORES["texto"], fontweight="bold")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
    ax.set_xlabel("ROI Médio", fontsize=13)
    ax.set_title("Top 10 Diretores por ROI Médio", fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
    fig.tight_layout()
    return _fig_para_bytes(fig)


GRAFICOS_DISPONIVEIS = {
    "producao_por_ano":      grafico_producao_por_ano,
    "distribuicao_ratings":  grafico_distribuicao_ratings,
    "correlacao":            grafico_correlacao,
    "adesao_generos":        grafico_adesao_generos,
    "generos_produzidos":    grafico_generos_produzidos,
    "rating_por_genero":     grafico_rating_por_genero,
    "lucro_por_genero":      grafico_lucro_por_genero,
    "faixas_orcamento":      grafico_faixas_orcamento,
    "orcamento_lucro":       grafico_orcamento_lucro,
    "duracao":               grafico_duracao,
    "top_diretores":         grafico_top_diretores,
    "roi_diretores":         grafico_roi_diretores,
}


def gerar_todos_graficos(df: pd.DataFrame) -> dict:
    resultado = {}
    for nome, funcao in GRAFICOS_DISPONIVEIS.items():
        try:
            dados = funcao(df)
            if dados:
                resultado[nome] = dados
        except Exception:
            pass
    return resultado
