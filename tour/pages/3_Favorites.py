"""
🐶 PawTrip Korea
즐겨찾기 페이지
"""


import streamlit as st
import json
import random


from utils.export import export_json



# ==========================
# Page Config
# ==========================


st.set_page_config(

    page_title="즐겨찾기 ❤️",

    page_icon="🐾",

    layout="wide"

)



# ==========================
# 초기 데이터
# ==========================


if "favorites" not in st.session_state:

    st.session_state.favorites=[]



if "history" not in st.session_state:

    st.session_state.history=[]



# ==========================
# Header
# ==========================


st.title(

    "❤️ 나의 PawTrip"

)


st.caption(

    "저장한 여행지를 관리하세요"

)



st.divider()



favorites = st.session_state.favorites



# ==========================
# 저장 목록
# ==========================


st.subheader(

    "🐾 즐겨찾기 목록"

)



if not favorites:


    st.info(

        """
        아직 저장한 여행지가 없습니다.

        여행지를 검색하고 ❤️ 버튼을 눌러 저장해보세요.

        """

    )


else:


    st.success(

        f"{len(favorites)}개의 장소 저장됨"

    )


    for idx,place in enumerate(

        favorites

    ):



        with st.container():



            col1,col2=st.columns(

                [1,3]

            )



            with col1:


                image=place.get(

                    "firstimage",

                    ""

                )


                if image:

                    st.image(

                        image

                    )


                else:

                    st.write(

                        "🐶 이미지 없음"

                    )



            with col2:


                st.subheader(

                    place.get(

                        "title",

                        "이름 없음"

                    )

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



                if st.button(

                    "❌ 삭제",

                    key=f"delete_{idx}"

                ):


                    favorites.pop(

                        idx

                    )


                    st.session_state.favorites=favorites


                    st.rerun()



            st.divider()




# ==========================
# Export
# ==========================


if favorites:


    json_data=export_json(

        favorites

    )


    st.download_button(

        "📤 즐겨찾기 JSON 저장",

        json_data,

        "pawtrip_favorites.json",

        "application/json"

    )



    if st.button(

        "🗑️ 전체 삭제"

    ):


        st.session_state.favorites=[]


        st.rerun()



# ==========================
# 검색 기록
# ==========================


st.divider()



st.subheader(

    "🔎 최근 검색어"

)



history=st.session_state.history



if history:


    for keyword in reversed(

        history[-10:]

    ):


        st.write(

            f"🔍 {keyword}"

        )


else:


    st.caption(

        "최근 검색 기록이 없습니다."

    )



# ==========================
# 추천 카드
# ==========================


st.divider()



st.subheader(

    "🐶 오늘의 추천 코스"

)



recommendations=[


    {

    "title":"🌲 제주 반려견 자연 여행",

    "desc":"오름 산책 + 애견 카페 코스"

    },


    {

    "title":"🏕️ 강원 캠핑 여행",

    "desc":"숲속 캠핑과 산책 코스"

    },


    {

    "title":"☕ 양평 카페 투어",

    "desc":"반려견 동반 카페 여행"

    },


    {

    "title":"🌊 강릉 바다 산책",

    "desc":"해변 산책 중심 힐링 코스"

    }

]


choice=random.choice(

    recommendations

)



st.markdown(

    f"""

<div style="
background:#EFFFF7;
padding:20px;
border-radius:20px;
">

<h3>{choice['title']}</h3>

<p>{choice['desc']}</p>

</div>

""",

unsafe_allow_html=True

)
