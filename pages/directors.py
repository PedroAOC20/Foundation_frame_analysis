import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

from utils import (
    nova_figura, novas_figuras, formatar_usd, caixa_insight,
    estatisticas_diretores, CORES, PALETA,
)


def render(df: pd.DataFrame) -> None:
    st.title("🎬 Análise de Diretores")
    st.markdown("Quem são os cineastas que mais lucram e mais agradam o público?")
    st.markdown("---")

    if "director" not in df.columns:
        st.warning("Coluna 'director' não encontrada no dataset.")
        return

    min_filmes = st.slider("Mínimo de filmes por diretor", 1, 10, 3)
    estatisticas = estatisticas_diretores(df, min_filmes=min_filmes)

    if estatisticas.empty:
        st.info("Nenhum diretor encontrado com o mínimo de filmes selecionado.")
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("🎬 Diretores Analisados", f"{len(estatisticas):,}")
    if "total_profit" in estatisticas.columns:
        primeiro = estatisticas.iloc[0]
        c2.metric("💰 Maior Lucro Total",  formatar_usd(primeiro["total_profit"]))
        c3.metric("🏆 Diretor Nº 1",       primeiro["director"])
    st.markdown("---")

    if "total_profit" in estatisticas.columns:
        st.subheader("💰 Top 10 Diretores Mais Lucrativos")
        top10_lucro = estatisticas.head(10)

        fig, ax = nova_figura(12, 6)
        cores_d = [CORES["primaria"] if i == 0 else CORES["destaque"]
                   for i in range(len(top10_lucro))]
        barras = ax.barh(top10_lucro["director"][::-1],
                         top10_lucro["total_profit"][::-1] / 1e6,
                         color=cores_d[::-1], edgecolor="none", height=0.65)
        for barra, val in zip(barras, top10_lucro["total_profit"][::-1]):
            ax.text(barra.get_width() + 5, barra.get_y() + barra.get_height() / 2,
                    formatar_usd(val), va="center", fontsize=11,
                    color=CORES["texto"], fontweight="bold")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
        ax.set_xlabel("Lucro Total (USD)", fontsize=13)
        ax.set_title("Diretores com Maior Lucro Acumulado",
                     fontsize=15, fontweight="bold")
        ax.set_xlim(0, top10_lucro["total_profit"].max() / 1e6 * 1.2)
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        caixa_insight(
            f"**{top10_lucro.iloc[0]['director']}** acumulou "
            f"**{formatar_usd(top10_lucro.iloc[0]['total_profit'])}** "
            f"em lucro ao longo de **{int(top10_lucro.iloc[0]['films'])}** filmes."
        )

    if "avg_rating" in estatisticas.columns:
        st.markdown("---")
        st.subheader("⭐ Top 10 Diretores Mais Bem Avaliados")
        top10_rating = estatisticas.sort_values("avg_rating", ascending=False).head(10)

        fig, ax = nova_figura(12, 6)
        paleta_r = sns.color_palette("YlOrRd_r", len(top10_rating))
        barras = ax.barh(top10_rating["director"][::-1],
                         top10_rating["avg_rating"][::-1],
                         color=paleta_r[::-1], edgecolor="none", height=0.65)
        for barra, val in zip(barras, top10_rating["avg_rating"][::-1]):
            ax.text(barra.get_width() + 0.05, barra.get_y() + barra.get_height() / 2,
                    f"{val:.2f}", va="center", fontsize=12,
                    color=CORES["texto"], fontweight="bold")
        ax.set_xlim(0, 10)
        ax.set_xlabel("Rating Médio IMDb", fontsize=13)
        ax.set_title("Diretores com Maior Rating Médio",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    if "avg_rating" in estatisticas.columns and "avg_profit" in estatisticas.columns:
        st.markdown("---")
        st.subheader("🔵 Lucro Médio × Rating Médio por Diretor")

        top_dispersao = estatisticas.dropna(subset=["avg_rating", "avg_profit"]).head(50)
        fig, ax = nova_figura(12, 6)
        dispersao = ax.scatter(
            top_dispersao["avg_rating"],
            top_dispersao["avg_profit"] / 1e6,
            s=top_dispersao["films"] * 35,
            c=top_dispersao["avg_roi"] if "avg_roi" in top_dispersao.columns else CORES["destaque"],
            cmap="RdYlGn", alpha=0.75, edgecolors="#444", linewidths=0.6,
        )
        for _, linha in top_dispersao.head(10).iterrows():
            ax.annotate(linha["director"].split()[-1],
                        (linha["avg_rating"], linha["avg_profit"] / 1e6),
                        fontsize=9, color=CORES["texto"], alpha=0.9,
                        xytext=(5, 5), textcoords="offset points")
        barra_cor = fig.colorbar(dispersao, ax=ax)
        barra_cor.set_label("ROI Médio", color=CORES["texto"], fontsize=12)
        barra_cor.ax.yaxis.set_tick_params(color=CORES["texto"], labelsize=11)
        plt.setp(barra_cor.ax.yaxis.get_ticklabels(), color=CORES["texto"])
        ax.axhline(0, color=CORES["suave"], linestyle="--", linewidth=1.5)
        ax.set_xlabel("Rating Médio IMDb", fontsize=13)
        ax.set_ylabel("Lucro Médio por Filme ($M)", fontsize=13)
        ax.set_title("Qualidade × Rentabilidade por Diretor\n(tamanho = nº de filmes  |  cor = ROI)",
                     fontsize=14, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    if "avg_roi" in estatisticas.columns:
        st.markdown("---")
        st.subheader("🔁 Top 10 Diretores por ROI Médio")
        top_roi = (estatisticas.dropna(subset=["avg_roi"])
                   .sort_values("avg_roi", ascending=False).head(10))

        fig, ax = nova_figura(12, 6)
        cores_roi = [CORES["positivo"] if v > 0 else CORES["negativo"]
                     for v in top_roi["avg_roi"]]
        barras = ax.barh(top_roi["director"][::-1],
                         top_roi["avg_roi"][::-1] * 100,
                         color=cores_roi[::-1], edgecolor="none", height=0.65)
        for barra, val in zip(barras, top_roi["avg_roi"][::-1]):
            ax.text(barra.get_width() + 1, barra.get_y() + barra.get_height() / 2,
                    f"{val*100:.0f}%", va="center", fontsize=12,
                    color=CORES["texto"], fontweight="bold")
        ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))
        ax.set_xlabel("ROI Médio", fontsize=13)
        ax.set_title("Diretores com Maior Retorno sobre Investimento (ROI)",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=12)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with st.expander("📋 Tabela Completa de Diretores"):
        exibir = estatisticas.copy()
        nomes_pt = {
            "director": "Diretor", "films": "Filmes",
            "avg_rating": "Rating Médio", "total_profit": "Lucro Total",
            "avg_profit": "Lucro Médio", "avg_roi": "ROI Médio",
        }
        exibir = exibir.rename(columns=nomes_pt)
        for col in ["Lucro Total", "Lucro Médio"]:
            if col in exibir.columns:
                exibir[col] = exibir[col].apply(formatar_usd)
        if "ROI Médio" in exibir.columns:
            exibir["ROI Médio"] = exibir["ROI Médio"].apply(
                lambda x: f"{x*100:.0f}%" if pd.notna(x) else "N/A")
        if "Rating Médio" in exibir.columns:
            exibir["Rating Médio"] = exibir["Rating Médio"].round(2)
        st.dataframe(exibir, use_container_width=True)
