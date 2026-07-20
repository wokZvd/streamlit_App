"""
Folium 지도 생성
"""


from typing import List,Dict
import folium



def create_map(

    places:List[Dict]

):


    center=[

        36.5,

        127.8

    ]


    fmap=folium.Map(

        location=center,

        zoom_start=7

    )



    for place in places:


        try:


            lat=float(
                place.get(
                    "mapy"
                )
            )


            lng=float(
                place.get(
                    "mapx"
                )
            )



            popup=f"""

            <b>
            {place.get('title')}
            </b>

            <br>

            {place.get('addr1','')}

            """



            folium.Marker(

                [

                    lat,

                    lng

                ],

                popup=popup,

                tooltip=
                place.get(
                    "title"
                )

            ).add_to(
                fmap
            )


        except:

            continue



    return fmap
