# app.py
import streamlit as st
import requests
import random

# --- 유틸 함수들 ---
def load_txt_from_url(url):
    response = requests.get(url)
    return response.text.splitlines()

def parse_grade_txt(lines):
    return lines[0].strip(), int(lines[1].strip()), "\n".join(lines[5:]).strip()

def parse_score_txt(lines):
    return (lines[0].strip(), int(lines[2].strip()), int(lines[3].strip()), int(lines[4].strip()), "\n".join(lines[5:]).strip())

# --- 앱 실행 흐름 관리 ---
def main():
    st.set_page_config(page_title="SEP ME 6", layout="wide")

    if 'step' not in st.session_state:
        st.session_state.step = 0
        st.session_state.user_name = ""
        st.session_state.agreed = False
        st.session_state.mode = None
        st.session_state.num_questions = 3  # 기본 3문항

    steps = {
        0: show_start_screen,
        1: show_intro,
        2: show_mode_selection,
        3: show_metacognition_checklist,
        4: run_grade_practice,
        5: run_score_practice,
        6: show_summary_result
    }
    steps[st.session_state.step]()

# --- 화면 0: 이름 입력 ---
def show_start_screen():
    st.title("📘 학생 글 채점 연습 프로그램 SEP ME 6")
    st.session_state.user_name = st.text_input("이름을 입력하세요")
    st.session_state.num_questions = st.slider("연습 문항 수 설정", 1, 15, 3)
    st.session_state.agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다.")

    if st.button("시작하기"):
        if not st.session_state.user_name.strip():
            st.warning("이름을 입력해야 시작할 수 있습니다.")
        elif not st.session_state.agreed:
            st.warning("개인정보 동의가 필요합니다.")
        else:
            st.session_state.step = 1

# --- 화면 1: 과제/기준/예시문 ---
def show_intro():
    st.subheader("쓰기 과제 및 평가 기준 안내")
    with st.expander("📝 쓰기 과제 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/assignment.png")
    with st.expander("📊 평가 기준 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/standard.png")
    with st.expander("📄 예시문 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/prompt.jpg")
    if st.button("연습 유형 선택으로 이동"):
        st.session_state.step = 2

# --- 화면 2: 연습 유형 선택 ---
def show_mode_selection():
    st.subheader("연습 유형을 선택하세요")
    mode = st.radio("실시할 연습 모드 선택", ["등급 추정만 하기", "점수 추정만 하기", "두 연습 모두 하기"])
    if st.button("선택 완료"):
        if "등급" in mode:
            st.session_state.mode = "grade_only"
            st.session_state.step = 3
        elif "점수" in mode:
            st.session_state.mode = "score_only"
            st.session_state.step = 5
        else:
            st.session_state.mode = "both"
            st.session_state.step = 3

# --- 화면 3: 상위 인지 점검 ---
def show_metacognition_checklist():
    st.subheader("상위 인지 점검 항목")
    items = [
        "1. 평가 목적과 전략을 설정했나요?",
        "2. 평가 기준을 점검했나요?",
        "3. 예시문 특징을 파악했나요?",
        "4. 유사한 글 수준을 떠올렸나요?",
        "5. 일관되게 평가하고 있나요?",
        "6. 공정하고 객관적인 평가인가요?",
        "7. 평가 과정을 반성했나요?"
    ]
    checks = [st.checkbox(label) for label in items]
    if all(checks):
        if st.button("등급 추정 연습 시작"):
            st.session_state.step = 4

# --- 화면 4: 등급 추정 연습 ---
def run_grade_practice():
    st.subheader("✏️ [연습1] 글의 등급 추정하기")
    if 'grade_urls' not in st.session_state:
        base = "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/grade/"
        urls = [f"{base}{i}.txt" for i in range(1, 16)]
        random.shuffle(urls)
        st.session_state.grade_urls = urls[:st.session_state.num_questions]
        st.session_state.grade_index = 0
        st.session_state.grade_results = []

    idx = st.session_state.grade_index
    if idx >= st.session_state.num_questions:
        st.session_state.step = 5 if st.session_state.mode == "both" else 6
        return

    lines = load_txt_from_url(st.session_state.grade_urls[idx])
    q_num, answer, text = parse_grade_txt(lines)
    st.markdown(f"<div style='color:black; font-size:18px; white-space:pre-wrap'>{text}</div>", unsafe_allow_html=True)
    user = st.radio("예상 등급을 선택하세요:", ["1", "2", "3", "4", "5"], key=f"grade_{idx}")

    if st.button("제출", key=f"grade_submit_{idx}"):
        if int(user) == answer:
            st.success("정답입니다!")
            st.session_state.grade_results.append(f"{q_num}번 문항: 정답")
        else:
            st.error("오답입니다. 아래 피드백을 참고하세요.")
            st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_grade/{q_num}.png")
            st.session_state.grade_results.append(f"{q_num}번 문항: 오답")

        if st.button("다음", key=f"grade_next_{idx}"):
            st.session_state.grade_index += 1
            st.experimental_rerun()

# --- 화면 5: 점수 추정 연습 ---
def run_score_practice():
    st.subheader("✏️ [연습2] 글의 점수 추정하기")
    if 'score_urls' not in st.session_state:
        base = "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/scre/"
        urls = [f"{base}{i}.txt" for i in range(1, 16)]
        random.shuffle(urls)
        st.session_state.score_urls = urls[:st.session_state.num_questions]
        st.session_state.score_index = 0
        st.session_state.score_results = []

    idx = st.session_state.score_index
    if idx >= st.session_state.num_questions:
        st.session_state.step = 6
        return

    lines = load_txt_from_url(st.session_state.score_urls[idx])
    q_num, c, o, e, text = parse_score_txt(lines)
    st.markdown(f"<div style='color:black; font-size:18px; white-space:pre-wrap'>{text}</div>", unsafe_allow_html=True)

    uc = st.number_input("내용 점수 (3~18)", 3, 18, key=f"uc_{idx}")
    uo = st.number_input("조직 점수 (2~12)", 2, 12, key=f"uo_{idx}")
    ue = st.number_input("표현 점수 (2~12)", 2, 12, key=f"ue_{idx}")

    if st.button("제출", key=f"score_submit_{idx}"):
        is_c = abs(uc - c) <= 1
        is_o = abs(uo - o) <= 1
        is_e = abs(ue - e) <= 1

        st.write(f"- 내용: {'정답' if is_c else '오답'}")
        st.write(f"- 조직: {'정답' if is_o else '오답'}")
        st.write(f"- 표현: {'정답' if is_e else '오답'}")

        if is_c and is_o and is_e:
            st.success("모든 요소 정답입니다!")
            st.session_state.score_results.append(f"{q_num}번 문항: 정답")
        else:
            st.error("오답 항목이 있습니다.")
            st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_score/{q_num}.png")
            st.session_state.score_results.append(f"{q_num}번 문항: 오답")

        if st.button("다음", key=f"score_next_{idx}"):
            st.session_state.score_index += 1
            st.experimental_rerun()

# --- 화면 6: 결과 ---
def show_summary_result():
    st.title("📊 연습 결과 요약")
    if 'grade_results' in st.session_state:
        st.subheader("등급 추정 결과")
        for r in st.session_state.grade_results:
            st.markdown(f"- {r}")
    if 'score_results' in st.session_state:
        st.subheader("점수 추정 결과")
        for r in st.session_state.score_results:
            st.markdown(f"- {r}")
    st.success("연습을 완료했습니다! 수고하셨습니다.")

if __name__ == "__main__":
    main()
