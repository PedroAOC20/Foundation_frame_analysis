from .data_loader import load_and_merge, load_single, load_sample

from .analysis import (
    expandir_generos, formatar_usd,
    popularidade_por_genero, quantidade_por_genero, financeiro_por_genero,
    faixas_orcamento, filmes_lucrativos, analise_duracao, estatisticas_diretores,
    explode_genres, fmt_usd,
    genre_popularity, genre_production_count, genre_financial,
    budget_buckets, profitable_films, runtime_analysis, director_stats,
)

from .theme import (
    aplicar_tema, nova_figura, novas_figuras,
    formatar_eixo_milhoes, rotulos_nas_barras,
    injetar_css, caixa_insight,
    CORES, PALETA,
    apply_theme, new_fig, new_figs, fmt_millions, add_bar_labels,
    inject_css, insight_box, COLORS, PALETTE,
)

from .visualization import (
    grafico_producao_por_ano, grafico_distribuicao_ratings, grafico_correlacao,
    grafico_adesao_generos, grafico_generos_produzidos, grafico_rating_por_genero,
    grafico_lucro_por_genero, grafico_faixas_orcamento, grafico_orcamento_lucro,
    grafico_duracao, grafico_top_diretores, grafico_roi_diretores,
    gerar_todos_graficos, GRAFICOS_DISPONIVEIS,
)

from .relatorio_pdf import gerar_relatorio_pdf
