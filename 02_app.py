import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="🌍 Global Top10 Stocks",
    page_icon="📈",
    layout="wide"
)

st.title("🌍 Global Market Cap Top10 Dashboard")
st.write("최근 1년간 글로벌 시가총액 Top10 기업의 주가 변화")

# -----------------------------
# 종목 목록
# -----------------------------
stocks = {
    "Microsoft": "MSFT",
    "NVIDIA": "NVDA",
    "Apple": "AAPL",
    "Amazon": "AMZN",
    "Alphabet": "GOOGL",
    "Meta": "META",
    "Broadcom": "AVGO",
    "TSMC": "TSM",
    "Tesla": "TSLA",
    "Saudi Aramco": "2222.SR",
}

# -----------------------------
# 사이드바
# -----------------------------
st.sidebar.header("설정")

selected = st.sidebar.multiselect(
    "종목 선택",
    list(stocks.keys()),
    default=["Microsoft", "NVIDIA", "Apple", "Amazon", "Meta"]
)

normalize = st.sidebar.checkbox(
    "첫날 가격 = 100으로 정규화",
    value=True
)

# -----------------------------
# 데이터 다운로드 함수
# -----------------------------
@st.cache_data(show_spinner=False)
def load_stock(name, ticker):

    df = yf.download(
        ticker,
        period="1y",
        auto_adjust=True,
        progress=False
    )

    if df.empty:
        return None

    # 최신 yfinance 대응
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if "Close" not in df.columns:
        return None

    df = df.reset_index()

    df = df[["Date", "Close"]]

    df["Company"] = name

    if normalize:
        first = df["Close"].iloc[0]
        df["Close"] = df["Close"] / first * 100

    return df


# -----------------------------
# 데이터 수집
# -----------------------------
frames = []

progress = st.progress(0)

for i, company in enumerate(selected):

    ticker = stocks[company]

    data = load_stock(company, ticker)

    if data is not None:
        frames.append(data)

    progress.progress((i + 1) / max(len(selected), 1))

progress.empty()

# -----------------------------
# 그래프
# -----------------------------
if len(frames) > 0:

    final = pd.concat(frames, ignore_index=True)

    final["Date"] = pd.to_datetime(final["Date"])
    final["Close"] = pd.to_numeric(final["Close"])

    fig = px.line(
        final,
        x="Date",
        y="Close",
        color="Company",
        title="최근 1년 주가 변화",
        template="plotly_dark"
    )

    fig.update_layout(
        height=700,
        hovermode="x unified",
        legend_title="Company",
        xaxis_title="Date",
        yaxis_title="Price" if not normalize else "Normalized (Start=100)"
    )

    st.plotly_chart(fig, use_container_width=True)

else:

    st.warning("데이터를 불러오지 못했습니다.")

# -----------------------------
# 마지막 가격
# -----------------------------
st.divider()

st.subheader("현재 선택된 종목")

cols = st.columns(5)

for i, company in enumerate(selected):

    ticker = stocks[company]

    df = yf.download(
        ticker,
        period="5d",
        auto_adjust=True,
        progress=False
    )

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if df.empty:
        continue

    price = float(df["Close"].iloc[-1])
    prev = float(df["Close"].iloc[-2])

    change = (price - prev) / prev * 100

    cols[i % 5].metric(
        company,
        f"${price:,.2f}",
        f"{change:.2f}%"
    )
