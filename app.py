import streamlit as st
import random
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="논설문 평가 연습", layout="wide")
st.title("✍️ 논설문 평가 연습 프로그램 (SEP ME Web Edition)")

# 이미지 불러오기 함수
def load_image_from_url(url):
    response = requests.get(url)
    if response.status_code == 200 and "image" in response.headers.get("Content-Type", ""):
        return BytesIO(response.content)
    return None

# 텍스트 데이터 불러오기 함수
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

# 학생 글 표시 함수
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

# 세션 상태 초기화
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "current_text" not in st.session_state:
    st.session_state.current_text = None

# 과제 안내 이미지
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

# 모드 선택
mode = st.radio("연습 모드를 선택하세요", ["등급 추정 연습", "점수 추정 연습"])

# 상위 인지 점검 체크리스트
with st.expander("🧠 문제 풀이 전 상위 인지 점검 리스트"):
    st.markdown("""
    - ✅ 글의 **주제가 분명히** 드러났는가?
    - ✅ 자신의 **주장이 일관성 있게** 유지되었는가?
    - ✅ 제시한 **근거가 충분하고 타당한가?**
    - ✅ 글의 **구성과 전개가 자연스러운가?**
    - ✅ 문장 **표현이 명확하고 오류가 없는가?**
    """)

# 등급 추정 연습
if mode == "등급 추정 연습":
    st.subheader("🎯 [연습1] 학생 글의 등급 추정하기")
    texts = load_texts_from_github("grade")

    if not texts:
        st.error("❗ 텍스트를 불러올 수 없습니다.")
    else:
        if not st.session_state.current_text:
            st.session_state.current_text = random.choice(texts)

        selected = st.session_state.current_text
        text_id = selected[0].strip()
        correct_grade = int(selected[1].strip())
        student_text = "\n".join(selected[5:])

        st.markdown("#### 학생 글")
        render_student_text(student_text)

        user_grade = st.radio("예상 등급을 선택하세요", [1, 2, 3, 4, 5], horizontal=True)

        if not st.session_state.submitted:
            if st.button("제출", key="submit_grade"):
                st.session_state.submitted = True
                if user_grade == correct_grade:
                    st.success("✅ 정답입니다!")
                else:
                    st.error("❌ 오답입니다.")
                    img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_grade/{text_id}.png"
                    img_data = load_image_from_url(img_url)
                    if img_data:
                        st.image(img_data, caption="등급 평가 해설")
                    else:
                        st.warning(f"이미지를 불러올 수 없습니다: {img_url}")

        if st.session_state.submitted:
            if st.button("다음 문제로 이동", key="next_grade"):
                st.session_state.current_text = random.choice(texts)
                st.session_state.submitted = False

# 점수 추정 연습
else:
    st.subheader("🧩 [연습2] 내용·조직·표현 점수 추정하기")
    texts = load_texts_from_github("score")

    if not texts:
        st.error("❗ 텍스트를 불러올 수 없습니다.")
    else:
        if not st.session_state.current_text:
            st.session_state.current_text = random.choice(texts)

        selected = st.session_state.current_text
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

        if not st.session_state.submitted:
            if st.button("제출", key="submit_score"):
                st.session_state.submitted = True
                messages = []
                correct_all = True

                if abs(user_c - answer_c) <= 1:
                    messages.append("✅ 내용 점수: 정답")
                else:
                    messages.append("❌ 내용 점수: 오답")
                    correct_all = False

                if abs(user_o - answer_o) <= 1:
                    messages.append("✅ 조직 점수: 정답")
                else:
                    messages.append("❌ 조직 점수: 오답")
                    correct_all = False

                if abs(user_e - answer_e) <= 1:
                    messages.append("✅ 표현 점수: 정답")
                else:
                    messages.append("❌ 표현 점수: 오답")
                    correct_all = False

                for m in messages:
                    st.write(m)

                if correct_all:
                    st.success("🎉 모든 점수를 정확히 맞추셨습니다!")
                else:
                    st.error("📌 일부 점수가 오답입니다. 해설 이미지를 참고하세요.")
                    img_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/sep_6/f_score/{text_id}.png"
                    img_data = load_image_from_url(img_url)
                    if img_data:
                        st.image(img_data, caption="요소별 평가 해설")
                    else:
                        st.warning(f"이미지를 불러올 수 없습니다: {img_url}")

        if st.session_state.submitted:
            if st.button("다음 문제로 이동", key="next_score"):
                st.session_state.current_text = random.choice(texts)
                st.session_state.submitted = False
