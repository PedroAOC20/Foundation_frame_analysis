import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import numpy as np

from utils import (
    nova_figura, novas_figuras, formatar_usd, caixa_insight,
    faixas_orcamento, filmes_lucrativos, analise_duracao,
    CORES, PALETA,
)


def render(df: pd.DataFrame) -> None:
    st.title("💰 Análise Financeira")
    st.markdown("Descubra quanto custa, quanto rende e qual o formato mais lucrativo.")
    st.markdown("---")

    tem_financeiro = "budget" in df.columns and "gross" in df.columns
    df_fin = df.dropna(subset=["budget", "gross"]) if tem_financeiro else pd.DataFrame()

    if not df_fin.empty:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("💵 Orçamento Médio",  formatar_usd(df_fin["budget"].mean()))
        c2.metric("💰 Receita Média",    formatar_usd(df_fin["gross"].mean()))
        c3.metric("📈 Lucro Médio",      formatar_usd(df_fin["profit"].mean()))
        c4.metric("🔁 ROI Médio",        f"{df_fin['roi'].mean()*100:.0f}%")
        st.markdown("---")

    st.subheader("🎯 Quanto custa produzir cada tipo de filme?")

    if not df_fin.empty:
        faixas = faixas_orcamento(df)
        fig, (ax1, ax2, ax3) = novas_figuras(1, 3, l=16, a=6)

        ax1.bar(faixas["budget_range"].astype(str), faixas["count"],
                color=CORES["destaque"], edgecolor="none", width=0.65)
        ax1.set_title("Filmes por Faixa de Orçamento", fontsize=13, fontweight="bold")
        ax1.set_ylabel("Quantidade", fontsize=12)
        ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=10)
        plt.setp(ax1.get_xticklabels(), rotation=30, ha="right")

        cores_lucro = [CORES["positivo"] if v > 0 else CORES["negativo"]
                       for v in faixas["avg_profit"]]
        ax2.bar(faixas["budget_range"].astype(str), faixas["avg_profit"] / 1e6,
                color=cores_lucro, edgecolor="none", width=0.65)
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
        st.pyplot(fig)
        plt.close(fig)

        melhor_roi   = faixas.loc[faixas["avg_roi"].idxmax()]
        melhor_lucro = faixas.loc[faixas["avg_profit"].idxmax()]
        caixa_insight(
            f"A faixa **{melhor_roi['budget_range']}** tem o maior ROI médio "
            f"(**{melhor_roi['avg_roi']*100:.0f}%**). "
            f"Já a faixa **{melhor_lucro['budget_range']}** gera o maior lucro absoluto médio "
            f"(**{formatar_usd(melhor_lucro['avg_profit'])}**)."
        )
    else:
        st.info("Dados financeiros não disponíveis neste dataset.")

    st.markdown("---")
    st.subheader("🌟 Filmes Lucrativos — Qual o Orçamento Típico?")

    if not df_fin.empty:
        lucrativos    = filmes_lucrativos(df, roi_minimo=0.5)
        nao_lucrativos = df_fin[df_fin["roi"] < 0]

        fig, (ax1, ax2) = novas_figuras(1, 2, l=14, a=6)

        ax1.hist(np.log10(lucrativos["budget"].clip(1)), bins=30,
                 alpha=0.75, color=CORES["positivo"],
                 label=f"Lucrativos (n={len(lucrativos):,})")
        ax1.hist(np.log10(nao_lucrativos["budget"].clip(1)), bins=30,
                 alpha=0.75, color=CORES["negativo"],
                 label=f"Prejuízo (n={len(nao_lucrativos):,})")
        ax1.set_xlabel("log₁₀(Orçamento USD)", fontsize=12)
        ax1.set_title("Distribuição de Orçamento", fontsize=13, fontweight="bold")
        ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        legenda = ax1.legend(fontsize=11)
        for t in legenda.get_texts():
            t.set_color(CORES["texto"])

        dados_box = pd.DataFrame({
            "Orçamento": pd.concat([lucrativos["budget"], nao_lucrativos["budget"]]),
            "Resultado": (["Lucrativo"] * len(lucrativos)) + (["Prejuízo"] * len(nao_lucrativos)),
        })
        sns.boxplot(data=dados_box, x="Resultado", y="Orçamento", ax=ax2,
                    palette={"Lucrativo": CORES["positivo"], "Prejuízo": CORES["negativo"]})
        ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
        ax2.set_title("Orçamento: Lucrativos vs Prejuízo", fontsize=13, fontweight="bold")
        ax2.set_ylabel("Orçamento (USD)", fontsize=12)
        ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=11)

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        mediana_lucro    = lucrativos["budget"].median()
        mediana_prejuizo = nao_lucrativos["budget"].median() if len(nao_lucrativos) else 0
        caixa_insight(
            f"Filmes lucrativos têm orçamento mediano de **{formatar_usd(mediana_lucro)}**, "
            f"enquanto os deficitários gastam em média **{formatar_usd(mediana_prejuizo)}**. "
            f"**{100*len(lucrativos)/len(df_fin):.0f}%** dos filmes com dados financeiros são lucrativos."
        )

        st.subheader("🏆 Top 10 Filmes Mais Lucrativos")
        colunas_tabela = [c for c in ["title", "genre", "director", "year",
                                       "budget", "gross", "profit", "roi"]
                          if c in lucrativos.columns]
        top10 = lucrativos[colunas_tabela].head(10).copy()

        nomes_pt = {
            "title": "Título", "genre": "Gênero", "director": "Diretor",
            "year": "Ano", "budget": "Orçamento", "gross": "Receita",
            "profit": "Lucro", "roi": "ROI",
        }
        top10 = top10.rename(columns=nomes_pt)
        for col in ["Orçamento", "Receita", "Lucro"]:
            if col in top10.columns:
                top10[col] = top10[col].apply(formatar_usd)
        if "ROI" in top10.columns:
            top10["ROI"] = top10["ROI"].apply(lambda x: f"{x*100:.0f}%")
        st.dataframe(top10, use_container_width=True)

    if not df_fin.empty:
        st.markdown("---")
        st.subheader("🔵 Relação entre Orçamento e Lucro")

        amostra = df_fin.sample(min(len(df_fin), 800), random_state=42)
        fig, ax = nova_figura(11, 5)
        dispersao = ax.scatter(
            amostra["budget"] / 1e6, amostra["profit"] / 1e6,
            c=amostra["roi"].clip(-1, 5), cmap="RdYlGn",
            alpha=0.65, s=25, vmin=-1, vmax=3,
        )
        ax.axhline(0, color=CORES["suave"], linestyle="--", linewidth=1.5)
        barra_cor = fig.colorbar(dispersao, ax=ax)
        barra_cor.set_label("ROI", color=CORES["texto"], fontsize=12)
        barra_cor.ax.yaxis.set_tick_params(color=CORES["texto"], labelsize=11)
        plt.setp(barra_cor.ax.yaxis.get_ticklabels(), color=CORES["texto"])
        ax.set_xlabel("Orçamento ($M)", fontsize=13)
        ax.set_ylabel("Lucro ($M)", fontsize=13)
        ax.set_title("Relação entre Orçamento e Lucro  (cor = ROI)",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    st.markdown("---")
    st.subheader("⏱️ Duração Ideal de um Filme")

    if "runtime" in df.columns:
        rt = analise_duracao(df)

        fig, (ax1, ax2) = novas_figuras(1, 2, l=14, a=6)

        ax1.bar(rt["runtime_range"].astype(str), rt["avg_rating"],
                color=PALETA[:len(rt)], edgecolor="none", width=0.65)
        for barra in ax1.patches:
            h = barra.get_height()
            ax1.text(barra.get_x() + barra.get_width() / 2, h + 0.05,
                     f"{h:.2f}", ha="center", fontsize=10,
                     color=CORES["texto"], fontweight="bold")
        ax1.set_title("Rating Médio por Duração", fontsize=13, fontweight="bold")
        ax1.set_ylabel("Rating Médio", fontsize=12)
        ax1.set_ylim(0, 10)
        ax1.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        plt.setp(ax1.get_xticklabels(), rotation=20, ha="right")

        if "avg_profit" in rt.columns:
            cores_dur = [CORES["positivo"] if v > 0 else CORES["negativo"]
                         for v in rt["avg_profit"].fillna(0)]
            ax2.bar(rt["runtime_range"].astype(str), rt["avg_profit"].fillna(0) / 1e6,
                    color=cores_dur, edgecolor="none", width=0.65)
            ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
            ax2.set_title("Lucro Médio por Duração", fontsize=13, fontweight="bold")
            ax2.set_ylabel("Lucro Médio (USD)", fontsize=12)
            ax2.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
            plt.setp(ax2.get_xticklabels(), rotation=20, ha="right")

        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        melhor_dur = rt.loc[rt["avg_rating"].idxmax()]
        caixa_insight(
            f"Filmes com duração entre **{melhor_dur['runtime_range']} minutos** "
            f"têm o melhor rating médio (**{melhor_dur['avg_rating']:.2f}**). "
            f"Essa é a faixa ideal para maximizar a aprovação do público."
        )

        fig, ax = nova_figura(10, 5)
        sns.violinplot(data=df.dropna(subset=["runtime"]), y="runtime",
                       ax=ax, color=CORES["destaque"], inner="box")
        mediana_dur = df["runtime"].median()
        ax.axhline(mediana_dur, color=CORES["secundaria"], linestyle="--",
                   linewidth=2.5, label=f"Mediana: {mediana_dur:.0f} min")
        ax.set_ylabel("Duração (minutos)", fontsize=13)
        ax.set_title("Distribuição da Duração dos Filmes",
                     fontsize=15, fontweight="bold")
        ax.tick_params(axis="both", colors=CORES["texto"], labelsize=11)
        legenda = ax.legend(fontsize=11)
        for t in legenda.get_texts():
            t.set_color(CORES["texto"])
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("Coluna de duração não encontrada no dataset.")
