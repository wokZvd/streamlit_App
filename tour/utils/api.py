"""
한국관광공사 TourAPI 연동 모듈
"""

from typing import Dict, List, Optional
import os
import requests
import streamlit as st
from dotenv import load_dotenv


load_dotenv()


BASE_URL = (
    "https://apis.data.go.kr/B551011/KorService1"
)


SERVICE_KEY = os.getenv(
    "TOUR_API_KEY",
    ""
)



# =========================
# API 공통 호출
# =========================

@st.cache_data(ttl=3600)
def request_api(
    endpoint:str,
    params:dict
) -> dict:

    try:

        url = (
            f"{BASE_URL}/{endpoint}"
        )


        params.update(

            {
                "serviceKey":SERVICE_KEY,
                "MobileOS":"ETC",
                "MobileApp":"PawTripKorea",
                "_type":"json"
            }

        )


        response = requests.get(
            url,
            params=params,
            timeout=10
        )


        response.raise_for_status()


        return response.json()


    except Exception as e:

        st.warning(
            f"관광 API 오류: {e}"
        )

        return {}



# =========================
# 지역 코드
# =========================


REGION_CODES = {


"서울":"1",

"인천":"2",

"대전":"3",

"대구":"4",

"광주":"5",

"부산":"6",

"울산":"7",

"세종":"8",

"경기":"31",

"강원":"32",

"충북":"33",

"충남":"34",

"경북":"35",

"경남":"36",

"전북":"37",

"전남":"38",

"제주":"39",

"전국":""

}




def get_area_code(
    region:str
)->str:

    return REGION_CODES.get(
        region,
        ""
    )




# =========================
# 관광지 검색
# =========================


def search_places(

    region:str="전국",

    keyword:str="",

    content_type:str=""

)->List[Dict]:


    params={}


    if keyword:

        params["keyword"] = keyword


        data=request_api(

            "searchKeyword1",

            params

        )


    else:


        params={

            "areaCode":
            get_area_code(region),

            "numOfRows":20

        }


        data=request_api(

            "areaBasedList1",

            params

        )



    try:

        items = (

            data
            ["response"]
            ["body"]
            ["items"]
            ["item"]

        )


        if isinstance(items,dict):

            items=[items]


        return items


    except:


        return []




# =========================
# 상세 정보
# =========================


def get_detail(

    content_id:str

)->Dict:


    data=request_api(

        "detailCommon1",

        {

            "contentId":
            content_id,

            "defaultYN":"Y",

            "addrinfoYN":"Y",

            "firstImageYN":"Y"

        }

    )


    try:

        item=(

            data
            ["response"]
            ["body"]
            ["items"]
            ["item"]

        )


        return item[0]


    except:


        return {}




# =========================
# 반려견 친화 필터
# =========================


def pet_filter(

    places:List[Dict]

)->List[Dict]:


    result=[]


    keywords=[

        "반려",

        "애견",

        "동반",

        "펫"

    ]


    for p in places:


        text=str(p)


        if any(

            k in text

            for k in keywords

        ):

            result.append(p)



    return result
