import streamlit as st
import requests
import random

def fetch_github_file_list(owner, repo, branch, folder):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{folder}?ref={branch}"
    res = requests.get(url)
    if res.status_code != 200:
        st.error(f"GitHub API 호출 실패: {res.status_code}")
        return []
    files = res.json()
    return [f["name"] for f in files if f["name"].endswith(".txt")]

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

def get_grade_file_urls():
    owner, repo, branch = "liisso", "sep-me-streamlit1", "main"
    folder = "data/grade"
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{folder}/"
    files = fetch_github_file_list(owner, repo, branch, folder)
    return [base_url + f for f in files]

def reset_state():
    st.session_state.clear()
    st.session_state.step = 0
    st.session_state.num_questions = 15
    st.session_state.grade_urls = []
    st.session_state.grade_index = 0
    st.session_state.grade_results = []
    st.session_state.submitted = False

def main():
    st.set_page_config(page_title="SEP ME 6 - 등급 추정 모드", layout="wide")

    if 'step' not in st.session_state:
        reset_state()

    if st.session_state.step == 0:
        start_screen()
    elif st.session_state.step == 1:
        practice_screen()
    elif st.session_state.step == 2:
        result_screen()
    else:
        st.error("알 수 없는 상태입니다. 초기화합니다.")
        reset_state()
        st.experimental_rerun()
        return

def start_screen():
    st.title("📘 학생 글 채점 연습 프로그램 SEP ME 6 (등급 추정 모드)")
    name = st.text_input("이름을 입력하세요", value=st.session_state.get('user_name', ''))
    agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다.", value=st.session_state.get('agreed', False))

    st.session_state.user_name = name
    st.session_state.agreed = agreed

    if st.button("시작하기"):
        if not name.strip():
            st.warning("이름을 입력하세요.")
        elif not agreed:
            st.warning("개인정보 수집 및 이용에 동의해주세요.")
        else:
            urls = get_grade_file_urls()
            if not urls:
                st.error("grade 폴더 내 파일을 불러올 수 없습니다.")
                return
            random.shuffle(urls)
            st.session_state.grade_urls = urls[:st.session_state.num_questions]
            st.session_state.grade_index = 0
            st.session_state.grade_results = []
            st.session_state.submitted = False
            st.session_state.step = 1
            st.experimental_rerun()
            return  # 중요!

def practice_screen():
    idx = st.session_state.grade_index
    total = st.session_state.num_questions

    if idx >= total:
        st.session_state.step = 2
        st.experimental_rerun()
        return  # 중요!

    url = st.session_state.grade_urls[idx]
    try:
        lines = load_txt_from_url(url)
        qnum, answer, text = parse_grade_txt(lines)
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
        choice = st.radio("예상 등급을 선택하세요:", ["1", "2", "3", "4", "5"], key=f"grade_{idx}")
        if st.button("제출", key=f"submit_{idx}"):
            st.session_state.user_choice = int(choice)
            st.session_state.submitted = True
            st.experimental_rerun()
            return  # 중요!
    else:
        if st.session_state.user_choice == answer:
            st.success("정답입니다!")
            if f"{qnum}번 문항: 정답" not in st.session_state.grade_results:
                st.session_state.grade_results.append(f"{qnum}번 문항: 정답")
        else:
            st.error("오답입니다. 아래 피드백을 참고하세요.")
            st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_grade/{qnum}.png")
            if f"{qnum}번 문항: 오답" not in st.session_state.grade_results:
                st.session_state.grade_results.append(f"{qnum}번 문항: 오답")

        if st.button("다음", key=f"next_{idx}"):
            st.session_state.grade_index += 1
            st.session_state.submitted = False
            st.experimental_rerun()
            return  # 중요!

def result_screen():
    st.subheader("✏️ 등급 추정 연습이 끝났습니다.")
    if st.session_state.grade_results:
        st.write("### 결과 요약")
        for r in st.session_state.grade_results:
            st.markdown(f"- {r}")
    else:
        st.info("결과가 없습니다.")

    if st.button("다시 시작하기"):
        reset_state()
        st.experimental_rerun()
        return  # 중요!

if __name__ == "__main__":
    main()

