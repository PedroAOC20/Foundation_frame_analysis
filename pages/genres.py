import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

from utils import (
    nova_figura, novas_figuras, formatar_usd, caixa_insight,
    popularidade_por_genero, quantidade_por_genero, financeiro_por_genero,
    expandir_generos, CORES, PALETA,
)


def render(df: pd.DataFrame) -> None:
    st.title("🎭 Análise de Gêneros")
    st.markdown("Entenda o que o público quer e quais segmentos dominam o mercado.")
    st.markdown("---")

    popularidade  = popularidade_por_genero(df)
    producao      = quantidade_por_genero(df)
    financeiro    = financeiro_por_genero(df)

    st.subheader("🏆 Gêneros com Maior Adesão do Público")
    st.caption("Pontuação = Rating Médio × log(Votos Médios) — combina qualidade percebida e alcance.")

    top_pop = popularidade.head(10)
    fig, ax = nova_figura(12, 6)
    barras = ax.barh(top_pop["genre"][::-1], top_pop["popularity_score"][::-1],
                     color=PALETA[:len(top_pop)], height=0.65)
    for barra, pontuacao in zip(barras, top_pop["popularity_score"][::-1]):
        ax.text(barra.get_width() + 0.5, barra.get_y() + barra.get_height() / 2,
                f"{pontuacao:.1f}", va="center", fontsize=12,
                color=CORES["texto"], fontweight="bold")
    ax.set_xlabel("Pontuação de Popularidade", fontsize=13)
    ax.set_title("Top 10 Gêneros — Adesão do Público", fontsize=15, fontweight="bold")
    ax.set_xlim(0, top_pop["popularity_score"].max() * 1.14)
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    melhor = top_pop.iloc[0]
    caixa_insight(
        f"**{melhor['genre']}** lidera em adesão com pontuação de **{melhor['popularity_score']:.1f}**, "
        f"combinando rating médio de **{melhor['avg_rating']:.2f}** e "
        f"**{int(melhor['avg_votes']):,}** votos médios por filme."
    )

    st.markdown("---")
    st.subheader("📊 Gêneros Mais Produzidos")

    top_prod = producao.head(10)
    fig, ax = nova_figura(12, 5)
    cores_prod = [CORES["primaria"] if i == 0 else CORES["destaque"]
                  for i in range(len(top_prod))]
    barras = ax.bar(top_prod["genre"], top_prod["count"],
                    color=cores_prod, edgecolor="none", width=0.65)
    for barra in barras:
        h = barra.get_height()
        ax.text(barra.get_x() + barra.get_width() / 2, h + 8,
                f"{int(h):,}", ha="center", fontsize=11,
                color=CORES["texto"], fontweight="bold")
    ax.set_xlabel("Gênero", fontsize=13)
    ax.set_ylabel("Número de Filmes", fontsize=13)
    ax.set_title("Volume de Produção por Gênero", fontsize=15, fontweight="bold")
    ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
    plt.xticks(rotation=30, ha="right")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    genero_lider = top_prod.iloc[0]["genre"]
    quantidade_lider = top_prod.iloc[0]["count"]
    caixa_insight(
        f"**{genero_lider}** é o gênero mais produzido com **{int(quantidade_lider):,}** filmes, "
        f"representando **{100 * quantidade_lider / len(df):.1f}%** da base total."
    )

    if "avg_rating" in popularidade.columns:
        st.markdown("---")
        st.subheader("⭐ Rating Médio por Gênero")
        pop_ordenado = popularidade.sort_values("avg_rating", ascending=False).head(12)

        fig, ax = nova_figura(12, 5)
        paleta_grad = sns.color_palette("YlOrRd", len(pop_ordenado))[::-1]
        barras = ax.bar(pop_ordenado["genre"], pop_ordenado["avg_rating"],
                        color=paleta_grad, edgecolor="none", width=0.65)
        media_geral = pop_ordenado["avg_rating"].mean()
        ax.axhline(media_geral, color=CORES["suave"], linestyle="--",
                   linewidth=2, label=f"Média geral: {media_geral:.2f}")
        for barra in barras:
            h = barra.get_height()
            ax.text(barra.get_x() + barra.get_width() / 2, h + 0.05,
                    f"{h:.2f}", ha="center", fontsize=10,
                    color=CORES["texto"], fontweight="bold")
        ax.set_ylim(0, 10)
        ax.set_ylabel("Rating Médio IMDb", fontsize=13)
        ax.set_title("Rating Médio por Gênero", fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        legenda = ax.legend(fontsize=11)
        for t in legenda.get_texts():
            t.set_color(CORES["texto"])
        plt.xticks(rotation=30, ha="right")
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    if not financeiro.empty and "avg_profit" in financeiro.columns:
        st.markdown("---")
        st.subheader("💰 Retorno Financeiro por Gênero")

        fin_top = financeiro.head(10)
        fig, (ax1, ax2) = novas_figuras(1, 2, l=15, a=6)

        cores_lucro = [CORES["positivo"] if v > 0 else CORES["negativo"]
                       for v in fin_top["avg_profit"]]
        ax1.bar(fin_top["genre"], fin_top["avg_profit"] / 1e6,
                color=cores_lucro, edgecolor="none", width=0.65)
        ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
        ax1.set_title("Lucro Médio por Gênero", fontsize=14, fontweight="bold")
        ax1.set_ylabel("Lucro Médio (USD)", fontsize=12)
        ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        plt.setp(ax1.get_xticklabels(), rotation=30, ha="right", fontsize=10)

        if "avg_roi" in fin_top.columns:
            cores_roi = [CORES["positivo"] if v > 0 else CORES["negativo"]
                         for v in fin_top["avg_roi"]]
            ax2.bar(fin_top["genre"], fin_top["avg_roi"] * 100,
                    color=cores_roi, edgecolor="none", width=0.65)
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
            ax2.set_title("ROI Médio por Gênero", fontsize=14, fontweight="bold")
            ax2.set_ylabel("ROI Médio (%)", fontsize=12)
            ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
            plt.setp(ax2.get_xticklabels(), rotation=30, ha="right", fontsize=10)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        melhor_fin = fin_top.iloc[0]
        caixa_insight(
            f"**{melhor_fin['genre']}** apresenta o maior lucro médio de "
            f"**{formatar_usd(melhor_fin['avg_profit'])}** por filme, "
            f"com ROI de **{melhor_fin['avg_roi']*100:.0f}%** e "
            f"custo médio de **{formatar_usd(melhor_fin['avg_budget'])}**."
        )

    if "rating" in df.columns and "votes" in df.columns:
        st.markdown("---")
        st.subheader("🔵 Qualidade × Alcance por Gênero")

        dg = expandir_generos(df).dropna(subset=["rating", "votes"])
        top_generos = dg["genre"].value_counts().head(8).index.tolist()
        dg_top = dg[dg["genre"].isin(top_generos)]

        fig, ax = nova_figura(12, 6)
        for i, genero in enumerate(top_generos):
            sub = dg_top[dg_top["genre"] == genero]
            ax.scatter(sub["rating"], np.log1p(sub["votes"]),
                       label=genero, alpha=0.65, s=35,
                       color=PALETA[i % len(PALETA)])
        ax.set_xlabel("Rating IMDb", fontsize=13)
        ax.set_ylabel("log(Votos)", fontsize=13)
        ax.set_title("Qualidade Percebida × Engajamento por Gênero",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        legenda = ax.legend(loc="upper left", fontsize=10, framealpha=0.6)
        for t in legenda.get_texts():
            t.set_color(CORES["texto"])
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
