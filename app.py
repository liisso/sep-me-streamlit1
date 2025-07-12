import streamlit as st
import os
import random
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="논설문 평가 연습", layout="wide")
st.title("✍️ 논설문 평가 연습 프로그램 (SEP ME Web Edition)")

# 이미지 로딩 함수
def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
        return BytesIO(response.content)
    else:
        st.warning(f"이미지를 불러올 수 없습니다: {url}")
        return None

# 텍스트 데이터 로딩
@st.cache_data
def load_texts_from_github(folder):
    base_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/{folder}/"
    file_list_url = f"https://api.github.com/repos/liisso/sep-me-streamlit1/contents/data/{folder}"
    try:
        file_list = requests.get(file_list_url).json()
        txts = []
        for f in file_list:
            if f["name"].endswith(".txt"):
                txt_url = base_url + f["name"]
                r = requests.get(txt_url)
                if r.status_code == 200:
                    lines = r.text.splitlines()
                    txts.append(lines)
        return txts
    except:
        return []

# HTML로 학생 글 출력
def render_student_text(text):
    st.markdown(
        f"""
        <div style="padding: 1rem; background-color: white; color: black;
                    border-radius: 8px; border: 1px solid lightgray;
                    font-family: 'Noto Sans KR', sans-serif;
                    white-space: pre-wrap; line-height: 1.6;">
            {text}
        </div>
        """,
        unsafe_allow_html=True
    )

# 과제 및 기준 이미지 안내
with st.expander("📑 쓰기 과제 및 평가 기준 보기"):
    imgs = {
        "쓰기 과제": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/assignment.png",
        "평가 기준": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/standard.png",
        "등급별 예시문": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/prompt.jpg"
    }
    for label, url in imgs.items():
        img_data = load_image_from_url(url)
        if img_data:
            st.image(img_data, caption=label)

# 연습 모드 선택
mode = st.radio("연습 모드를 선택하세요", ["등급 추정 연습", "점수 추정 연습"])

# [연습1] 등급 추정
if mode == "등급 추정 연습":
    st.subheader("🎯 [연습1] 학생 글의 등급 추정하기")

    texts = load_texts_from_github("grade")
    if not texts:
        st.error("❗ 등급 연습용 텍스트를 불러오지 못했습니다.")
    else:
        selected = random.choice(texts)
        text_id = selected[0].strip()
        correct_grade = int(selected[1].strip())
        student_text = "\n".join(selected[5:])

        st.markdown("#### 학생 글")
        render_student_text(student_text)

        user_grade = st.radio("예상 등급을 선택하세요 (1: 우수 ~ 5: 미흡)", [1, 2, 3, 4, 5], horizontal=True)
        if st.button("제출", key="grade_submit"):
            if user_grade == correct_grade:
                st.success("✅ 정답입니다! 정확하게 맞추셨습니다.")
            else:
                st.error("❌ 오답입니다. 아래 해설을 확인해 보세요.")
                img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_grade/{text_id}.png"
                img_data = load_image_from_url(img_url)
                if img_data:
                    st.image(img_data, caption="등급 평가 해설")

# [연습2] 점수 추정
else:
    st.subheader("🧩 [연습2] 내용·조직·표현 점수 추정하기")

    texts = load_texts_from_github("score")
    if not texts:
        st.error("❗ 점수 연습용 텍스트를 불러오지 못했습니다.")
    else:
        selected = random.choice(texts)
        text_id = selected[0].strip()
        answer_c = int(selected[2].strip())
        answer_o = int(selected[3].strip())
        answer_e = int(selected[4].strip())
        student_text = "\n".join(selected[5:])

        st.markdown("#### 학생 글")
        render_student_text(student_text)

        col1, col2, col3 = st.columns(3)
        with col1:
            user_c = st.number_input("내용 점수 (3~18)", min_value=3, max_value=18, step=1)
        with col2:
            user_o = st.number_input("조직 점수 (2~12)", min_value=2, max_value=12, step=1)
        with col3:
            user_e = st.number_input("표현 점수 (2~12)", min_value=2, max_value=12, step=1)

        if st.button("제출", key="score_submit"):
            result_msg = []
            correct_all = True

            if abs(user_c - answer_c) <= 1:
                result_msg.append("✅ 내용 점수: 정답")
            else:
                result_msg.append("❌ 내용 점수: 오답")
                correct_all = False

            if abs(user_o - answer_o) <= 1:
                result_msg.append("✅ 조직 점수: 정답")
            else:
                result_msg.append("❌ 조직 점수: 오답")
                correct_all = False

            if abs(user_e - answer_e) <= 1:
                result_msg.append("✅ 표현 점수: 정답")
            else:
                result_msg.append("❌ 표현 점수: 오답")
                correct_all = False

            for msg in result_msg:
                st.write(msg)

            if correct_all:
                st.success("🎉 모든 점수를 정확하게 추정하셨습니다!")
            else:
                st.error("📌 일부 점수가 오답입니다. 해설 이미지를 참고하세요.")
                img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_score/{text_id}.png"
                img_data = load_image_from_url(img_url)
                if img_data:
                    st.image(img_data, caption="요소별 평가 해설")
