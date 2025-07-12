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
    """세션 상태 초기화"""
    if 'stage' not in st.session_state:
        st.session_state.stage = 'intro'
        st.session_state.user_name = ''
        st.session_state.selected_practice = None
        st.session_state.current_question = 1
        st.session_state.practice1_results = []
        st.session_state.practice2_results = []
        st.session_state.start_time = datetime.now()

def load_student_texts():
    """glob을 활용한 동적 파일 감지 및 기존 파싱 로직 적용"""
    samples = []
    
    st.info("📁 glob 패턴으로 txt 파일들을 자동 감지합니다...")
    
    try:
        # grade 폴더의 모든 txt 파일을 glob으로 찾기
        grade_pattern = "data/grade/*.txt"
        grade_files = glob.glob(grade_pattern)
        grade_files.sort()
        
        st.write(f"🔍 grade 폴더에서 발견된 파일들: {[os.path.basename(f) for f in grade_files]}")
        
        # 연습1용 데이터 로드
        grade_count = 0
        for i, file_path in enumerate(grade_files[:15], 1):
            try:
                # 다중 인코딩 시도
                content = None
                for encoding in ['utf-8', 'cp949', 'euc-kr']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    continue
                
                # 기존 파싱 로직 적용
                lines = [line.rstrip() for line in content.split('\n')]
                
                # 디버깅: 파일 내용 확인
                st.write(f"**{os.path.basename(file_path)} 분석:**")
                st.write(f"- 총 줄 수: {len(lines)}")
                st.write(f"- 첫 5줄: {lines[:5]}")
                
                if len(lines) >= 6:
                    try:
                        correct_grade = int(lines[0].strip())
                        content_score = int(lines[1].strip())
                        organization_score = int(lines[2].strip())
                        expression_score = int(lines[3].strip())
                        
                        # 학생 글 내용 추출 (5번째 줄부터)
                        student_text_lines = []
                        for line_idx in range(5, len(lines)):
                            if lines[line_idx].strip():  # 빈 줄이 아닌 경우만
                                student_text_lines.append(lines[line_idx])
                        
                        student_text = '\n'.join(student_text_lines).strip()
                        
                        st.write(f"- 추출된 글 길이: {len(student_text)}자")
                        st.write(f"- 글 미리보기: {student_text[:100]}...")
                        
                        if student_text and len(student_text) > 20:
                            samples.append({
                                'id': i,
                                'text': student_text,
                                'correct_grade': correct_grade,
                                'content_score': content_score,
                                'organization_score': organization_score,
                                'expression_score': expression_score,
                                'type': 'grade',
                                'filename': os.path.basename(file_path)
                            })
                            grade_count += 1
                            st.success(f"✅ {os.path.basename(file_path)} 로드 성공")
                        else:
                            st.warning(f"⚠️ {os.path.basename(file_path)}: 학생 글 내용이 없거나 너무 짧습니다.")
                    except ValueError as e:
                        st.error(f"❌ {os.path.basename(file_path)}: 점수 파싱 오류 - {e}")
                else:
                    st.warning(f"⚠️ {os.path.basename(file_path)}: 줄 수 부족 ({len(lines)}줄)")
                        
            except Exception as e:
                st.error(f"❌ {os.path.basename(file_path)} 처리 오류: {e}")
        
        # score 폴더도 동일하게 처리
        score_pattern = "data/score/*.txt"
        score_files = glob.glob(score_pattern)
        score_files.sort()
        
        score_count = 0
        for i, file_path in enumerate(score_files[:15], 1):
            try:
                content = None
                for encoding in ['utf-8', 'cp949', 'euc-kr']:
                    try:
                        with open(file_path, 'r', encoding=encoding) as f:
                            content = f.read()
                        break
                    except UnicodeDecodeError:
                        continue
                
                if content is None:
                    continue
                
                lines = [line.rstrip() for line in content.split('\n')]
                
                if len(lines) >= 6:
                    try:
                        correct_grade = int(lines[0].strip())
                        content_score = int(lines[1].strip())
                        organization_score = int(lines[2].strip())
                        expression_score = int(lines[3].strip())
                        
                        student_text_lines = []
                        for line_idx in range(5, len(lines)):
                            if lines[line_idx].strip():
                                student_text_lines.append(lines[line_idx])
                        
                        student_text = '\n'.join(student_text_lines).strip()
                        
                        if student_text and len(student_text) > 20:
                            samples.append({
                                'id': i + 15,
                                'text': student_text,
                                'correct_grade': correct_grade,
                                'content_score': content_score,
                                'organization_score': organization_score,
                                'expression_score': expression_score,
                                'type': 'score',
                                'filename': os.path.basename(file_path)
                            })
                            score_count += 1
                    except ValueError:
                        continue
                        
            except Exception:
                continue
        
        st.info(f"📊 연습2 (score): {score_count}개 파일 로드 완료")
        
        if len(samples) > 0:
            st.success(f"🎉 총 {len(samples)}개 파일 로드 성공!")
            return samples
        else:
            st.error("❌ 파일 로드 실패. 강제 샘플 데이터 사용")
            return generate_fallback_data()
            
    except Exception as e:
        st.error(f"❌ 전체 로딩 오류: {e}")
        return generate_fallback_data()

def generate_fallback_data():
    """강제 샘플 데이터 생성"""
    st.warning("🔧 강제 샘플 데이터를 생성합니다.")
    
    sample_text = """인간이 사용할 약이나 화장품 등이 인간에게 해를 끼치지 않는지를 알아보기 위해 대부분의 회사나 공공 기관들이 동물 실험을 한다. 하지만 본래 인간과 동물은 다르기 때문에 인간과 동물에게서 나타나는 효과가 다르다. 독일의 입덧 방지약에 들어있던 탈리도마이드라는 물질은 쥐나 개, 고양이에 대한 동물 실험에서 아무런 부작용을 일으키지 않았지만 정작 원숭이와 사람에게는 팔이나 다리뼈가 발달하지 않거나 극단적으로 짧은 기형아를 발생시켰다."""
    
    samples = []
    
    # 연습1용 데이터
    for i in range(15):
        samples.append({
            'id': i + 1,
            'text': sample_text + f" 따라서 동물 실험에 대한 신중한 접근이 필요하다. (연습1 문제 {i+1}번)",
            'correct_grade': 3,
            'content_score': 12,
            'organization_score': 8,
            'expression_score': 7,
            'type': 'grade'
        })
    
    # 연습2용 데이터
    for i in range(15):
        samples.append({
            'id': i + 16,
            'text': sample_text + f" 윤리적 고려와 함께 대안 방법을 모색해야 한다. (연습2 문제 {i+1}번)",
            'correct_grade': 3,
            'content_score': 12,
            'organization_score': 8,
            'expression_score': 7,
            'type': 'score'
        })
    
    return samples

def show_intro_page():
    """소개 페이지"""
    st.title("🎯 SEP ME ver.6")
    st.subheader("학생 글 채점 연습 프로그램")
    
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
    """과제 및 평가기준 안내"""
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
    
    # 등급 기준표
    st.subheader("🎯 등급 기준")
    grade_df = pd.DataFrame({
        '등급': ['1등급', '2등급', '3등급', '4등급', '5등급'],
        '점수 범위': ['29-33점', '27-28점', '24-26점', '20-23점', '13-19점'],
        '수준': ['매우 우수', '우수', '보통', '미흡', '매우 미흡']
    })
    st.table(grade_df)
    
    # 체크리스트
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
    """연습 유형 선택 페이지"""
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
            st.session_state.current_question = 1  # 명시적으로 1로 초기화
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
            st.session_state.current_question = 1  # 명시적으로 1로 초기화
            st.rerun()

def show_practice1():
    """연습1 - 등급 추정"""
    st.title("📚 연습1: 글의 등급 추정하기")
    
    # 현재 문제 번호 디버깅
    st.write(f"🔍 **디버깅 정보**: 현재 문제 번호 = {st.session_state.current_question}")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    
    # 현재 문제 데이터 가져오기
    if 'student_data' in st.session_state and st.session_state.student_data:
        grade_data = [item for item in st.session_state.student_data if item.get('type') == 'grade']
        
        st.write(f"🔍 **사용 가능한 grade 데이터**: {len(grade_data)}개")
        
        if len(grade_data) >= st.session_state.current_question:
            current_data = grade_data[st.session_state.current_question - 1]
            
            # 현재 데이터 디버깅
            st.write(f"🔍 **현재 데이터 ID**: {current_data.get('id', 'N/A')}")
            st.write(f"🔍 **파일명**: {current_data.get('filename', 'N/A')}")
            st.write(f"🔍 **텍스트 길이**: {len(current_data.get('text', ''))}자")
            
            st.markdown("### 📖 학생 글")
            if current_data.get('text'):
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
                <strong>문제 {st.session_state.current_question}번</strong><br><br>
                {current_data['text']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ 학생 글 내용이 비어있습니다.")
                st.write(f"**전체 데이터**: {current_data}")
            
            # 등급 선택
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
                # 결과 저장
                is_correct = selected_grade == current_data['correct_grade']
                result = {
                    'question': st.session_state.current_question,
                    'selected': selected_grade,
                    'correct': current_data['correct_grade'],
                    'is_correct': is_correct,
                    'timestamp': datetime.now()
                }
                
                # 중복 저장 방지
                if not any(r['question'] == st.session_state.current_question for r in st.session_state.practice1_results):
                    st.session_state.practice1_results.append(result)
                
                # 피드백
                st.markdown("---")
                if is_correct:
                    st.success("🎉 정답입니다! 훌륭한 판단력을 보여주셨습니다.")
                else:
                    st.error(f"😔 아쉽지만 오답입니다. 정답: {current_data['correct_grade']}등급, 선택: {selected_grade}등급")
                    
                    # 피드백 이미지 표시 (현재 문제 번호 사용)
                    feedback_paths = [
                        f"data/f_grade/{st.session_state.current_question}.png",
                        f"data/g_feed/{st.session_state.current_question}.png"
                    ]
                    
                    image_found = False
                    for feedback_path in feedback_paths:
                        if os.path.exists(feedback_path):
                            st.image(feedback_path, caption=f"문제 {st.session_state.current_question}번 피드백")
                            image_found = True
                            break
                    
                    if not image_found:
                        st.info(f"피드백 이미지 ({st.session_state.current_question}.png)를 찾을 수 없습니다.")
                
                # 다음 문제로
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn2:
                    if st.session_state.current_question < 15:
                        if st.button("다음 문제 →", type="primary", use_container_width=True):
                            st.session_state.current_question += 1  # 문제 번호 증가
                            st.rerun()
                    else:
                        if st.button("결과 보기 →", type="primary", use_container_width=True):
                            st.session_state.stage = 'results'
                            st.rerun()
        else:
            st.error(f"연습1 데이터가 부족합니다. (현재: {len(grade_data)}개, 필요: {st.session_state.current_question}개)")
    else:
        st.error("학생 글 데이터를 로드할 수 없습니다.")

def show_practice2():
    """연습2 - 점수 추정"""
    st.title("📊 연습2: 글의 점수 추정하기")
    
    # 현재 문제 번호 디버깅
    st.write(f"🔍 **디버깅 정보**: 현재 문제 번호 = {st.session_state.current_question}")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    
    # 현재 문제 데이터 가져오기
    if 'student_data' in st.session_state and st.session_state.student_data:
        score_data = [item for item in st.session_state.student_data if item.get('type') == 'score']
        
        if len(score_data) >= st.session_state.current_question:
            current_data = score_data[st.session_state.current_question - 1]
            
            st.markdown("### 📖 학생 글")
            if current_data.get('text'):
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
                <strong>문제 {st.session_state.current_question}번</strong><br><br>
                {current_data['text']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error("❌ 학생 글 내용이 비어있습니다.")
            
            # 점수 입력
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
                    # 결과 저장
                    correct_total = current_data['content_score'] + current_data['organization_score'] + current_data['expression_score']
                    result = {
                        'question': st.session_state.current_question,
                        'content': content,
                        'organization': organization,
                        'expression': expression,
                        'total': total,
                        'correct_total': correct_total,
                        'timestamp': datetime.now()
                    }
                    
                    # 중복 저장 방지
                    if not any(r['question'] == st.session_state.current_question for r in st.session_state.practice2_results):
                        st.session_state.practice2_results.append(result)
                    
                    # 피드백
                    total_diff = abs(total - correct_total)
                    if total_diff <= 2:
                        st.success("🎉 매우 정확한 채점입니다!")
                    elif total_diff <= 5:
                        st.info("👍 양호한 채점입니다.")
                    else:
                        st.warning("💡 채점 기준을 다시 검토해보세요.")
                    
                    # 피드백 이미지 표시
                    feedback_paths = [
                        f"data/f_score/{st.session_state.current_question}.png",
                        f"data/s_feed/{st.session_state.current_question}.png"
                    ]
                    
                    for feedback_path in feedback_paths:
                        if os.path.exists(feedback_path):
                            st.image(feedback_path, caption=f"문제 {st.session_state.current_question}번 피드백")
                            break
                    
                    # 다음 문제로
                    st.markdown("---")
                    if st.session_state.current_question < 15:
                        if st.button("다음 문제 →", type="primary", use_container_width=True):
                            st.session_state.current_question += 1  # 문제 번호 증가
                            st.rerun()
                    else:
                        if st.button("결과 보기 →", type="primary", use_container_width=True):
                            st.session_state.stage = 'results'
                            st.rerun()

def show_results():
    """결과 페이지"""
    st.title("🎉 학습 완료!")
    st.balloons()
    
    total_time = datetime.now() - st.session_state.start_time
    st.success(f"🎊 {st.session_state.user_name}님, 연습을 완료하셨습니다! (소요시간: {total_time.seconds // 60}분)")
    
    # 결과 표시
    if st.session_state.practice1_results:
        st.subheader("📈 연습1 결과")
        results_df = pd.DataFrame(st.session_state.practice1_results)
        st.dataframe(results_df)
    
    if st.session_state.practice2_results:
        st.subheader("📊 연습2 결과")
        results_df = pd.DataFrame(st.session_state.practice2_results)
        st.dataframe(results_df)
    
    # 다시 시작 버튼
    if st.button("🏠 처음으로", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def main():
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바
    st.sidebar.title("📊 진행 현황")
    
    if st.session_state.user_name:
        st.sidebar.success(f"👋 {st.session_state.user_name}님")
        
        # 현재 문제 번호 표시
        if st.session_state.stage in ['practice1', 'practice2']:
            st.sidebar.write(f"**현재 문제**: {st.session_state.current_question}/15")
    
    # 리셋 버튼
    if st.sidebar.button("🔄 처음부터 다시 시작"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # 단계별 페이지 표시
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
