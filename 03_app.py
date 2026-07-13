import streamlit as st
import pandas as pd
import folium
import chardet
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장 지도",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 정보")

st.write("CSV 또는 Excel 파일을 업로드하세요.")

uploaded_file = st.file_uploader(
    "파일 선택",
    type=["csv", "xlsx"]
)

# -----------------------------
# 파일 읽기 함수
# -----------------------------
def load_data(uploaded_file):

    if uploaded_file.name.endswith(".csv"):

        raw = uploaded_file.read()

        result = chardet.detect(raw)

        encoding = result["encoding"]

        uploaded_file.seek(0)

        try:
            df = pd.read_csv(uploaded_file, encoding=encoding)

        except:
            uploaded_file.seek(0)

            try:
                df = pd.read_csv(uploaded_file, encoding="cp949")

            except:
                uploaded_file.seek(0)

                try:
                    df = pd.read_csv(uploaded_file, encoding="euc-kr")

                except:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, encoding="utf-8")

    else:
        df = pd.read_excel(uploaded_file)

    return df


# -----------------------------
# 메인
# -----------------------------
if uploaded_file is not None:

    try:

        df = load_data(uploaded_file)

        st.success("파일 업로드 성공!")

        st.subheader("데이터 미리보기")

        st.dataframe(df)

        st.markdown("---")

        cols = list(df.columns)

        st.sidebar.header("컬럼 선택")

        lat_col = st.sidebar.selectbox("위도", cols)

        lon_col = st.sidebar.selectbox("경도", cols)

        name_col = st.sidebar.selectbox("주차장명", cols)

        address_col = st.sidebar.selectbox("주소", cols)

        fee_col = st.sidebar.selectbox("요금", cols)

        time_col = st.sidebar.selectbox(
            "운영시간(없으면 아무 컬럼)",
            cols
        )

        capacity_col = st.sidebar.selectbox(
            "주차가능대수(없으면 아무 컬럼)",
            cols
        )

        keyword = st.sidebar.text_input("주차장 검색")

        if keyword:
            df = df[
                df[name_col]
                .astype(str)
                .str.contains(keyword, case=False)
            ]

        if len(df) == 0:
            st.warning("검색 결과가 없습니다.")
            st.stop()

        center = [
            df[lat_col].astype(float).mean(),
            df[lon_col].astype(float).mean()
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
            💰 {row[fee_col]}<br>
            🕒 {row[time_col]}<br>
            🚗 {row[capacity_col]}
            """

            folium.Marker(
                location=[
                    float(row[lat_col]),
                    float(row[lon_col])
                ],
                tooltip=str(row[name_col]),
                popup=folium.Popup(
                    popup,
                    max_width=300
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="info-sign"
                )
            ).add_to(m)

        st.subheader("🗺️ 공영주차장 지도")

        st_folium(
            m,
            width=1200,
            height=700
        )

        st.subheader("📋 주차장 목록")

        st.dataframe(
            df[
                [
                    name_col,
                    address_col,
                    fee_col,
                    time_col,
                    capacity_col
                ]
            ]
        )

    except Exception as e:

        st.error("파일을 읽는 중 오류가 발생했습니다.")

        st.exception(e)
