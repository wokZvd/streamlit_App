import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Market Cap Top10 Dashboard",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Market Cap Top10 Stock Dashboard")
st.markdown("최근 1년간 글로벌 시가총액 Top10 기업의 주가 변화")

# 글로벌 시가총액 Top10 (2025 기준)
stocks = {
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Saudi Aramco": "2222.SR",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Tesla": "TSLA"
}

selected = st.multiselect(
    "종목 선택",
    list(stocks.keys()),
    default=list(stocks.keys())[:5]
)

normalize = st.checkbox(
    "Normalize (첫날=100)",
    value=True
)

@st.cache_data
def load_data(ticker):

    df = yf.download(
        ticker,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    return df


dfs = []

for company in selected:

    ticker = stocks[company]

    df = load_data(ticker)

    if df.empty:
        continue

    df = df[['Close']].copy()

    if normalize:
        df["Close"] = df["Close"] / df["Close"].iloc[0] * 100

    df["Company"] = company
    df["Date"] = df.index

    dfs.append(df)

if dfs:

    final = pd.concat(dfs)

    fig = px.line(
        final,
        x="Date",
        y="Close",
        color="Company",
        template="plotly_dark",
        title="Top Global Market Cap Stocks (1 Year)"
    )

    fig.update_layout(
        height=700,
        legend_title="Company",
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

else:
    st.warning("선택한 종목의 데이터를 불러올 수 없습니다.")

st.divider()

st.subheader("현재 종목")

cols = st.columns(5)

for i, company in enumerate(stocks):

    cols[i % 5].metric(
        company,
        stocks[company]
    )
