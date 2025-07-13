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

def initialize_session_state():
    """세션 상태 초기화 함수"""
    if 'step' not in st.session_state:
        st.session_state.step = 0
    if 'num_questions' not in st.session_state:
        st.session_state.num_questions = 15
    if 'grade_urls' not in st.session_state:
        st.session_state.grade_urls = []
    if 'grade_index' not in st.session_state:
        st.session_state.grade_index = 0
    if 'grade_results' not in st.session_state:
        st.session_state.grade_results = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'user_choice' not in st.session_state:
        st.session_state.user_choice = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = ""
    if 'agreed' not in st.session_state:
        st.session_state.agreed = False

def reset_state():
    """앱 재시작을 위한 상태 초기화"""
    st.session_state.step = 0
    st.session_state.num_questions = 15
    st.session_state.grade_urls = []
    st.session_state.grade_index = 0
    st.session_state.grade_results = []
    st.session_state.submitted = False
    st.session_state.user_choice = None
    st.session_state.user_name = ""
    st.session_state.agreed = False

def start_screen():
    st.title("📘 학생 글 채점 연습 프로그램 SEP ME 6 (등급 추정 모드)")
    
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
            st.session_state.step = 1  # 과제 안내 단계로
            st.rerun()

def guide_screen():
    """📋 과제 및 평가 기준 안내 화면"""
    st.title("📋 쓰기 과제 및 평가 기준 안내")
    
    st.markdown("### 연습을 시작하기 전에 아래 내용을 확인해주세요!")
    
    # 탭으로 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📝 쓰기 과제", "📊 평가 기준", "📚 등급별 예시", "🧠 상위인지 점검"])
    
    with tab1:
        st.markdown("#### 📝 쓰기 과제")
        try:
            st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/assignment.png", 
                    caption="쓰기 과제 안내", use_column_width=True)
        except:
            st.error("과제 안내 이미지를 불러올 수 없습니다.")
    
    with tab2:
        st.markdown("#### 📊 평가 기준")
        try:
            st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/standard.png", 
                    caption="평가 기준 안내", use_column_width=True)
        except:
            st.error("평가 기준 이미지를 불러올 수 없습니다.")
    
    with tab3:
        st.markdown("#### 📚 등급별 예시 글")
        try:
            st.image("https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/prompt.jpg", 
                    caption="등급별 예시 글", use_column_width=True)
        except:
            st.error("예시 글 이미지를 불러올 수 없습니다.")
    
    with tab4:
        st.markdown("#### 🧠 상위인지 점검")
        st.markdown("**연습을 시작하기 전에 다음 항목들을 확인해보세요:**")
        
        # 등급 추정용 상위인지 점검 체크리스트
        metacognitive_items = [
            "쓰기 과제의 내용과 요구사항을 충분히 이해했다",
            "등급별 평가 기준과 특징을 숙지했다",
            "1등급부터 5등급까지의 차이점을 파악했다",
            "등급별 예시 글의 특징을 분석했다",
            "학생 글을 객관적으로 평가할 준비가 되었다"
        ]
        
        # 체크박스로 각 항목 확인
        checked_items = []
        for i, item in enumerate(metacognitive_items):
            checked = st.checkbox(item, key=f"meta_{i}")
            checked_items.append(checked)
        
        # 모든 항목 체크 여부 확인
        all_checked = all(checked_items)
        
        if all_checked:
            st.success("✅ 모든 항목을 확인했습니다! 연습을 시작할 준비가 되었습니다.")
        else:
            st.warning("⚠️ 모든 항목을 확인한 후 연습을 시작하는 것을 권장합니다.")
        
        # 추가 안내 메시지
        st.info("""
        **💡 상위인지 점검의 중요성:**
        - 자신의 학습 상태를 스스로 점검하는 능력을 기릅니다
        - 효과적인 채점을 위한 사전 준비를 도와줍니다
        - 학습 목표를 명확히 하고 집중력을 높입니다
        """)
    
    st.markdown("---")
    st.markdown("### 🎯 등급 추정 연습 안내")
    st.info("""
    **등급 추정 연습에서는:**
    - 학생이 작성한 글을 읽고 전체적인 등급을 추정합니다
    - **1등급 (최우수)부터 5등급 (미흡)까지** 5단계로 평가합니다
    - 각 등급별 특징과 기준을 바탕으로 종합적으로 판단합니다
    - 틀린 문항에 대해서는 상세한 피드백을 제공합니다
    """)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ 이전으로"):
            st.session_state.step = 0
            st.rerun()
    
    with col2:
        # 상위인지 점검 완료 여부에 따라 버튼 활성화
        if all_checked:
            if st.button("🚀 연습 시작하기"):
                st.session_state.step = 2  # 연습 단계로
                st.rerun()
        else:
            st.button("🚀 연습 시작하기", disabled=True, 
                     help="모든 상위인지 점검 항목을 확인해주세요")

def practice_screen():
    st.subheader("✏️ [연습1] 글의 등급 추정하기")

    # 문제 URL 초기화
    if not st.session_state.grade_urls:
        urls = get_grade_file_urls()
        if not urls:
            st.error("grade 폴더 내 파일을 불러올 수 없습니다.")
            return
        random.shuffle(urls)
        st.session_state.grade_urls = urls[:st.session_state.num_questions]
        st.session_state.grade_index = 0
        st.session_state.grade_results = []
        st.session_state.submitted = False
        st.session_state.user_choice = None

    idx = st.session_state.grade_index
    total = st.session_state.num_questions

    # 모든 문제를 완료했으면 결과 화면으로
    if idx >= total:
        st.session_state.step = 3  # 결과 화면으로
        st.rerun()

    # 현재 문제 로드
    url = st.session_state.grade_urls[idx]
    try:
        lines = load_txt_from_url(url)
        qnum, answer, text = parse_grade_txt(lines)
    except Exception as e:
        st.error(f"파일 파싱 중 오류 발생: {e}")
        return

    # 진행률 표시
    progress = (idx) / total
    st.progress(progress, text=f"진행률: {idx}/{total} ({progress*100:.1f}%)")

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

    # 등급 선택 및 제출 전
    if not st.session_state.submitted:
        st.markdown("#### 이 글의 등급을 선택하세요:")
        
        # 등급 설명과 함께 라디오 버튼
        grade_options = [
            "1등급 - 최우수 (내용이 매우 충실하고 조직과 표현이 뛰어남)",
            "2등급 - 우수 (내용이 충실하고 조직과 표현이 좋음)",
            "3등급 - 보통 (내용이 적절하고 조직과 표현이 무난함)",
            "4등급 - 미흡 (내용이 부족하고 조직과 표현에 문제가 있음)",
            "5등급 - 매우 미흡 (내용이 매우 부족하고 조직과 표현이 불량함)"
        ]
        
        choice = st.radio("예상 등급을 선택하세요:", grade_options, key=f"grade_{idx}")
        
        # 선택한 등급 번호 추출
        selected_grade = int(choice.split("등급")[0])
        
        if st.button("제출", key=f"submit_{idx}"):
            st.session_state.user_choice = selected_grade
            st.session_state.submitted = True
            st.rerun()
    
    # 등급 제출 후 결과 표시
    else:
        st.markdown("#### 📊 채점 결과")
        
        # 결과를 메트릭으로 표시
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("내가 선택한 등급", f"{st.session_state.user_choice}등급")
        
        with col2:
            st.metric("정답 등급", f"{answer}등급")
        
        with col3:
            if st.session_state.user_choice == answer:
                st.metric("결과", "정답", delta="✅")
            else:
                st.metric("결과", "오답", delta="❌")

        # 전체 결과 판정
        if st.session_state.user_choice == answer:
            st.success("🎉 정답입니다!")
            result_text = f"{qnum}번 문항: 정답"
        else:
            st.error("📚 오답입니다. 아래 피드백을 참고하세요.")
            
            # 등급별 상세 설명
            grade_descriptions = {
                1: "1등급: 내용이 매우 충실하고, 조직이 체계적이며, 표현이 정확하고 효과적입니다.",
                2: "2등급: 내용이 충실하고, 조직이 체계적이며, 표현이 대체로 정확합니다.",
                3: "3등급: 내용이 적절하고, 조직이 대체로 체계적이며, 표현이 무난합니다.",
                4: "4등급: 내용이 부족하고, 조직이 미흡하며, 표현에 문제가 있습니다.",
                5: "5등급: 내용이 매우 부족하고, 조직이 불분명하며, 표현이 부정확합니다."
            }
            
            st.info(f"**정답 해설:** {grade_descriptions[answer]}")
            
            try:
                st.image(f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/main/data/f_grade/{qnum}.png")
            except:
                st.warning("피드백 이미지를 불러올 수 없습니다.")
            
            result_text = f"{qnum}번 문항: 오답"

        # 결과 저장 (중복 방지)
        if result_text not in st.session_state.grade_results:
            st.session_state.grade_results.append(result_text)

        if st.button("다음 문제로", key=f"next_{idx}"):
            st.session_state.grade_index += 1
            st.session_state.submitted = False
            st.session_state.user_choice = None
            st.rerun()

def result_screen():
    st.title("📊 등급 추정 연습 결과 요약")

    if st.session_state.grade_results:
        # 정답/오답 개수 계산
        correct_count = len([r for r in st.session_state.grade_results if "정답" in r])
        total_count = len(st.session_state.grade_results)
        accuracy = (correct_count / total_count * 100) if total_count > 0 else 0
        
        # 요약 통계
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("총 문항 수", total_count)
        with col2:
            st.metric("정답 수", correct_count)
        with col3:
            st.metric("정답률", f"{accuracy:.1f}%")
        
        # 성취도에 따른 메시지
        if accuracy >= 80:
            st.success("🎉 우수한 성과입니다! 등급 추정 능력이 뛰어납니다.")
        elif accuracy >= 60:
            st.info("👍 양호한 성과입니다. 조금 더 연습하면 더 좋아질 것입니다.")
        else:
            st.warning("📚 더 많은 연습이 필요합니다. 평가 기준을 다시 확인해보세요.")
        
        st.markdown("### 📝 상세 결과")
        for r in st.session_state.grade_results:
            if "정답" in r:
                st.markdown(f"✅ {r}")
            else:
                st.markdown(f"❌ {r}")
    else:
        st.info("결과가 없습니다.")

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 과제 다시보기"):
            st.session_state.step = 1
            st.rerun()
    
    with col2:
        if st.button("🔄 다시 연습하기"):
            # 연습 관련 상태만 초기화
            st.session_state.step = 2
            st.session_state.grade_urls = []
            st.session_state.grade_index = 0
            st.session_state.grade_results = []
            st.session_state.submitted = False
            st.session_state.user_choice = None
            st.rerun()
    
    with col3:
        if st.button("🏠 프로그램 종료"):
            reset_state()
            st.rerun()

def main():
    st.set_page_config(page_title="SEP ME 6 - 등급 추정 모드", layout="wide")

    # 세션 상태 초기화
    initialize_session_state()

    # 단계별 화면 매핑 (단계 추가)
    steps = {
        0: start_screen,      # 시작 화면
        1: guide_screen,      # 과제 및 기준 안내 (새로 추가)
        2: practice_screen,   # 연습 화면
        3: result_screen,     # 결과 화면
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
