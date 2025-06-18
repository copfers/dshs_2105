import streamlit as st
import pandas as pd
import numpy as np
import io

# 타이틀
st.title("Population Trends Data Preprocessing")

# 파일 업로드
uploaded_file = st.file_uploader("CSV 파일을 업로드하세요", type="csv")

if uploaded_file is not None:
    # CSV 파일 읽기
    df = pd.read_csv(uploaded_file)

    st.subheader("원본 데이터 미리보기")
    st.dataframe(df.head())

    # '세종' 지역 필터링
    sejong_df = df[df['행정구역'].str.contains('세종', na=False)].copy()

    # '-' 기호를 0으로 대체
    sejong_df.replace('-', 0, inplace=True)

    # 숫자로 변환할 열 목록
    numeric_columns = ['인구', '출생아수(명)', '사망자수(명)']
    
    # 열을 숫자(float)로 변환
    for col in numeric_columns:
        sejong_df[col] = pd.to_numeric(sejong_df[col], errors='coerce').fillna(0)

    st.subheader("전처리된 '세종' 지역 데이터 미리보기")
    st.dataframe(sejong_df.head())

    # 데이터 요약 통계
    st.subheader("요약 통계 (describe())")
    st.dataframe(sejong_df.describe())

    # info 출력 - 문자열로 출력
    buffer = io.StringIO()
    sejong_df.info(buf=buffer)
    info_str = buffer.getvalue()

    st.subheader("데이터프레임 정보 (info())")
    st.text(info_str)

else:
    st.info("CSV 파일을 업로드해 주세요.")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io

st.title("National Population Trend and 2035 Projection")

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")

if uploaded_file:
    # CSV 로딩
    df = pd.read_csv(uploaded_file)

    # '-' -> 0 치환, 숫자형 변환
    df.replace('-', 0, inplace=True)
    numeric_cols = ['인구', '출생아수(명)', '사망자수(명)']
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # '전국' 데이터만 필터링
    nat_df = df[df['지역'].str.contains('전국', na=False)].copy()

    # 연도 정렬
    nat_df['연도'] = pd.to_numeric(nat_df['연도'], errors='coerce')
    nat_df.sort_values(by='연도', inplace=True)

    # 최근 3년 데이터 가져오기
    recent_df = nat_df.tail(3)
    avg_births = recent_df['출생아수(명)'].mean()
    avg_deaths = recent_df['사망자수(명)'].mean()
    net_increase = avg_births - avg_deaths

    # 마지막 연도와 인구
    last_year = int(nat_df['연도'].max())
    last_population = nat_df[nat_df['연도'] == last_year]['인구'].values[0]

    # 2035년까지 예측 (단순 선형 누적)
    years_to_project = 2035 - last_year
    estimated_2035 = last_population + (net_increase * years_to_project)

    # 시각화
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(nat_df['연도'], nat_df['인구'], marker='o', label='Observed')

    # 2035년 예측치 추가
    ax.plot(2035, estimated_2035, 'ro', label='Projected 2035')
    ax.annotate(f"{int(estimated_2035):,}", xy=(2035, estimated_2035), xytext=(2035 - 5, estimated_2035 + 10000),
                arrowprops=dict(arrowstyle="->", color='red'))

    ax.set_title("Population Trend (National)", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Population")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # 예측 결과 출력
    st.subheader("2035 Population Projection")
    st.write(f"Estimated population in 2035: **{int(estimated_2035):,}** (based on average net increase of last 3 years)")

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.title("5-Year Regional Population Change (Excluding National Total)")

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")

# 지역 영어 번역 사전
region_translation = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju",
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon",
    "충북": "Chungbuk", "충남": "Chungnam", "전북": "Jeonbuk", "전남": "Jeonnam", "경북": "Gyeongbuk",
    "경남": "Gyeongnam", "제주": "Jeju"
}

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 전처리
    df.replace('-', 0, inplace=True)
    df['인구'] = pd.to_numeric(df['인구'], errors='coerce').fillna(0)
    df['연도'] = pd.to_numeric(df['연도'], errors='coerce')

    # 전국 제외
    df = df[df['지역'] != '전국']

    # 연도별 마지막 5년 추출
    recent_years = sorted(df['연도'].unique())[-5:]
    df_recent = df[df['연도'].isin(recent_years)]

    # 지역별 인구 변화 계산
    pivot_df = df_recent.pivot_table(index='지역', columns='연도', values='인구')

    # 변화량 및 변화율 계산
    change_df = pd.DataFrame()
    change_df['absolute_change'] = (pivot_df[recent_years[-1]] - pivot_df[recent_years[0]]) / 1000  # 천명 단위
    change_df['percent_change'] = ((pivot_df[recent_years[-1]] - pivot_df[recent_years[0]]) / pivot_df[recent_years[0]]) * 100

    # 지역명 영문화
    change_df['region'] = change_df.index.map(region_translation)
    change_df.sort_values('absolute_change', ascending=False, inplace=True)

    # 첫 번째 그래프: 인구 변화량
    fig1, ax1 = plt.subplots(figsize=(10, 7))
    sns.barplot(data=change_df, y='region', x='absolute_change', ax=ax1, palette='coolwarm')
    for i, val in enumerate(change_df['absolute_change']):
        ax1.text(val + 1, i, f"{val:.1f}", va='center', fontsize=9)
    ax1.set_title("Population Change over Last 5 Years")
    ax1.set_xlabel("Change (in thousands)")
    ax1.set_ylabel("Region")

    # 두 번째 그래프: 변화율
    fig2, ax2 = plt.subplots(figsize=(10, 7))
    sns.barplot(data=change_df, y='region', x='percent_change', ax=ax2, palette='viridis')
    for i, val in enumerate(change_df['percent_change']):
        ax2.text(val + 0.5, i, f"{val:.1f}%", va='center', fontsize=9)
    ax2.set_title("Population Growth Rate (5-Year)")
    ax2.set_xlabel("Growth Rate (%)")
    ax2.set_ylabel("Region")

    # 시각화 출력
    st.pyplot(fig1)
    st.pyplot(fig2)

    # 해설 제공
    st.subheader("Interpretation")
    top_growth = change_df.iloc[0]
    bottom_growth = change_df.iloc[-1]

    st.markdown(f"""
    - **{top_growth['region']}** had the **highest population increase** over the past 5 years with a gain of **{top_growth['absolute_change']:.1f} thousand** people.
    - **{bottom_growth['region']}** experienced the **greatest population loss** or the **smallest gain**, totaling **{bottom_growth['absolute_change']:.1f} thousand**.
    - The **growth rate** graph indicates relative change: some regions with small absolute changes may show large percentage increases or decreases.
    """)
import streamlit as st
import pandas as pd
import numpy as np

st.title("Top 100 Population Changes by Region and Year")

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 전처리
    df.replace("-", 0, inplace=True)
    df['인구'] = pd.to_numeric(df['인구'], errors='coerce').fillna(0)
    df['연도'] = pd.to_numeric(df['연도'], errors='coerce')

    # 전국 제외
    df = df[df['지역'] != '전국']

    # 지역-연도별 정렬 및 증감량(diff) 계산
    df.sort_values(by=['지역', '연도'], inplace=True)
    df['증감'] = df.groupby('지역')['인구'].diff()

    # 상위 100개 (절댓값 기준)
    top_changes = df.dropna(subset=['증감']).copy()
    top_changes['증감_abs'] = top_changes['증감'].abs()
    top_100 = top_changes.nlargest(100, '증감_abs')

    # 천단위 콤마 포맷 적용용 컬럼
    top_100_display = top_100[['연도', '지역', '인구', '증감']].copy()
    top_100_display['인구'] = top_100_display['인구'].map(lambda x: f"{int(x):,}")
    top_100_display['증감'] = top_100_display['증감'].map(lambda x: f"{int(x):,}")

    # 스타일 지정용 컬럼 (숫자용)
    top_100_numeric = top_100[['연도', '지역', '인구', '증감']].copy()

    # 시각화
    st.subheader("Top 100 Population Changes")
    styled_df = top_100_numeric.style\
        .format({"인구": "{:,.0f}", "증감": "{:,.0f}"})\
        .background_gradient(subset='증감', cmap='RdBu_r', vmin=-top_100_numeric['증감'].abs().max(), vmax=top_100_numeric['증감'].abs().max())

    st.dataframe(styled_df, use_container_width=True)

else:
    st.info("Please upload a CSV file.")
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.title("Population Trend Area Plot by Region")

# 지역 한글-영문 변환 사전
region_translation = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju",
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon",
    "충북": "Chungbuk", "충남": "Chungnam", "전북": "Jeonbuk", "전남": "Jeonnam", "경북": "Gyeongbuk",
    "경남": "Gyeongnam", "제주": "Jeju"
}

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 전처리
    df.replace("-", 0, inplace=True)
    df['인구'] = pd.to_numeric(df['인구'], errors='coerce').fillna(0)
    df['연도'] = pd.to_numeric(df['연도'], errors='coerce')

    # 전국 제외
    df = df[df['지역'] != '전국']

    # 지역명을 영문으로 변환
    df['region_en'] = df['지역'].map(region_translation)

    # 피벗 테이블 생성 (index: 연도, columns: region, values: 인구)
    pivot_df = df.pivot_table(index='연도', columns='region_en', values='인구', aggfunc='sum')
    pivot_df = pivot_df.fillna(0).sort_index()

    # 누적 영역 그래프 (stacked area plot)
    fig, ax = plt.subplots(figsize=(12, 7))
    pivot_df_div = pivot_df / 1000  # 단위: 천 명
    pivot_df_div.plot(kind='area', stacked=True, ax=ax, colormap='tab20')

    ax.set_title("Stacked Area Plot of Regional Populations", fontsize=14)
    ax.set_xlabel("Year")
    ax.set_ylabel("Population (thousands)")
    ax.legend(title="Region", loc='upper left', bbox_to_anchor=(1.0, 1.0))
    ax.grid(True)

    st.pyplot(fig)

    st.subheader("Pivot Table Preview")
    st.dataframe(pivot_df_div.style.format("{:,.0f}"))
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

st.set_page_config(layout="wide")
st.title("Population Trends EDA Dashboard")

uploaded_file = st.file_uploader("Upload population_trends.csv", type="csv")

# 지역 영문 매핑
region_translation = {
    "서울": "Seoul", "부산": "Busan", "대구": "Daegu", "인천": "Incheon", "광주": "Gwangju",
    "대전": "Daejeon", "울산": "Ulsan", "세종": "Sejong", "경기": "Gyeonggi", "강원": "Gangwon",
    "충북": "Chungbuk", "충남": "Chungnam", "전북": "Jeonbuk", "전남": "Jeonnam", "경북": "Gyeongbuk",
    "경남": "Gyeongnam", "제주": "Jeju"
}

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # 공통 전처리
    df.replace("-", 0, inplace=True)
    df['연도'] = pd.to_numeric(df['연도'], errors='coerce')
    for col in ['인구', '출생아수(명)', '사망자수(명)']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    df['region_en'] = df['지역'].map(region_translation)

    # 탭 구성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Basic Statistics", "Trend by Year", "Analysis by Region",
        "Change Analysis", "Visualization"
    ])

    with tab1:
        st.header("Basic Statistics")
        st.subheader("DataFrame Info")
        buf = io.StringIO()
        df.info(buf=buf)
        st.text(buf.getvalue())

        st.subheader("Descriptive Statistics")
        st.dataframe(df.describe().style.format("{:,.0f}"))

    with tab2:
        st.header("National Population Trend and 2035 Projection")
        nat_df = df[df['지역'] == '전국'].copy()
        nat_df.sort_values(by='연도', inplace=True)
        recent = nat_df.tail(3)
        net = (recent['출생아수(명)'] - recent['사망자수(명)']).mean()
        last_pop = nat_df['인구'].iloc[-1]
        last_year = nat_df['연도'].iloc[-1]
        pred_2035 = last_pop + (2035 - last_year) * net

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(nat_df['연도'], nat_df['인구'], marker='o', label='Observed')
        ax.plot(2035, pred_2035, 'ro', label='Projected 2035')
        ax.annotate(f"{int(pred_2035):,}", (2035, pred_2035), textcoords="offset points", xytext=(-40,10), ha='center')
        ax.set_title("National Population Trend")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population")
        ax.legend()
        st.pyplot(fig)
        st.markdown(f"**Estimated population in 2035**: {int(pred_2035):,}")

    with tab3:
        st.header("5-Year Regional Population Change")
        non_nat = df[df['지역'] != '전국']
        recent_years = sorted(df['연도'].unique())[-5:]
        pivot = non_nat[non_nat['연도'].isin(recent_years)].pivot_table(index='지역', columns='연도', values='인구')
        change = pd.DataFrame()
        change['diff'] = (pivot[recent_years[-1]] - pivot[recent_years[0]]) / 1000
        change['rate'] = ((pivot[recent_years[-1]] - pivot[recent_years[0]]) / pivot[recent_years[0]]) * 100
        change['region'] = change.index.map(region_translation)
        change.sort_values('diff', ascending=False, inplace=True)

        fig1, ax1 = plt.subplots(figsize=(10, 7))
        sns.barplot(data=change, y='region', x='diff', ax=ax1, palette='coolwarm')
        for i, v in enumerate(change['diff']):
            ax1.text(v + 0.5, i, f"{v:.1f}", va='center')
        ax1.set_title("Population Change (Thousands)")
        ax1.set_xlabel("Change")
        st.pyplot(fig1)

        fig2, ax2 = plt.subplots(figsize=(10, 7))
        sns.barplot(data=change, y='region', x='rate', ax=ax2, palette='viridis')
        for i, v in enumerate(change['rate']):
            ax2.text(v + 0.5, i, f"{v:.1f}%", va='center')
        ax2.set_title("Population Growth Rate (%)")
        ax2.set_xlabel("Growth Rate")
        st.pyplot(fig2)

    with tab4:
        st.header("Top 100 Annual Population Changes")
        df_non_nat = df[df['지역'] != '전국'].copy()
        df_non_nat.sort_values(['지역', '연도'], inplace=True)
        df_non_nat['증감'] = df_non_nat.groupby('지역')['인구'].diff()
        change_abs = df_non_nat.dropna(subset=['증감']).copy()
        top100 = change_abs.assign(abs_change=lambda x: x['증감'].abs()).nlargest(100, 'abs_change')
        styled = top100[['연도', '지역', '인구', '증감']].copy()
        styled['인구'] = styled['인구'].map(lambda x: f"{int(x):,}")
        styled['증감'] = styled['증감'].map(lambda x: f"{int(float(x)):,}")
        df_for_style = top100[['연도', '지역', '인구', '증감']].copy()
        st.dataframe(df_for_style.style
                     .format({"인구": "{:,.0f}", "증감": "{:,.0f}"})
                     .background_gradient(subset='증감', cmap='RdBu_r',
                                          vmin=-df_for_style['증감'].abs().max(),
                                          vmax=df_for_style['증감'].abs().max()))

    with tab5:
        st.header("Stacked Area Chart by Region")
        pivot_area = df[df['지역'] != '전국'].pivot_table(
            index='연도', columns='region_en', values='인구', aggfunc='sum'
        ).fillna(0).sort_index()
        pivot_area /= 1000  # 단위: 천명
        fig, ax = plt.subplots(figsize=(12, 7))
        pivot_area.plot(kind='area', stacked=True, ax=ax, colormap='tab20')
        ax.set_title("Stacked Area Plot by Region")
        ax.set_xlabel("Year")
        ax.set_ylabel("Population (Thousands)")
        ax.legend(title="Region", loc='upper left', bbox_to_anchor=(1, 1))
        st.pyplot(fig)

else:
    st.warning("Please upload a valid CSV file.")
