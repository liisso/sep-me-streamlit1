import streamlit as st
import random
import requests
from io import BytesIO
from PIL import Image
import time
import pandas as pd
import io
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
        "grade_start_time": None,
        "score_start_time": None,
        "grade_results": [],
        "score_results": []
    }
    for key, value in default_keys.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session()

# --- 사이드바 ---
with st.sidebar:
    st.header("📌 진행 내역")
    st.write("사용자:", st.session_state.username or "(미입력)")
    st.write("현재 모드:", st.session_state.mode or "등급 추정 연습")
    current_text = st.session_state.current_text_grade if st.session_state.mode == "등급 추정 연습" else st.session_state.current_text_score
    st.write("현재 문항 번호:", current_text[0] if current_text else "(없음)")
    st.write("진행률:", f"{current_text[0]} / 15" if current_text else "(없음)")
    if st.button("◀ 이전 화면으로 이동"):
        st.session_state.page = "instructions"
        st.session_state.current_text_grade = None
        st.session_state.current_text_score = None
        st.session_state.submitted = False

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

# --- 결과 다운로드 기능 ---
grade_time = format_time(time.time() - st.session_state.grade_start_time) if st.session_state.grade_start_time else "-"
score_time = format_time(time.time() - st.session_state.score_start_time) if st.session_state.score_start_time else "-"

if (
    (st.session_state.score_results and st.session_state.current_text_score and int(st.session_state.current_text_score[0]) == 15) or
    (st.session_state.grade_results and st.session_state.current_text_grade and int(st.session_state.current_text_grade[0]) == 15)
):
    df_score = pd.DataFrame(st.session_state.score_results)
    df_grade = pd.DataFrame(st.session_state.grade_results)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        pd.DataFrame({
            "사용자명": [st.session_state.username],
            "등급 추정 소요 시간 (분:초)": [grade_time],
            "점수 추정 소요 시간 (분:초)": [score_time]
        }).to_excel(writer, index=False, sheet_name="연습 시간 요약")

        if not df_score.empty:
            df_score["총점 (정답)"] = df_score[["내용 점수 (정답)", "조직 점수 (정답)", "표현 점수 (정답)"]].sum(axis=1)
            df_score["총점 (입력)"] = df_score[[ "내용 점수 (입력)", "조직 점수 (입력)", "표현 점수 (입력)"]].sum(axis=1)
            df_score.to_excel(writer, index=False, sheet_name="점수 추정 결과")

        if not df_grade.empty:
            df_grade.to_excel(writer, index=False, sheet_name="등급 추정 결과")

    st.sidebar.download_button(
        label="📥 연습 결과 다운로드 (Excel)",
        data=buffer.getvalue(),
        file_name=f"{st.session_state.username}_평가결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
