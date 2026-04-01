import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

CORES = {
    "Vivo": "#6d28d9",   # violeta — contraste 7.1:1 sobre fundo branco
    "TIM": "#1d4ed8",    # azul — contraste 8.3:1
    "Oi": "#b45309",     # âmbar escuro — contraste 6.9:1
}

LAYOUT_BASE = dict(
    font=dict(family="Inter, sans-serif", size=13),
    plot_bgcolor="#ffffff",
    paper_bgcolor="#f8f9fa",
    font_color="#212529",
    legend=dict(
        bgcolor="rgba(255,255,255,0.9)",
        bordercolor="#dee2e6",
        borderwidth=1,
    ),
    xaxis=dict(gridcolor="rgba(0,0,0,0.07)", showgrid=True, linecolor="#dee2e6"),
    yaxis=dict(gridcolor="rgba(0,0,0,0.07)", showgrid=True, linecolor="#dee2e6"),
    margin=dict(t=50, b=40, l=50, r=20),
)


def grafico_precos(df: pd.DataFrame, periodo_ma: int = None) -> go.Figure:
    fig = px.line(
        df,
        title="Preço de Fechamento (R$)",
        labels={"value": "Preço (R$)", "index": "Data", "variable": "Operadora"},
        color_discrete_map=CORES,
    )
    fig.update_traces(line=dict(width=2.5))

    if periodo_ma:
        for nome in df.columns:
            ma = df[nome].rolling(window=periodo_ma).mean()
            cor = CORES.get(nome, "#999999")
            fig.add_trace(go.Scatter(
                x=df.index,
                y=ma,
                name=f"{nome} MM{periodo_ma}",
                line=dict(dash="dash", width=1.5, color=cor),
                opacity=0.55,
                showlegend=True,
            ))

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
        y=100, line_dash="dot", line_color="rgba(0,0,0,0.25)",
        annotation_text="Base inicial", annotation_font_color="rgba(0,0,0,0.45)"
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
