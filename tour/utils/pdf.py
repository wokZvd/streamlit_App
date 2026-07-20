"""
PawTrip Korea
여행 일정 PDF 생성 모듈

reportlab 사용
"""

from typing import Dict
from io import BytesIO
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont



# ==========================
# 한글 폰트 등록
# ==========================

pdfmetrics.registerFont(
    UnicodeCIDFont(
        "HYSMyeongJo-Medium"
    )
)



# ==========================
# PDF 생성
# ==========================

def create_pdf(
    planner: Dict
) -> bytes:


    buffer = BytesIO()


    doc = SimpleDocTemplate(
        buffer
    )


    styles = getSampleStyleSheet()


    for style in styles.byName.values():

        style.fontName = (
            "HYSMyeongJo-Medium"
        )



    elements=[]



    # 제목

    elements.append(

        Paragraph(

            "🐶 PawTrip Korea 여행 일정",

            styles["Title"]

        )

    )


    elements.append(
        Spacer(1,20)
    )



    elements.append(

        Paragraph(

            f"""
            생성일 :
            {datetime.now().strftime('%Y-%m-%d')}

            <br/>

            여행명 :
            {planner.get('title','')}

            """,

            styles["Normal"]

        )

    )



    elements.append(
        Spacer(1,20)
    )



    # 일정표

    for day in planner.get(
        "days",
        []
    ):


        elements.append(

            Paragraph(

                f"Day {day['day']}",

                styles["Heading2"]

            )

        )


        table_data=[

            [

                "시간",

                "장소"

            ]

        ]



        for item in day.get(
            "schedule",
            []
        ):

            table_data.append(

                [

                    item.get(
                        "time",
                        ""
                    ),

                    item.get(
                        "place",
                        ""
                    )

                ]

            )



        table=Table(
            table_data
        )


        table.setStyle(

            TableStyle(

                [

                    (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    0.5,
                    None
                    )

                ]

            )

        )


        elements.append(
            table
        )


        elements.append(
            Spacer(1,20)
        )



    # 준비물

    elements.append(

        Paragraph(

            """
            🦴 반려견 준비물 체크리스트

            <br/>

            □ 배변봉투

            <br/>

            □ 물통

            <br/>

            □ 사료

            <br/>

            □ 이동장

            <br/>

            □ 산책줄

            """,

            styles["Normal"]

        )

    )


    doc.build(
        elements
    )


    buffer.seek(0)


    return buffer.read()
