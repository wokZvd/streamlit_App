"""
🐶 PawTrip Korea
AI 여행 일정 생성 페이지
"""


import streamlit as st
import json


from utils.planner import (
    rule_planner
)


from utils.pdf import (
    create_pdf
)


from utils.export import (
    export_json,
    import_json
)


from utils.checklist import (
    dog_items,
    travel_checklist
)



# ==========================
# Page Config
# ==========================

st.set_page_config(

    page_title="AI 여행 플래너 🐶",

    page_icon="🦴",

    layout="wide"

)



# ==========================
# Header
# ==========================


st.title(
    "🦴 AI PawTrip Planner"
)


st.caption(
    "반려견 맞춤 여행 일정을 만들어드립니다"
)



st.divider()



# ==========================
# 입력 영역
# ==========================


col1,col2,col3=st.columns(3)



with col1:


    region=st.selectbox(

        "📍 여행 지역",

        [

            "서울",

            "경기",

            "강원",

            "부산",

            "제주"

        ]

    )



    days=st.number_input(

        "📅 여행 기간",

        min_value=1,

        max_value=7,

        value=2

    )



with col2:


    dog_size=st.selectbox(

        "🐶 반려견 크기",

        [

            "소형",

            "중형",

            "대형"

        ]

    )



    style=st.selectbox(

        "🌲 여행 스타일",

        [

            "힐링",

            "자연",

            "카페",

            "캠핑",

            "액티비티"

        ]

    )



with col3:


    st.info(

        """
        🐾 추천 기준

        - 이동 거리

        - 반려견 체력

        - 휴식 시간

        - 산책 환경

        """

    )



st.write("")



# ==========================
# 생성 버튼
# ==========================


if st.button(

    "✨ AI 일정 만들기"

):


    planner=rule_planner(

        region,

        days,

        dog_size,

        style

    )


    st.session_state.planner=planner



    st.success(

        "여행 일정 생성 완료 🐶"

    )



# ==========================
# 일정 출력
# ==========================


planner=st.session_state.get(

    "planner"

)



if planner:


    st.subheader(

        "🗺️ 추천 일정"

    )


    st.markdown(

        f"""
        ## {planner['title']}

        생성일:
        {planner['created']}

        """

    )



    for day in planner["days"]:


        st.markdown(

            f"""
            ## Day {day['day']} 🐾
            """

        )


        for item in day["schedule"]:


            st.write(

                f"""

                ⏰ {item['time']}

                📍 {item['place']}

                """

            )


            st.divider()



    # ======================
    # PDF 다운로드
    # ======================


    pdf=create_pdf(

        planner

    )


    st.download_button(

        label="📄 여행 일정 PDF 다운로드",

        data=pdf,

        file_name="PawTrip_schedule.pdf",

        mime="application/pdf"

    )



    # ======================
    # JSON Export
    # ======================


    json_data=export_json(

        planner

    )


    st.download_button(

        label="📤 일정 JSON 공유",

        data=json_data,

        file_name="pawtrip_plan.json",

        mime="application/json"

    )



# ==========================
# Import
# ==========================


st.divider()



st.subheader(

    "📥 일정 불러오기"

)



upload=st.file_uploader(

    "JSON 일정 파일 업로드",

    type=[

        "json"

    ]

)



if upload:


    try:


        imported=import_json(

            upload

        )


        st.session_state.planner=imported


        st.success(

            "일정 가져오기 완료!"

        )


        st.rerun()



    except Exception:


        st.error(

            "올바른 JSON 파일이 아닙니다."

        )



# ==========================
# 체크리스트
# ==========================


st.divider()



st.subheader(

    "🎒 반려견 여행 준비물"

)



if planner:


    items=dog_items(

        dog_size

    )


else:


    items=[]



for item in items:


    st.checkbox(

        item

    )



st.subheader(

    "🧳 기본 여행 체크리스트"

)


for item in travel_checklist():


    st.checkbox(

        item

    )
