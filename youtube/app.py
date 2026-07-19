import streamlit as st
import pandas as pd
import re
import nltk
import matplotlib.pyplot as plt
from collections import Counter
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from wordcloud import WordCloud
import plotly.express as px
from nltk.sentiment.vader import SentimentIntensityAnalyzer

st.set_page_config(page_title="YouTube 댓글 분석기", page_icon="🎬", layout="wide")

try:
    nltk.data.find("sentiment/vader_lexicon")
except:
    nltk.download("vader_lexicon")

def extract_video_id(url):
    patterns=[
        r"youtube\.com/watch\?v=([^&]+)",
        r"youtu\.be/([^?&]+)",
        r"youtube\.com/shorts/([^?&]+)",
        r"youtube\.com/embed/([^?&]+)"
    ]
    for p in patterns:
        m=re.search(p,url)
        if m:
            return m.group(1)
    return None

def get_youtube(api_key):
    return build(
        "youtube",
        "v3",
        developerKey=api_key
    )

def get_video_info(youtube,video_id):
    try:
        result=youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()

        if not result["items"]:
            return None

        item=result["items"][0]

        return {
            "title":item["snippet"]["title"],
            "channel":item["snippet"]["channelTitle"],
            "date":item["snippet"]["publishedAt"],
            "views":item["statistics"].get("viewCount",0),
            "likes":item["statistics"].get("likeCount",0),
            "comments":item["statistics"].get("commentCount",0)
        }

    except HttpError:
        return None

def get_comments(youtube,video_id,limit):
    comments=[]
    token=None

    while len(comments)<limit:
        try:
            data=youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=min(100,limit-len(comments)),
                pageToken=token,
                textFormat="plainText"
            ).execute()

        except:
            break

        for item in data["items"]:
            c=item["snippet"]["topLevelComment"]["snippet"]

            comments.append({
                "author":c.get("authorDisplayName",""),
                "text":c.get("textDisplay",""),
                "likes":c.get("likeCount",0),
                "date":c.get("publishedAt","")
            })

            if len(comments)>=limit:
                break

        token=data.get("nextPageToken")

        if not token:
            break

    return pd.DataFrame(comments)

def clean_text(text):
    text=str(text)
    text=re.sub(r"http\S+","",text)
    text=re.sub(r"[^가-힣a-zA-Z0-9\s]","",text)
    return text

def sentiment(text):
    score=SentimentIntensityAnalyzer().polarity_scores(text)["compound"]

    if score>=0.05:
        return "긍정"
    elif score<=-0.05:
        return "부정"
    else:
        return "중립"

def analyze_comments(df):
    df["date"]=pd.to_datetime(df["date"],errors="coerce")
    df["hour"]=df["date"].dt.hour
    df["sentiment"]=df["text"].apply(sentiment)
    return df

def sentiment_data(df):
    result=df["sentiment"].value_counts().reset_index()
    result.columns=["감정","개수"]
    return result

def hourly_data(df):
    return df.groupby("hour").size().reset_index(name="댓글수")

def daily_data(df):
    return df.groupby(df["date"].dt.date).size().reset_index(name="댓글수")

def make_wordcloud(df):
    text=" ".join(
        clean_text(x)
        for x in df["text"]
    )

    if not text:
        return None

def make_wordcloud(df):
    text=" ".join(
        clean_text(x)
        for x in df["text"]
    )

    if not text:
        return None

    font_path="/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

    return WordCloud(
        font_path=font_path,
        width=900,
        height=500,
        background_color="white",
        max_words=100
    ).generate(text)

def top_words(df,n=20):
    words=[]

    for text in df["text"]:
        words.extend(clean_text(text).split())

    stop=[
        "영상",
        "댓글",
        "정말",
        "너무",
        "진짜",
        "감사합니다",
        "좋아요"
    ]

    words=[
        w for w in words
        if len(w)>1 and w not in stop
    ]

    return pd.DataFrame(
        Counter(words).most_common(n),
        columns=["단어","빈도"]
    )
def show_charts(df):
    st.subheader("시간대별 댓글 작성 추이")
    hourly=hourly_data(df)
    fig=px.bar(
        hourly,
        x="hour",
        y="댓글수",
        labels={"hour":"시간","댓글수":"댓글 개수"}
    )
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("날짜별 댓글 작성 추이")
    daily=daily_data(df)
    fig=px.line(
        daily,
        x="date",
        y="댓글수",
        markers=True
    )
    st.plotly_chart(fig,use_container_width=True)

    st.subheader("댓글 반응도")
    senti=sentiment_data(df)
    fig=px.pie(
        senti,
        names="감정",
        values="개수"
    )
    st.plotly_chart(fig,use_container_width=True)

def show_wordcloud(df):
    st.subheader("댓글 워드클라우드")
    wc=make_wordcloud(df)

    if wc:
        fig,ax=plt.subplots(figsize=(10,5))
        ax.imshow(wc,interpolation="bilinear")
        ax.axis("off")
        st.pyplot(fig)

def csv_download(df):
    return df.to_csv(
        index=False,
        encoding="utf-8-sig"
    )

st.title("🎬 YouTube 댓글 분석기")
st.write("YouTube 영상 댓글을 수집하고 반응을 분석합니다.")

with st.sidebar:
    api_key=st.text_input(
        "YouTube API Key",
        type="password"
    )

    url=st.text_input(
        "YouTube 영상 URL"
    )

    limit=st.slider(
        "분석 댓글 개수",
        100,
        5000,
        1000,
        100
    )

    start=st.button(
        "분석 시작"
    )

if start:
    if not api_key:
        st.error("API Key를 입력하세요.")
        st.stop()

    if not url:
        st.error("YouTube URL을 입력하세요.")
        st.stop()

    video_id=extract_video_id(url)

    if not video_id:
        st.error("올바른 YouTube URL이 아닙니다.")
        st.stop()

    with st.spinner("데이터 분석 중..."):
        youtube=get_youtube(api_key)

        info=get_video_info(
            youtube,
            video_id
        )

        comments=get_comments(
            youtube,
            video_id,
            limit
        )

    if comments.empty:
        st.warning("댓글이 없습니다.")
        st.stop()

    comments=analyze_comments(
        comments
    )

    st.success("분석 완료")

    st.subheader("영상")

    col1,col2=st.columns([2,1])

    with col1:
        st.video(
            f"https://youtube.com/watch?v={video_id}"
        )

    with col2:
        if info:
            st.write(
                "제목:",
                info["title"]
            )

            st.write(
                "채널:",
                info["channel"]
            )

            st.write(
                "조회수:",
                info["views"]
            )

            st.write(
                "좋아요:",
                info["likes"]
            )

            st.write(
                "댓글:",
                info["comments"]
            )

    st.divider()

    c1,c2,c3=st.columns(3)

    c1.metric(
        "분석 댓글",
        len(comments)
    )

    c2.metric(
        "평균 좋아요",
        round(
            comments["likes"].mean(),
            2
        )
    )

    c3.metric(
        "작성자 수",
        comments["author"].nunique()
    )

    st.divider()

    show_charts(
        comments
    )

    st.divider()

    show_wordcloud(
        comments
    )

    st.divider()

    st.subheader("많이 사용된 단어 TOP20")

    words=top_words(
        comments
    )

    st.dataframe(
        words,
        use_container_width=True
    )

    st.subheader("좋아요 많은 댓글")

    popular=comments.sort_values(
        "likes",
        ascending=False
    ).head(10)

    for _,row in popular.iterrows():
        st.write(
            f"👍 {row['likes']}  {row['text']}"
        )
        st.caption(
            row["author"]
        )

    st.divider()

    st.download_button(
        "댓글 CSV 다운로드",
        csv_download(comments),
        "youtube_comments.csv",
        "text/csv"
    )

else:
    st.info(
        "왼쪽 메뉴에서 API Key와 영상 URL을 입력하세요."
    )
