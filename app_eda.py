import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(layout="wide")
st.title("Population Trends EDA Dashboard")

# 공통 설정
region_translation = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju",
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon",
    "충북": "Chungbuk", "충남": "Chungnam", "전북": "Jeonbuk", "전남": "Jeonnam", "경북": "Gyeongbuk",
    "경남": "Gyeongnam", "제주": "Jeju"
}

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv", key="main_uploader")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df.replace("-", 0, inplace=True)
    df['연도'] = pd.to_numeric(df['연도'], errors='coerce')
    for col in ['인구', '출생아수(명)', '사망자수(명)']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['region_en'] = df['지역'].map(region_translation)

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "기초 통계", "전국 추세", "세종 지역", "5년 지역 변화", "Top 100 변화", "누적 영역 그래프"
    ])

    with tab1:
        st.header("기초 통계")
        buf = io.StringIO()
        df.info(buf=buf)
        st.text(buf.getvalue())
        st.dataframe(df.describe().style.format("{:,.0f}"))

    with tab2:
        st.header("전국 인구 추세 및 2035 예측")
        nat_df = df[df['지역'] == '전국'].copy()
        nat_df.sort_values('연도', inplace=True)
        recent = nat_df.tail(3)
        net = (recent['출생아수(명)'] - recent['사망자수(명)']).mean()
        pred = nat_df['인구'].iloc[-1] + (2035 - nat_df['연도'].iloc[-1]) * net

        fig, ax = plt.subplots()
        ax.plot(nat_df['연도'], nat_df['인구'], marker='o', label='Observed')
        ax.plot(2035, pred, 'ro', label='2035 Projected')
        ax.set_title("National Trend")
        ax.legend()
        st.pyplot(fig)
        st.write(f"**2035 예상 인구**: {int(pred):,}")

    with tab3:
        st.header("세종 지역 분석")
        if '행정구역' in df.columns:
            sejong = df[df['행정구역'].astype(str).str.contains('세종')].copy()
        else:
            sejong = df[df['지역'].astype(str).str.contains('세종')].copy()

        if not sejong.empty:
            st.dataframe(sejong.head())
            st.dataframe(sejong.describe().style.format("{:,.0f}"))
        else:
            st.warning("세종 데이터 없음")

    with tab4:
        st.header("최근 5년 지역 변화")
        non_nat = df[df['지역'] != '전국']
        years = sorted(non_nat['연도'].unique())[-5:]
        pivot = non_nat[non_nat['연도'].isin(years)].pivot_table(index='지역', columns='연도', values='인구')
        change = pd.DataFrame()
        change['변화량'] = (pivot[years[-1]] - pivot[years[0]]) / 1000
        change['변화율'] = ((pivot[years[-1]] - pivot[years[0]]) / pivot[years[0]]) * 100
        change['region'] = change.index.map(region_translation)
        change.sort_values('변화량', ascending=False, inplace=True)

        fig1, ax1 = plt.subplots()
        sns.barplot(data=change, x='변화량', y='region', ax=ax1)
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        sns.barplot(data=change, x='변화율', y='region', ax=ax2)
        st.pyplot(fig2)

    with tab5:
        st.header("Top 100 인구 변화")
        df_diff = df[df['지역'] != '전국'].copy()
        df_diff.sort_values(['지역', '연도'], inplace=True)
        df_diff['증감'] = df_diff.groupby('지역')['인구'].diff()
        top100 = df_diff.dropna().assign(abs_change=lambda x: x['증감'].abs()).nlargest(100, 'abs_change')
        st.dataframe(top100[['연도', '지역', '인구', '증감']].style
                     .format({"인구": "{:,.0f}", "증감": "{:,.0f}"})
                     .background_gradient(subset='증감', cmap='RdBu_r'))

    with tab6:
        st.header("누적 영역 그래프")
        pivot_area = df[df['지역'] != '전국'].pivot_table(index='연도', columns='region_en', values='인구')
        pivot_area = pivot_area.fillna(0).sort_index() / 1000
        fig, ax = plt.subplots(figsize=(12, 7))
        pivot_area.plot.area(ax=ax, stacked=True, colormap='tab20')
        ax.set_ylabel("Population (thousands)")
        ax.set_title("Regional Population Trend")
        st.pyplot(fig)

else:
    st.warning("CSV 파일을 업로드해 주세요.")
