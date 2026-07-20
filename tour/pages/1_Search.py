"""
🐶 PawTrip Korea
관광지 검색 페이지
"""

import streamlit as st
import pandas as pd

from streamlit_folium import st_folium

from utils.api import (
    search_places,
    pet_filter
)

from utils.map import create_map



# ==========================
# 페이지 설정
# ==========================

st.set_page_config(
    page_title="여행지 검색 🗺️",
    page_icon="🐶",
    layout="wide"
)



# ==========================
# CSS
# ==========================

st.markdown(
    """
<style>

.place-card {

background:white;

padding:20px;

border-radius:20px;

box-shadow:
0 3px 12px rgba(0,0,0,0.1);

margin-bottom:20px;

}


.pet {

background:#EFFFF7;

padding:5px 10px;

border-radius:15px;

color:#26966b;

}

</style>

""",
unsafe_allow_html=True
)



st.title(
    "🐶 반려견 여행지 검색"
)


st.caption(
    "한국관광공사 TourAPI 기반"
)



# ==========================
# 검색 옵션
# ==========================


col1,col2,col3=st.columns(3)



with col1:

    region=st.selectbox(

        "📍 지역",

        [

            "전국",

            "서울",

            "경기",

            "강원",

            "부산",

            "제주"

        ]

    )


with col2:

    keyword=st.text_input(

        "🔎 키워드",

        placeholder="예: 캠핑, 카페"

    )



with col3:

    category=st.multiselect(

        "🏷️ 유형",

        [

            "관광지",

            "음식점",

            "숙박",

            "문화시설",

            "쇼핑"

        ],

        default=[

            "관광지"

        ]

    )



pet_only=st.checkbox(

    "🐾 반려견 동반 가능 장소만 보기"

)



search_btn=st.button(

    "🔍 검색하기"

)



# ==========================
# 검색 실행
# ==========================


if search_btn:


    with st.spinner(
        "여행지를 찾는 중..."
    ):


        results=search_places(

            region,

            keyword

        )



        if pet_only:

            results=pet_filter(
                results
            )



        st.session_state.results=results



        if keyword:

            if "history" not in st.session_state:

                st.session_state.history=[]


            st.session_state.history.append(

                keyword

            )



# ==========================
# 결과 출력
# ==========================


results=st.session_state.get(

    "results",

    []

)



if not results:


    st.info(

        "검색 결과가 없습니다 🐾"

    )


else:


    st.success(

        f"{len(results)}개의 여행지를 찾았습니다"

    )


    # 지도


    st.subheader(
        "🗺️ 지도"
    )


    fmap=create_map(
        results
    )


    st_folium(

        fmap,

        width=1000,

        height=500

    )



    st.divider()



    # 카드


    for place in results:



        with st.container():


            st.markdown(

                "<div class='place-card'>",

                unsafe_allow_html=True

            )



            col1,col2=st.columns(

                [1,2]

            )


            with col1:


                img=place.get(

                    "firstimage",

                    ""

                )


                if img:

                    st.image(
                        img
                    )

                else:

                    st.write(
                        "🐶 이미지 없음"
                    )



            with col2:


                title=place.get(

                    "title",

                    "이름 없음"

                )


                st.subheader(

                    title

                )


                st.write(

                    place.get(

                        "addr1",

                        ""

                    )

                )


                st.write(

                    "☎️",

                    place.get(

                        "tel",

                        "정보 없음"

                    )

                )



                st.markdown(

                    "<span class='pet'>🐾 반려견 여행 추천</span>",

                    unsafe_allow_html=True

                )



                if st.button(

                    "❤️ 즐겨찾기",

                    key=str(

                        place.get(
                            "contentid"
                        )

                    )

                ):


                    if place not in st.session_state.favorites:


                        st.session_state.favorites.append(

                            place

                        )


                    st.success(
                        "저장 완료!"
                    )



            st.markdown(

                "</div>",

                unsafe_allow_html=True

            )



# ==========================
# CSV 다운로드
# ==========================


if results:


    df=pd.DataFrame(
        results
    )


    csv=df.to_csv(

        index=False,

        encoding="utf-8-sig"

    )


    st.download_button(

        "📥 검색 결과 CSV 저장",

        csv,

        "pawtrip_places.csv",

        "text/csv"

    )
