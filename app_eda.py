# 동일한 코드 시작 - 생략 없이 전체 유지되며, 모든 그래프 요소는 영어로
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(layout="wide")
st.title("Population Trends EDA Dashboard")

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
        "Basic Stats", "National Trend", "Sejong Region", "5-Year Change", "Top 100 Changes", "Area Chart"
    ])

    with tab1:
        st.header("Basic Statistics")
        buf = io.StringIO()
        df.info(buf=buf)
        st.text(buf.getvalue())
        st.dataframe(df.describe().style.format("{:,.0f}"))

    with tab2:
        st.header("National Population Trend & Projection (2035)")
        nat_df = df[df['지역'] == '전국'].copy()
        nat_df.sort_values('연도', inplace=True)
        recent = nat_df.tail(3)
        net = (recent['출생아수(명)'] - recent['사망자수(명)']).mean()
        pred = nat_df['인구'].iloc[-1] + (2035 - nat_df['연도'].iloc[-1]) * net

        fig, ax = plt.subplots()
        ax.plot(nat_df['연도'], nat_df['인구'], marker='o', label='Observed')
        ax.plot(2035, pred, 'ro', label='Projected 2035')
        ax.set_title("National Population Trend")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population")
        ax.legend()
        st.pyplot(fig)
        st.write(f"**Estimated population in 2035**: {int(pred):,}")

    with tab3:
        st.header("Sejong Region Analysis")
        if '행정구역' in df.columns:
            sejong = df[df['행정구역'].astype(str).str.contains('세종')].copy()
        else:
            sejong = df[df['지역'].astype(str).str.contains('세종')].copy()

        if not sejong.empty:
            st.dataframe(sejong.head())
            st.dataframe(sejong.describe().style.format("{:,.0f}"))
        else:
            st.warning("No data for Sejong region found.")

    with tab4:
        st.header("5-Year Regional Population Change")
        non_nat = df[df['지역'] != '전국']
        years = sorted(non_nat['연도'].unique())[-5:]
        pivot = non_nat[non_nat['연도'].isin(years)].pivot_table(index='지역', columns='연도', values='인구')
        change = pd.DataFrame()
        change['Change (thousands)'] = (pivot[years[-1]] - pivot[years[0]]) / 1000
        change['Growth Rate (%)'] = ((pivot[years[-1]] - pivot[years[0]]) / pivot[years[0]]) * 100
        change['Region'] = change.index.map(region_translation)
        change.sort_values('Change (thousands)', ascending=False, inplace=True)

        fig1, ax1 = plt.subplots()
        sns.barplot(data=change, x='Change (thousands)', y='Region', ax=ax1)
        ax1.set_title("Population Change Over 5 Years")
        ax1.set_xlabel("Change (thousands)")
        ax1.set_ylabel("Region")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots()
        sns.barplot(data=change, x='Growth Rate (%)', y='Region', ax=ax2)
        ax2.set_title("Population Growth Rate Over 5 Years")
        ax2.set_xlabel("Growth Rate (%)")
        ax2.set_ylabel("Region")
        st.pyplot(fig2)

    with tab5:
        st.header("Top 100 Annual Population Changes")
        df_diff = df[df['지역'] != '전국'].copy()
        df_diff.sort_values(['지역', '연도'], inplace=True)
        df_diff['Change'] = df_diff.groupby('지역')['인구'].diff()
        top100 = df_diff.dropna().assign(abs_change=lambda x: x['Change'].abs()).nlargest(100, 'abs_change')
        st.dataframe(top100[['연도', '지역', '인구', 'Change']].style
                     .format({"인구": "{:,.0f}", "Change": "{:,.0f}"})
                     .background_gradient(subset='Change', cmap='RdBu_r'))

    with tab6:
        st.header("Stacked Area Plot by Region")
        pivot_area = df[df['지역'] != '전국'].pivot_table(index='연도', columns='region_en', values='인구')
        pivot_area = pivot_area.fillna(0).sort_index() / 1000
        fig, ax = plt.subplots(figsize=(12, 7))
        pivot_area.plot.area(ax=ax, stacked=True, colormap='tab20')
        ax.set_title("Regional Population Over Time")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population (thousands)")
        ax.legend(title="Region", loc='upper left', bbox_to_anchor=(1, 1))
        st.pyplot(fig)

else:
    st.warning("Please upload a valid CSV file.")

