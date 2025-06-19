import streamlit as st
import pyrebase
import time
import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------
# Firebase 설정
# ---------------------
firebase_config = {
    "apiKey": "AIzaSyCswFmrOGU3FyLYxwbNPTp7hvQxLfTPIZw",
    "authDomain": "sw-projects-49798.firebaseapp.com",
    "databaseURL": "https://sw-projects-49798-default-rtdb.firebaseio.com",
    "projectId": "sw-projects-49798",
    "storageBucket": "sw-projects-49798.firebasestorage.app",
    "messagingSenderId": "812186368395",
    "appId": "1:812186368395:web:be2f7291ce54396209d78e"
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
firestore = firebase.database()
storage = firebase.storage()

# ---------------------
# 세션 상태 초기화
# ---------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user_email = ""
    st.session_state.id_token = ""
    st.session_state.user_name = ""
    st.session_state.user_gender = "선택 안함"
    st.session_state.user_phone = ""
    st.session_state.profile_image_url = ""

# ---------------------
# 홈 페이지 클래스
# ---------------------
class Home:
    def __init__(self, login_page, register_page, findpw_page):
        st.title("🏠 Home")
        if st.session_state.get("logged_in"):
            st.success(f"{st.session_state.get('user_email')}님 환영합니다.")

        
        st.markdown("""
                ---
                **인구 데이터셋**  
                - 제공처: 구글 클래스룸 
                - 설명: 전국 인구수 관련 데이터  
                - 주요 변수:  
                  "기초 통계", "연도별 추이", "지역별 분석", "변화량 분석"
                """)

# ---------------------
# 로그인 페이지 클래스
# ---------------------
class Login:
    def __init__(self):
        st.title("🔐 로그인")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        if st.button("로그인"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.logged_in = True
                st.session_state.user_email = email
                st.session_state.id_token = user['idToken']

                user_info = firestore.child("users").child(email.replace(".", "_")).get().val()
                if user_info:
                    st.session_state.user_name = user_info.get("name", "")
                    st.session_state.user_gender = user_info.get("gender", "선택 안함")
                    st.session_state.user_phone = user_info.get("phone", "")
                    st.session_state.profile_image_url = user_info.get("profile_image_url", "")

                st.success("로그인 성공!")
                time.sleep(1)
                st.rerun()
            except Exception:
                st.error("로그인 실패")

# ---------------------
# 회원가입 페이지 클래스
# ---------------------
class Register:
    def __init__(self, login_page_url):
        st.title("📝 회원가입")
        email = st.text_input("이메일")
        password = st.text_input("비밀번호", type="password")
        name = st.text_input("성명")
        gender = st.selectbox("성별", ["선택 안함", "남성", "여성"])
        phone = st.text_input("휴대전화번호")

        if st.button("회원가입"):
            try:
                auth.create_user_with_email_and_password(email, password)
                firestore.child("users").child(email.replace(".", "_")).set({
                    "email": email,
                    "name": name,
                    "gender": gender,
                    "phone": phone,
                    "role": "user",
                    "profile_image_url": ""
                })
                st.success("회원가입 성공! 로그인 페이지로 이동합니다.")
                time.sleep(1)
                st.switch_page(login_page_url)
            except Exception:
                st.error("회원가입 실패")

# ---------------------
# 비밀번호 찾기 페이지 클래스
# ---------------------
class FindPassword:
    def __init__(self):
        st.title("🔎 비밀번호 찾기")
        email = st.text_input("이메일")
        if st.button("비밀번호 재설정 메일 전송"):
            try:
                auth.send_password_reset_email(email)
                st.success("비밀번호 재설정 이메일을 전송했습니다.")
                time.sleep(1)
                st.rerun()
            except:
                st.error("이메일 전송 실패")

# ---------------------
# 사용자 정보 수정 페이지 클래스
# ---------------------
class UserInfo:
    def __init__(self):
        st.title("👤 사용자 정보")

        email = st.session_state.get("user_email", "")
        new_email = st.text_input("이메일", value=email)
        name = st.text_input("성명", value=st.session_state.get("user_name", ""))
        gender = st.selectbox(
            "성별",
            ["선택 안함", "남성", "여성"],
            index=["선택 안함", "남성", "여성"].index(st.session_state.get("user_gender", "선택 안함"))
        )
        phone = st.text_input("휴대전화번호", value=st.session_state.get("user_phone", ""))

        uploaded_file = st.file_uploader("프로필 이미지 업로드", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            file_path = f"profiles/{email.replace('.', '_')}.jpg"
            storage.child(file_path).put(uploaded_file, st.session_state.id_token)
            image_url = storage.child(file_path).get_url(st.session_state.id_token)
            st.session_state.profile_image_url = image_url
            st.image(image_url, width=150)
        elif st.session_state.get("profile_image_url"):
            st.image(st.session_state.profile_image_url, width=150)

        if st.button("수정"):
            st.session_state.user_email = new_email
            st.session_state.user_name = name
            st.session_state.user_gender = gender
            st.session_state.user_phone = phone

            firestore.child("users").child(new_email.replace(".", "_")).update({
                "email": new_email,
                "name": name,
                "gender": gender,
                "phone": phone,
                "profile_image_url": st.session_state.get("profile_image_url", "")
            })

            st.success("사용자 정보가 저장되었습니다.")
            time.sleep(1)
            st.rerun()

# ---------------------
# 로그아웃 페이지 클래스
# ---------------------
class Logout:
    def __init__(self):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.id_token = ""
        st.session_state.user_name = ""
        st.session_state.user_gender = "선택 안함"
        st.session_state.user_phone = ""
        st.session_state.profile_image_url = ""
        st.success("로그아웃 되었습니다.")
        time.sleep(1)
        st.rerun()

# ---------------------
# EDA 페이지 클래스
# ---------------------
class EDA:
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


# ---------------------
# 페이지 객체 생성
# ---------------------
Page_Login    = st.Page(Login,    title="Login",    icon="🔐", url_path="login")
Page_Register = st.Page(lambda: Register(Page_Login.url_path), title="Register", icon="📝", url_path="register")
Page_FindPW   = st.Page(FindPassword, title="Find PW", icon="🔎", url_path="find-password")
Page_Home     = st.Page(lambda: Home(Page_Login, Page_Register, Page_FindPW), title="Home", icon="🏠", url_path="home", default=True)
Page_User     = st.Page(UserInfo, title="My Info", icon="👤", url_path="user-info")
Page_Logout   = st.Page(Logout,   title="Logout",  icon="🔓", url_path="logout")
Page_EDA      = st.Page(EDA,      title="EDA",     icon="📊", url_path="eda")

# ---------------------
# 네비게이션 실행
# ---------------------
if st.session_state.logged_in:
    pages = [Page_Home, Page_User, Page_Logout, Page_EDA]
else:
    pages = [Page_Home, Page_Login, Page_Register, Page_FindPW]

selected_page = st.navigation(pages)
selected_page.run()