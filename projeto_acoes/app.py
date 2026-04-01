import streamlit as st
from datetime import date
from data import baixar_dados, calcular_retorno_acumulado, calcular_metricas, ACOES
from charts import grafico_precos, grafico_retorno_acumulado, grafico_volatilidade

st.set_page_config(
    page_title="Telecom Brasil — Análise de Ações",
    page_icon="📡",
    layout="wide",
)

st.markdown("""
<style>
    /* Fundo geral */
    .stApp { background-color: #f8f9fa; }

    /* Título principal */
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

    /* Cards de KPI */
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

    /* Separador de seção */
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a1a2e;
        border-left: 4px solid #4361ee;
        padding-left: 12px;
        margin-top: 36px;
        margin-bottom: 14px;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background-color: #f1f3f5;
        border-right: 1px solid #dee2e6;
    }
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #212529;
    }
</style>
""", unsafe_allow_html=True)

# --- Cabeçalho ---
st.markdown('<p class="main-title">📡 Telecom Brasil — Análise de Ações</p>', unsafe_allow_html=True)
st.markdown('<p class="main-subtitle">Comparativo de desempenho das principais operadoras listadas na B3 • Dados via Yahoo Finance</p>', unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.markdown("### Filtros")

    data_inicio = st.date_input("Data de início", value=date(2025, 1, 2), min_value=date(2020, 1, 1))
    data_fim = st.date_input("Data de fim", value=date(2025, 12, 31), max_value=date.today())

    st.markdown("---")
    st.markdown("**Operadoras:**")
    opcoes = list(ACOES.keys())
    selecionadas = [acao for acao in opcoes if st.checkbox(acao, value=True)]

    st.markdown("---")
    st.markdown("**Tickers:**")
    for nome, ticker in ACOES.items():
        st.caption(f"{nome} → `{ticker}`")

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

# --- KPI Cards ---
cols = st.columns(len(selecionadas))
for i, nome in enumerate(selecionadas):
    preco_atual = df[nome].iloc[-1]
    variacao = metricas.loc[nome, "Variação Total (%)"]
    delta_class = "kpi-delta-pos" if variacao >= 0 else "kpi-delta-neg"
    sinal = "▲" if variacao >= 0 else "▼"
    with cols[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{nome} ({ACOES[nome]})</div>
            <div class="kpi-value">R$ {preco_atual:.2f}</div>
            <div class="{delta_class}">{sinal} {abs(variacao):.2f}% no período</div>
        </div>
        """, unsafe_allow_html=True)

# --- Seção 1: Preços Históricos ---
st.markdown('<p class="section-title">Preços Históricos</p>', unsafe_allow_html=True)
st.plotly_chart(grafico_precos(df), use_container_width=True)

# --- Seção 2: Retorno Acumulado ---
st.markdown('<p class="section-title">Retorno Acumulado</p>', unsafe_allow_html=True)
df_retorno = calcular_retorno_acumulado(df)
st.plotly_chart(grafico_retorno_acumulado(df_retorno), use_container_width=True)

# --- Seção 3: Volatilidade ---
st.markdown('<p class="section-title">Volatilidade</p>', unsafe_allow_html=True)
st.plotly_chart(grafico_volatilidade(metricas), use_container_width=True)

# --- Seção 4: Comparativo Final ---
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

# --- Seção 5: Relatório e Análise ---
st.markdown('<p class="section-title">Relatório de Análise</p>', unsafe_allow_html=True)

melhor = metricas["Variação Total (%)"].idxmax()
pior = metricas["Variação Total (%)"].idxmin()
mais_volatil = metricas["Volatilidade (Desvio Padrão)"].idxmax()
menos_volatil = metricas["Volatilidade (Desvio Padrão)"].idxmin()

var_melhor = metricas.loc[melhor, "Variação Total (%)"]
var_pior = metricas.loc[pior, "Variação Total (%)"]

sinal_melhor = "alta" if var_melhor >= 0 else "queda"
sinal_pior = "alta" if var_pior >= 0 else "queda"

st.markdown(f"""
<div style="background:#ffffff; border:1px solid #dee2e6; border-radius:12px; padding:24px 28px; line-height:1.9; color:#343a40; font-size:0.95rem; box-shadow:0 1px 4px rgba(0,0,0,0.06);">

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

# --- Seção 6: Situação da Oi ---
if "Oi" in selecionadas:
    st.markdown('<p class="section-title">Situação da Oi (OIBR3)</p>', unsafe_allow_html=True)
    st.markdown("""
<div style="background:#fffbeb; border:1px solid #d97706; border-radius:12px; padding:24px 28px; line-height:1.9; color:#343a40; font-size:0.95rem;">

<b style="color:#92400e; font-size:1rem;">⚠️ Oi S.A. — Recuperação Judicial</b><br><br>

A Oi S.A. entrou em recuperação judicial em 2022 — um dos maiores processos do tipo na história do Brasil.
A empresa enfrentou uma combinação de dívida bilionária, perda de clientes para concorrentes e queda de receita,
o que a levou a vender sua operação de telefonia móvel para Claro, TIM e Vivo em 2022.<br><br>

Atualmente, a Oi opera apenas com serviços de infraestrutura (fibra ótica B2B) e ainda está em processo de
reestruturação sob supervisão judicial. A ação OIBR3 continua negociada na B3, mas representa uma empresa
em situação financeira crítica.<br><br>

<b style="color:#1a1a2e;">Vale investir?</b><br>
A OIBR3 é considerada uma <b>ação especulativa de altíssimo risco</b>. Investidores institucionais e
analistas, em sua maioria, não recomendam para carteiras conservadoras ou moderadas.
Pequenos movimentos positivos no processo judicial podem causar valorizações expressivas no curto prazo,
o que atrai investidores especulativos — mas o risco de perda total do capital é real e não deve ser ignorado.<br><br>

<span style="color:#6c757d; font-size:0.88rem;">
Recomendação: somente investidores com perfil <b style="color:#343a40;">arrojado</b>, que compreendem os riscos de empresas em recuperação judicial
e estejam dispostos a perder todo o capital alocado, devem considerar este ativo.
</span>

</div>
""", unsafe_allow_html=True)

# --- Disclaimer ---
st.markdown('<p class="section-title">Aviso Legal</p>', unsafe_allow_html=True)
st.markdown("""
<div style="background:#ffffff; border:1px solid #dee2e6; border-radius:12px; padding:18px 24px; color:#6c757d; font-size:0.88rem; line-height:1.8;">

⚠️ <b style="color:#343a40;">Disclaimer:</b> As informações apresentadas neste painel têm caráter <b>exclusivamente educacional e informativo</b>.
Nenhum conteúdo aqui exibido constitui recomendação de investimento, consultoria financeira ou oferta de compra/venda de valores mobiliários.
Desempenho passado não é garantia de resultados futuros. Antes de investir, consulte um profissional certificado pela CVM.
Dados obtidos via Yahoo Finance e sujeitos a atrasos e imprecisões.

</div>
""", unsafe_allow_html=True)
