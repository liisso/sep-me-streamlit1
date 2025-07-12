import streamlit as st
import os
import random
import requests
from io import BytesIO
from PIL import Image

# --- 설정 ---
st.set_page_config(page_title="논설문 평가 연습", layout="wide")
st.title("✍️ 논설문 평가 연습 프로그램 (SEP ME Web Edition)")

# --- 유틸 함수 ---
def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))

@st.cache_data
def load_texts_from_github(folder_name):
    # GitHub raw base URL
    base = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/{folder_name}/"
    txt_list = []
    for file in os.listdir(f"data/{folder_name}"):  # 파일명은 중요하지 않음
        if file.endswith(".txt"):
            url = base + file
            try:
                r = requests.get(url)
                lines = r.text.splitlines()
                txt_list.append(lines)
            except:
                continue
    return txt_list

# --- 이미지 안내 ---
with st.expander("📑 쓰기 과제 및 평가 기준 보기"):
    st.image(load_image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/assignment.png"), caption="쓰기 과제")
    st.image(load_image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/standard.png"), caption="쓰기 평가 기준")
    st.image(load_image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/prompt.jpg"), caption="등급별 예시문")

# --- 모드 선택 ---
mode = st.radio("연습 모드를 선택하세요", ["등급 추정 연습", "점수 추정 연습"])

# --- 등급 추정 연습 ---
if mode == "등급 추정 연습":
    st.subheader("🎯 [연습1] 학생 글의 등급 추정하기")
    texts = load_texts_from_github("grade")
    if len(texts) == 0:
        st.warning("등급 연습용 데이터를 불러오지 못했습니다.")
    else:
        selected = random.choice(texts)
        student_text = "\n".join(selected[5:])
        correct_grade = int(selected[1].strip())

        st.markdown("#### 학생 글")
        st.text_area("학생 글을 읽고 아래에서 등급을 선택하세요.", student_text, height=300)

        user_grade = st.radio("예상 등급을 선택하세요", [1, 2, 3, 4, 5], horizontal=True)
        if st.button("제출"):
            if user_grade == correct_grade:
                st.success("✅ 정답입니다! 정확하게 맞추셨습니다.")
            else:
                st.error("❌ 오답입니다. 아래 해설을 참고하세요.")
                img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_grade/{selected[0].strip()}.png"
                st.image(load_image(img_url), caption="정답 해설 이미지")

# --- 점수 추정 연습 ---
else:
    st.subheader("🧩 [연습2] 내용·조직·표현 점수 추정하기")
    texts = load_texts_from_github("score")
    if len(texts) == 0:
        st.warning("점수 연습용 데이터를 불러오지 못했습니다.")
    else:
        selected = random.choice(texts)
        student_text = "\n".join(selected[5:])
        c, o, e = int(selected[2]), int(selected[3]), int(selected[4])

        st.markdown("#### 학생 글")
        st.text_area("학생 글을 읽고 아래에 점수를 입력하세요.", student_text, height=300)

        sc_c = st.number_input("내용 점수 (3~18점)", min_value=3, max_value=18, step=1)
        sc_o = st.number_input("조직 점수 (2~12점)", min_value=2, max_value=12, step=1)
        sc_e = st.number_input("표현 점수 (2~12점)", min_value=2, max_value=12, step=1)

        if st.button("제출"):
            feedbacks = []
            if abs(sc_c - c) <= 1:
                feedbacks.append("✅ 내용 점수: 정답")
            else:
                feedbacks.append("❌ 내용 점수: 오답")

            if abs(sc_o - o) <= 1:
                feedbacks.append("✅ 조직 점수: 정답")
            else:
                feedbacks.append("❌ 조직 점수: 오답")

            if abs(sc_e - e) <= 1:
                feedbacks.append("✅ 표현 점수: 정답")
            else:
                feedbacks.append("❌ 표현 점수: 오답")

            for f in feedbacks:
                st.write(f)

            if all(["✅" in f for f in feedbacks]):
                st.success("🎉 모든 요소 점수를 정확하게 추정하셨습니다!")
            else:
                st.error("📌 일부 점수가 오답입니다. 해설 이미지를 참고하세요.")
                img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_score/{selected[0].strip()}.png"
                st.image(load_image(img_url), caption="정답 해설 이미지")
