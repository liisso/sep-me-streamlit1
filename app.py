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
        grade_files.sort()  # 파일명 순으로 정렬
        
        st.write(f"🔍 grade 폴더에서 발견된 파일들: {[os.path.basename(f) for f in grade_files]}")
        
        # 연습1용 데이터 로드 (기존 파싱 로직 적용)
        grade_count = 0
        for i, file_path in enumerate(grade_files[:15], 1):  # 최대 15개
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
                    st.warning(f"⚠️ {os.path.basename(file_path)}: 인코딩을 읽을 수 없습니다.")
                    continue
                
                # 기존 파싱 로직: 줄바꿈으로 분리
                lines = content.strip().split('\n')
                
                if len(lines) >= 6:  # 최소 6줄 이상이어야 함
                    # 정답 정보 추출 (첫 5줄)
                    try:
                        file_id = int(lines[0].strip())  # 1행: 글 번호
                        correct_grade = int(lines[1].strip())  # 2행: 등급 답
                        content_score = int(lines[2].strip())  # 3행: 내용 점수
                        organization_score = int(lines[3].strip())  # 4행: 조직 점수
                        expression_score = int(lines[4].strip())  # 5행: 표현 점수
                        
                        # 실제 학생 글 내용 (6번째 줄부터)
                        student_text = '\n'.join(lines[5:]).strip()
                        
                        if student_text and len(student_text) > 10:  # 최소 길이 확인
                            samples.append({
                                'id': i,
                                'file_id': file_id,  # 파일 내 글 번호 (피드백 이미지용)
                                'text': student_text,
                                'correct_grade': correct_grade,
                                'content_score': content_score,
                                'organization_score': organization_score,
                                'expression_score': expression_score,
                                'type': 'grade'
                            })
                            grade_count += 1
                            st.success(f"✅ {os.path.basename(file_path)} 로드 성공 (글번호: {file_id})")
                        else:
                            st.warning(f"⚠️ {os.path.basename(file_path)}: 학생 글 내용이 없습니다.")
                    except ValueError as e:
                        st.warning(f"⚠️ {os.path.basename(file_path)}: 점수 형식 오류 - {e}")
                else:
                    st.warning(f"⚠️ {os.path.basename(file_path)}: 파일 형식이 올바르지 않습니다. (줄 수: {len(lines)})")
                    
            except Exception as e:
                st.warning(f"⚠️ {os.path.basename(file_path)} 처리 오류: {e}")
        
        st.info(f"📚 연습1 (grade): {grade_count}개 파일 로드 완료")
        
    except Exception as e:
        st.error(f"❌ grade 폴더 접근 오류: {e}")
    
    try:
        # score 폴더의 모든 txt 파일을 glob으로 찾기
        score_pattern = "data/score/*.txt"
        score_files = glob.glob(score_pattern)
        score_files.sort()  # 파일명 순으로 정렬
        
        st.write(f"🔍 score 폴더에서 발견된 파일들: {[os.path.basename(f) for f in score_files]}")
        
        # 연습2용 데이터 로드 (기존 파싱 로직 적용)
        score_count = 0
        for i, file_path in enumerate(score_files[:15], 1):  # 최대 15개
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
                    st.warning(f"⚠️ {os.path.basename(file_path)}: 인코딩을 읽을 수 없습니다.")
                    continue
                
                # 기존 파싱 로직: 줄바꿈으로 분리
                lines = content.strip().split('\n')
                
                if len(lines) >= 6:  # 최소 6줄 이상이어야 함
                    # 정답 정보 추출 (첫 5줄)
                    try:
                        file_id = int(lines[0].strip())  # 1행: 글 번호
                        correct_grade = int(lines[1].strip())  # 2행: 등급 답
                        content_score = int(lines[2].strip())  # 3행: 내용 점수
                        organization_score = int(lines[3].strip())  # 4행: 조직 점수
                        expression_score = int(lines[4].strip())  # 5행: 표현 점수
                        
                        # 실제 학생 글 내용 (6번째 줄부터)
                        student_text = '\n'.join(lines[5:]).strip()
                        
                        if student_text and len(student_text) > 10:  # 최소 길이 확인
                            samples.append({
                                'id': i + 15,
                                'file_id': file_id,  # 파일 내 글 번호 (피드백 이미지용)
                                'text': student_text,
                                'correct_grade': correct_grade,
                                'content_score': content_score,
                                'organization_score': organization_score,
                                'expression_score': expression_score,
                                'type': 'score'
                            })
                            score_count += 1
                            st.success(f"✅ {os.path.basename(file_path)} 로드 성공 (글번호: {file_id})")
                        else:
                            st.warning(f"⚠️ {os.path.basename(file_path)}: 학생 글 내용이 없습니다.")
                    except ValueError as e:
                        st.warning(f"⚠️ {os.path.basename(file_path)}: 점수 형식 오류 - {e}")
                else:
                    st.warning(f"⚠️ {os.path.basename(file_path)}: 파일 형식이 올바르지 않습니다. (줄 수: {len(lines)})")
                    
            except Exception as e:
                st.warning(f"⚠️ {os.path.basename(file_path)} 처리 오류: {e}")
        
        st.info(f"📊 연습2 (score): {score_count}개 파일 로드 완료")
        
    except Exception as e:
        st.error(f"❌ score 폴더 접근 오류: {e}")
    
    # 결과 반환
    if len(samples) > 0:
        st.success(f"🎉 glob 패턴으로 총 {len(samples)}개 파일 로드 성공!")
        return samples
    else:
        st.error("❌ 모든 시도 실패. 샘플 데이터로 대체합니다.")
        return generate_fallback_data()

def generate_fallback_data():
    """txt 파일 로딩 실패 시 대체 샘플 데이터"""
    st.info("대체 샘플 데이터를 생성합니다.")
    
    # 실제 학생 글 예시 (제공해주신 내용)
    sample_text = """과학 연구를 위해 동물실험을 하는 것에 대해 반대한다. 왜냐하면 참고 자료에도 나와있다시피 쥐나 개, 고양이에 대한 실험에서는 아무런 부작용이 없었지만 사람이나 원숭이에게는 뼈가 성장하지 않거나 기형아가 발생하거나, 쥐에게는 독성을 보였지만 사람이나 원숭이에게는 효과가 좋았다고 한다. 이처럼 많은 의약품이 동물과 인간에게 나타나는 효과가 다르다. 그래서 모든 부작용을 정확하게 예측할 수 없기 때문에 이 동물실험에 의미가 있는지 의문이고, 동물과 사람이 공유하는 병은 1%정도로 극히 드물기 때문에 더 의문이 든다."""
    
    samples = []
    
    # 연습1용 샘플 데이터
    for i in range(15):
        samples.append({
            'id': i + 1,
            'file_id': i + 1,
            'text': sample_text + f" (연습1 샘플 문제 {i+1}번)",
            'correct_grade': 3,
            'content_score': 12,
            'organization_score': 7,
            'expression_score': 7,
            'type': 'grade'
        })
    
    # 연습2용 샘플 데이터
    for i in range(15):
        samples.append({
            'id': i + 16,
            'file_id': i + 1,
            'text': sample_text + f" (연습2 샘플 문제 {i+1}번)",
            'correct_grade': 3,
            'content_score': 12,
            'organization_score': 7,
            'expression_score': 7,
            'type': 'score'
        })
    
    return samples

def show_intro_page():
    """소개 페이지"""
    st.title("🎯 SEP ME ver.6")
    st.subheader("학생 글 채점 연습 프로그램")
    
    st.markdown("""
    **SEP ME**는 학생 글 채점 능력 향상을 위한 AI 기반 학습 도구입니다.
    실제 학생들이 작성한 글을 바탕으로 채점 연습을 할 수 있습니다.
    """)
    
    # 사용자 정보 입력
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
    
    st.info("평가를 시작하기 전에 쓰기 과제 및 쓰기 평가 기준을 확인해 주세요.")
    
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
    
    # 영역별 점수 기준
    st.subheader("📝 영역별 점수 기준")
    score_df = pd.DataFrame({
        '영역': ['내용', '조직', '표현'],
        '점수 범위': ['3-18점', '2-12점', '2-12점'],
        '평가 요소': [
            '주제 적합성, 내용의 충실성, 독창성',
            '글의 구성, 단락 구성, 논리적 연결',
            '어휘 사용, 문장 표현, 맞춤법'
        ]
    })
    st.table(score_df)
    
    # 체크리스트
    st.subheader("✅ 평가 전 점검 항목")
    
    with st.form("checklist"):
        st.markdown("**상위 인지 요소 점검**")
        
        check1 = st.checkbox("1. 학생 글을 평가하는 목적을 설정하고 평가 전략을 세웠다.")
        check2 = st.checkbox("2. 쓰기 과제 및 평가 기준을 확인하고 변별 방법을 점검했다.")
        check3 = st.checkbox("3. 평가 기준을 고려하여 예시문의 특징을 정확히 파악했다.")
        check4 = st.checkbox("4. 평가 기준에 적합한 학생 글의 예를 머릿속으로 떠올렸다.")
        check5 = st.checkbox("5. 학생 글을 일관되게 평가할 것을 다짐했다.")
        check6 = st.checkbox("6. 학생 글을 공정하고 객관적으로 평가할 것을 다짐했다.")
        check7 = st.checkbox("7. 평가 과정과 결과를 반성적으로 점검할 것을 다짐했다.")
        
        if st.form_submit_button("다음 단계로 →", type="primary", use_container_width=True):
            if all([check1, check2, check3, check4, check5, check6, check7]):
                st.session_state.stage = 'practice_selection'
                st.session_state.student_data = load_student_texts()
                st.success("모든 준비가 완료되었습니다! 연습 유형을 선택해주세요.")
                st.rerun()
            else:
                st.warning("모든 항목을 확인해주세요.")

def show_practice_selection():
    """연습 유형 선택 페이지"""
    st.title("🎯 연습 유형 선택")
    
    st.markdown("""
    어떤 연습을 하시겠습니까? 각 연습은 15문제로 구성되어 있습니다.
    """)
    
    # 연습 유형 선택 카드
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
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3>📚 연습1: 등급 추정</h3>
            <p>학생 글을 읽고 1~5등급 중 선택</p>
            <ul style="text-align: left; margin-top: 1rem;">
                <li>15개의 학생 글 제시</li>
                <li>1~5등급 중 선택</li>
                <li>즉시 피드백 제공</li>
                <li>등급별 특성 학습</li>
            </ul>
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
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        ">
            <h3>📊 연습2: 점수 추정</h3>
            <p>내용/조직/표현 영역별 점수 입력</p>
            <ul style="text-align: left; margin-top: 1rem;">
                <li>15개의 학생 글 제시</li>
                <li>내용/조직/표현 영역별 점수</li>
                <li>상세 분석 제공</li>
                <li>정확한 채점 기준 학습</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📊 연습2 시작하기", type="primary", use_container_width=True):
            st.session_state.selected_practice = 'practice2'
            st.session_state.stage = 'practice2'
            st.session_state.current_question = 1
            st.rerun()
    
    # 두 연습 모두 하기 옵션
    st.markdown("---")
    col_both1, col_both2, col_both3 = st.columns([1, 2, 1])
    
    with col_both2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        ">
            <h4>🎯 두 연습 모두 하기</h4>
            <p>연습1 완료 후 자동으로 연습2로 이동</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎯 두 연습 모두 시작하기", type="secondary", use_container_width=True):
            st.session_state.selected_practice = 'both'
            st.session_state.stage = 'practice1'
            st.session_state.current_question = 1
            st.rerun()

def show_practice1():
    """연습1 - 등급 추정"""
    st.title("📚 연습1: 글의 등급 추정하기")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    
    # 현재 문제 데이터 가져오기
    if 'student_data' in st.session_state and st.session_state.student_data:
        # 연습1용 데이터만 필터링
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
            <strong>문제 {st.session_state.current_question}번</strong><br><br>
            {current_data['text']}
            </div>
            """, unsafe_allow_html=True)
            
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
                    
                    # 피드백 이미지 표시 (file_id 기반)
                    feedback_path = f"data/f_grade/{current_data['file_id']}.png"
                    if os.path.exists(feedback_path):
                        st.image(feedback_path, caption="상세 피드백")
                    else:
                        # 대체 경로 시도 (g_feed 폴더)
                        alt_feedback_path = f"data/g_feed/{current_data['file_id']}.png"
                        if os.path.exists(alt_feedback_path):
                            st.image(alt_feedback_path, caption="상세 피드백")
                
                # 다음 문제로
                st.markdown("---")
                col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
                
                with col_btn2:
                    if st.session_state.current_question < 15:
                        if st.button("다음 문제 →", type="primary", use_container_width=True):
                            st.session_state.current_question += 1
                            st.rerun()
                    else:
                        # 연습1 완료 후 다음 단계 결정
                        if st.session_state.selected_practice == 'both':
                            if st.button("연습2로 이동 →", type="primary", use_container_width=True):
                                st.session_state.stage = 'practice2'
                                st.session_state.current_question = 1
                                st.rerun()
                        elif st.session_state.selected_practice == 'practice1':
                            if st.button("결과 보기 →", type="primary", use_container_width=True):
                                st.session_state.stage = 'results'
                                st.rerun()
                        else:
                            # 기본값: 연습2로 이동
                            if st.button("연습2로 이동 →", type="primary", use_container_width=True):
                                st.session_state.stage = 'practice2'
                                st.session_state.current_question = 1
                                st.rerun()
        else:
            st.error(f"연습1 데이터가 부족합니다. (현재: {len(grade_data)}개, 필요: 15개)")
    else:
        st.error("학생 글 데이터를 로드할 수 없습니다.")

def show_practice2():
    """연습2 - 점수 추정"""
    st.title("📊 연습2: 글의 점수 추정하기")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.markdown(f"**진행 상황: {st.session_state.current_question}/15 문제**")
    
    # 현재 문제 데이터 가져오기
    if 'student_data' in st.session_state and st.session_state.student_data:
        # 연습2용 데이터만 필터링
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
            <strong>문제 {st.session_state.current_question}번</strong><br><br>
            {current_data['text']}
            </div>
            """, unsafe_allow_html=True)
            
            # 점수 입력
            st.markdown("### 🎯 영역별 점수를 입력하세요")
            
            with st.form(f"score_form_{st.session_state.current_question}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**내용 영역 (3-18점)**")
                    st.caption("주제 적합성, 내용의 충실성, 독창성")
                    content = st.number_input("내용 점수", min_value=3, max_value=18, value=10, label_visibility="collapsed")
                
                with col2:
                    st.markdown("**조직 영역 (2-12점)**")
                    st.caption("글의 구성, 단락 구성, 논리적 연결")
                    organization = st.number_input("조직 점수", min_value=2, max_value=12, value=7, label_visibility="collapsed")
                
                with col3:
                    st.markdown("**표현 영역 (2-12점)**")
                    st.caption("어휘 사용, 문장 표현, 맞춤법")
                    expression = st.number_input("표현 점수", min_value=2, max_value=12, value=7, label_visibility="collapsed")
                
                total = content + organization + expression
                
                # 총점 표시
                st.markdown("---")
                col_total1, col_total2, col_total3 = st.columns(3)
                with col_total2:
                    st.markdown(f"""
                    <div style="
                        background: white;
                        padding: 1.5rem;
                        border-radius: 12px;
                        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                        text-align: center;
                        border: 1px solid #e9ecef;
                    ">
                    <h3>총점: {total}점</h3>
                    <h4>예상 등급: {score_to_grade(total)}등급</h4>
                    </div>
                    """, unsafe_allow_html=True)
                
                if st.form_submit_button("점수 제출하기", type="primary", use_container_width=True):
                    # 결과 저장
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
                        'timestamp': datetime.now()
                    }
                    
                    # 중복 저장 방지
                    if not any(r['question'] == st.session_state.current_question for r in st.session_state.practice2_results):
                        st.session_state.practice2_results.append(result)
                    
                    # 피드백
                    show_score_feedback(result, current_data['file_id'])
                    
                    # 다음 문제로
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
    """총점을 등급으로 변환"""
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
    """점수 피드백 표시"""
    content_diff = result['content'] - result['correct_content']
    org_diff = result['organization'] - result['correct_organization']
    exp_diff = result['expression'] - result['correct_expression']
    total_diff = result['total'] - result['correct_total']
    
    st.markdown("### 📊 채점 결과 분석")
    
    # 점수 비교 표시
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "내용 영역",
            f"{result['content']}점",
            f"{content_diff:+d}점"
        )
        st.caption(f"정답: {result['correct_content']}점")
    
    with col2:
        st.metric(
            "조직 영역", 
            f"{result['organization']}점",
            f"{org_diff:+d}점"
        )
        st.caption(f"정답: {result['correct_organization']}점")
    
    with col3:
        st.metric(
            "표현 영역",
            f"{result['expression']}점", 
            f"{exp_diff:+d}점"
        )
        st.caption(f"정답: {result['correct_expression']}점")
    
    with col4:
        st.metric(
            "총점",
            f"{result['total']}점",
            f"{total_diff:+d}점"
        )
        st.caption(f"정답: {result['correct_total']}점")
    
    # 정확도 평가
    abs_total_diff = abs(total_diff)
    if abs_total_diff <= 2:
        st.success("🎉 매우 정확한 채점입니다! 훌륭한 평가 능력을 보여주셨습니다.")
    elif abs_total_diff <= 5:
        st.info("👍 양호한 채점입니다. 조금 더 세밀한 관찰이 필요합니다.")
    else:
        st.warning("💡 채점 기준을 다시 검토해보세요. 각 영역별 특성을 더 자세히 살펴보시기 바랍니다.")
    
    # 피드백 이미지 표시 (file_id 기반)
    feedback_path = f"data/f_score/{file_id}.png"
    if os.path.exists(feedback_path):
        st.image(feedback_path, caption="상세 피드백")
    else:
        # 대체 경로 시도 (s_feed 폴더)
        alt_feedback_path = f"data/s_feed/{file_id}.png"
        if os.path.exists(alt_feedback_path):
            st.image(alt_feedback_path, caption="상세 피드백")

def show_results():
    """결과 페이지"""
    st.title("🎉 학습 완료!")
    st.balloons()
    
    # 완료 메시지
    total_time = datetime.now() - st.session_state.start_time
    st.success(f"🎊 {st.session_state.user_name}님, 연습을 완료하셨습니다! (소요시간: {total_time.seconds // 60}분)")
    
    # 선택한 연습에 따른 결과 표시
    if st.session_state.selected_practice == 'practice1':
        st.info("📚 연습1 (등급 추정) 결과만 표시됩니다.")
    elif st.session_state.selected_practice == 'practice2':
        st.info("📊 연습2 (점수 추정) 결과만 표시됩니다.")
    else:
        st.info("🎯 두 연습 모두 완료하셨습니다!")
    
    # 결과 요약
    st.markdown("### 📊 종합 결과")
    
    # 동적으로 컬럼 수 조정
    results_available = []
    if st.session_state.practice1_results:
        results_available.append('practice1')
    if st.session_state.practice2_results:
        results_available.append('practice2')
    
    if len(results_available) == 1:
        col1, col2, col3 = st.columns(3)
        cols = [col1, col2, col3]
    else:
        col1, col2, col3, col4 = st.columns(4)
        cols = [col1, col2, col3, col4]
    
    col_idx = 0
    
    # 연습1 결과
    if st.session_state.practice1_results:
        p1_correct = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
        p1_accuracy = (p1_correct / len(st.session_state.practice1_results)) * 100
        
        with cols[col_idx]:
            st.metric("연습1 정답률", f"{p1_accuracy:.1f}%", f"{p1_correct}/15")
        col_idx += 1
    
    # 연습2 결과
    if st.session_state.practice2_results:
        avg_error = np.mean([abs(r['total'] - r['correct_total']) for r in st.session_state.practice2_results])
        accuracy = max(0, 100 - avg_error * 8)
        
        with cols[col_idx]:
            st.metric("연습2 정확도", f"{accuracy:.1f}%")
        col_idx += 1
        
        if col_idx < len(cols):
            with cols[col_idx]:
                st.metric("평균 오차", f"{avg_error:.1f}점")
            col_idx += 1
    
    # 전체 성과 (두 연습 모두 완료한 경우)
    if st.session_state.practice1_results and st.session_state.practice2_results and col_idx < len(cols):
        with cols[col_idx]:
            overall_score = (p1_accuracy + accuracy) / 2
            st.metric("종합 점수", f"{overall_score:.1f}점")
    
    # 상세 결과 표시
    st.markdown("---")
    
    # 탭 구성 (완료한 연습에 따라)
    tabs = []
    if st.session_state.practice1_results:
        tabs.append("📈 연습1 결과")
    if st.session_state.practice2_results:
        tabs.append("📊 연습2 결과")
    
    if len(tabs) == 1:
        # 하나의 연습만 완료한 경우
        st.markdown(f"### {tabs[0]}")
        if st.session_state.practice1_results:
            results_df = pd.DataFrame(st.session_state.practice1_results)
            display_df = results_df[['question', 'selected', 'correct', 'is_correct']].copy()
            display_df.columns = ['문제번호', '선택등급', '정답등급', '정답여부']
            display_df['정답여부'] = display_df['정답여부'].map({True: '✅', False: '❌'})
            st.dataframe(display_df, use_container_width=True)
        else:
            results_df = pd.DataFrame(st.session_state.practice2_results)
            display_df = results_df[['question', 'content', 'organization', 'expression', 'total', 'correct_total']].copy()
            display_df.columns = ['문제번호', '내용점수', '조직점수', '표현점수', '총점', '정답총점']
            display_df['점수차이'] = display_df['총점'] - display_df['정답총점']
            st.dataframe(display_df, use_container_width=True)
    else:
        # 두 연습 모두 완료한 경우
        tab1, tab2 = st.tabs(tabs)
        
        with tab1:
            if st.session_state.practice1_results:
                results_df = pd.DataFrame(st.session_state.practice1_results)
                display_df = results_df[['question', 'selected', 'correct', 'is_correct']].copy()
                display_df.columns = ['문제번호', '선택등급', '정답등급', '정답여부']
                display_df['정답여부'] = display_df['정답여부'].map({True: '✅', False: '❌'})
                st.dataframe(display_df, use_container_width=True)
        
        with tab2:
            if st.session_state.practice2_results:
                results_df = pd.DataFrame(st.session_state.practice2_results)
                display_df = results_df[['question', 'content', 'organization', 'expression', 'total', 'correct_total']].copy()
                display_df.columns = ['문제번호', '내용점수', '조직점수', '표현점수', '총점', '정답총점']
                display_df['점수차이'] = display_df['총점'] - display_df['정답총점']
                st.dataframe(display_df, use_container_width=True)
    
    # 액션 버튼들
    st.markdown("---")
    col_action1, col_action2, col_action3 = st.columns(3)
    
    with col_action1:
        if st.button("📊 결과 다운로드", use_container_width=True):
            # CSV 다운로드 기능
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
            # 기존 결과는 유지하고 새로운 연습만 시작
            st.rerun()
    
    with col_action3:
        if st.button("🏠 처음으로", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

def create_results_csv():
    """결과를 CSV 형태로 생성"""
    data = {
        'user_name': st.session_state.user_name,
        'selected_practice': st.session_state.selected_practice,
        'completion_time': datetime.now().isoformat(),
        'total_time_minutes': (datetime.now() - st.session_state.start_time).seconds // 60
    }
    
    # 연습1 결과 요약
    if st.session_state.practice1_results:
        p1_correct = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
        data['practice1_accuracy'] = (p1_correct / 15) * 100
        data['practice1_correct_count'] = p1_correct
    
    # 연습2 결과 요약
    if st.session_state.practice2_results:
        avg_error = np.mean([abs(r['total'] - r['correct_total']) for r in st.session_state.practice2_results])
        data['practice2_avg_error'] = avg_error
        data['practice2_accuracy'] = max(0, 100 - avg_error * 8)
    
    df = pd.DataFrame([data])
    return df.to_csv(index=False, encoding='utf-8-sig')

def main():
    # 세션 상태 초기화
    initialize_session_state()
    
    # 사이드바
    st.sidebar.title("📊 진행 현황")
    
    if st.session_state.user_name:
        st.sidebar.success(f"👋 {st.session_state.user_name}님")
        
        # 선택한 연습 표시
        if st.session_state.selected_practice:
            practice_name = {
                'practice1': '📚 연습1 (등급 추정)',
                'practice2': '📊 연습2 (점수 추정)',
                'both': '🎯 두 연습 모두'
            }.get(st.session_state.selected_practice, '연습 선택됨')
            st.sidebar.info(f"선택한 연습: {practice_name}")
        
        # 경과 시간
        elapsed = datetime.now() - st.session_state.start_time
        st.sidebar.metric("⏱️ 경과 시간", f"{elapsed.seconds // 60}분 {elapsed.seconds % 60}초")
        
        # 진행률 표시
        if st.session_state.stage in ['practice1', 'practice2']:
            progress = (st.session_state.current_question - 1) / 15
            st.sidebar.progress(progress)
            stage_name = "연습1" if st.session_state.stage == 'practice1' else "연습2"
            st.sidebar.write(f"**{stage_name} 진행률**: {st.session_state.current_question}/15")
            
            if st.session_state.practice1_results:
                correct_count = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
                st.sidebar.metric("연습1 정답률", f"{(correct_count/len(st.session_state.practice1_results)*100):.1f}%")
    
    # 도움말
    with st.sidebar.expander("❓ 사용 가이드"):
        st.markdown("""
        **📚 연습1 - 등급 추정**
        - 학생 글을 읽고 1~5등급 중 선택
        - 즉시 정답 여부와 피드백 제공
        
        **📊 연습2 - 점수 추정**
        - 내용/조직/표현 영역별 점수 입력
        - 각 영역별 상세 분석 제공
        
        **💡 팁**
        - 평가 기준을 숙지하고 시작하세요
        - 천천히 읽고 신중하게 판단하세요
        - 피드백을 통해 학습하세요
        """)
    
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
