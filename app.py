import streamlit as st
import pandas as pd
import os
import glob
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="SEP ME ver.6 - 학생 글 채점 연습",
    page_icon="📝",
    layout="wide"
)

def initialize_session_state():
    if 'stage' not in st.session_state:
        st.session_state.stage = 'intro'
        st.session_state.user_name = ''
        st.session_state.selected_practice = None
        st.session_state.current_question = 0  # 0부터 시작
        st.session_state.practice1_results = []
        st.session_state.practice2_results = []
        st.session_state.start_time = datetime.now()
        st.session_state.student_data = None
        st.session_state.grade_ids = []
        st.session_state.score_ids = []

def load_student_texts():
    samples = []
    grade_ids = []
    score_ids = []
    # grade 폴더
    grade_files = glob.glob("data/grade/*.txt")
    grade_files.sort()
    for file_path in grade_files:
        lines = None
        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        if lines and len(lines) >= 6:
            try:
                file_id = int(lines[0].strip())
                correct_grade = int(lines[1].strip())
                content_score = int(lines[2].strip())
                organization_score = int(lines[3].strip())
                expression_score = int(lines[4].strip())
                student_text = ''.join(lines[5:]).strip()
                if student_text and len(student_text) > 10:
                    samples.append({
                        'file_id': file_id,
                        'text': student_text,
                        'correct_grade': correct_grade,
                        'content_score': content_score,
                        'organization_score': organization_score,
                        'expression_score': expression_score,
                        'type': 'grade',
                        'filename': os.path.basename(file_path)
                    })
                    grade_ids.append(file_id)
            except Exception:
                continue
    # score 폴더
    score_files = glob.glob("data/score/*.txt")
    score_files.sort()
    for file_path in score_files:
        lines = None
        for encoding in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    lines = f.readlines()
                break
            except UnicodeDecodeError:
                continue
        if lines and len(lines) >= 6:
            try:
                file_id = int(lines[0].strip())
                correct_grade = int(lines[1].strip())
                content_score = int(lines[2].strip())
                organization_score = int(lines[3].strip())
                expression_score = int(lines[4].strip())
                student_text = ''.join(lines[5:]).strip()
                if student_text and len(student_text) > 10:
                    samples.append({
                        'file_id': file_id,
                        'text': student_text,
                        'correct_grade': correct_grade,
                        'content_score': content_score,
                        'organization_score': organization_score,
                        'expression_score': expression_score,
                        'type': 'score',
                        'filename': os.path.basename(file_path)
                    })
                    score_ids.append(file_id)
            except Exception:
                continue
    return samples, grade_ids, score_ids

def show_intro_page():
    st.title("🎯 SEP ME ver.6")
    st.subheader("학생 글 채점 연습 프로그램")
    st.markdown("""
    **SEP ME**는 학생 글 채점 능력 향상을 위한 AI 기반 학습 도구입니다.
    실제 학생들이 작성한 글을 바탕으로 채점 연습을 할 수 있습니다.
    """)
    with st.form("user_info"):
        st.markdown("#### 📝 사용자 정보")
        name = st.text_input("이름을 입력해주세요:", placeholder="홍길동")
        agreement = st.checkbox("개인정보 수집 및 이용에 동의합니다 (학습 목적)")
        if st.form_submit_button("🚀 학습 시작하기", type="primary"):
            if name and agreement:
                st.session_state.user_name = name
                st.session_state.stage = 'assignment_info'
                st.success("등록이 완료되었습니다!")
                st.rerun()
            else:
                if not name:
                    st.error("이름을 입력해주세요.")
                if not agreement:
                    st.error("개인정보 수집 및 이용에 동의해주세요.")

def show_assignment_info():
    st.title("📋 쓰기 과제 및 평가 기준")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("📝 쓰기 과제")
        if os.path.exists("data/assignment.png"):
            st.image("data/assignment.png", caption="쓰기 과제")
        else:
            st.info("과제 이미지가 준비되면 여기에 표시됩니다.")
    with col2:
        st.subheader("📊 평가 기준")
        if os.path.exists("data/standard.png"):
            st.image("data/standard.png", caption="평가 기준")
        else:
            st.info("평가기준 이미지가 준비되면 여기에 표시됩니다.")
    st.subheader("🎯 등급 기준")
    grade_df = pd.DataFrame({
        '등급': ['1등급', '2등급', '3등급', '4등급', '5등급'],
        '점수 범위': ['29-33점', '27-28점', '24-26점', '20-23점', '13-19점'],
        '수준': ['매우 우수', '우수', '보통', '미흡', '매우 미흡']
    })
    st.table(grade_df)
    st.subheader("✅ 평가 전 점검 항목")
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
                samples, grade_ids, score_ids = load_student_texts()
                st.session_state.student_data = samples
                st.session_state.grade_ids = grade_ids
                st.session_state.score_ids = score_ids
                st.session_state.stage = 'practice_selection'
                st.success("모든 준비가 완료되었습니다!")
                st.rerun()
            else:
                st.warning("모든 항목을 확인해주세요.")

def show_practice_selection():
    st.title("🎯 연습 유형 선택")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📚 연습1: 등급 추정")
        if st.button("📚 연습1 시작하기", type="primary"):
            st.session_state.selected_practice = 'practice1'
            st.session_state.stage = 'practice1'
            st.session_state.current_question = 0
            st.rerun()
    with col2:
        st.markdown("#### 📊 연습2: 점수 추정")
        if st.button("📊 연습2 시작하기", type="primary"):
            st.session_state.selected_practice = 'practice2'
            st.session_state.stage = 'practice2'
            st.session_state.current_question = 0
            st.rerun()

def show_practice1():
    st.title("📚 연습1: 글의 등급 추정하기")
    grade_data = [item for item in st.session_state.student_data if item.get('type') == 'grade']
    grade_ids = st.session_state.grade_ids
    q = st.session_state.current_question
    if q < len(grade_data):
        current_data = grade_data[q]
        st.markdown("### 📖 학생 글")
        st.markdown(
            f"<div style='background:#f8f9fa;color:#222;padding:1rem;border-radius:10px;white-space:pre-wrap'>{current_data['text']}</div>",
            unsafe_allow_html=True
        )
        st.markdown("### 🎯 이 글의 등급을 선택하세요")
        cols = st.columns(5)
        selected_grade = None
        for i, grade in enumerate([1,2,3,4,5]):
            with cols[i]:
                if st.button(f"{grade}등급", key=f"grade_{grade}_{q}"):
                    selected_grade = grade
        if selected_grade is not None:
            is_correct = selected_grade == current_data['correct_grade']
            st.write(f"정답: {current_data['correct_grade']}등급, 선택: {selected_grade}등급")
            file_id = current_data['file_id']
            feedback_path = f"data/f_grade/{file_id}.png"
            if os.path.exists(feedback_path):
                st.image(feedback_path, caption="상세 피드백")
            if q < len(grade_data) - 1:
                if st.button("다음 문제 →"):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("연습2로 이동 →"):
                    st.session_state.stage = 'practice2'
                    st.session_state.current_question = 0
                    st.rerun()
    else:
        st.error("연습1 데이터가 부족합니다.")

def show_practice2():
    st.title("📊 연습2: 글의 점수 추정하기")
    score_data = [item for item in st.session_state.student_data if item.get('type') == 'score']
    score_ids = st.session_state.score_ids
    q = st.session_state.current_question
    if q < len(score_data):
        current_data = score_data[q]
        st.markdown("### 📖 학생 글")
        st.markdown(
            f"<div style='background:#f8f9fa;color:#222;padding:1rem;border-radius:10px;white-space:pre-wrap'>{current_data['text']}</div>",
            unsafe_allow_html=True
        )
        with st.form(f"score_form_{q}"):
            content = st.number_input("내용 점수 (3-18)", min_value=3, max_value=18, value=10)
            organization = st.number_input("조직 점수 (2-12)", min_value=2, max_value=12, value=7)
            expression = st.number_input("표현 점수 (2-12)", min_value=2, max_value=12, value=7)
            total = content + organization + expression
            if st.form_submit_button("점수 제출하기"):
                st.write(f"정답: 내용 {current_data['content_score']}, 조직 {current_data['organization_score']}, 표현 {current_data['expression_score']}")
                st.write(f"총점: {total} / 정답 총점: {current_data['content_score'] + current_data['organization_score'] + current_data['expression_score']}")
                file_id = current_data['file_id']
                feedback_path = f"data/f_score/{file_id}.png"
                if os.path.exists(feedback_path):
                    st.image(feedback_path, caption="상세 피드백")
                if q < len(score_data) - 1:
                    if st.button("다음 문제 →"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("결과 보기 →"):
                        st.session_state.stage = 'results'
                        st.rerun()
    else:
        st.error("연습2 데이터가 부족합니다.")

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
    st.sidebar.title("📊 진행 현황")
    if st.session_state.user_name:
        st.sidebar.success(f"👋 {st.session_state.user_name}님")
        if st.session_state.selected_practice:
            practice_name = {
                'practice1': '📚 연습1 (등급 추정)',
                'practice2': '📊 연습2 (점수 추정)',
                'both': '🎯 두 연습 모두'
            }.get(st.session_state.selected_practice, '연습 선택됨')
            st.sidebar.info(f"선택한 연습: {practice_name}")
        elapsed = datetime.now() - st.session_state.start_time
        st.sidebar.metric("⏱️ 경과 시간", f"{elapsed.seconds // 60}분 {elapsed.seconds % 60}초")
        if st.session_state.stage in ['practice1', 'practice2']:
            if st.session_state.selected_practice == 'practice1':
                total = len(st.session_state.grade_ids)
            else:
                total = len(st.session_state.score_ids)
            progress = (st.session_state.current_question) / (total if total else 1)
            st.sidebar.progress(progress)
            stage_name = "연습1" if st.session_state.stage == 'practice1' else "연습2"
            st.sidebar.write(f"**{stage_name} 진행률**: {st.session_state.current_question+1}/{total}")
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
