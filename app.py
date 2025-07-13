import streamlit as st
import requests
import random

def load_txt_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

def parse_grade_txt(lines):
    if len(lines) < 6:
        raise ValueError("파일 형식 오류: 6행 이상 필요")
    qnum = lines[0].strip()
    answer = int(lines[1].strip())
    text = "\n".join(lines[5:]).strip()
    return qnum, answer, text

def parse_score_txt(lines):
    if len(lines) < 6:
        raise ValueError("파일 형식 오류: 6행 이상 필요")
    qnum = lines[0].strip()
    content = int(lines[2].strip())
    organization = int(lines[3].strip())
    expression = int(lines[4].strip())
    text = "\n".join(lines[5:]).strip()
    return qnum, content, organization, expression, text

def fetch_github_file_list(owner, repo, branch, folder):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}?ref={branch}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"GitHub API 호출 실패: {res.status_code}")
        return []
    files = res.json()
    return [f["name"] for f in files if f["name"].endswith(".txt")]

def get_grade_file_urls():
    owner, repo, branch = "liisso", "sep-me-streamlit1", "main"
    folder = "data/grade"
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{folder}/"
    files = fetch_github_file_list(owner, repo, branch, folder)
    return [base_url + f for f in files]

def get_score_file_urls():
    owner, repo, branch = "liisso", "sep-me-streamlit1", "main"
    folder = "data/scre"
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{folder}/"
    files = fetch_github_file_list(owner, repo, branch, folder)
    return [base_url + f for f in files]

def reset_states():
    st.session_state.clear()
    st.session_state.step = 0
    st.session_state.num_questions = 15

def main():
    st.set_page_config(page_title="SEP ME 6", layout="wide")

    if 'step' not in st.session_state:
        reset_states()

    steps = {
        0: start_screen,
        1: intro_screen,
        2: mode_selection_screen,
        3: metacognition_checklist_screen,
        4: grade_practice_screen,
        5: score_practice_screen,
        6: summary_screen,
        7: grade_end_screen,
        8: score_end_screen,
    }

    if st.session_state.step not in steps:
        st.warning("잘못된 단계 값. 초기화 합니다.")
        reset_states()
        return

    steps[st.session_state.step]()

def start_screen():
    st.title("📘 학생 글 채점 연습 프로그램 SEP ME 6")
    name = st.text_input("이름을 입력하세요", value=st.session_state.get('user_name', ''))
    agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다.", value=st.session_state.get('agreed', False))
    st.session_state.user_name = name
    st.session_state.agreed = agreed

    if st.button("시작하기"):
        if not name.strip():
            st.warning("이름을 입력해야 시작할 수 있습니다.")
        elif not agreed:
            st.warning("개인정보 동의가 필요합니다.")
        else:
            st.session_state.step = 1
            st.experimental_rerun()

def intro_screen():
    st.subheader("쓰기 과제 및 평가 기준 안내")
    with st.expander("📝 쓰기 과제 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/assignment.png")
    with st.expander("📊 평가 기준 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/standard.png")
    with st.expander("📄 예시문 보기"):
        st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/prompt.jpg")
    if st.button("연습 유형 선택으로 이동"):
        st.session_state.step = 2
        st.experimental_rerun()

def mode_selection_screen():
    st.subheader("연습 유형을 선택하세요")
    mode = st.radio("실시할 연습 모드 선택", ["등급 추정만 하기", "점수 추정만 하기", "두 연습 모두 하기"], index=0)
    st.session_state.mode = mode
    if st.button("선택 완료"):
        if mode == "등급 추정만 하기":
            st.session_state.step = 3
        elif mode == "점수 추정만 하기":
            st.session_state.step = 5
        else:
            st.session_state.step = 3
        st.experimental_rerun()

def metacognition_checklist_screen():
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
    checks = [st.checkbox(item, key=f"chk{i}") for i, item in enumerate(items)]
    if all(checks):
        if st.button("등급 추정 연습 시작"):
            st.session_state.grade_urls = []
            st.session_state.score_urls = []
            st.session_state.grade_index = 0
            st.session_state.score_index = 0
            st.session_state.grade_results = []
            st.session_state.score_results = []
            st.session_state.submitted = False
            st.session_state.score_submitted = False
            st.session_state.step = 4
            st.experimental_rerun()

def grade_practice_screen():
    st.subheader("✏️ [연습1] 글의 등급 추정하기")

    if not st.session_state.get('grade_urls'):
        urls = get_grade_file_urls()
        if not urls:
            st.error("grade 폴더 내 파일을 불러올 수 없습니다.")
            return
        random.shuffle(urls)
        st.session_state.grade_urls = urls[:st.session_state.num_questions]
        st.session_state.grade_index = 0
        st.session_state.grade_results = []
        st.session_state.submitted = False

    idx = st.session_state.grade_index
    total = st.session_state.num_questions

    if idx >= total:
        if st.session_state.mode == "두 연습 모두 하기":
            st.session_state.step = 5  # 점수 연습 시작
        else:
            st.session_state.step = 7  # 등급 연습 종료 화면
        st.experimental_rerun()
        return

    lines = load_txt_from_url(st.session_state.grade_urls[idx])
    try:
        q_num, answer, text = parse_grade_txt(lines)
    except Exception as e:
        st.error(f"파일 파싱 중 오류 발생: {e}")
        return

    st.markdown(f"### 문항 {idx + 1} / {total}")
    st.markdown(f"""<div style="
        background-color: white;
        color: black;
        font-size: 18px;
        white-space: pre-wrap;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
        ">{text}</div>""", unsafe_allow_html=True)

    if not st.session_state.submitted:
        user_choice = st.radio("예상 등급을 선택하세요:", ["1", "2", "3", "4", "5"], key=f"grade_{idx}")
        if st.button("제출", key=f"grade_submit_{idx}"):
            st.session_state.user_choice = int(user_choice)
            st.session_state.submitted = True
    else:
        if st.session_state.user_choice == answer:
            st.success("정답입니다!")
            if f"{q_num}번 문항: 정답" not in st.session_state.grade_results:
                st.session_state.grade_results.append(f"{q_num}번 문항: 정답")
        else:
            st.error("오답입니다. 아래 피드백을 참고하세요.")
            st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_grade/{q_num}.png")
            if f"{q_num}번 문항: 오답" not in st.session_state.grade_results:
                st.session_state.grade_results.append(f"{q_num}번 문항: 오답")

        if st.button("다음", key=f"grade_next_{idx}"):
            st.session_state.grade_index += 1
            st.session_state.submitted = False
            st.experimental_rerun()

def score_practice_screen():
    st.subheader("✏️ [연습2] 글의 점수 추정하기")

    if not st.session_state.get('score_urls'):
        urls = get_score_file_urls()
        if not urls:
            st.error("scre 폴더 내 파일을 불러올 수 없습니다.")
            return
        random.shuffle(urls)
        st.session_state.score_urls = urls[:st.session_state.num_questions]
        st.session_state.score_index = 0
        st.session_state.score_results = []
        st.session_state.score_submitted = False

    idx = st.session_state.score_index
    total = st.session_state.num_questions

    if idx >= total:
        st.session_state.step = 8
        st.experimental_rerun()
        return

    lines = load_txt_from_url(st.session_state.score_urls[idx])
    try:
        q_num, c, o, e, text = parse_score_txt(lines)
    except Exception as ex:
        st.error(f"파일 파싱 중 오류 발생: {ex}")
        return

    st.markdown(f"### 문항 {idx + 1} / {total}")
    st.markdown(f"""<div style="
        background-color: white;
        color: black;
        font-size: 18px;
        white-space: pre-wrap;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 0 5px rgba(0,0,0,0.1);
        ">{text}</div>""", unsafe_allow_html=True)

    if not st.session_state.score_submitted:
        uc = st.number_input("내용 점수 (3~18)", 3, 18, key=f"uc_{idx}")
        uo = st.number_input("조직 점수 (2~12)", 2, 12, key=f"uo_{idx}")
        ue = st.number_input("표현 점수 (2~12)", 2, 12, key=f"ue_{idx}")
        if st.button("제출", key=f"score_submit_{idx}"):
            st.session_state.uc = uc
            st.session_state.uo = uo
            st.session_state.ue = ue
            st.session_state.score_submitted = True
    else:
        is_c = abs(st.session_state.uc - c) <= 1
        is_o = abs(st.session_state.uo - o) <= 1
        is_e = abs(st.session_state.ue - e) <= 1

        st.write(f"- 내용: {'정답' if is_c else '오답'}")
        st.write(f"- 조직: {'정답' if is_o else '오답'}")
        st.write(f"- 표현: {'정답' if is_e else '오답'}")

        if is_c and is_o and is_e:
            st.success("모든 요소 정답입니다!")
            if f"{q_num}번 문항: 정답" not in st.session_state.score_results:
                st.session_state.score_results.append(f"{q_num}번 문항: 정답")
        else:
            st.error("오답 항목이 있습니다.")
            st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_score/{q_num}.png")
            if f"{q_num}번 문항: 오답" not in st.session_state.score_results:
                st.session_state.score_results.append(f"{q_num}번 문항: 오답")

        if st.button("다음", key=f"score_next_{idx}"):
            st.session_state.score_index += 1
            st.session_state.score_submitted = False
            st.experimental_rerun()

def grade_end_screen():
    st.subheader("✏️ [연습1] 등급 추정 연습이 끝났습니다.")
    if st.session_state.grade_results:
        st.write("### 결과 요약")
        for r in st.session_state.grade_results:
            st.markdown(f"- {r}")
    else:
        st.info("결과가 없습니다.")

    if st.button("연습 모드 선택하기"):
        st.session_state.step = 2
        st.experimental_rerun()

    if st.button("프로그램 종료하기"):
        reset_states()
        st.experimental_rerun()

def score_end_screen():
    st.subheader("✏️ [연습2] 점수 추정 연습이 끝났습니다.")
    if st.session_state.score_results:
        st.write("### 결과 요약")
        for r in st.session_state.score_results:
            st.markdown(f"- {r}")
    else:
        st.info("결과가 없습니다.")

    if st.button("연습 모드 선택하기"):
        st.session_state.step = 2
        st.experimental_rerun()

    if st.button("프로그램 종료하기"):
        reset_states()
        st.experimental_rerun()

def summary_screen():
    st.title("📊 연습 결과 요약")
    if st.session_state.grade_results:
        st.subheader("등급 추정 결과")
        for r in st.session_state.grade_results:
            st.markdown(f"- {r}")
    else:
        st.info("등급 추정 연습 결과가 없습니다.")
    if st.session_state.score_results:
        st.subheader("점수 추정 결과")
        for r in st.session_state.score_results:
            st.markdown(f"- {r}")
    else:
        st.info("점수 추정 연습 결과가 없습니다.")

    if st.button("다른 연습 모드 선택하러 가기"):
        st.session_state.step = 2
        st.experimental_rerun()

if __name__ == "__main__":
    main()
