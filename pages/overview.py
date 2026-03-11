import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

from utils import nova_figura, novas_figuras, formatar_usd, caixa_insight, CORES, PALETA, aplicar_tema

new_fig  = nova_figura
new_figs = novas_figuras
fmt_usd  = formatar_usd
COLORS   = CORES
PALETTE  = PALETA
apply_theme = aplicar_tema
insight_box = caixa_insight


def render(df: pd.DataFrame) -> None:
    st.title("🏠 Visão Geral da Base de Dados")
    st.markdown(f"**{len(df):,} filmes** carregados com os filtros aplicados.")
    st.markdown("---")

    colunas = st.columns(5)
    indicadores = [
        ("🎬 Total de Filmes",  f"{len(df):,}"),
        ("⭐ Rating Médio",      f"{df['rating'].mean():.2f}" if "rating" in df.columns else "N/A"),
        ("💵 Orçamento Médio",   formatar_usd(df["budget"].mean()) if "budget" in df.columns else "N/A"),
        ("💰 Receita Média",     formatar_usd(df["gross"].mean()) if "gross" in df.columns else "N/A"),
        ("📅 Período",           f"{int(df['year'].min())} – {int(df['year'].max())}" if "year" in df.columns else "N/A"),
    ]
    for col, (rotulo, valor) in zip(colunas, indicadores):
        col.metric(rotulo, valor)

    st.markdown("---")

    if "year" in df.columns:
        st.subheader("📅 Produção de Filmes por Ano")
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
        st.pyplot(fig)
        plt.close(fig)

    if "rating" in df.columns:
        st.subheader("⭐ Distribuição de Ratings")
        fig, ax = nova_figura(11, 5)

        sns.histplot(df["rating"].dropna(), bins=40, kde=True, ax=ax,
                     color=CORES["secundaria"], edgecolor="none", alpha=0.85)

        media   = df["rating"].mean()
        mediana = df["rating"].median()

        ax.axvline(media,   color=CORES["primaria"],  linestyle="--",
                   linewidth=2.5, label=f"Média: {media:.2f}")
        ax.axvline(mediana, color=CORES["destaque"],  linestyle=":",
                   linewidth=2.5, label=f"Mediana: {mediana:.2f}")

        ax.set_xlabel("Rating IMDb", fontsize=13)
        ax.set_ylabel("Frequência",  fontsize=13)
        ax.set_title("Distribuição de Ratings dos Filmes",
                     fontsize=15, fontweight="bold")

        legenda = ax.legend(fontsize=12, framealpha=0.8)
        for texto in legenda.get_texts():
            texto.set_color(CORES["texto"])

        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        pico = df["rating"].mode()[0]
        caixa_insight(
            f"A maioria dos filmes tem rating entre "
            f"**{df['rating'].quantile(0.25):.1f}** e "
            f"**{df['rating'].quantile(0.75):.1f}**. "
            f"O pico de frequência fica em torno de **{pico:.1f}**. "
            f"Filmes com rating acima de **7,0** são considerados acima da média pelo público."
        )

    colunas_num = [c for c in ["rating", "budget", "gross", "profit", "runtime", "votes"]
                   if c in df.columns]
    if len(colunas_num) >= 3:
        st.subheader("🔗 Correlação entre Variáveis")
        correlacao = df[colunas_num].corr()
        fig, ax = nova_figura(9, 6)
        mascara = np.triu(np.ones_like(correlacao, dtype=bool))

        nomes_pt = {
            "rating": "Rating", "budget": "Orçamento", "gross": "Receita",
            "profit": "Lucro",  "runtime": "Duração",  "votes": "Votos",
        }
        correlacao.index   = [nomes_pt.get(c, c) for c in correlacao.index]
        correlacao.columns = [nomes_pt.get(c, c) for c in correlacao.columns]

        sns.heatmap(
            correlacao, mask=mascara, annot=True, fmt=".2f",
            cmap="RdYlGn", ax=ax, linewidths=0.6, linecolor="#1A1A1A",
            annot_kws={"size": 11, "weight": "bold", "color": "white"},
            vmin=-1, vmax=1,
        )
        ax.set_title("Mapa de Correlação entre Variáveis",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        if "budget" in df.columns and "gross" in df.columns:
            r = df[["budget", "gross"]].corr().iloc[0, 1]
            caixa_insight(
                f"A correlação entre **orçamento** e **receita** é de **{r:.2f}**. "
                f"{'Gastar mais tende a gerar mais receita, mas não garante lucro.' if r > 0.5 else 'O orçamento por si só não determina o sucesso comercial.'}"
            )

    with st.expander("🔍 Explorar dados brutos"):
        colunas_exibir = [c for c in ["title", "genre", "director", "year",
                                       "rating", "budget", "gross", "profit", "roi", "runtime"]
                          if c in df.columns]
        st.dataframe(
            df[colunas_exibir].head(100).style.background_gradient(
                subset=[c for c in ["rating", "budget", "gross"] if c in df.columns],
                cmap="RdYlGn",
            ),
            use_container_width=True,
        )
        st.caption(f"Exibindo 100 de {len(df):,} registros.")
