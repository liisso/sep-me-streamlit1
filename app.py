import streamlit as st
import os
import glob
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="SEP ME ver.6", page_icon="📝", layout="wide")

# ========== 경로 진단 ==========
# ========== 데이터 로딩 ==========
def load_student_texts(folder, type_):
    samples = []
    files = sorted([f for f in os.listdir(folder) if f.endswith('.txt')])
    for fname in files:
        path = os.path.join(folder, fname)
        lines = None
        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(path, encoding=encoding) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        if lines and len(lines) >= 6:
            try:
                qnum = int(lines[0].strip())
                grade = int(lines[1].strip())
                content = int(lines[2].strip())
                org = int(lines[3].strip())
                expr = int(lines[4].strip())
                text = ''.join(lines[5:]).strip()
                if text:
                    samples.append({
                        'question_num': qnum,
                        'text': text,
                        'correct_grade': grade,
                        'content_score': content,
                        'organization_score': org,
                        'expression_score': expr,
                        'type': type_,
                        'filename': fname
                    })
            except Exception:
                continue
    samples.sort(key=lambda x: x['question_num'])
    return samples

def load_all_data():
    grade_samples = load_student_texts("data/grade", "grade")
    score_samples = load_student_texts("data/score", "score")
    return grade_samples, score_samples

def get_feedback_image_path(kind, question_num):
    path = f"data/f_{kind}/{question_num}.png"
    return path if os.path.exists(path) else None

def initialize_session_state():
    if 'stage' not in st.session_state:
        st.session_state.stage = 'intro'
        st.session_state.user_name = ''
        st.session_state.selected_practice = None
        st.session_state.current_idx = 0
        st.session_state.practice1_results = []
        st.session_state.practice2_results = []
        st.session_state.start_time = datetime.now()
        st.session_state.grade_samples = []
        st.session_state.score_samples = []

# ========== UI 함수 ==========
def show_intro_page():
    st.title("🎯 SEP ME ver.6")
    st.subheader("학생 글 채점 연습 프로그램")
    st.markdown("""
    **SEP ME**는 학생 글 채점 능력 향상을 위한 AI 기반 학습 도구입니다.
    실제 학생들이 작성한 글을 바탕으로 채점 연습을 할 수 있습니다.
    """)
    with st.form("user_info"):
        name = st.text_input("이름을 입력해주세요:", placeholder="홍길동")
        agreement = st.checkbox("개인정보 수집 및 이용에 동의합니다 (학습 목적)")
        if st.form_submit_button("학습 시작하기", type="primary"):
            if name and agreement:
                st.session_state.user_name = name
                st.session_state.stage = 'assignment_info'
                st.rerun()
            else:
                st.error("이름과 동의 체크를 모두 해주세요.")

def show_assignment_info():
    st.title("📋 쓰기 과제 및 평가 기준")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 쓰기 과제")
        if os.path.exists("data/assignment.png"):
            st.image("data/assignment.png", caption="쓰기 과제")
    with col2:
        st.subheader("📊 평가 기준")
        if os.path.exists("data/standard.png"):
            st.image("data/standard.png", caption="평가 기준")
    st.subheader("🎯 등급 기준")
    grade_df = pd.DataFrame({
        '등급': ['1등급', '2등급', '3등급', '4등급', '5등급'],
        '점수 범위': ['29-33점', '27-28점', '24-26점', '20-23점', '13-19점'],
        '수준': ['매우 우수', '우수', '보통', '미흡', '매우 미흡']
    })
    st.table(grade_df)
    with st.form("checklist"):
        st.markdown("**상위 인지 요소 점검**")
        checks = []
        checks.append(st.checkbox("1. 학생 글을 평가하는 목적을 설정하고 평가 전략을 세웠다."))
        checks.append(st.checkbox("2. 쓰기 과제 및 평가 기준을 확인하고 변별 방법을 점검했다."))
        checks.append(st.checkbox("3. 평가 기준을 고려하여 예시문의 특징을 정확히 파악했다."))
        checks.append(st.checkbox("4. 평가 기준에 적합한 학생 글의 예를 머릿속으로 떠올렸다."))
        checks.append(st.checkbox("5. 학생 글을 일관되게 평가할 것을 다짐했다."))
        checks.append(st.checkbox("6. 학생 글을 공정하고 객관적으로 평가할 것을 다짐했다."))
        checks.append(st.checkbox("7. 평가 과정과 결과를 반성적으로 점검할 것을 다짐했다."))
        if st.form_submit_button("다음 단계로 →", type="primary"):
            if all(checks):
                st.session_state.stage = 'practice_selection'
                st.session_state.grade_samples, st.session_state.score_samples = load_all_data()
                st.session_state.current_idx = 0
                st.rerun()
            else:
                st.warning("모든 항목을 체크해주세요.")

def show_practice_selection():
    st.title("🎯 연습 유형 선택")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📚 연습1: 등급 추정")
        if st.button("연습1 시작", type="primary"):
            st.session_state.selected_practice = 'practice1'
            st.session_state.stage = 'practice1'
            st.session_state.current_idx = 0
            st.rerun()
    with col2:
        st.markdown("#### 📊 연습2: 점수 추정")
        if st.button("연습2 시작", type="primary"):
            st.session_state.selected_practice = 'practice2'
            st.session_state.stage = 'practice2'
            st.session_state.current_idx = 0
            st.rerun()

def show_practice1():
    samples = st.session_state.grade_samples
    idx = st.session_state.current_idx
    st.title("📚 연습1: 글의 등급 추정하기")
    st.progress(idx / len(samples))
    st.markdown(f"**진행 상황: {idx+1}/{len(samples)} 문제**")
    current_sample = samples[idx]
    st.markdown(f"""
    <div style="
        background-color: #f8f9fa;
        color: #222;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
    ">
    <strong>문제 {idx+1}번</strong> (문제번호: {current_sample['question_num']})<br><br>
    {current_sample['text']}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### 🎯 이 글의 등급을 선택하세요")
    cols = st.columns(5)
    selected_grade = None
    for i, grade in enumerate([1,2,3,4,5]):
        with cols[i]:
            if st.button(f"{grade}등급", key=f"grade_{grade}_{idx}"):
                selected_grade = grade
    if selected_grade is not None:
        is_correct = selected_grade == current_sample['correct_grade']
        st.write(f"정답: {current_sample['correct_grade']}등급, 선택: {selected_grade}등급")
        feedback_path = get_feedback_image_path('grade', current_sample['question_num'])
        if feedback_path:
            st.image(feedback_path, caption=f"문제 {current_sample['question_num']}번 피드백")
        if idx < len(samples) - 1:
            if st.button("다음 문제 →"):
                st.session_state.current_idx += 1
                st.rerun()
        else:
            if st.button("결과 보기 →"):
                st.session_state.stage = 'results'
                st.rerun()

def show_practice2():
    samples = st.session_state.score_samples
    idx = st.session_state.current_idx
    st.title("📊 연습2: 글의 점수 추정하기")
    st.progress(idx / len(samples))
    st.markdown(f"**진행 상황: {idx+1}/{len(samples)} 문제**")
    current_sample = samples[idx]
    st.markdown(f"""
    <div style="
        background-color: #f8f9fa;
        color: #222;
        padding: 2rem;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        margin: 1rem 0;
        font-size: 1.1rem;
        line-height: 1.6;
        white-space: pre-wrap;
    ">
    <strong>문제 {idx+1}번</strong> (문제번호: {current_sample['question_num']})<br><br>
    {current_sample['text']}
    </div>
    """, unsafe_allow_html=True)
    with st.form(f"score_form_{idx}"):
        content = st.number_input("내용 점수 (3-18)", min_value=3, max_value=18, value=10)
        organization = st.number_input("조직 점수 (2-12)", min_value=2, max_value=12, value=7)
        expression = st.number_input("표현 점수 (2-12)", min_value=2, max_value=12, value=7)
        total = content + organization + expression
        st.write(f"**총점: {total}점**")
        if st.form_submit_button("점수 제출하기"):
            st.write(f"정답: 내용 {current_sample['content_score']}, 조직 {current_sample['organization_score']}, 표현 {current_sample['expression_score']}")
            st.write(f"총점: {total} / 정답 총점: {current_sample['content_score'] + current_sample['organization_score'] + current_sample['expression_score']}")
            feedback_path = get_feedback_image_path('score', current_sample['question_num'])
            if feedback_path:
                st.image(feedback_path, caption=f"문제 {current_sample['question_num']}번 피드백")
            if idx < len(samples) - 1:
                if st.button("다음 문제 →"):
                    st.session_state.current_idx += 1
                    st.rerun()
            else:
                if st.button("결과 보기 →"):
                    st.session_state.stage = 'results'
                    st.rerun()

def show_results():
    st.title("🎉 학습 완료!")
    st.balloons()
    st.success(f"{st.session_state.user_name}님, 연습을 완료하셨습니다!")
    if st.button("처음으로"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    initialize_session_state()
    show_path_diagnostics()  # 경로 및 파일 구조 진단
    st.sidebar.title("📊 진행 현황")
    if st.session_state.user_name:
        st.sidebar.success(f"👋 {st.session_state.user_name}님")
        if st.session_state.selected_practice:
            st.sidebar.info(f"선택한 연습: {st.session_state.selected_practice}")
        elapsed = datetime.now() - st.session_state.start_time
        st.sidebar.metric("⏱️ 경과 시간", f"{elapsed.seconds // 60}분 {elapsed.seconds % 60}초")
    if st.sidebar.button("🔄 처음부터 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    if st.session_state.stage == 'intro':
        show_intro_page()
    elif st.session_state.stage == 'assignment_info':
        show_assignment_info()
    elif st.session_state.stage == 'practice_selection':
        show_practice_selection()
    elif st.session_state.stage == 'practice1':
        show_practice1()
    elif st.session_state.stage == 'practice2':
        show_practice2()
    elif st.session_state.stage == 'results':
        show_results()

if __name__ == "__main__":
    main()
