import io, os, datetime
import numpy as np
import pandas as pd

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, HRFlowable, PageBreak, KeepTogether,
)
from reportlab.platypus.flowables import HRFlowable

from .analysis import (
    popularidade_por_genero, quantidade_por_genero, financeiro_por_genero,
    faixas_orcamento, analise_duracao, estatisticas_diretores, formatar_usd,
)
from .visualization import gerar_todos_graficos

VERMELHO  = colors.HexColor("#E50914")
DOURADO   = colors.HexColor("#C9A84C")
AMARELO   = colors.HexColor("#F5C518")
ESCURO    = colors.HexColor("#0D0D0D")
SUPERFICIE= colors.HexColor("#1A1A1A")
CINZA     = colors.HexColor("#2A2A2A")
CINZA_MED = colors.HexColor("#666666")
CINZA_CLR = colors.HexColor("#AAAAAA")
BRANCO    = colors.white
VERDE     = colors.HexColor("#2ECC71")
NEGATIVO  = colors.HexColor("#E74C3C")

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
LOGO_PDF  = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo_pdf.png")


def _estilos():
    return {
        "titulo_capa": ParagraphStyle(
            "titulo_capa", fontName="Helvetica-Bold", fontSize=32,
            textColor=BRANCO, spaceAfter=4, leading=38, alignment=1,
        ),
        "sub_capa": ParagraphStyle(
            "sub_capa", fontName="Helvetica", fontSize=14,
            textColor=CINZA_CLR, spaceAfter=4, leading=18, alignment=1,
        ),
        "data_capa": ParagraphStyle(
            "data_capa", fontName="Helvetica", fontSize=10,
            textColor=CINZA_MED, spaceAfter=4, alignment=1,
        ),
        "secao": ParagraphStyle(
            "secao", fontName="Helvetica-Bold", fontSize=15,
            textColor=DOURADO, spaceBefore=14, spaceAfter=5,
        ),
        "subsecao": ParagraphStyle(
            "subsecao", fontName="Helvetica-Bold", fontSize=11,
            textColor=BRANCO, spaceBefore=8, spaceAfter=4,
        ),
        "corpo": ParagraphStyle(
            "corpo", fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#DDDDDD"), leading=15, spaceAfter=5,
        ),
        "insight": ParagraphStyle(
            "insight", fontName="Helvetica-Oblique", fontSize=10,
            textColor=AMARELO, leading=15, spaceAfter=5,
            leftIndent=14, rightIndent=14,
        ),
        "rodape": ParagraphStyle(
            "rodape", fontName="Helvetica", fontSize=7, textColor=CINZA_MED,
        ),
    }


def _img(dados: bytes, larg_cm=17) -> Image:
    buf = io.BytesIO(dados)
    img = Image(buf)
    prop = img.imageHeight / img.imageWidth
    w = larg_cm * cm
    img.drawWidth, img.drawHeight = w, w * prop
    return img


def _img_path(caminho: str, larg_cm: float, alt_cm: float = None) -> Image:
    img = Image(caminho)
    prop = img.imageHeight / img.imageWidth
    w = larg_cm * cm
    h = (alt_cm * cm) if alt_cm else w * prop
    img.drawWidth, img.drawHeight = w, h
    return img


def _tabela(cab, linhas, largs, cab_cor=VERMELHO):
    tabela = Table([cab] + linhas, colWidths=largs)
    tabela.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,0),  cab_cor),
        ("TEXTCOLOR",      (0,0),(-1,0),  BRANCO),
        ("FONTNAME",       (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",       (0,0),(-1,0),  9),
        ("ALIGN",          (0,0),(-1,-1), "CENTER"),
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,1),(-1,-1), [SUPERFICIE, CINZA]),
        ("TEXTCOLOR",      (0,1),(-1,-1), BRANCO),
        ("FONTNAME",       (0,1),(-1,-1), "Helvetica"),
        ("FONTSIZE",       (0,1),(-1,-1), 9),
        ("GRID",           (0,0),(-1,-1), 0.3, CINZA_MED),
        ("TOPPADDING",     (0,0),(-1,-1), 5),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 5),
        ("LEFTPADDING",    (0,0),(-1,-1), 6),
        ("RIGHTPADDING",   (0,0),(-1,-1), 6),
    ]))
    return tabela


def _linha():
    return HRFlowable(width="100%", thickness=0.4, color=CINZA_MED,
                      spaceAfter=5, spaceBefore=5)


def _espaco(h=0.3):
    return Spacer(1, h * cm)


def _cabecalho_rodape(canvas, doc):
    canvas.saveState()
    larg, alt = A4

    canvas.setFillColor(ESCURO)
    canvas.rect(0, 0, larg, alt, fill=1, stroke=0)

    canvas.setFillColor(colors.HexColor("#1A0A00"))
    canvas.rect(0, alt - 1.4*cm, larg, 1.4*cm, fill=1, stroke=0)
    canvas.setStrokeColor(DOURADO)
    canvas.setLineWidth(0.8)
    canvas.line(0, alt - 1.4*cm, larg, alt - 1.4*cm)

    if os.path.exists(LOGO_PDF):
        logo_h = 1.1 * cm
        logo_w = logo_h * (704 / 768)
        canvas.drawImage(LOGO_PDF, 1.2*cm, alt - 1.3*cm,
                         width=logo_w, height=logo_h,
                         mask="auto", preserveAspectRatio=True)
        texto_x = 1.2*cm + logo_w + 0.3*cm
    else:
        texto_x = 1.2*cm

    canvas.setFillColor(BRANCO)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawString(texto_x, alt - 0.75*cm, "Foundation Frame Studios")
    canvas.setFillColor(CINZA_CLR)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(texto_x + 4.5*cm, alt - 0.75*cm, "— Relatório de Análise de Filmes")
    canvas.setFillColor(CINZA_CLR)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(larg - 1.2*cm, alt - 0.75*cm, f"Página {doc.page}")

    canvas.setFillColor(colors.HexColor("#111111"))
    canvas.rect(0, 0, larg, 0.9*cm, fill=1, stroke=0)
    canvas.setStrokeColor(DOURADO)
    canvas.setLineWidth(0.5)
    canvas.line(0, 0.9*cm, larg, 0.9*cm)
    canvas.setFillColor(CINZA_MED)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(1.2*cm, 0.3*cm, "Gerado automaticamente — Foundation Frame Studios Analytics")
    canvas.drawRightString(larg - 1.2*cm, 0.3*cm,
                           datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))

    canvas.restoreState()


def _pagina_capa(canvas, doc):
    _cabecalho_rodape(canvas, doc)
    canvas.saveState()
    larg, alt = A4

    canvas.setFillColor(DOURADO)
    canvas.setLineWidth(1.5)
    canvas.setStrokeColor(DOURADO)
    canvas.rect(1.2*cm, 1.2*cm, larg - 2.4*cm, alt - 2.4*cm, fill=0, stroke=1)
    canvas.setLineWidth(0.4)
    canvas.setStrokeColor(colors.HexColor("#3A2A00"))
    canvas.rect(1.5*cm, 1.5*cm, larg - 3.0*cm, alt - 3.0*cm, fill=0, stroke=1)

    if os.path.exists(LOGO_PATH):
        logo_w, logo_h = 9*cm, 4.9*cm
        logo_x = (larg - logo_w) / 2
        logo_y = alt * 0.52
        canvas.drawImage(LOGO_PATH, logo_x, logo_y,
                         width=logo_w, height=logo_h,
                         mask="auto", preserveAspectRatio=True)

    canvas.setFillColor(DOURADO)
    canvas.setLineWidth(0.6)
    canvas.line(2.5*cm, alt * 0.49, larg - 2.5*cm, alt * 0.49)

    canvas.setFillColor(BRANCO)
    canvas.setFont("Helvetica-Bold", 26)
    canvas.drawCentredString(larg/2, alt * 0.43, "RELATÓRIO DE ANÁLISE DE FILMES")

    canvas.setFillColor(CINZA_CLR)
    canvas.setFont("Helvetica", 13)
    canvas.drawCentredString(larg/2, alt * 0.38, "Base de Dados TMDB 5000 — Insights para Produtores")

    canvas.setFillColor(DOURADO)
    canvas.setLineWidth(0.6)
    canvas.line(2.5*cm, alt * 0.35, larg - 2.5*cm, alt * 0.35)

    canvas.setFillColor(CINZA_MED)
    canvas.setFont("Helvetica", 10)
    data_str = datetime.datetime.now().strftime("%d de %B de %Y")
    canvas.drawCentredString(larg/2, alt * 0.30, f"Gerado em {data_str}")

    canvas.setFillColor(DOURADO)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.drawCentredString(larg/2, alt * 0.24, "CONFIDENCIAL — USO INTERNO")

    canvas.restoreState()


def gerar_relatorio_pdf(df: pd.DataFrame) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2.2*cm,  bottomMargin=1.5*cm,
    )

    s        = _estilos()
    graficos = gerar_todos_graficos(df)
    paginas  = []

    col_dir    = "diretor"    if "diretor"    in df.columns else "director"
    col_gen    = "genre"
    col_rat    = "avaliacao"  if "avaliacao"  in df.columns else "rating"
    col_orc    = "orcamento"  if "orcamento"  in df.columns else "budget"
    col_rec    = "receita"    if "receita"    in df.columns else "gross"
    col_luc    = "lucro"      if "lucro"      in df.columns else "profit"
    col_dur    = "duracao"    if "duracao"    in df.columns else "runtime"
    col_ano    = "ano"        if "ano"        in df.columns else "year"
    col_titulo = "titulo"     if "titulo"     in df.columns else "title"

    paginas.append(_espaco(10))

    paginas.append(PageBreak())

    paginas.append(_espaco(0.3))

    periodo = ""
    if col_ano in df.columns:
        periodo = f"  •  Período: {int(df[col_ano].min())}–{int(df[col_ano].max())}"

    paginas.append(Paragraph(
        f"Base com <b>{len(df):,} filmes</b> analisados{periodo}.",
        s["corpo"],
    ))
    paginas.append(_espaco(0.4))

    kpis = []
    if col_rat in df.columns: kpis.append(("Avaliação Média", f"{df[col_rat].mean():.2f}"))
    if col_orc in df.columns: kpis.append(("Orçamento Médio", formatar_usd(df[col_orc].mean())))
    if col_rec in df.columns: kpis.append(("Receita Média",   formatar_usd(df[col_rec].mean())))
    if col_luc in df.columns: kpis.append(("Lucro Médio",     formatar_usd(df[col_luc].mean())))

    if kpis:
        w = 17*cm / len(kpis)
        tb = Table([[r for r,_ in kpis],[v for _,v in kpis]], colWidths=[w]*len(kpis))
        tb.setStyle(TableStyle([
            ("BACKGROUND",     (0,0),(-1,0), CINZA),
            ("BACKGROUND",     (0,1),(-1,1), SUPERFICIE),
            ("TEXTCOLOR",      (0,0),(-1,0), CINZA_CLR),
            ("TEXTCOLOR",      (0,1),(-1,1), AMARELO),
            ("FONTNAME",       (0,0),(-1,0), "Helvetica"),
            ("FONTNAME",       (0,1),(-1,1), "Helvetica-Bold"),
            ("FONTSIZE",       (0,0),(-1,0), 8),
            ("FONTSIZE",       (0,1),(-1,1), 13),
            ("ALIGN",          (0,0),(-1,-1), "CENTER"),
            ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
            ("TOPPADDING",     (0,0),(-1,-1), 7),
            ("BOTTOMPADDING",  (0,0),(-1,-1), 7),
            ("GRID",           (0,0),(-1,-1), 0.3, CINZA_MED),
            ("BOX",            (0,0),(-1,-1), 1.2, DOURADO),
        ]))
        paginas.append(tb)

    paginas.append(PageBreak())
    paginas.append(Paragraph("1. Que Tipo de Filme o Público Prefere?", s["secao"]))
    paginas.append(_linha())

    pop = popularidade_por_genero(df)
    if not pop.empty:
        top1 = pop.iloc[0]
        paginas.append(Paragraph(
            f"O gênero <b>{top1['genre']}</b> é o favorito do público, com pontuação de popularidade "
            f"de <b>{top1['popularity_score']:.1f}</b> — combinando avaliação média de "
            f"<b>{top1['avg_rating']:.2f}</b> e <b>{int(top1['avg_votes']):,}</b> votos médios por filme.",
            s["corpo"],
        ))
        paginas.append(Paragraph(
            f"Recomendação: Produções do gênero {top1['genre']} tendem a maximizar o engajamento "
            "e a aprovação do público.",
            s["insight"],
        ))
        if "adesao_generos" in graficos:
            paginas.append(_img(graficos["adesao_generos"]))

        top5 = pop.head(5)
        paginas.append(Paragraph("Top 5 Gêneros por Preferência do Público", s["subsecao"]))
        paginas.append(_tabela(
            ["#", "Gênero", "Avaliação Média", "Votos Médios", "Pontuação"],
            [[str(i+1), r["genre"], f"{r['avg_rating']:.2f}",
              f"{int(r['avg_votes']):,}", f"{r['popularity_score']:.1f}"]
             for i, (_,r) in enumerate(top5.iterrows())],
            [1*cm, 5.5*cm, 3*cm, 3.5*cm, 4*cm],
        ))

    if "rating_por_genero" in graficos:
        paginas.append(_espaco(0.5))
        paginas.append(Paragraph("Avaliação Média por Gênero", s["subsecao"]))
        paginas.append(_img(graficos["rating_por_genero"]))

    paginas.append(PageBreak())
    paginas.append(Paragraph("2. Gêneros Mais Produzidos no Mercado", s["secao"]))
    paginas.append(_linha())

    prod = quantidade_por_genero(df).head(10)
    if not prod.empty:
        lider = prod.iloc[0]
        paginas.append(Paragraph(
            f"<b>{lider['genre']}</b> domina a produção com <b>{int(lider['count']):,}</b> filmes "
            f"— <b>{100*lider['count']/len(df):.1f}%</b> do total da base.",
            s["corpo"],
        ))
        if "generos_produzidos" in graficos:
            paginas.append(_img(graficos["generos_produzidos"]))
        paginas.append(Paragraph("Volume de Produção por Gênero", s["subsecao"]))
        paginas.append(_tabela(
            ["#", "Gênero", "Total de Filmes", "% da Base"],
            [[str(i+1), r["genre"], f"{int(r['count']):,}", f"{100*r['count']/len(df):.1f}%"]
             for i, (_,r) in enumerate(prod.iterrows())],
            [1*cm, 6*cm, 5*cm, 5*cm],
        ))

    paginas.append(PageBreak())
    paginas.append(Paragraph("3. Quanto Custa Produzir um Filme?", s["secao"]))
    paginas.append(_linha())

    faixas = faixas_orcamento(df)
    if not faixas.empty:
        m_roi  = faixas.loc[faixas["avg_roi"].idxmax()]
        m_luc  = faixas.loc[faixas["avg_profit"].idxmax()]
        paginas.append(Paragraph(
            f"A faixa <b>{m_roi['budget_range']}</b> oferece o melhor ROI médio "
            f"(<b>{m_roi['avg_roi']*100:.0f}%</b>). Filmes na faixa "
            f"<b>{m_luc['budget_range']}</b> geram o maior lucro absoluto: "
            f"<b>{formatar_usd(m_luc['avg_profit'])}</b> por filme em média.",
            s["corpo"],
        ))
        paginas.append(Paragraph(
            "Para maximizar o ROI invista nas faixas menores. "
            "Para lucro total, filmes de grande orçamento têm maior retorno absoluto quando bem executados.",
            s["insight"],
        ))
        if "faixas_orcamento" in graficos:
            paginas.append(_img(graficos["faixas_orcamento"]))
        paginas.append(Paragraph("Análise por Faixa de Orçamento", s["subsecao"]))
        paginas.append(_tabela(
            ["Faixa de Orçamento", "Filmes", "Lucro Médio", "ROI Médio", "Avaliação Média"],
            [[str(r["budget_range"]), str(int(r["count"])),
              formatar_usd(r["avg_profit"]), f"{r['avg_roi']*100:.0f}%",
              f"{r['avg_rating']:.2f}"]
             for _,r in faixas.iterrows()],
            [4.5*cm, 2.5*cm, 3.5*cm, 3*cm, 3.5*cm],
        ))
    if "orcamento_lucro" in graficos:
        paginas.append(_espaco(0.3))
        paginas.append(_img(graficos["orcamento_lucro"]))

    paginas.append(PageBreak())
    paginas.append(Paragraph("4. Retorno Financeiro por Gênero", s["secao"]))
    paginas.append(_linha())

    fin = financeiro_por_genero(df).head(8)
    if not fin.empty and "avg_profit" in fin.columns:
        mf = fin.iloc[0]
        paginas.append(Paragraph(
            f"<b>{mf['genre']}</b> é o gênero mais rentável com lucro médio de "
            f"<b>{formatar_usd(mf['avg_profit'])}</b> por filme, ROI de "
            f"<b>{mf['avg_roi']*100:.0f}%</b> e orçamento médio de "
            f"<b>{formatar_usd(mf['avg_budget'])}</b>.",
            s["corpo"],
        ))
        if "lucro_por_genero" in graficos:
            paginas.append(_img(graficos["lucro_por_genero"]))
        paginas.append(Paragraph("Desempenho Financeiro por Gênero", s["subsecao"]))
        paginas.append(_tabela(
            ["Gênero", "Orçamento Médio", "Receita Média", "Lucro Médio", "ROI Médio"],
            [[r["genre"], formatar_usd(r["avg_budget"]), formatar_usd(r["avg_gross"]),
              formatar_usd(r["avg_profit"]), f"{r['avg_roi']*100:.0f}%"]
             for _,r in fin.iterrows()],
            [4*cm, 3.5*cm, 3.5*cm, 3*cm, 3*cm],
        ))

    paginas.append(PageBreak())
    paginas.append(Paragraph("5. Duração Ideal de um Filme", s["secao"]))
    paginas.append(_linha())

    if col_dur in df.columns:
        rt = analise_duracao(df)
        md = rt.loc[rt["avg_rating"].idxmax()]
        paginas.append(Paragraph(
            f"Filmes com duração entre <b>{md['runtime_range']} minutos</b> "
            f"alcançam a melhor avaliação média: <b>{md['avg_rating']:.2f}</b>. "
            "Essa faixa equilibra entretenimento e atenção do espectador.",
            s["corpo"],
        ))
        paginas.append(Paragraph(
            f"Recomendação: Planeje sua produção para durar {md['runtime_range']} minutos "
            "para maximizar a satisfação do público.",
            s["insight"],
        ))
        if "duracao" in graficos:
            paginas.append(_img(graficos["duracao"]))
        paginas.append(Paragraph("Avaliação e Lucro por Faixa de Duração", s["subsecao"]))
        cab_rt = ["Duração", "Filmes", "Avaliação Média"]
        larg_rt = [4.5*cm, 3*cm, 4*cm]
        if "avg_profit" in rt.columns:
            cab_rt.append("Lucro Médio")
            larg_rt.append(5.5*cm)
        linhas_rt = []
        for _,row in rt.iterrows():
            l = [str(row["runtime_range"]), str(int(row["count"])), f"{row['avg_rating']:.2f}"]
            if "avg_profit" in rt.columns:
                l.append(formatar_usd(row["avg_profit"]) if pd.notna(row.get("avg_profit")) else "N/A")
            linhas_rt.append(l)
        paginas.append(_tabela(cab_rt, linhas_rt, larg_rt))

    paginas.append(PageBreak())
    paginas.append(Paragraph("6. Diretores Mais Lucrativos", s["secao"]))
    paginas.append(_linha())

    if col_dir in df.columns:
        df_dir = df.copy()
        if col_dir != "director":
            df_dir["director"] = df_dir[col_dir]
        stats = estatisticas_diretores(df_dir, min_filmes=3)
        if not stats.empty:
            pr = stats.iloc[0]
            paginas.append(Paragraph(
                f"<b>{pr['director']}</b> é o diretor mais lucrativo, acumulando "
                f"<b>{formatar_usd(pr['total_profit'])}</b> com <b>{int(pr['films'])}</b> filmes "
                f"e avaliação média de <b>{pr['avg_rating']:.2f}</b>.",
                s["corpo"],
            ))
            if "top_diretores" in graficos:
                paginas.append(_img(graficos["top_diretores"]))
            if "roi_diretores" in graficos:
                paginas.append(_img(graficos["roi_diretores"]))
            paginas.append(Paragraph("Top 10 Diretores — Lucro Total", s["subsecao"]))
            paginas.append(_tabela(
                ["#", "Diretor", "Filmes", "Avaliação", "Lucro Total", "ROI Médio"],
                [[str(i+1), r["director"], str(int(r["films"])),
                  f"{r['avg_rating']:.2f}", formatar_usd(r["total_profit"]),
                  f"{r['avg_roi']*100:.0f}%" if pd.notna(r.get("avg_roi")) else "N/A"]
                 for i,(_,r) in enumerate(stats.head(10).iterrows())],
                [0.8*cm, 5*cm, 1.8*cm, 2.2*cm, 4*cm, 3.2*cm],
            ))

    paginas.append(PageBreak())
    paginas.append(Paragraph("7. Resumo Executivo e Recomendações", s["secao"]))
    paginas.append(_linha())

    if os.path.exists(LOGO_PDF):
        logo_w, logo_h = 4*cm, 4*(768/704)*cm
        paginas.append(Table(
            [[_img_path(LOGO_PDF, 4, 4*(768/704)),
              Paragraph(
                  "Com base na análise completa da base de dados TMDB 5000, "
                  "a Foundation Frame Studios identificou as principais oportunidades "
                  "para maximizar o retorno e a aceitação do público nas próximas produções.",
                  s["corpo"]
              )]],
            colWidths=[4.5*cm, 12.5*cm],
            style=TableStyle([
                ("VALIGN", (0,0),(-1,-1), "MIDDLE"),
                ("LEFTPADDING", (0,0),(-1,-1), 0),
                ("RIGHTPADDING", (0,0),(-1,-1), 8),
            ]),
        ))
    else:
        paginas.append(Paragraph(
            "Com base na análise completa da base de dados TMDB 5000, "
            "a Foundation Frame Studios identificou as principais oportunidades "
            "para maximizar o retorno e a aceitação do público.",
            s["corpo"],
        ))

    paginas.append(_espaco(0.3))

    recs = []
    pop2 = popularidade_por_genero(df)
    if not pop2.empty:
        g,r = pop2.iloc[0]["genre"], pop2.iloc[0]["avg_rating"]
        recs.append(f"<b>Gênero recomendado:</b> {g} — maior adesão do público (avaliação média {r:.2f}).")

    faixas2 = faixas_orcamento(df)
    if not faixas2.empty:
        fr = faixas2.loc[faixas2["avg_roi"].idxmax()]
        recs.append(f"<b>Orçamento ideal para ROI:</b> Faixa {fr['budget_range']} — ROI médio de {fr['avg_roi']*100:.0f}%.")

    if col_dur in df.columns:
        rt2 = analise_duracao(df)
        dr  = rt2.loc[rt2["avg_rating"].idxmax()]
        recs.append(f"<b>Duração ideal:</b> {dr['runtime_range']} minutos — melhor avaliação média ({dr['avg_rating']:.2f}).")

    if col_dir in df.columns:
        df_dir2 = df.copy()
        if col_dir != "director":
            df_dir2["director"] = df_dir2[col_dir]
        st2 = estatisticas_diretores(df_dir2, min_filmes=3)
        if not st2.empty:
            d = st2.iloc[0]
            recs.append(f"<b>Diretor de referência:</b> {d['director']} — maior retorno acumulado ({formatar_usd(d['total_profit'])}).")

    fin2 = financeiro_por_genero(df)
    if not fin2.empty and "avg_profit" in fin2.columns:
        fg = fin2.iloc[0]
        recs.append(f"<b>Gênero mais rentável:</b> {fg['genre']} — lucro médio de {formatar_usd(fg['avg_profit'])} por filme.")

    for rec in recs:
        paginas.append(KeepTogether([
            Paragraph(f"▸  {rec}", s["corpo"]),
            _espaco(0.15),
        ]))

    paginas.append(_espaco(0.8))
    paginas.append(_linha())
    paginas.append(Paragraph(
        "Este relatório foi gerado automaticamente pelo sistema de análise da Foundation Frame Studios. "
        "Os dados são provenientes da base TMDB 5000 e os insights refletem os filtros aplicados pelo usuário. "
        "Para informações adicionais, consulte o dashboard interativo.",
        s["rodape"],
    ))

    doc.build(paginas, onFirstPage=_pagina_capa, onLaterPages=_cabecalho_rodape)
    buf.seek(0)
    return buf.read()
