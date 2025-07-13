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
    """세션 상태 초기화 함수"""
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
    """앱 재시작을 위한 상태 초기화"""
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
    
    # 입력값을 세션 상태에 저장
    st.session_state.user_name = name
    st.session_state.agreed = agreed

    if st.button("시작하기"):
        if not name.strip():
            st.warning("이름을 입력해야 시작할 수 있습니다.")
        elif not agreed:
            st.warning("개인정보 동의가 필요합니다.")
        else:
            st.session_state.step = 1
            st.rerun()

def practice_screen():
    st.subheader("✏️ [연습2] 글의 점수 추정하기")

    # 문제 URL 초기화
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

    # 모든 문제를 완료했으면 결과 화면으로
    if idx >= total:
        st.session_state.step = 2
        st.rerun()

    # 현재 문제 로드
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

    # 점수 입력 및 제출 전
    if not st.session_state.score_submitted:
        st.markdown("#### 각 영역별 점수를 입력하세요:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            uc = st.number_input("내용 점수", min_value=3, max_value=18, value=10, key=f"uc_{idx}")
        with col2:
            uo = st.number_input("조직 점수", min_value=2, max_value=12, value=7, key=f"uo_{idx}")
        with col3:
            ue = st.number_input("표현 점수", min_value=2, max_value=12, value=7, key=f"ue_{idx}")

        if st.button("제출", key=f"submit_{idx}"):
            st.session_state.uc = uc
            st.session_state.uo = uo
            st.session_state.ue = ue
            st.session_state.score_submitted = True
            st.rerun()
    
    # 점수 제출 후 결과 표시
    else:
        # 정답 여부 판정 (±1점 허용)
        is_c = abs(st.session_state.uc - c) <= 1
        is_o = abs(st.session_state.uo - o) <= 1
        is_e = abs(st.session_state.ue - e) <= 1

        st.markdown("#### 📊 채점 결과")
        
        # 결과를 표로 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("영역", "내용")
            st.metric("내 점수", st.session_state.uc)
            st.metric("정답", c)
            if is_c:
                st.success("✅ 정답")
            else:
                st.error("❌ 오답")
        
        with col2:
            st.metric("영역", "조직")
            st.metric("내 점수", st.session_state.uo)
            st.metric("정답", o)
            if is_o:
                st.success("✅ 정답")
            else:
                st.error("❌ 오답")
        
        with col3:
            st.metric("영역", "표현")
            st.metric("내 점수", st.session_state.ue)
            st.metric("정답", e)
            if is_e:
                st.success("✅ 정답")
            else:
                st.error("❌ 오답")
        
        with col4:
            total_score_user = st.session_state.uc + st.session_state.uo + st.session_state.ue
            total_score_answer = c + o + e
            st.metric("총점 (내)", total_score_user)
            st.metric("총점 (정답)", total_score_answer)
            if is_c and is_o and is_e:
                st.success("🎉 완벽!")
            else:
                st.warning("📚 학습 필요")

        # 전체 결과 판정
        if is_c and is_o and is_e:
            st.success("🎉 모든 요소 정답입니다!")
            result_text = f"{qnum}번 문항: 정답"
        else:
            st.error("📚 오답 항목이 있습니다. 아래 피드백을 참고하세요.")
            try:
                st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_score/{qnum}.png")
            except:
                st.warning("피드백 이미지를 불러올 수 없습니다.")
            result_text = f"{qnum}번 문항: 오답"

        # 결과 저장 (중복 방지)
        if result_text not in st.session_state.score_results:
            st.session_state.score_results.append(result_text)

        if st.button("다음 문제로", key=f"next_{idx}"):
            st.session_state.score_index += 1
            st.session_state.score_submitted = False
            st.session_state.uc = None
            st.session_state.uo = None
            st.session_state.ue = None
            st.rerun()

def result_screen():
    st.title("📊 점수 추정 연습 결과 요약")

    if st.session_state.score_results:
        # 정답/오답 개수 계산
        correct_count = len([r for r in st.session_state.score_results if "정답" in r])
        total_count = len(st.session_state.score_results)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # 요약 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 문항 수", total_count)
        with col2:
            st.metric("정답 수", correct_count)
        with col3:
            st.metric("정답률", f"{accuracy:.1f}%")
        
        st.markdown("### 📝 상세 결과")
        for r in st.session_state.score_results:
            if "정답" in r:
                st.markdown(f"✅ {r}")
            else:
                st.markdown(f"❌ {r}")
    else:
        st.info("결과가 없습니다.")

    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🏠 프로그램 종료하기"):
            reset_state()
            st.rerun()
    
    with col2:
        if st.button("🔄 다시 연습하기"):
            # 연습 관련 상태만 초기화
            st.session_state.step = 1
            st.session_state.score_urls = []
            st.session_state.score_index = 0
            st.session_state.score_results = []
            st.session_state.score_submitted = False
            st.session_state.uc = None
            st.session_state.uo = None
            st.session_state.ue = None
            st.rerun()

def main():
    st.set_page_config(page_title="SEP ME 6 - 점수 추정 모드", layout="wide")

    # 세션 상태 초기화
    initialize_session_state()

    # 단계별 화면 매핑
    steps = {
        0: start_screen,
        1: practice_screen,
        2: result_screen,
    }

    # 유효하지 않은 단계값 처리
    if st.session_state.step not in steps:
        st.warning("잘못된 단계 값입니다. 초기화합니다.")
        reset_state()
        st.rerun()

    # 현재 단계의 화면 실행
    steps[st.session_state.step]()

if __name__ == "__main__":
    main()
