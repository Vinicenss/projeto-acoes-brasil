import yfinance as yf
import pandas as pd

ACOES = {
    "Vivo": "VIVT3.SA",
    "TIM": "TIMS3.SA",
    "Oi": "OIBR3.SA",
}


def baixar_dados(tickers: list[str], inicio: str, fim: str) -> pd.DataFrame:
    """Baixa preços de fechamento ajustados para os tickers no período."""
    frames = {}
    for nome in tickers:
        simbolo = ACOES[nome]
        hist = yf.Ticker(simbolo).history(start=inicio, end=fim)
        if not hist.empty:
            hist.index = hist.index.tz_localize(None)
            frames[nome] = hist["Close"]

    if not frames:
        return pd.DataFrame()

    df = pd.DataFrame(frames)
    df.dropna(how="all", inplace=True)
    return df


def calcular_retorno_acumulado(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna o retorno acumulado percentual (base 100)."""
    return (df / df.iloc[0]) * 100


def calcular_metricas(df: pd.DataFrame) -> pd.DataFrame:
    """Retorna tabela de métricas: mín, máx, média, variação total e volatilidade."""
    metricas = pd.DataFrame({
        "Preço Mínimo (R$)": df.min().round(2),
        "Preço Máximo (R$)": df.max().round(2),
        "Preço Médio (R$)": df.mean().round(2),
        "Variação Total (%)": ((df.iloc[-1] / df.iloc[0] - 1) * 100).round(2),
        "Volatilidade (Desvio Padrão)": df.std().round(2),
    })
    return metricas
