"""
AI 여행 일정 생성 엔진

OpenAI 사용 가능
없으면 Rule 기반 생성
"""


from typing import List,Dict
import os
from datetime import datetime


try:

    from openai import OpenAI

except:

    OpenAI=None



OPENAI_KEY=os.getenv(
    "OPENAI_API_KEY"
)




def rule_planner(

    region:str,

    days:int,

    dog_size:str,

    style:str

)->Dict:



    courses={


        "힐링":[

            "반려견 산책 명소",

            "애견 카페",

            "호수 공원",

            "숙소 휴식"

        ],


        "캠핑":[

            "캠핑장",

            "숲 산책",

            "바비큐",

            "별보기"

        ],


        "자연":[

            "자연휴양림",

            "둘레길",

            "전망대",

            "계곡"

        ],


        "카페":[

            "애견 카페",

            "브런치",

            "산책",

            "야경"

        ],


        "액티비티":[

            "해변 산책",

            "체험",

            "레저",

            "휴식"

        ]

    }


    selected=(
        courses.get(
            style
        )
    )



    result={

        "title":

        f"{region} 반려견 {style} 여행",


        "created":

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),


        "days":[]

    }



    for d in range(
        1,
        days+1
    ):


        result["days"].append(

            {

            "day":d,

            "schedule":[


                {

                "time":"09:00",

                "place":selected[0]

                },


                {

                "time":"11:30",

                "place":selected[1]

                },


                {

                "time":"13:00",

                "place":selected[2]

                },


                {

                "time":"16:00",

                "place":selected[3]

                },


                {

                "time":"18:00",

                "place":"숙소 휴식"

                }


            ]

            }

        )


    return result
