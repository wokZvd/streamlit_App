"""
PawTrip Korea
반려견과 함께 떠나는 국내 여행

Main Application
"""

from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
import os
import random


# ==============================
# 환경 설정
# ==============================

load_dotenv()


st.set_page_config(
    page_title="PawTrip Korea 🐶",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==============================
# CSS
# ==============================

def load_css():

    st.markdown(
        """
        <style>

        .main {
            background-color:#FFFFFF;
        }


        .hero {

            background:
            linear-gradient(
            135deg,
            #56C596,
            #B8F5D5
            );

            padding:40px;
            border-radius:25px;

            color:white;

            text-align:center;

        }


        .hero h1 {

            font-size:48px;

        }


        .card {

            background:white;

            padding:20px;

            border-radius:20px;

            box-shadow:
            0 4px 15px
            rgba(0,0,0,0.08);

            margin-bottom:20px;

        }


        .stButton button {

            width:100%;

            height:50px;

            border-radius:15px;

            background:#56C596;

            color:white;

            font-size:18px;

            font-weight:bold;

        }


        .badge {

            display:inline-block;

            padding:5px 12px;

            border-radius:20px;

            background:#EFFFF7;

            color:#2D8F68;

        }


        </style>
        """,
        unsafe_allow_html=True
    )


load_css()



# ==============================
# Session State
# ==============================


def init_state():

    defaults = {

        "favorites": [],

        "history": [],

        "planner": None,

        "dark_mode":False

    }


    for key,value in defaults.items():

        if key not in st.session_state:

            st.session_state[key]=value



init_state()



# ==============================
# Sidebar
# ==============================


with st.sidebar:

    st.title("🐶 PawTrip Korea")

    st.caption(
        "반려견과 함께 떠나는 국내 여행"
    )


    st.divider()


    dark = st.toggle(
        "🌙 다크모드",
        value=st.session_state.dark_mode
    )


    st.session_state.dark_mode = dark


    st.divider()


    st.info(
        """
        🦴 여행지 검색

        🌲 AI 일정 추천

        🏕️ 반려견 여행 관리
        """
    )



# ==============================
# Hero
# ==============================


st.markdown(
    """
    <div class="hero">

    <h1>🐶 PawTrip Korea</h1>

    <h3>
    반려견과 함께 떠나는 국내 여행
    </h3>

    <p>
    관광공사 데이터를 활용한
    반려견 친화 여행 플랫폼
    </p>

    </div>
    """,
    unsafe_allow_html=True
)



st.write("")



# ==============================
# Quick Search
# ==============================


st.subheader(
    "🐾 어디로 떠날까요?"
)


col1,col2,col3 = st.columns(3)


with col1:

    region = st.selectbox(

        "📍 지역",

        [

            "서울",

            "경기",

            "강원",

            "부산",

            "제주",

            "전국"

        ]

    )


with col2:

    keyword = st.text_input(

        "🔎 검색어",

        placeholder="예: 카페, 캠핑장"

    )


with col3:

    style = st.selectbox(

        "🌲 여행 스타일",

        [

            "힐링",

            "자연",

            "카페",

            "액티비티",

            "캠핑"

        ]

    )



st.write("")



if st.button(
    "🚀 여행 시작하기"
):

    st.session_state.search_region = region

    st.session_state.search_keyword = keyword

    st.session_state.search_style = style


    st.switch_page(
        "pages/1_Search.py"
    )



# ==============================
# 오늘의 추천
# ==============================


st.divider()


st.subheader(
    "🐕 오늘의 추천 여행지"
)


recommendations = [

    "🌊 강릉 애견 해변 산책",

    "🌲 제주 반려견 오름 여행",

    "🏕️ 홍천 반려견 캠핑",

    "☕ 양평 애견 카페 투어",

    "🏞️ 남해 자연 힐링 여행"

]


choice=random.choice(
    recommendations
)



st.success(choice)



# ==============================
# Stats
# ==============================


st.divider()


a,b,c = st.columns(3)


with a:

    st.metric(
        "🐾 등록 여행지",
        "1,000+"
    )


with b:

    st.metric(
        "🦴 추천 코스",
        "300+"
    )


with c:

    st.metric(
        "🌲 사용자 저장",
        len(
            st.session_state.favorites
        )
    )



st.caption(
    """
    PawTrip Korea © 2026
    """
)
