# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install dependencies:**
```bash
cd projeto_acoes
pip install -r requirements.txt
```

**Run the application:**
```bash
python3 -m streamlit run projeto_acoes/app.py
```

**Stop the application:**
```bash
pkill -f streamlit
```

## GitHub

**Repository:** https://github.com/Vinicenss/projeto-acoes-brasil

**Auto-publish:** A `post-commit` git hook (`.git/hooks/post-commit`) automatically runs `git push origin main` after every commit. To publish changes, just commit normally:
```bash
git add .
git commit -m "descrição da alteração"
```
The push to GitHub happens automatically — no manual `git push` needed.

## Testes automatizados (Playwright)

**Instalar dependências de teste:**
```bash
python3 -m pip install -r requirements-test.txt
python3 -m playwright install chromium
```

**Rodar toda a suíte** (app deve estar no ar em localhost:8501):
```bash
python3 -m pytest
```

**Rodar apenas testes smoke (rápidos):**
```bash
python3 -m pytest -m smoke
```

**Rodar um arquivo específico:**
```bash
python3 -m pytest tests/test_navegacao.py
```

**Rodar com browser visível (útil ao depurar):**
```bash
python3 -m pytest --headed
```

### Estrutura dos testes

```
tests/
├── conftest.py              # fixtures: dashboard, dashboard_relatorio, dashboard_tecnica
├── pages/
│   └── dashboard.py         # Page Object Model — encapsula todos os seletores e ações
├── test_navegacao.py        # carregamento inicial, tabs, KPI cards
├── test_filtros.py          # atalhos de período, datas, seleção de operadoras
├── test_graficos.py         # charts, média móvel (toggle + slider), relatório
└── test_exportacao.py       # download CSV, expanders (Oi, Aviso Legal)
```

A fixture `dashboard` (em `conftest.py`) navega para o app e aguarda o `.status-bar` ficar visível — esse é o indicador de que o Streamlit terminou de carregar. Após interações que causam rerun, use `wait_for_rerun()` ou `wait_for_app_ready()`.

## Architecture

This is a Streamlit dashboard for comparing stock performance of Brazilian telecom companies on B3 (Vivo/VIVT3.SA, TIM/TIMS3.SA, Oi/OIBR3.SA), located in `projeto_acoes/`.

The app is split into three modules with clear separation of concerns:

- **`data.py`** — Data fetching (via `yfinance`) and metric calculations. Contains the `ACOES` ticker dictionary, `baixar_dados()` for price history, `calcular_retorno_acumulado()` for base-100 cumulative returns, and `calcular_metricas()` for summary stats.
- **`charts.py`** — Plotly visualizations with a shared light theme (`LAYOUT_BASE`). Contains `grafico_precos(df, periodo_ma=None)` (accepts optional moving average period), `grafico_retorno_acumulado()`, and `grafico_volatilidade()`. Company colors are defined in the `CORES` dict.
- **`app.py`** — Streamlit UI orchestration. Manages sidebar filters (date range, company checkboxes), renders KPI cards via inline HTML/CSS, calls chart functions, and displays the metrics table and analysis text.

Data flows from sidebar inputs → `data.py` → `charts.py` + `app.py` rendering. Streamlit reruns the entire script on each user interaction.

Note: Oi (OIBR3.SA) is in judicial recovery — the app includes a special warning section for it.
