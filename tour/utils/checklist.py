"""
반려견 여행 체크리스트 생성
"""


from typing import List



def dog_items(
    size:str
)->List[str]:


    base=[

        "🐾 배변봉투",

        "💧 물통",

        "🦴 간식",

        "🧻 물티슈",

        "🪮 빗",

        "🦮 산책줄",

    ]



    if size=="소형":

        base += [

            "👜 이동 가방",

            "🧸 담요"

        ]



    elif size=="중형":

        base += [

            "🚗 차량 안전벨트",

            "🏕️ 야외 매트"

        ]



    elif size=="대형":

        base += [

            "🦮 튼튼한 리드줄",

            "🚙 차량 보호 커버"

        ]



    return base




def travel_checklist()->List[str]:


    return [

        "📱 신분증",

        "💳 카드",

        "🔋 충전기",

        "🗺️ 여행 일정",

        "🏠 숙소 예약 확인"

    ]
