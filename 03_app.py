import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장 안내",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 안내")

uploaded_file = st.file_uploader(
    "서울 열린데이터광장 CSV 파일을 업로드하세요.",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    try:
        # ------------------------
        # 파일 읽기
        # ------------------------
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, encoding="cp949")
        else:
            df = pd.read_excel(uploaded_file)

        st.success("파일을 성공적으로 불러왔습니다.")

        # ------------------------
        # 컬럼명 자동 인식
        # ------------------------
        cols = df.columns

        def find_col(keyword):
            for c in cols:
                if keyword in c:
                    return c
            return None

        name_col = find_col("주차장명")
        addr_col = find_col("주소")
        lat_col = find_col("위도")
        lon_col = find_col("경도")
        fee_col = find_col("기본 주차 요금")
        base_time_col = find_col("기본 주차 시간")
        extra_fee_col = find_col("추가 단위 요금")
        extra_time_col = find_col("추가 단위 시간")
        day_max_col = find_col("일 최대")
        capacity_col = find_col("총 주차면")

        # ------------------------
        # 필수 컬럼 확인
        # ------------------------
        if (
            name_col is None
            or lat_col is None
            or lon_col is None
        ):
            st.error("주차장명, 위도, 경도 컬럼을 찾을 수 없습니다.")
            st.stop()

        # ------------------------
        # 숫자형 변환
        # ------------------------
        df[lat_col] = pd.to_numeric(df[lat_col], errors="coerce")
        df[lon_col] = pd.to_numeric(df[lon_col], errors="coerce")

        df = df.dropna(subset=[lat_col, lon_col])

        # ------------------------
        # 검색
        # ------------------------
        keyword = st.sidebar.text_input("🔍 주차장명 검색")

        if keyword:
            df = df[
                df[name_col]
                .astype(str)
                .str.contains(keyword, case=False)
            ]

        if len(df) == 0:
            st.warning("검색 결과가 없습니다.")
            st.stop()

        # ------------------------
        # 지도 생성
        # ------------------------
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

            popup = f"<b>{row[name_col]}</b><br>"

            if addr_col:
                popup += f"📍 {row[addr_col]}<br>"

            if capacity_col:
                popup += f"🚗 주차면수 : {row[capacity_col]}면<br>"

            if fee_col:
                popup += f"💰 기본요금 : {row[fee_col]}원"

            if base_time_col:
                popup += f" / {row[base_time_col]}분"

            popup += "<br>"

            if extra_fee_col:
                popup += f"➕ 추가요금 : {row[extra_fee_col]}원"

            if extra_time_col:
                popup += f" / {row[extra_time_col]}분"

            popup += "<br>"

            if day_max_col:
                popup += f"🏷️ 일 최대요금 : {row[day_max_col]}원"

            folium.Marker(
                location=[
                    row[lat_col],
                    row[lon_col]
                ],
                tooltip=row[name_col],
                popup=folium.Popup(
                    popup,
                    max_width=350
                ),
                icon=folium.Icon(
                    color="blue",
                    icon="info-sign"
                )
            ).add_to(m)

        st.subheader("🗺️ 공영주차장 지도")

        st_folium(
            m,
            width=None,
            height=700
        )

        # ------------------------
        # 목록
        # ------------------------
        st.subheader("📋 공영주차장 목록")

        show_cols = []

        for c in [
            name_col,
            addr_col,
            capacity_col,
            fee_col,
            base_time_col,
            extra_fee_col,
            extra_time_col,
            day_max_col
        ]:
            if c is not None:
                show_cols.append(c)

        st.dataframe(
            df[show_cols],
            use_container_width=True
        )

    except Exception as e:
        st.error("파일을 읽는 중 오류가 발생했습니다.")
        st.exception(e)
