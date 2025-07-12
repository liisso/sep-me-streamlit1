import streamlit as st
import random
import requests
from io import BytesIO
from PIL import Image
import time
from datetime import timedelta

st.set_page_config(page_title="논설문 평가 연습", layout="wide")

# --- 세션 상태 초기화 ---
def init_session():
    default_keys = {
        "username": None,
        "mode": None,
        "submitted": False,
        "page": "intro",
        "current_text_grade": None,
        "current_text_score": None,
        "next_trigger": False,
        "grade_results": [],
        "score_results": []
    }
    for key, value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# --- 유틸 함수 ---
def load_image_from_url(url):
    r = requests.get(url)
    if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
        return BytesIO(r.content)
    return None

def load_texts_from_github(folder):
    base_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/{folder}/"
    api_url = f"https://api.github.com/repos/liisso/sep-me-streamlit1/contents/data/{folder}"
    try:
        res = requests.get(api_url).json()
        return [r.text.splitlines() for f in res if f['name'].endswith('.txt') and (r := requests.get(base_url + f['name'])).status_code == 200]
    except:
        return []

def format_time(seconds):
    return str(timedelta(seconds=int(seconds))) if isinstance(seconds, (int, float)) else "-"

# --- 사이드바 ---
with st.sidebar:
    st.header("📌 진행 내역")
    st.write("사용자:", st.session_state.username or "(미입력)")
    st.write("현재 모드:", st.session_state.mode or "(선택 전)")
    current_text = st.session_state.current_text_grade if st.session_state.mode == "등급 추정 연습" else st.session_state.current_text_score
    st.write("현재 문항 번호:", current_text[0] if current_text else "(없음)")
    st.write("진행률:", f"{current_text[0]} / 15" if current_text else "(없음)")
    if st.button("◀ 이전 화면으로 이동"):
        st.session_state.page = "instructions"
        st.session_state.current_text_grade = None
        st.session_state.current_text_score = None
        st.session_state.submitted = False

# --- 화면 구성 ---
if st.session_state.page == "intro":
    st.title("📝 논설문 평가 연습 프로그램")
    st.subheader("이름을 입력하고 개인정보 제공에 동의해주세요.")
    with st.form("user_form"):
        name = st.text_input("이름을 입력하세요")
        agree = st.checkbox("입력한 이름은 평가 결과 저장에 사용될 수 있음에 동의합니다.")
        submitted = st.form_submit_button("연습 시작하기")
        if submitted:
            if name and agree:
                st.session_state.username = name
                st.session_state.page = "instructions"
            else:
                st.warning("이름을 입력하고 동의란에 체크해주세요.")

elif st.session_state.page == "instructions":
    st.header("🗂 쓰기 과제 및 평가 기준 안내")
    st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/assignment.png")
    st.markdown("""
    - **등급 추정 연습**: 글을 읽고 전체적인 완성도를 고려하여 등급(A~D)을 추정합니다.  
    - **점수 추정 연습**: 글의 세 영역(내용, 조직, 표현)을 각각 5점 만점 기준으로 평가합니다.
    """)
    if st.button("등급 추정 연습 시작하기"):
        st.session_state.mode = "등급 추정 연습"
        st.session_state.page = "practice"
    if st.button("점수 추정 연습 시작하기"):
        st.session_state.mode = "점수 추정 연습"
        st.session_state.page = "practice"

elif st.session_state.page == "practice":
    folder = "grade" if st.session_state.mode == "등급 추정 연습" else "scre"
    texts = load_texts_from_github(folder)
    texts = sorted(texts, key=lambda x: int(x[0].strip()))

    if st.session_state.mode == "등급 추정 연습":
        current = st.session_state.current_text_grade or next((t for t in texts if int(t[0].strip()) == 1), None)
    else:
        current = st.session_state.current_text_score or next((t for t in texts if int(t[0].strip()) == 1), None)

    if not current:
        st.info("📂 문항을 불러올 수 없습니다.")
    else:
        q_num = int(current[0].strip())
        if st.session_state.mode == "등급 추정 연습":
            answer = current[1].strip()
            st.session_state.current_text_grade = current
        else:
            a_c, a_o, a_e = map(int, current[2:5])
            st.session_state.current_text_score = current

        st.subheader(f"✍ 문항 {q_num}")
        st.markdown("<div style='color: black; font-size: 1.1em;'>" + "\n".join(current[5:]) + "</div>", unsafe_allow_html=True)

        if st.session_state.mode == "등급 추정 연습":
            sel = st.radio("예상 등급을 선택하세요", ["A", "B", "C", "D"], horizontal=True)
            if st.button("제출하기", key=f"submit_{q_num}"):
                st.session_state.submitted = True
                if sel == answer:
                    st.success("✅ 정답입니다!")
                else:
                    st.error("❌ 오답입니다.")
                    image_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/f_grade/{q_num}.png"
                    img_data = load_image_from_url(image_url)
                    if img_data:
                        st.image(Image.open(img_data), caption="피드백 참고 이미지")
            if st.session_state.submitted:
                if st.button("다음 문제로 이동", key=f"next_{q_num}"):
                    next_q = next((t for t in texts if int(t[0].strip()) == q_num + 1), None)
                    if next_q:
                        st.session_state.current_text_grade = next_q
                        st.session_state.submitted = False
                        st.experimental_rerun()
                    else:
                        st.success("🎉 모든 문항을 완료했습니다.")
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                c = st.number_input("내용 점수", min_value=0, max_value=5, step=1, key=f"c_{q_num}")
            with col2:
                o = st.number_input("조직 점수", min_value=0, max_value=5, step=1, key=f"o_{q_num}")
            with col3:
                e = st.number_input("표현 점수", min_value=0, max_value=5, step=1, key=f"e_{q_num}")
            if st.button("제출하기", key=f"submit_score_{q_num}"):
                st.session_state.submitted = True
                if (c, o, e) == (a_c, a_o, a_e):
                    st.success("✅ 정답입니다!")
                else:
                    st.error("❌ 오답입니다.")
                    image_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/f_score/{q_num}.png"
                    img_data = load_image_from_url(image_url)
                    if img_data:
                        st.image(Image.open(img_data), caption="피드백 참고 이미지")
            if st.session_state.submitted:
                if st.button("다음 문제로 이동", key=f"next_score_{q_num}"):
                    next_q = next((t for t in texts if int(t[0].strip()) == q_num + 1), None)
                    if next_q:
                        st.session_state.current_text_score = next_q
                        st.session_state.submitted = False
                        st.experimental_rerun()
                    else:
                        st.success("🎉 모든 문항을 완료했습니다.")
