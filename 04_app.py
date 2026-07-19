import streamlit as st
import pandas as pd
import numpy as np
import re
import requests
from datetime import datetime

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import plotly.express as px

from wordcloud import WordCloud
import matplotlib.pyplot as plt

from collections import Counter

import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer


st.set_page_config(
    page_title="YouTube 댓글 분석기",
    page_icon="🎬",
    layout="wide"
)


st.markdown(
"""
<style>

.main-title {
    font-size:40px;
    font-weight:bold;
}

.box {
    padding:20px;
    border-radius:10px;
    background:#f5f5f5;
}

</style>
""",
unsafe_allow_html=True
)


try:
    nltk.data.find(
        "sentiment/vader_lexicon"
    )

except:

    nltk.download(
        "vader_lexicon"
    )



def extract_video_id(url):

    """
    다양한 형태의 YouTube URL에서
    video id 추출
    """

    patterns = [

        r"youtube\.com/watch\?v=([^&]+)",

        r"youtu\.be/([^?&]+)",

        r"youtube\.com/embed/([^?&]+)",

        r"youtube\.com/shorts/([^?&]+)"

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            url
        )

        if match:

            return match.group(1)


    return None




def get_youtube_service(api_key):

    return build(
        "youtube",
        "v3",
        developerKey=api_key
    )



def get_video_info(
        youtube,
        video_id
):

    try:

        response = youtube.videos().list(

            part="snippet,statistics,contentDetails",

            id=video_id

        ).execute()



        if not response["items"]:

            return None



        item=response["items"][0]


        snippet=item["snippet"]

        stats=item["statistics"]



        data={

            "title":
                snippet.get(
                    "title",
                    ""
                ),

            "channel":
                snippet.get(
                    "channelTitle",
                    ""
                ),

            "published":
                snippet.get(
                    "publishedAt",
                    ""
                ),

            "views":
                stats.get(
                    "viewCount",
                    0
                ),

            "likes":
                stats.get(
                    "likeCount",
                    0
                ),

            "comments":
                stats.get(
                    "commentCount",
                    0
                )

        }


        return data


    except HttpError as e:

        st.error(
            f"YouTube API 오류: {e}"
        )

        return None





def get_comments(
        youtube,
        video_id,
        max_comments=1000
):

    comments=[]


    next_page_token=None



    while len(comments)<max_comments:


        try:


            result = youtube.commentThreads().list(

                part="snippet",

                videoId=video_id,

                maxResults=min(
                    100,
                    max_comments
                    -
                    len(comments)
                ),

                pageToken=next_page_token,

                textFormat="plainText"

            ).execute()



        except HttpError:


            break




        for item in result["items"]:


            comment = item["snippet"]["topLevelComment"]["snippet"]


            comments.append(

                {

                    "author":
                        comment.get(
                            "authorDisplayName",
                            ""
                        ),


                    "text":
                        comment.get(
                            "textDisplay",
                            ""
                        ),


                    "likes":
                        comment.get(
                            "likeCount",
                            0
                        ),


                    "published":
                        comment.get(
                            "publishedAt",
                            ""
                        )

                }

            )



            if len(comments)>=max_comments:

                break



        next_page_token = result.get(
            "nextPageToken"
        )


        if not next_page_token:

            break



    return pd.DataFrame(
        comments
    )


def process_comment_dates(df):

    if df.empty:
        return df


    df["published"] = pd.to_datetime(
        df["published"],
        errors="coerce"
    )


    df["date"] = df["published"].dt.date


    df["hour"] = df["published"].dt.hour


    return df


def analyze_sentiment(text):

    """
    VADER 기반 감성 분석

    score 기준:
    > 0.05 긍정
    < -0.05 부정
    그 외 중립

    """

    analyzer = SentimentIntensityAnalyzer()


    result = analyzer.polarity_scores(
        text
    )


    compound=result["compound"]


    if compound >= 0.05:

        return "긍정"


    elif compound <= -0.05:

        return "부정"


    else:

        return "중립"






def add_sentiment_column(df):


    if df.empty:

        return df



    df["sentiment"] = df["text"].apply(

        analyze_sentiment

    )


    return df



def sentiment_summary(df):


    if df.empty:

        return pd.DataFrame()



    result=(

        df["sentiment"]

        .value_counts()

        .reset_index()

    )


    result.columns=[

        "감정",

        "개수"

    ]


    result["비율"]=round(

        result["개수"]

        /

        result["개수"].sum()

        *

        100,

        2

    )


    return result



def hourly_comment_trend(df):


    if df.empty:

        return pd.DataFrame()



    trend=(

        df.groupby(

            "hour"

        )

        .size()

        .reset_index(

        name="댓글수"

        )

    )


    return trend




def daily_comment_trend(df):


    if df.empty:

        return pd.DataFrame()



    trend=(

        df.groupby(

            "date"

        )

        .size()

        .reset_index(

            name="댓글수"

        )

    )


    return trend



def clean_text(text):


    text=str(text)


    text=re.sub(

        r"http\S+",

        "",

        text

    )


    text=re.sub(

        r"[^가-힣a-zA-Z0-9\s]",

        "",

        text

    )


    return text




def prepare_words(df):


    if df.empty:

        return ""



    texts=[]


    for t in df["text"]:

        texts.append(

            clean_text(t)

        )



    return " ".join(texts)





def get_top_words(df, count=20):


    text=prepare_words(df)


    words=text.split()



    stopwords=[

        "그리고",

        "하는",

        "입니다",

        "있습니다",

        "영상",

        "댓글",

        "정말",

        "너무",

        "진짜",

        "오늘",

        "감사합니다",

        "좋아요"

    ]



    filtered=[

        w

        for w in words

        if w not in stopwords

        and len(w)>1

    ]



    counter=Counter(

        filtered

    )


    return pd.DataFrame(

        counter.most_common(count),

        columns=[

            "단어",

            "빈도"

        ]

    )


def create_wordcloud(df):


    text=prepare_words(df)



    if not text:

        return None



    wc=WordCloud(

        font_path=

        "NanumGothic.ttf",

        width=900,

        height=500,

        background_color="white",

        max_words=100

    )



    image=wc.generate(

        text

    )



    return image




def convert_csv(df):


    return df.to_csv(

        index=False,

        encoding="utf-8-sig"

    )




def top_liked_comments(df, n=10):


    if df.empty:

        return df



    return (

        df.sort_values(

            "likes",

            ascending=False

        )

        .head(n)

    )

def draw_hourly_chart(df):

    if df.empty:
        return None


    fig = px.bar(

        df,

        x="hour",

        y="댓글수",

        title="시간대별 댓글 작성 추이",

        labels={

            "hour":"시간",

            "댓글수":"댓글 개수"

        }

    )


    fig.update_layout(

        xaxis=dict(

            dtick=1

        )

    )


    return fig






def draw_daily_chart(df):


    if df.empty:

        return None



    fig = px.line(

        df,

        x="date",

        y="댓글수",

        markers=True,

        title="날짜별 댓글 작성 추이"

    )


    return fig






def draw_sentiment_chart(df):


    if df.empty:

        return None



    fig = px.pie(

        df,

        names="감정",

        values="개수",

        title="댓글 감성 분석"

    )


    return fig







def draw_top_words_chart(df):


    if df.empty:

        return None



    fig=px.bar(

        df,

        x="빈도",

        y="단어",

        orientation="h",

        title="댓글 TOP 20 키워드"

    )


    return fig





st.markdown(

"""
<div class="main-title">
🎬 YouTube 댓글 분석기
</div>
""",

unsafe_allow_html=True

)


st.write(

"YouTube 영상 댓글을 분석하여 반응과 트렌드를 확인합니다."

)




with st.sidebar:


    st.header(

        "⚙️ 분석 설정"

    )


    api_key = st.text_input(

        "YouTube API Key",

        type="password"

    )



    video_url = st.text_input(

        "YouTube 영상 URL"

    )



    comment_limit = st.slider(

        "분석 댓글 개수",

        min_value=100,

        max_value=5000,

        value=1000,

        step=100

    )



    analyze_button = st.button(

        "🚀 분석 시작"

    )



if analyze_button:



    if not api_key:


        st.error(

            "YouTube API Key를 입력하세요."

        )

        st.stop()



    if not video_url:


        st.error(

            "YouTube URL을 입력하세요."

        )

        st.stop()





    video_id = extract_video_id(

        video_url

    )



    if not video_id:


        st.error(

            "올바른 YouTube URL이 아닙니다."

        )

        st.stop()






    with st.spinner(

        "YouTube 데이터를 가져오는 중..."

    ):



        youtube = get_youtube_service(

            api_key

        )



        video_info = get_video_info(

            youtube,

            video_id

        )



        comments_df = get_comments(

            youtube,

            video_id,

            comment_limit

        )





    if video_info is None:


        st.error(

            "영상 정보를 가져올 수 없습니다."

        )

        st.stop()






    if comments_df.empty:


        st.warning(

            "댓글을 찾을 수 없습니다."

        )

        st.stop()







    # 날짜 처리

    comments_df = process_comment_dates(

        comments_df

    )



    # 감성 분석

    with st.spinner(

        "댓글 감성 분석 중..."

    ):


        comments_df = add_sentiment_column(

            comments_df

        )




    st.subheader(

        "🎬 영상"

    )


    col1,col2 = st.columns(

        [2,1]

    )


    with col1:


        st.video(

            f"https://youtube.com/watch?v={video_id}"

        )



    with col2:


        st.write(

            "### 제목"

        )


        st.write(

            video_info["title"]

        )



        st.write(

            "채널:",

            video_info["channel"]

        )


        st.write(

            "조회수:",

            video_info["views"]

        )


        st.write(

            "좋아요:",

            video_info["likes"]

        )


        st.write(

            "댓글수:",

            video_info["comments"]

        )





    st.divider()




    st.subheader(

        "💬 분석 결과"

    )


    c1,c2,c3 = st.columns(3)



    c1.metric(

        "분석 댓글",

        len(comments_df)

    )


    c2.metric(

        "평균 좋아요",

        round(

            comments_df["likes"].mean(),

            2

        )

    )


    c3.metric(

        "댓글 작성자",

        comments_df["author"].nunique()

    )


    st.divider()




    hourly = hourly_comment_trend(

        comments_df

    )


    fig_hour = draw_hourly_chart(

        hourly

    )


    if fig_hour:


        st.plotly_chart(

            fig_hour,

            use_container_width=True

        )






    daily = daily_comment_trend(

        comments_df

    )


    fig_daily = draw_daily_chart(

        daily

    )



    if fig_daily:


        st.plotly_chart(

            fig_daily,

            use_container_width=True

        )



    st.subheader(
        "😊 댓글 반응도 분석"
    )


    sentiment_df = sentiment_summary(

        comments_df

    )


    sentiment_fig = draw_sentiment_chart(

        sentiment_df

    )


    if sentiment_fig:


        st.plotly_chart(

            sentiment_fig,

            use_container_width=True

        )



    st.dataframe(

        sentiment_df,

        use_container_width=True

    )


    st.divider()




    st.subheader(

        "☁️ 댓글 워드클라우드"

    )


    wc = create_wordcloud(

        comments_df

    )


    if wc:


        fig, ax = plt.subplots(

            figsize=(12,6)

        )


        ax.imshow(

            wc,

            interpolation="bilinear"

        )


        ax.axis(

            "off"

        )


        st.pyplot(

            fig

        )


    else:


        st.info(

            "워드클라우드를 생성할 수 없습니다."

        )




    st.divider()





    st.subheader(

        "🔥 많이 언급된 단어 TOP20"

    )


    top_words = get_top_words(

        comments_df,

        20

    )


    keyword_fig = draw_top_words_chart(

        top_words

    )



    if keyword_fig:


        st.plotly_chart(

            keyword_fig,

            use_container_width=True

        )


    st.dataframe(

        top_words,

        use_container_width=True

    )






    st.divider()




    st.subheader(

        "👍 좋아요 많은 댓글 TOP10"

    )


    popular_comments = top_liked_comments(

        comments_df,

        10

    )


    for idx,row in popular_comments.iterrows():


        with st.container():


            st.write(

                f"👍 {row['likes']} 좋아요"

            )


            st.write(

                row["text"]

            )


            st.caption(

                row["author"]

            )


            st.divider()





    st.subheader(

        "📥 데이터 다운로드"

    )


    csv = convert_csv(

        comments_df

    )


    st.download_button(

        label="댓글 데이터 CSV 다운로드",

        data=csv,

        file_name="youtube_comments.csv",

        mime="text/csv"

    )








    st.success(

        "🎉 분석 완료!"

    )


else:


    st.info(

        """
        👈 왼쪽 메뉴에서 설정 후 분석을 시작하세요.

        사용 방법:

        1. YouTube Data API Key 입력
        2. YouTube 영상 URL 입력
        3. 분석할 댓글 개수 선택
        4. 분석 시작 버튼 클릭

        제공 기능:

        ✅ 영상 표시  
        ✅ 댓글 수집  
        ✅ 시간대별 댓글 추이  
        ✅ 감성 분석  
        ✅ 워드클라우드  
        ✅ 인기 댓글 분석  
        ✅ CSV 다운로드  

        """

    )
