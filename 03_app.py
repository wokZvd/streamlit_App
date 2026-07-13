import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장 지도",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 지도")

st.write("CSV 또는 Excel 파일을 업로드하세요.")

uploaded_file = st.file_uploader(
    "파일 업로드",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

    else:
        df = pd.read_excel(uploaded_file)

    st.success("파일 업로드 완료!")

    st.subheader("데이터 미리보기")
    st.dataframe(df)

    st.markdown("---")

    # 컬럼 선택
    lat_col = st.selectbox("위도 컬럼", df.columns)
    lon_col = st.selectbox("경도 컬럼", df.columns)

    name_col = st.selectbox("주차장명", df.columns)

    fee_col = st.selectbox("요금 컬럼", df.columns)

    address_col = st.selectbox("주소 컬럼", df.columns)

    if "운영시간" in df.columns:
        time_col = "운영시간"
    else:
        time_col = None

    if "주차가능대수" in df.columns:
        capacity_col = "주차가능대수"
    else:
        capacity_col = None

    # 요금 필터
    st.sidebar.header("검색")

    keyword = st.sidebar.text_input("주차장명 검색")

    if keyword:
        df = df[df[name_col].astype(str).str.contains(keyword)]

    # 지도 중심
    center = [
        df[lat_col].mean(),
        df[lon_col].mean()
    ]

    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles="CartoDB positron"
    )

    for _, row in df.iterrows():

        popup = f"""
        <b>{row[name_col]}</b><br>
        📍 {row[address_col]}<br>
        💰 {row[fee_col]}
        """

        if time_col:
            popup += f"<br>🕒 {row[time_col]}"

        if capacity_col:
            popup += f"<br>🚗 {row[capacity_col]}"

        folium.Marker(
            location=[row[lat_col], row[lon_col]],
            popup=folium.Popup(popup, max_width=300),
            tooltip=row[name_col],
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)

    st.subheader("지도")

    st_folium(
        m,
        width=1200,
        height=700
    )

    st.subheader("주차장 목록")

    show_cols = [
        name_col,
        address_col,
        fee_col
    ]

    if time_col:
        show_cols.append(time_col)

    if capacity_col:
        show_cols.append(capacity_col)

    st.dataframe(df[show_cols])
