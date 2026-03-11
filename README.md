<div align="center">

```
███████╗ ██████╗ ██╗   ██╗███╗   ██╗██████╗  █████╗ ████████╗██╗ ██████╗ ███╗   ██╗
██╔════╝██╔═══██╗██║   ██║████╗  ██║██╔══██╗██╔══██╗╚══██╔══╝██║██╔═══██╗████╗  ██║
█████╗  ██║   ██║██║   ██║██╔██╗ ██║██║  ██║███████║   ██║   ██║██║   ██║██╔██╗ ██║
██╔══╝  ██║   ██║██║   ██║██║╚██╗██║██║  ██║██╔══██║   ██║   ██║██║   ██║██║╚██╗██║
██║     ╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║   ██║   ██║╚██████╔╝██║ ╚████║
╚═╝      ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝ ╚═════╝ ╚═╝  ╚═══╝

███████╗██████╗  █████╗ ███╗   ███╗███████╗    ███████╗████████╗██╗   ██╗██████╗ ██╗ ██████╗ ███████╗
██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝    ██╔════╝╚══██╔══╝██║   ██║██╔══██╗██║██╔═══██╗██╔════╝
█████╗  ██████╔╝███████║██╔████╔██║█████╗      ███████╗   ██║   ██║   ██║██║  ██║██║██║   ██║███████╗
██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝      ╚════██║   ██║   ██║   ██║██║  ██║██║██║   ██║╚════██║
██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗    ███████║   ██║   ╚██████╔╝██████╔╝██║╚██████╔╝███████║
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚══════╝   ╚═╝    ╚═════╝ ╚═════╝ ╚═╝ ╚═════╝ ╚══════╝
```

**Dashboard interativo de análise de filmes para produtores de cinema**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-red?style=flat-square&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.2%2B-150458?style=flat-square&logo=pandas)
![ReportLab](https://img.shields.io/badge/ReportLab-PDF-orange?style=flat-square)
![uv](https://img.shields.io/badge/uv-gerenciador-green?style=flat-square)

</div>

---

# 🎬 Sobre o Projeto

O **Foundation Frame Studios Analytics** é uma ferramenta de inteligência de dados desenvolvida para apoiar decisões de produção cinematográfica. A partir de uma base com até **400 mil filmes**, o dashboard responde perguntas estratégicas como:

- 🎭 Que tipo de filme o público prefere?
- 💰 Quanto custa produzir um filme lucrativo?
- ⏱️ Qual a duração ideal para maximizar aprovação?
- 🏆 Quais gêneros têm o melhor retorno financeiro?
- 🎬 Quais diretores entregam mais resultado?

Ao final de qualquer análise, é possível exportar um **relatório PDF completo** com todos os gráficos, tabelas e recomendações geradas automaticamente — com a identidade visual da Foundation Frame Studios.

---

# 🗂️ Estrutura do Projeto

```
imdb-dashboard/
│
├── app.py                        ← Ponto de entrada do Streamlit
│
├── assets/
│   ├── logo.png                  ← Logo principal (sidebar + topo)
│   ├── logo_pdf.png              ← Logo recortada para o PDF
│   └── logo_sidebar.png          ← Logo otimizada para sidebar
│
├── data/                         ← Coloque seu CSV dataset
│   └── tmdb_5000_movies.csv
│
├── pages/
│   ├── overview.py               ← Aba: Visão Geral
│   ├── genres.py                 ← Aba: Análise de Gêneros
│   ├── financial.py              ← Aba: Análise Financeira
│   └── directors.py              ← Aba: Análise de Diretores
│
├── utils/
│   ├── data_loader.py            ← Leitura e normalização de CSV
│   ├── analysis.py               ← Funções de análise estatística
│   ├── visualization.py          ← Geração de gráficos (retorna bytes PNG)
│   ├── relatorio_pdf.py          ← Geração do relatório PDF completo
│   └── theme.py                  ← Paleta de cores, estilos e CSS
│
├── mise.toml                ← Gerenciador de versao de python
├── pyproject.toml                ← Dependências (gerenciado pelo uv)
├── uv.lock                ← Dependências (gerenciado pelo uv, rodando o comando uv sync)
└── README.md
```

---

# ✨ Funcionalidades

## Abas do Dashboard

| Aba                | O que mostra                                                                           |
| ------------------ | -------------------------------------------------------------------------------------- |
| 🏠 **Visão Geral** | KPIs principais, produção por ano, distribuição de avaliações, mapa de correlação      |
| 🎭 **Gêneros**     | Popularidade, volume de produção, rating médio, retorno financeiro por gênero          |
| 💰 **Financeiro**  | Faixas de orçamento × ROI, filmes lucrativos, scatter orçamento × lucro, duração ideal |
| 🎬 **Diretores**   | Top 10 por lucro total, por avaliação, por ROI — com tabela completa filtrável         |

## Filtros Globais

- **Período** — selecione o intervalo de anos da análise
- **Avaliação mínima** — filtre apenas filmes acima de determinada nota

## Relatório PDF

- Capa com identidade visual da Foundation Frame Studios
- 7 seções com gráficos, tabelas e insights automáticos
- Logo no cabeçalho de cada página
- Resumo executivo com recomendações geradas a partir dos dados filtrados

## Formatos de dados suportados

- **CSV**
- **Dados de demonstração** (500 filmes sintéticos, sem download necessário)

---

# 🚀 Como Rodar

## Pré-requisitos

- Python 3.10 ou superior
- Mise

```bash
# Instalar o uv (caso não tenha)
pip install uv
```

```bash
# Instalar o mise (caso não tenha)
curl https://mise.run | sh
```

## 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/imdb-dashboard.git
cd imdb-dashboard
```

## 2. Instale as dependências

```bash
# Baixar versao do python usado no projeto
mise install

# Baixar dependencia dentro da .venv
uv sync
```

## 3. (Opcional) Adicione sua base de dados

> Sem dados, o dashboard já funciona com **dados de demonstração**. Para usar a base completa:

**a)** Coloque o arquivo CSV na pasta `data/`:

- Existe as bases de exemplo que estao zipados, voce pode extrair os arquivos na pasta `data/`

```
imdb-dashboard/
└── data/
    └── datasets.zip   ← qualquer nome .csv com mais de 10 MB funciona
```

> ⚠️ O arquivo tem ~250 MB. **Não tente fazer upload pelo browser** — o Streamlit tem limite de 200 MB.
> Copie diretamente para a pasta `data/` e reinicie o dashboard.

## 4. Inicie o dashboard

```bash
uv run streamlit run app.py
```

Acesse em: **http://localhost:8501**

---

# 📸 Fluxo de uso

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FOUNDATION FRAME STUDIOS                         │
│                     Analytics Dashboard                             │
├────────────────┬────────────────────────────────────────────────────┤
│                │                                                    │
│   SIDEBAR      │   ABAS PRINCIPAIS                                  │
│                │                                                    │
│  [Logo]        │  🏠 Visão Geral │ 🎭 Gêneros │ 💰 Financeiro │ 🎬 │
│                │                                                    │
│  📂 Base       │  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  ○ CSV único   │  │  KPIs    │  │  Gráfico │  │  Tabela  │        │
│  ○ Dois CSVs   │  │ 4.821    │  │  ██████  │  │ Top 10   │        │
│  ○ Demo        │  │ filmes   │  │  ████    │  │ ...      │        │
│                │  └──────────┘  └──────────┘  └──────────┘        │
│  🔧 Filtros    │                                                    │
│  Ano: ──●──    │  ┌────────────────────────────────────┐           │
│  Nota: ─●──    │  │        💡 Insight automático        │           │
│                │  │  Drama lidera com score 42.3 ...   │           │
│  📄 PDF        │  └────────────────────────────────────┘           │
│  [Gerar ▼]     │                                                    │
│                │                                                    │
└────────────────┴────────────────────────────────────────────────────┘
```

```
Clicou em "Gerar PDF"?
        │
        ▼
┌───────────────────┐     ┌──────────────────────┐     ┌─────────────┐
│  Gera 12 gráficos │────▶│  Monta 7 seções PDF  │────▶│  Download   │
│  em segundo plano │     │  com logo + tabelas  │     │  .pdf pronto│
└───────────────────┘     └──────────────────────┘     └─────────────┘
```

---

# 🛠️ Stack Técnica

| Biblioteca               | Uso                            |
| ------------------------ | ------------------------------ |
| `streamlit`              | Interface web interativa       |
| `pandas`                 | Manipulação e análise de dados |
| `matplotlib` + `seaborn` | Geração de gráficos            |
| `numpy`                  | Cálculos numéricos             |
| `reportlab`              | Geração de PDF                 |
| `uv`                     | Gerenciamento de dependências  |

---

## 📄 Licença

Projeto desenvolvido pela **Foundation Frame Studios** para uso interno de análise de mercado cinematográfico.

---

<div align="center">
  Feito por <strong>Pedro Aoc</strong>
</div>
