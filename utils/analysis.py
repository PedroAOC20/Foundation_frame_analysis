import pandas as pd
import numpy as np


def expandir_generos(df):
    if "genre" not in df.columns:
        return df
    d = df.copy()
    d["genre"] = d["genre"].str.split(r",\s*")
    return d.explode("genre").reset_index(drop=True)

explode_genres = expandir_generos


def formatar_usd(valor, decimais=1):
    if pd.isna(valor):
        return "N/A"
    abs_val = abs(valor)
    sinal = "-" if valor < 0 else ""
    if abs_val >= 1e9:
        return f"{sinal}${abs_val/1e9:.{decimais}f}B"
    if abs_val >= 1e6:
        return f"{sinal}${abs_val/1e6:.{decimais}f}M"
    if abs_val >= 1e3:
        return f"{sinal}${abs_val/1e3:.{decimais}f}K"
    return f"{sinal}${abs_val:.0f}"

fmt_usd = formatar_usd


def popularidade_por_genero(df):
    g = expandir_generos(df)
    agg = g.groupby("genre").agg(
        quantidade=("title", "count"),
        media_rating=("rating", "mean"),
        media_votos=("votes", "mean"),
    ).dropna()
    agg["pontuacao_popularidade"] = agg["media_rating"] * np.log1p(agg["media_votos"])
    agg = agg.rename(columns={
        "quantidade":            "count",
        "media_rating":          "avg_rating",
        "media_votos":           "avg_votes",
        "pontuacao_popularidade":"popularity_score",
    })
    return agg.sort_values("popularity_score", ascending=False).reset_index()

genre_popularity = popularidade_por_genero


def quantidade_por_genero(df):
    g = expandir_generos(df)
    resultado = g["genre"].value_counts().reset_index()
    resultado.columns = ["genre", "count"]
    return resultado

genre_production_count = quantidade_por_genero


def financeiro_por_genero(df):
    g = expandir_generos(df)
    fin = g.dropna(subset=["budget", "gross"])
    return fin.groupby("genre").agg(
        avg_budget=("budget", "mean"),
        avg_gross=("gross", "mean"),
        avg_profit=("profit", "mean"),
        avg_roi=("roi", "mean"),
        count=("title", "count"),
    ).reset_index().sort_values("avg_profit", ascending=False)

genre_financial = financeiro_por_genero


def faixas_orcamento(df):
    d = df.dropna(subset=["budget", "gross"]).copy()
    bins   = [0, 1e6, 10e6, 50e6, 100e6, 200e6, np.inf]
    labels = ["< $1M", "$1–10M", "$10–50M", "$50–100M", "$100–200M", "> $200M"]
    d["budget_range"] = pd.cut(d["budget"], bins=bins, labels=labels)
    return d.groupby("budget_range", observed=True).agg(
        count=("title", "count"),
        avg_gross=("gross", "mean"),
        avg_profit=("profit", "mean"),
        avg_roi=("roi", "mean"),
        avg_rating=("rating", "mean"),
    ).reset_index()

budget_buckets = faixas_orcamento


def filmes_lucrativos(df, roi_minimo=1.0):
    d = df.dropna(subset=["budget", "profit"])
    return d[d["roi"] >= roi_minimo].sort_values("profit", ascending=False)

profitable_films = filmes_lucrativos


def analise_duracao(df):
    d = df.dropna(subset=["runtime"]).copy()
    bins   = [0, 80, 100, 120, 140, 160, np.inf]
    labels = ["< 80 min", "80–100", "100–120", "120–140", "140–160", "> 160 min"]
    d["runtime_range"] = pd.cut(d["runtime"], bins=bins, labels=labels)
    agg = d.groupby("runtime_range", observed=True).agg(
        count=("title", "count"),
        avg_rating=("rating", "mean"),
    )
    if "profit" in d.columns:
        agg["avg_profit"] = d.groupby("runtime_range", observed=True)["profit"].mean()
    return agg.reset_index()

runtime_analysis = analise_duracao


def estatisticas_diretores(df, min_filmes=3):
    d = df.dropna(subset=["director"])
    tem_profit = "profit" in d.columns
    tem_roi    = "roi" in d.columns
    agg = d.groupby("director").agg(
        films=("title", "count"),
        avg_rating=("rating", "mean"),
        total_profit=("profit", "sum")  if tem_profit else ("title", "count"),
        avg_profit=("profit", "mean")   if tem_profit else ("title", "count"),
        avg_roi=("roi", "mean")         if tem_roi    else ("title", "count"),
    ).reset_index()
    return agg[agg["films"] >= min_filmes].sort_values("total_profit", ascending=False)

director_stats = estatisticas_diretores
