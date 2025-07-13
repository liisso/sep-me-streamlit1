import streamlit as st
import requests
import random

def load_txt_from_url(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text.splitlines()

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

def get_score_file_urls():
    owner, repo, branch = "liisso", "sep-me-streamlit1", "main"
    folder = "data/scre"
    base_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{folder}/"
    files = fetch_github_file_list(owner, repo, branch, folder)
    return [base_url + f for f in files]

def initialize_session_state():
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = 15
    if 'score_urls' not in st.session_state:
        st.session_state.score_urls = []
    if 'score_index' not in st.session_state:
        st.session_state.score_index = 0
    if 'score_results' not in st.session_state:
        st.session_state.score_results = []
    if 'score_submitted' not in st.session_state:
        st.session_state.score_submitted = False
    if 'uc' not in st.session_state:
        st.session_state.uc = None
    if 'uo' not in st.session_state:
        st.session_state.uo = None
    if 'ue' not in st.session_state:
        st.session_state.ue = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'agreed' not in st.session_state:
        st.session_state.agreed = False

def reset_state():
    st.session_state.step = 0
    st.session_state.num_questions = 15
    st.session_state.score_urls = []
    st.session_state.score_index = 0
    st.session_state.score_results = []
    st.session_state.score_submitted = False
    st.session_state.uc = None
    st.session_state.uo = None
    st.session_state.ue = None
    st.session_state.user_name = ""
    st.session_state.agreed = False

def start_screen():
    st.title("📘 학생 글 채점 연습 프로그램 SEP ME 6 (점수 추정 모드)")

    name = st.text_input("이름을 입력하세요", value=st.session_state.user_name)
    agreed = st.checkbox("개인정보 수집 및 이용에 동의합니다.", value=st.session_state.agreed)
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
            return

def practice_screen():
    st.subheader("✏️ [연습2] 글의 점수 추정하기")

    if not st.session_state.score_urls:
        urls = get_score_file_urls()
        if not urls:
            st.error("scre 폴더 내 파일을 불러올 수 없습니다.")
            return
        random.shuffle(urls)
        st.session_state.score_urls = urls[:st.session_state.num_questions]
        st.session_state.score_index = 0
        st.session_state.score_results = []
        st.session_state.score_submitted = False
        st.session_state.uc = None
        st.session_state.uo = None
        st.session_state.ue = None

    idx = st.session_state.score_index
    total = st.session_state.num_questions

    if idx >= total:
        st.session_state.step = 2
        st.experimental_rerun()
        return

    url = st.session_state.score_urls[idx]
    try:
        lines = load_txt_from_url(url)
        qnum, c, o, e, text = parse_score_txt(lines)
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

        if st.button("제출", key=f"submit_{idx}"):
            st.session_state.uc = uc
            st.session_state.uo = uo
            st.session_state.ue = ue
            st.session_state.score_submitted = True
            st.experimental_rerun()
            return
    else:
        is_c = abs(st.session_state.uc - c) <= 1
        is_o = abs(st.session_state.uo - o) <= 1
        is_e = abs(st.session_state.ue - e) <= 1

        st.write(f"- 내용: {'정답' if is_c else '오답'}")
        st.write(f"- 조직: {'정답' if is_o else '오답'}")
        st.write(f"- 표현: {'정답' if is_e else '오답'}")

        if is_c and is_o and is_e:
            st.success("모든 요소 정답입니다!")
            result_text = f"{qnum}번 문항: 정답"
        else:
            st.error("오답 항목이 있습니다.")
            try:
                st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_score/{qnum}.png")
            except:
                st.warning("피드백 이미지를 불러올 수 없습니다.")
            result_text = f"{qnum}번 문항: 오답"

        if result_text not in st.session_state.score_results:
            st.session_state.score_results.append(result_text)

        if st.button("다음", key=f"next_{idx}"):
            st.session_state.score_index += 1
            st.session_state.score_submitted = False
            st.session_state.uc = None
            st.session_state.uo = None
            st.session_state.ue = None
            st.experimental_rerun()
            return

def result_screen():
    st.title("📊 점수 추정 연습 결과 요약")

    if st.session_state.score_results:
        for r in st.session_state.score_results:
            st.markdown(f"- {r}")
    else:
        st.info("결과가 없습니다.")

    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("프로그램 종료하기"):
            reset_state()
            st.experimental_rerun()
            return
    
    with col2:
        if st.button("다시 연습하기"):
            st.session_state.step = 1
            st.session_state.score_urls = []
            st.session_state.score_index = 0
            st.session_state.score_results = []
            st.session_state.score_submitted = False
            st.session_state.uc = None
            st.session_state.uo = None
            st.session_state.ue = None
            st.experimental_rerun()
            return

def main():
    st.set_page_config(page_title="SEP ME 6 - 점수 추정 모드", layout="wide")

    initialize_session_state()

    steps = {
        0: start_screen,
        1: practice_screen,
        2: result_screen,
    }

    if st.session_state.step not in steps:
        st.warning("잘못된 단계 값입니다. 초기화합니다.")
        reset_state()
        st.experimental_rerun()
        return

    steps[st.session_state.step]()

if __name__ == "__main__":
    main()
