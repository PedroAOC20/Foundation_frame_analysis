import ast, json, os
import numpy as np
import pandas as pd

TRADUCAO_GENEROS = {
    "Action":"Ação","Adventure":"Aventura","Animation":"Animação",
    "Comedy":"Comédia","Crime":"Crime","Documentary":"Documentário",
    "Drama":"Drama","Family":"Família","Fantasy":"Fantasia",
    "Foreign":"Internacional","History":"Histórico","Horror":"Terror",
    "Music":"Musical","Mystery":"Mistério","Romance":"Romance",
    "Science Fiction":"Ficção Científica","Sci-Fi":"Ficção Científica",
    "TV Movie":"Filme de TV","Thriller":"Suspense","War":"Guerra",
    "Western":"Faroeste","Biography":"Biografia","Sport":"Esporte",
    "News":"Jornalismo","Short":"Curta-metragem","Talk-Show":"Talk Show",
    "Reality-TV":"Reality TV","Game-Show":"Game Show",
}

TRADUCAO_IDIOMAS = {
    "en":"Inglês","fr":"Francês","es":"Espanhol","de":"Alemão",
    "it":"Italiano","ja":"Japonês","ko":"Coreano","zh":"Chinês",
    "pt":"Português","ru":"Russo","hi":"Hindi","ar":"Árabe",
    "nl":"Holandês","sv":"Sueco","pl":"Polonês","tr":"Turco",
}

def _ler_csv(caminho):
    for enc in ("utf-8", "utf-8-sig", "latin1"):
        try:
            return pd.read_csv(caminho, encoding=enc, low_memory=False)
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Não foi possível ler {caminho}")

def _parse(val):
    if pd.isna(val):
        return []
    if isinstance(val, (list, dict)):
        return val
    try:
        return json.loads(val)
    except Exception:
        try:
            return ast.literal_eval(val)
        except Exception:
            return []

def _nomes_json(val, chave="name"):
    p = _parse(val)
    return [i.get(chave,"") for i in p if isinstance(i, dict)] if isinstance(p, list) else []

def _diretor_json(crew_val):
    for m in _parse(crew_val):
        if isinstance(m, dict) and m.get("job") == "Director":
            return m.get("name")
    return None

def _traduzir_generos(texto):
    if not texto or (isinstance(texto, float) and np.isnan(texto)):
        return None
    partes = [g.strip() for g in str(texto).split(",")]
    traduzidos = [TRADUCAO_GENEROS.get(g, g) for g in partes if g]
    return ", ".join(traduzidos) if traduzidos else None

def _normalizar(df: pd.DataFrame) -> pd.DataFrame:
    """Garante colunas canônicas e calcula métricas derivadas."""
    for col in ("budget","gross","profit","roi","runtime","rating","votes","year"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ("budget","gross"):
        if col in df.columns:
            df[col] = df[col].replace(0, np.nan)

    if "budget" in df.columns and "gross" in df.columns:
        if "profit" not in df.columns:
            df["profit"] = df["gross"] - df["budget"]
        if "roi" not in df.columns:
            df["roi"] = (df["profit"] / df["budget"]).replace([np.inf,-np.inf], np.nan)

    if "genre" in df.columns:
        df["genre"] = df["genre"].apply(_traduzir_generos)
        df = df[df["genre"].notna() & (df["genre"].str.strip() != "")]

    if "title" in df.columns:
        df = df.dropna(subset=["title"])
        df["title"] = df["title"].str.strip()

    if "language" in df.columns:
        df["language"] = df["language"].map(
            lambda x: TRADUCAO_IDIOMAS.get(str(x).strip(), str(x)) if pd.notna(x) else x)

    return df.reset_index(drop=True)


def _detectar_formato(df: pd.DataFrame) -> str:
    """Identifica qual schema o CSV tem."""
    colunas = set(df.columns.str.lower())
    if "vote_average" in colunas and "genres" in colunas:
        return "tmdb_antigo"
    if {"averagerating","numvotes","primarytitle"} & colunas:
        return "imdb_puro"
    if {"director","genres","budget","revenue"} <= colunas:
        return "merged_novo"
    if {"director","genre","budget","revenue"} <= colunas:
        return "merged_novo_alt"
    if {"director","genre","budget","gross"} <= colunas:
        return "merged_gross"
    return "generico"


def _processar_tmdb_antigo(df_filmes: pd.DataFrame,
                            df_creditos: pd.DataFrame = None) -> pd.DataFrame:
    """Processa o formato TMDB 5000 (dois CSVs com JSON aninhado)."""
    if df_creditos is not None:
        if "movie_id" in df_creditos.columns:
            df_creditos = df_creditos.rename(columns={"movie_id":"id"})
        if "title" in df_creditos.columns:
            df_creditos = df_creditos.drop(columns=["title"])
        df = df_filmes.merge(df_creditos, on="id", how="left")
    else:
        df = df_filmes.copy()

    df["genre"]    = df.get("genres", pd.Series(dtype=str)).apply(
        lambda v: ", ".join(_nomes_json(v)))
    df["director"] = df.get("crew",   pd.Series(dtype=str)).apply(_diretor_json)

    mapa = {
        "vote_average":"rating","vote_count":"votes",
        "revenue":"gross","runtime":"runtime",
        "release_date":"data_lancamento","original_language":"language",
        "popularity":"popularity","overview":"sinopse","title":"title",
    }
    df = df.rename(columns={k:v for k,v in mapa.items() if k in df.columns})

    if "data_lancamento" in df.columns:
        df["year"] = pd.to_datetime(df["data_lancamento"], errors="coerce").dt.year

    df = df.rename(columns={"budget":"budget"})
    return _normalizar(df)


def _processar_merged_novo(df: pd.DataFrame) -> pd.DataFrame:
    """Processa o novo CSV merged (TMDB+IMDB, ~400k filmes, um único arquivo)."""
    df = df.copy()

    mapa_colunas = {
        "averageRating":    "rating",
        "averagerating":    "rating",
        "numVotes":         "votes",
        "numvotes":         "votes",
        "primaryTitle":     "title",
        "primarytitle":     "title",
        "originalTitle":    "original_title",
        "revenue":          "gross",
        "runtimeMinutes":   "runtime",
        "startYear":        "year",
        "startyear":        "year",
        "primaryName":      "director",
        "primaryname":      "director",
        "genres":           "genre",
        "tconst":           "imdb_id",
        "isAdult":          "adulto",
    }
    df = df.rename(columns={k:v for k,v in mapa_colunas.items() if k in df.columns})

    if "genre" not in df.columns and "genre_x" in df.columns:
        df["genre"] = df["genre_x"]
    if "genre" not in df.columns and "genre_y" in df.columns:
        df["genre"] = df["genre_y"]

    if "genre" in df.columns:
        df["genre"] = df["genre"].astype(str).str.replace(r"[\\N]","", regex=True)
        df["genre"] = df["genre"].replace({"nan":None, "":None, "\\N":None})

    if "title" not in df.columns and "title_x" in df.columns:
        df["title"] = df["title_x"]

    for col in ("budget","gross"):
        if col not in df.columns:
            for alt in (col+"_x", col+"_y", "budget_usd", "revenue_usd"):
                if alt in df.columns:
                    df[col] = df[alt]
                    break

    if "adulto" in df.columns:
        df = df[df["adulto"].astype(str).isin(["0","False","false",""])]

    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce")
        df = df[df["year"].between(1900, 2030, inclusive="both") | df["year"].isna()]

    return _normalizar(df)


def _processar_generico(df: pd.DataFrame) -> pd.DataFrame:
    """Tenta mapear qualquer CSV desconhecido para o schema canônico."""
    df = df.copy()
    candidatos = {
        "title":    ["title","primaryTitle","movie_title","name","film_title","titulo"],
        "rating":   ["rating","vote_average","averageRating","imdb_score","score"],
        "votes":    ["votes","vote_count","numVotes","num_voted_users"],
        "budget":   ["budget","budget_usd"],
        "gross":    ["gross","revenue","box_office","gross_income"],
        "runtime":  ["runtime","runtimeMinutes","duration","film_length"],
        "year":     ["year","startYear","release_year","title_year"],
        "director": ["director","primaryName","director_name"],
        "genre":    ["genre","genres","film_genre","category"],
        "language": ["language","original_language","primaryLanguage"],
    }
    for destino, fontes in candidatos.items():
        if destino not in df.columns:
            for fonte in fontes:
                if fonte in df.columns:
                    df[destino] = df[fonte]
                    break
    return _normalizar(df)


def load_single(caminho: str) -> pd.DataFrame:
    """Carrega UM CSV (novo formato merged ou qualquer outro arquivo único)."""
    if not os.path.exists(caminho):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    df = _ler_csv(caminho)
    fmt = _detectar_formato(df)

    if fmt == "tmdb_antigo":
        return _processar_tmdb_antigo(df)
    elif fmt in ("merged_novo","merged_novo_alt","merged_gross","imdb_puro"):
        return _processar_merged_novo(df)
    else:
        return _processar_generico(df)


def load_and_merge(movies_path: str, credits_path: str) -> pd.DataFrame:
    """Carrega e une dois CSVs (formato TMDB 5000 antigo)."""
    df_m = _ler_csv(movies_path)
    df_c = _ler_csv(credits_path)
    return _processar_tmdb_antigo(df_m, df_c)


def load_sample() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n   = 500
    generos = ["Ação","Comédia","Drama","Terror","Romance",
               "Suspense","Animação","Ficção Científica","Crime","Aventura"]
    diretores = ["Christopher Nolan","Steven Spielberg","Martin Scorsese",
                 "Quentin Tarantino","James Cameron","Ridley Scott",
                 "David Fincher","Denis Villeneuve","Greta Gerwig","Jordan Peele"]
    orc = rng.exponential(30_000_000, n).clip(500_000, 300_000_000)
    rec = orc * rng.uniform(0.2, 6.0, n)
    df  = pd.DataFrame({
        "title":    [f"Filme {i}" for i in range(n)],
        "genre":    rng.choice(generos, n),
        "director": rng.choice(diretores, n),
        "year":     rng.integers(1990, 2024, n).astype(float),
        "runtime":  rng.normal(110, 20, n).clip(70, 200),
        "rating":   rng.normal(6.5, 1.2, n).clip(1, 10),
        "votes":    rng.exponential(100_000, n),
        "budget":   orc,
        "gross":    rec,
        "language": rng.choice(["Inglês","Francês","Espanhol","Alemão","Japonês"],
                                n, p=[0.7,0.08,0.08,0.07,0.07]),
    })
    df["profit"] = df["gross"] - df["budget"]
    df["roi"]    = df["profit"] / df["budget"]
    return df
