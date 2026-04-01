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
streamlit run projeto_acoes/app.py
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

## Architecture

This is a Streamlit dashboard for comparing stock performance of Brazilian telecom companies on B3 (Vivo/VIVT3.SA, TIM/TIMS3.SA, Oi/OIBR3.SA), located in `projeto_acoes/`.

The app is split into three modules with clear separation of concerns:

- **`data.py`** — Data fetching (via `yfinance`) and metric calculations. Contains the `ACOES` ticker dictionary, `baixar_dados()` for price history, `calcular_retorno_acumulado()` for base-100 cumulative returns, and `calcular_metricas()` for summary stats.
- **`charts.py`** — Plotly visualizations with a shared dark theme (`LAYOUT_BASE`, background `#0e1117`). Contains `grafico_precos()`, `grafico_retorno_acumulado()`, and `grafico_volatilidade()`. Company colors are defined in the `CORES` dict.
- **`app.py`** — Streamlit UI orchestration. Manages sidebar filters (date range, company checkboxes), renders KPI cards via inline HTML/CSS, calls chart functions, and displays the metrics table and analysis text.

Data flows from sidebar inputs → `data.py` → `charts.py` + `app.py` rendering. Streamlit reruns the entire script on each user interaction.

Note: Oi (OIBR3.SA) is in judicial recovery — the app includes a special warning section for it.
