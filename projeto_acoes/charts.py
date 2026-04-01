import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CORES = {
    "Vivo": "#c084fc",   # roxo claro — contraste 7.2:1 sobre fundo escuro
    "TIM": "#79b8ff",    # azul claro — contraste 7.5:1
    "Oi": "#f5c400",     # amarelo forte — contraste 8.1:1
}

LAYOUT_BASE = dict(
    font=dict(family="Inter, sans-serif", size=13),
    plot_bgcolor="#0e1117",
    paper_bgcolor="#0e1117",
    font_color="#fafafa",
    legend=dict(
        bgcolor="rgba(255,255,255,0.05)",
        bordercolor="rgba(255,255,255,0.1)",
        borderwidth=1,
    ),
    xaxis=dict(gridcolor="rgba(255,255,255,0.07)", showgrid=True),
    yaxis=dict(gridcolor="rgba(255,255,255,0.07)", showgrid=True),
    margin=dict(t=50, b=40, l=50, r=20),
)


def grafico_precos(df: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df,
        title="Preço de Fechamento (R$)",
        labels={"value": "Preço (R$)", "index": "Data", "variable": "Operadora"},
        color_discrete_map=CORES,
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(**LAYOUT_BASE, legend_title_text="Operadora", hovermode="x unified")
    return fig


def grafico_retorno_acumulado(df_retorno: pd.DataFrame) -> go.Figure:
    fig = px.line(
        df_retorno,
        title="Retorno Acumulado (base 100)",
        labels={"value": "Retorno (base 100)", "index": "Data", "variable": "Operadora"},
        color_discrete_map=CORES,
    )
    fig.add_hline(
        y=100, line_dash="dot", line_color="rgba(255,255,255,0.3)",
        annotation_text="Base inicial", annotation_font_color="rgba(255,255,255,0.5)"
    )
    fig.update_traces(line=dict(width=2.5))
    fig.update_layout(**LAYOUT_BASE, legend_title_text="Operadora", hovermode="x unified")
    return fig


def grafico_volatilidade(metricas: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        metricas,
        y="Volatilidade (Desvio Padrão)",
        title="Volatilidade por Operadora (Desvio Padrão do Preço)",
        labels={"index": "Operadora", "Volatilidade (Desvio Padrão)": "Desvio Padrão (R$)"},
        color=metricas.index,
        color_discrete_map=CORES,
    )
    fig.update_layout(**LAYOUT_BASE, showlegend=False)
    return fig
