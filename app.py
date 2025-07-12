import streamlit as st
import pandas as pd
import numpy as np
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
        st.session_state.current_question = 1
        st.session_state.practice1_results = []
        st.session_state.practice2_results = []
        st.session_state.start_time = datetime.now()
        st.session_state.student_data = None

def load_student_texts():
    samples = []
    # grade 폴더의 모든 txt 파일을 glob으로 찾기
    grade_files = glob.glob("data/grade/*.txt")
    grade_files.sort()
    for i, file_path in enumerate(grade_files[:15], 1):
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
                        'id': i,
                        'file_id': file_id,
                        'text': student_text,
                        'correct_grade': correct_grade,
                        'content_score': content_score,
                        'organization_score': organization_score,
                        'expression_score': expression_score,
                        'type': 'grade',
                        'filename': os.path.basename(file_path)
                    })
            except Exception:
                continue
    # score 폴더의 모든 txt 파일을 glob으로 찾기
    score_files = glob.glob("data/score/*.txt")
    score_files.sort()
    for i, file_path in enumerate(score_files[:15], 1):
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
                        'id': i + 15,
                        'file_id': file_id,
                        'text': student_text,
                        'correct_grade': correct_grade,
                        'content_score': content_score,
                        'organization_score': organization_score,
                        'expression_score': expression_score,
                        'type': 'score',
                        'filename': os.path.basename(file_path)
                    })
            except Exception:
                continue
    return samples

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
        if st.form_submit_button("🚀 학습 시작하기", type="primary", use_container_width=True):
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
        if st.form_submit_button("다음 단계로 →", type="primary", use_container_width=True):
            if all(checks):
                st.session_state.stage = 'practice_selection'
                st.session_state.student_data = load_student_texts()
                st.success("모든 준비가 완료되었습니다!")
                st.rerun()
            else:
                st.warning("모든 항목을 확인해주세요.")

def show_practice_selection():
    st.title("🎯 연습 유형 선택")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        ">
            <h3>📚 연습1: 등급 추정</h3>
            <p>학생 글을 읽고 1~5등급 중 선택</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📚 연습1 시작하기", type="primary", use_container_width=True):
            st.session_state.selected_practice = 'practice1'
            st.session_state.stage = 'practice1'
            st.session_state.current_question = 1
            st.rerun()
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2rem;
            border-radius: 15px;
            color: white;
            text-align: center;
            margin: 1rem 0;
        ">
            <h3>📊 연습2: 점수 추정</h3>
            <p>내용/조직/표현 영역별 점수 입력</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 연습2 시작하기", type="primary", use_container_width=True):
            st.session_state.selected_practice = 'practice2'
            st.session_state.stage = 'practice2'
            st.session_state.current_question = 1
            st.rerun()

def show_practice1():
    st.title("📚 연습1: 글의 등급 추정하기")
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    if st.session_state.student_data:
        grade_data = [item for item in st.session_state.student_data if item.get('type') == 'grade']
        if len(grade_data) >= st.session_state.current_question:
            current_data = grade_data[st.session_state.current_question - 1]
            st.markdown("### 📖 학생 글")
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 2rem;
                border-radius: 10px;
                border-left: 5px solid #007bff;
                margin: 1rem 0;
                font-size: 1.1rem;
                line-height: 1.6;
                white-space: pre-wrap;
            ">
            <strong>문제 {st.session_state.current_question}번</strong> (파일: {current_data.get('filename', 'unknown')})<br><br>
            {current_data['text']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### 🎯 이 글의 등급을 선택하세요")
            cols = st.columns(5)
            selected_grade = None
            grade_options = {
                1: "1등급\n(29-33점)",
                2: "2등급\n(27-28점)",
                3: "3등급\n(24-26점)",
                4: "4등급\n(20-23점)",
                5: "5등급\n(13-19점)"
            }
            for i, (grade, description) in enumerate(grade_options.items()):
                with cols[i]:
                    if st.button(description, key=f"grade_{grade}_{st.session_state.current_question}", use_container_width=True):
                        selected_grade = grade
            if selected_grade:
                is_correct = selected_grade == current_data['correct_grade']
                result = {
                    'question': st.session_state.current_question,
                    'selected': selected_grade,
                    'correct': current_data['correct_grade'],
                    'is_correct': is_correct,
                    'filename': current_data.get('filename', 'unknown'),
                    'timestamp': datetime.now()
                }
                if not any(r['question'] == st.session_state.current_question for r in st.session_state.practice1_results):
                    st.session_state.practice1_results.append(result)
                st.markdown("---")
                if is_correct:
                    st.success("🎉 정답입니다! 훌륭한 판단력을 보여주셨습니다.")
                else:
                    st.error(f"😔 아쉽지만 오답입니다. 정답: {current_data['correct_grade']}등급, 선택: {selected_grade}등급")
                    file_id = current_data.get('file_id', st.session_state.current_question)
                    feedback_paths = [
                        f"data/f_grade/{file_id}.png",
                        f"data/g_feed/{file_id}.png",
                        f"data/f_grade/{st.session_state.current_question}.png",
                        f"data/g_feed/{st.session_state.current_question}.png"
                    ]
                    for feedback_path in feedback_paths:
                        if os.path.exists(feedback_path):
                            st.image(feedback_path, caption="상세 피드백")
                            break
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                with col_btn2:
                    if st.session_state.current_question < 15:
                        if st.button("다음 문제 →", type="primary", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        if st.button("결과 보기 →", type="primary", use_container_width=True):
                            st.session_state.stage = 'results'
                            st.rerun()
        else:
            st.error(f"연습1 데이터가 부족합니다. (현재: {len(grade_data)}개, 필요: 15개)")
    else:
        st.error("학생 글 데이터를 로드할 수 없습니다.")

def show_practice2():
    st.title("📊 연습2: 글의 점수 추정하기")
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    if st.session_state.student_data:
        score_data = [item for item in st.session_state.student_data if item.get('type') == 'score']
        if len(score_data) >= st.session_state.current_question:
            current_data = score_data[st.session_state.current_question - 1]
            st.markdown("### 📖 학생 글")
            st.markdown(f"""
            <div style="
                background-color: #f8f9fa;
                padding: 2rem;
                border-radius: 10px;
                border-left: 5px solid #007bff;
                margin: 1rem 0;
                font-size: 1.1rem;
                line-height: 1.6;
                white-space: pre-wrap;
            ">
            <strong>문제 {st.session_state.current_question}번</strong> (파일: {current_data.get('filename', 'unknown')})<br><br>
            {current_data['text']}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("### 🎯 영역별 점수를 입력하세요")
            with st.form(f"score_form_{st.session_state.current_question}"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**내용 영역 (3-18점)**")
                    content = st.number_input("내용 점수", min_value=3, max_value=18, value=10)
                with col2:
                    st.markdown("**조직 영역 (2-12점)**")
                    organization = st.number_input("조직 점수", min_value=2, max_value=12, value=7)
                with col3:
                    st.markdown("**표현 영역 (2-12점)**")
                    expression = st.number_input("표현 점수", min_value=2, max_value=12, value=7)
                total = content + organization + expression
                st.write(f"**총점: {total}점**")
                if st.form_submit_button("점수 제출하기", type="primary", use_container_width=True):
                    correct_total = current_data['content_score'] + current_data['organization_score'] + current_data['expression_score']
                    result = {
                        'question': st.session_state.current_question,
                        'content': content,
                        'organization': organization,
                        'expression': expression,
                        'total': total,
                        'correct_content': current_data['content_score'],
                        'correct_organization': current_data['organization_score'],
                        'correct_expression': current_data['expression_score'],
                        'correct_total': correct_total,
                        'filename': current_data.get('filename', 'unknown'),
                        'timestamp': datetime.now()
                    }
                    if not any(r['question'] == st.session_state.current_question for r in st.session_state.practice2_results):
                        st.session_state.practice2_results.append(result)
                    show_score_feedback(result, current_data.get('file_id', st.session_state.current_question))
                    st.markdown("---")
                    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                    with col_btn2:
                        if st.session_state.current_question < 15:
                            if st.button("다음 문제 →", type="primary", use_container_width=True):
                                st.session_state.current_question += 1
                                st.rerun()
                        else:
                            if st.button("결과 보기 →", type="primary", use_container_width=True):
                                st.session_state.stage = 'results'
                                st.rerun()
        else:
            st.error(f"연습2 데이터가 부족합니다. (현재: {len(score_data)}개, 필요: 15개)")
    else:
        st.error("학생 글 데이터를 로드할 수 없습니다.")

def score_to_grade(total_score):
    if total_score >= 29:
        return 1
    elif total_score >= 27:
        return 2
    elif total_score >= 24:
        return 3
    elif total_score >= 20:
        return 4
    else:
        return 5

def show_score_feedback(result, file_id):
    content_diff = result['content'] - result['correct_content']
    org_diff = result['organization'] - result['correct_organization']
    exp_diff = result['expression'] - result['correct_expression']
    total_diff = result['total'] - result['correct_total']
    st.markdown("### 📊 채점 결과 분석")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("내용 영역", f"{result['content']}점", f"{content_diff:+d}점")
        st.caption(f"정답: {result['correct_content']}점")
    with col2:
        st.metric("조직 영역", f"{result['organization']}점", f"{org_diff:+d}점")
        st.caption(f"정답: {result['correct_organization']}점")
    with col3:
        st.metric("표현 영역", f"{result['expression']}점", f"{exp_diff:+d}점")
        st.caption(f"정답: {result['correct_expression']}점")
    with col4:
        st.metric("총점", f"{result['total']}점", f"{total_diff:+d}점")
        st.caption(f"정답: {result['correct_total']}점")
    abs_total_diff = abs(total_diff)
    if abs_total_diff <= 2:
        st.success("🎉 매우 정확한 채점입니다! 훌륭한 평가 능력을 보여주셨습니다.")
    elif abs_total_diff <= 5:
        st.info("👍 양호한 채점입니다. 조금 더 세밀한 관찰이 필요합니다.")
    else:
        st.warning("💡 채점 기준을 다시 검토해보세요. 각 영역별 특성을 더 자세히 살펴보시기 바랍니다.")
    feedback_paths = [
        f"data/f_score/{file_id}.png",
        f"data/s_feed/{file_id}.png",
        f"data/f_score/{st.session_state.current_question}.png",
        f"data/s_feed/{st.session_state.current_question}.png"
    ]
    for feedback_path in feedback_paths:
        if os.path.exists(feedback_path):
            st.image(feedback_path, caption="상세 피드백")
            break

def show_results():
    st.title("🎉 학습 완료!")
    st.balloons()
    total_time = datetime.now() - st.session_state.start_time
    st.success(f"🎊 {st.session_state.user_name}님, 연습을 완료하셨습니다! (소요시간: {total_time.seconds // 60}분)")
    st.markdown("### 📊 종합 결과")
    col1, col2, col3, col4 = st.columns(4)
    if st.session_state.practice1_results:
        p1_correct = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
        p1_accuracy = (p1_correct / len(st.session_state.practice1_results)) * 100
        with col1:
            st.metric("연습1 정답률", f"{p1_accuracy:.1f}%", f"{p1_correct}/15")
    if st.session_state.practice2_results:
        avg_error = np.mean([abs(r['total'] - r['correct_total']) for r in st.session_state.practice2_results])
        accuracy = max(0, 100 - avg_error * 8)
        with col2:
            st.metric("연습2 정확도", f"{accuracy:.1f}%")
        with col3:
            st.metric("평균 오차", f"{avg_error:.1f}점")
    with col4:
        if st.session_state.practice1_results and st.session_state.practice2_results:
            overall_score = (p1_accuracy + accuracy) / 2
            st.metric("종합 점수", f"{overall_score:.1f}점")
    st.markdown("---")
    tabs = []
    if st.session_state.practice1_results:
        tabs.append("📈 연습1 결과")
    if st.session_state.practice2_results:
        tabs.append("📊 연습2 결과")
    if len(tabs) == 1:
        st.markdown(f"### {tabs[0]}")
        if st.session_state.practice1_results:
            results_df = pd.DataFrame(st.session_state.practice1_results)
            display_df = results_df[['question', 'selected', 'correct', 'is_correct', 'filename']].copy()
            display_df.columns = ['문제번호', '선택등급', '정답등급', '정답여부', '파일명']
            display_df['정답여부'] = display_df['정답여부'].map({True: '✅', False: '❌'})
            st.dataframe(display_df, use_container_width=True)
        else:
            results_df = pd.DataFrame(st.session_state.practice2_results)
            display_df = results_df[['question', 'content', 'organization', 'expression', 'total', 'correct_total', 'filename']].copy()
            display_df.columns = ['문제번호', '내용점수', '조직점수', '표현점수', '총점', '정답총점', '파일명']
            display_df['점수차이'] = display_df['총점'] - display_df['정답총점']
            st.dataframe(display_df, use_container_width=True)
    else:
        tab1, tab2 = st.tabs(tabs)
        with tab1:
            if st.session_state.practice1_results:
                results_df = pd.DataFrame(st.session_state.practice1_results)
                display_df = results_df[['question', 'selected', 'correct', 'is_correct', 'filename']].copy()
                display_df.columns = ['문제번호', '선택등급', '정답등급', '정답여부', '파일명']
                display_df['정답여부'] = display_df['정답여부'].map({True: '✅', False: '❌'})
                st.dataframe(display_df, use_container_width=True)
        with tab2:
            if st.session_state.practice2_results:
                results_df = pd.DataFrame(st.session_state.practice2_results)
                display_df = results_df[['question', 'content', 'organization', 'expression', 'total', 'correct_total', 'filename']].copy()
                display_df.columns = ['문제번호', '내용점수', '조직점수', '표현점수', '총점', '정답총점', '파일명']
                display_df['점수차이'] = display_df['총점'] - display_df['정답총점']
                st.dataframe(display_df, use_container_width=True)
    st.markdown("---")
    col_action1, col_action2, col_action3 = st.columns(3)
    with col_action1:
        if st.button("📊 결과 다운로드", use_container_width=True):
            csv_data = create_results_csv()
            st.download_button(
                label="CSV 파일 다운로드",
                data=csv_data,
                file_name=f"sep_results_{st.session_state.user_name}_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    with col_action2:
        if st.button("🔄 다른 연습 하기", use_container_width=True):
            st.session_state.stage = 'practice_selection'
            st.session_state.current_question = 1
            st.rerun()
    with col_action3:
        if st.button("🏠 처음으로", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def create_results_csv():
    data = {
        'user_name': st.session_state.user_name,
        'selected_practice': st.session_state.selected_practice,
        'completion_time': datetime.now().isoformat(),
        'total_time_minutes': (datetime.now() - st.session_state.start_time).seconds // 60
    }
    if st.session_state.practice1_results:
        p1_correct = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
        data['practice1_accuracy'] = (p1_correct / 15) * 100
        data['practice1_correct_count'] = p1_correct
    if st.session_state.practice2_results:
        avg_error = np.mean([abs(r['total'] - r['correct_total']) for r in st.session_state.practice2_results])
        data['practice2_avg_error'] = avg_error
        data['practice2_accuracy'] = max(0, 100 - avg_error * 8)
    df = pd.DataFrame([data])
    return df.to_csv(index=False, encoding='utf-8-sig')

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
            progress = (st.session_state.current_question - 1) / 15
            st.sidebar.progress(progress)
            stage_name = "연습1" if st.session_state.stage == 'practice1' else "연습2"
            st.sidebar.write(f"**{stage_name} 진행률**: {st.session_state.current_question}/15")
            if st.session_state.practice1_results:
                correct_count = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
                st.sidebar.metric("연습1 정답률", f"{(correct_count/len(st.session_state.practice1_results)*100):.1f}%")
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
