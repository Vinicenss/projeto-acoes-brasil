import streamlit as st
from datetime import date, timedelta
from data import baixar_dados, calcular_retorno_acumulado, calcular_metricas, ACOES
from charts import grafico_precos, grafico_retorno_acumulado, grafico_volatilidade

st.set_page_config(
    page_title="Telecom Brasil — Análise de Ações",
    page_icon="📡",
    layout="wide",
)

st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }

    .main-title {
        font-size: 2rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 0;
    }
    .main-subtitle {
        font-size: 0.95rem;
        color: #6c757d;
        margin-top: 4px;
        margin-bottom: 24px;
    }

    .kpi-card {
        background: #ffffff;
        border: 1px solid #dee2e6;
        border-radius: 12px;
        padding: 18px 22px;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .kpi-label {
        font-size: 0.82rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 6px;
        font-weight: 600;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .kpi-delta-pos { color: #1a7340; font-size: 0.9rem; font-weight: 700; }
    .kpi-delta-neg { color: #c0392b; font-size: 0.9rem; font-weight: 700; }
    .kpi-rank { font-size: 1.1rem; margin-bottom: 4px; }

    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a1a2e;
        border-left: 4px solid #4361ee;
        padding-left: 12px;
        margin-top: 36px;
        margin-bottom: 14px;
    }

    .status-bar {
        background: #e8f5e9;
        border: 1px solid #a5d6a7;
        border-radius: 8px;
        padding: 8px 16px;
        font-size: 0.88rem;
        color: #1a7340;
        font-weight: 600;
        margin-bottom: 20px;
        display: inline-block;
    }

    section[data-testid="stSidebar"] {
        background-color: #f1f3f5;
        border-right: 1px solid #dee2e6;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "data_inicio" not in st.session_state:
    st.session_state.data_inicio = date(2025, 1, 2)
if "data_fim" not in st.session_state:
    st.session_state.data_fim = date(2025, 12, 31)

# --- Cabeçalho ---
st.markdown('<p class="main-title">📡 Telecom Brasil — Análise de Ações</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Comparativo de desempenho das principais operadoras listadas na B3 • Dados via Yahoo Finance</p>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Filtros")

    # Atalhos de período
    st.markdown("**Período rápido:**")
    col1, col2, col3 = st.columns(3)
    hoje = date.today()
    periodos_rapidos = [
        ("1M",  col1, hoje - timedelta(days=30),  hoje),
        ("3M",  col2, hoje - timedelta(days=90),  hoje),
        ("6M",  col3, hoje - timedelta(days=180), hoje),
        ("YTD", col1, date(hoje.year, 1, 1),      hoje),
        ("1A",  col2, hoje - timedelta(days=365),  hoje),
        ("2A",  col3, hoje - timedelta(days=730),  hoje),
    ]
    for label, col, inicio, fim in periodos_rapidos:
        with col:
            if st.button(label, use_container_width=True, key=f"btn_{label}"):
                st.session_state.data_inicio = inicio
                st.session_state.data_fim = fim
                st.rerun()

    st.markdown("")

    data_inicio = st.date_input(
        "Data de início",
        key="data_inicio",
        min_value=date(2020, 1, 1),
        max_value=date.today(),
    )
    data_fim = st.date_input(
        "Data de fim",
        key="data_fim",
        min_value=date(2020, 1, 2),
        max_value=date.today(),
    )

    st.markdown("---")
    st.markdown("**Operadoras:**")
    opcoes = list(ACOES.keys())
    selecionadas = [acao for acao in opcoes if st.checkbox(acao, value=True, key=f"chk_{acao}")]

    st.markdown("---")
    st.markdown("**Tickers:**")
    for nome, ticker in ACOES.items():
        st.caption(f"{nome} → `{ticker}`")

# --- Validações ---
if not selecionadas:
    st.warning("Selecione ao menos uma operadora na sidebar.")
    st.stop()

if data_inicio >= data_fim:
    st.error("A data de início deve ser anterior à data de fim.")
    st.stop()

# --- Download de dados ---
with st.spinner("Buscando cotações..."):
    df = baixar_dados(selecionadas, str(data_inicio), str(data_fim))

if df.empty:
    st.error("Não foi possível obter dados para o período selecionado.")
    st.stop()

metricas = calcular_metricas(df)

# --- Status bar ---
pregoes = len(df)
st.markdown(
    f'<div class="status-bar">✓ {pregoes} pregões carregados '
    f'• {data_inicio.strftime("%d/%m/%Y")} a {data_fim.strftime("%d/%m/%Y")}'
    f' • {len(selecionadas)} operadora{"s" if len(selecionadas) > 1 else ""}</div>',
    unsafe_allow_html=True,
)

# --- KPI Cards com ranking ---
ranking = metricas["Variação Total (%)"].rank(ascending=False).astype(int)
medalhas = {1: "🥇", 2: "🥈", 3: "🥉"}

cols = st.columns(len(selecionadas))
for i, nome in enumerate(selecionadas):
    preco_atual = df[nome].iloc[-1]
    variacao = metricas.loc[nome, "Variação Total (%)"]
    delta_class = "kpi-delta-pos" if variacao >= 0 else "kpi-delta-neg"
    sinal = "▲" if variacao >= 0 else "▼"
    pos = ranking.loc[nome]
    medalha = medalhas.get(pos, "")
    with cols[i]:
        st.markdown(f"""
        <div class="kpi-card" data-company="{nome}">
            <div class="kpi-rank">{medalha}</div>
            <div class="kpi-label">{nome} ({ACOES[nome]})</div>
            <div class="kpi-value">R$ {preco_atual:.2f}</div>
            <div class="{delta_class}">{sinal} {abs(variacao):.2f}% no período</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("")

# --- Tabs de navegação ---
tab_precos, tab_tecnica, tab_retorno, tab_relatorio = st.tabs([
    "📊 Preços",
    "📈 Análise Técnica",
    "💹 Retorno Acumulado",
    "📋 Relatório",
])

# ── Tab 1: Preços ──────────────────────────────────────────────────────────────
with tab_precos:
    st.markdown('<p class="section-title">Preços Históricos</p>', unsafe_allow_html=True)
    st.plotly_chart(grafico_precos(df), use_container_width=True, key="chart_precos")

# ── Tab 2: Análise Técnica ─────────────────────────────────────────────────────
with tab_tecnica:
    st.markdown('<p class="section-title">Análise Técnica</p>', unsafe_allow_html=True)

    col_toggle, col_slider = st.columns([1, 2])
    with col_toggle:
        usar_ma = st.toggle("Exibir Média Móvel", value=False, key="toggle_ma")
    with col_slider:
        periodo_ma = None
        if usar_ma:
            periodo_ma = st.slider(
                "Período da Média Móvel (dias)",
                min_value=5,
                max_value=60,
                value=20,
                step=1,
                key="slider_ma",
            )

    st.plotly_chart(
        grafico_precos(df, periodo_ma=periodo_ma),
        use_container_width=True,
        key="chart_tecnica",
    )

    st.markdown('<p class="section-title">Volatilidade</p>', unsafe_allow_html=True)
    st.plotly_chart(grafico_volatilidade(metricas), use_container_width=True, key="chart_vol")

# ── Tab 3: Retorno Acumulado ───────────────────────────────────────────────────
with tab_retorno:
    st.markdown('<p class="section-title">Retorno Acumulado</p>', unsafe_allow_html=True)
    df_retorno = calcular_retorno_acumulado(df)
    st.plotly_chart(grafico_retorno_acumulado(df_retorno), use_container_width=True, key="chart_retorno")

# ── Tab 4: Relatório ───────────────────────────────────────────────────────────
with tab_relatorio:
    st.markdown('<p class="section-title">Comparativo Final</p>', unsafe_allow_html=True)

    def destacar(val):
        if isinstance(val, (int, float)):
            if val == metricas["Variação Total (%)"].max():
                return "background-color: #d1fae5; color: #1a7340; font-weight: bold"
            if val == metricas["Variação Total (%)"].min():
                return "background-color: #fee2e2; color: #c0392b; font-weight: bold"
        return ""

    st.dataframe(
        metricas.style.map(destacar, subset=["Variação Total (%)"]),
        use_container_width=True,
    )
    st.caption("Verde = melhor desempenho no período | Vermelho = pior desempenho no período")

    csv_data = metricas.to_csv(index=True).encode("utf-8")
    st.download_button(
        label="⬇️ Exportar métricas (CSV)",
        data=csv_data,
        file_name=f"metricas_telecom_{data_inicio}_{data_fim}.csv",
        mime="text/csv",
        key="btn_export_csv",
    )

    # Análise automática
    st.markdown('<p class="section-title">Relatório de Análise</p>', unsafe_allow_html=True)

    melhor = metricas["Variação Total (%)"].idxmax()
    pior = metricas["Variação Total (%)"].idxmin()
    mais_volatil = metricas["Volatilidade (Desvio Padrão)"].idxmax()
    menos_volatil = metricas["Volatilidade (Desvio Padrão)"].idxmin()
    var_melhor = metricas.loc[melhor, "Variação Total (%)"]
    var_pior = metricas.loc[pior, "Variação Total (%)"]
    sinal_melhor = "alta" if var_melhor >= 0 else "queda"

    st.markdown(f"""
<div style="background:#ffffff; border:1px solid #dee2e6; border-radius:12px; padding:24px 28px;
            line-height:1.9; color:#343a40; font-size:0.95rem; box-shadow:0 1px 4px rgba(0,0,0,0.06);">

<b style="color:#1a1a2e; font-size:1rem;">Resumo do Período ({data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')})</b><br><br>

No período analisado, <b style="color:#1a1a2e;">{melhor}</b> foi a operadora com melhor desempenho,
registrando uma {sinal_melhor} de <b style="color:#1a7340;">{abs(var_melhor):.2f}%</b>.
Já <b style="color:#1a1a2e;">{pior}</b> apresentou o pior resultado, com
{'alta' if var_pior >= 0 else 'queda'} de <b style="color:#c0392b;">{abs(var_pior):.2f}%</b>.<br><br>

Em termos de risco, <b style="color:#1a1a2e;">{mais_volatil}</b> foi a ação mais volátil do período
(maior variação diária de preço), enquanto <b style="color:#1a1a2e;">{menos_volatil}</b> se mostrou
a opção mais estável.

</div>
""", unsafe_allow_html=True)

    # Avisos em expanders
    if "Oi" in selecionadas:
        with st.expander("⚠️ Situação da Oi (OIBR3) — clique para expandir"):
            st.markdown("""
<div style="background:#fffbeb; border:1px solid #d97706; border-radius:12px; padding:24px 28px;
            line-height:1.9; color:#343a40; font-size:0.95rem;">

<b style="color:#92400e; font-size:1rem;">Oi S.A. — Recuperação Judicial</b><br><br>

A Oi S.A. entrou em recuperação judicial em 2022 — um dos maiores processos do tipo na história do Brasil.
A empresa enfrentou uma combinação de dívida bilionária, perda de clientes para concorrentes e queda de receita,
o que a levou a vender sua operação de telefonia móvel para Claro, TIM e Vivo em 2022.<br><br>

Atualmente, a Oi opera apenas com serviços de infraestrutura (fibra ótica B2B) e ainda está em processo de
reestruturação sob supervisão judicial. A ação OIBR3 continua negociada na B3, mas representa uma empresa
em situação financeira crítica.<br><br>

<b style="color:#1a1a2e;">Vale investir?</b><br>
A OIBR3 é considerada uma <b>ação especulativa de altíssimo risco</b>. Somente investidores com perfil
<b>arrojado</b>, que compreendem os riscos e estão dispostos a perder todo o capital alocado,
devem considerar este ativo.

</div>
""", unsafe_allow_html=True)

    with st.expander("📄 Aviso Legal"):
        st.markdown("""
<div style="background:#ffffff; border:1px solid #dee2e6; border-radius:12px; padding:18px 24px;
            color:#6c757d; font-size:0.88rem; line-height:1.8;">

⚠️ <b style="color:#343a40;">Disclaimer:</b> As informações apresentadas neste painel têm caráter
<b>exclusivamente educacional e informativo</b>.
Nenhum conteúdo aqui exibido constitui recomendação de investimento, consultoria financeira ou oferta
de compra/venda de valores mobiliários.
Desempenho passado não é garantia de resultados futuros. Antes de investir, consulte um profissional
certificado pela CVM. Dados obtidos via Yahoo Finance e sujeitos a atrasos e imprecisões.

</div>
""", unsafe_allow_html=True)
