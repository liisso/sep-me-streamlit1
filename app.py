import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime
import random

# 페이지 설정
st.set_page_config(
    page_title="SEP ME ver.6 - 학생 글 채점 연습",
    page_icon="📝",
    layout="wide"
)

# 세션 상태 초기화
if 'stage' not in st.session_state:
    st.session_state.stage = 'intro'
    st.session_state.user_name = ''
    st.session_state.current_question = 1
    st.session_state.practice1_results = []
    st.session_state.practice2_results = []
    st.session_state.start_time = datetime.now()

def load_sample_data():
    """샘플 데이터 로드"""
    # 실제 파일이 있으면 로드, 없으면 샘플 데이터 생성
    try:
        if os.path.exists("data/samples.csv"):
            df = pd.read_csv("data/samples.csv")
            return df.to_dict('records')
    except:
        pass
    
    # 샘플 데이터 생성
    sample_texts = []
    for i in range(30):
        sample_texts.append({
            'id': i + 1,
            'text': f"환경 보호는 우리 모두의 책임입니다. 지구 온난화로 인해 빙하가 녹고 있고, 해수면이 상승하고 있습니다. 우리는 일회용품 사용을 줄이고, 재활용을 실천해야 합니다. (문제 {i+1}번 샘플 텍스트)",
            'correct_grade': random.randint(1, 5),
            'content_score': random.randint(8, 16),
            'organization_score': random.randint(4, 10),
            'expression_score': random.randint(4, 10)
        })
    return sample_texts

def show_intro_page():
    """소개 페이지"""
    st.title("🎯 SEP ME ver.6")
    st.subheader("학생 글 채점 연습 프로그램")
    
    # 사용자 정보 입력
    with st.form("user_info"):
        name = st.text_input("이름을 입력해주세요:")
        agreement = st.checkbox("개인정보 수집 및 이용에 동의합니다")
        
        if st.form_submit_button("시작하기", type="primary"):
            if name and agreement:
                st.session_state.user_name = name
                st.session_state.stage = 'assignment_info'
                st.rerun()
            else:
                st.error("이름을 입력하고 동의해주세요.")

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
    
    if st.button("연습 시작하기", type="primary"):
        st.session_state.stage = 'practice1'
        st.session_state.student_data = load_sample_data()
        st.rerun()

def show_practice1():
    """연습1 - 등급 추정"""
    st.title("📚 연습1: 글의 등급 추정하기")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.write(f"진행 상황: {st.session_state.current_question}/15")
    
    # 현재 문제
    if 'student_data' in st.session_state:
        current_data = st.session_state.student_data[st.session_state.current_question - 1]
        
        st.subheader(f"📖 문제 {st.session_state.current_question}번")
        st.write(current_data['text'])
        
        # 등급 선택
        st.subheader("🎯 이 글의 등급을 선택하세요")
        
        cols = st.columns(5)
        selected_grade = None
        
        for i, grade in enumerate([1, 2, 3, 4, 5]):
            with cols[i]:
                if st.button(f"{grade}등급", key=f"grade_{grade}", use_container_width=True):
                    selected_grade = grade
        
        if selected_grade:
            # 결과 저장
            is_correct = selected_grade == current_data['correct_grade']
            result = {
                'question': st.session_state.current_question,
                'selected': selected_grade,
                'correct': current_data['correct_grade'],
                'is_correct': is_correct
            }
            st.session_state.practice1_results.append(result)
            
            # 피드백
            if is_correct:
                st.success("🎉 정답입니다!")
            else:
                st.error(f"오답입니다. 정답: {current_data['correct_grade']}등급")
            
            # 다음 문제로
            if st.session_state.current_question < 15:
                if st.button("다음 문제 →", type="primary"):
                    st.session_state.current_question += 1
                    st.rerun()
            else:
                if st.button("연습2로 이동 →", type="primary"):
                    st.session_state.stage = 'practice2'
                    st.session_state.current_question = 1
                    st.rerun()

def show_practice2():
    """연습2 - 점수 추정"""
    st.title("📊 연습2: 글의 점수 추정하기")
    
    # 진행률
    progress = (st.session_state.current_question - 1) / 15
    st.progress(progress)
    st.write(f"진행 상황: {st.session_state.current_question}/15")
    
    # 현재 문제
    if 'student_data' in st.session_state:
        current_data = st.session_state.student_data[15 + st.session_state.current_question - 1]
        
        st.subheader(f"📖 문제 {st.session_state.current_question}번")
        st.write(current_data['text'])
        
        # 점수 입력
        st.subheader("🎯 영역별 점수를 입력하세요")
        
        with st.form(f"score_form_{st.session_state.current_question}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                content = st.number_input("내용 (3-18점)", min_value=3, max_value=18, value=10)
            with col2:
                organization = st.number_input("조직 (2-12점)", min_value=2, max_value=12, value=7)
            with col3:
                expression = st.number_input("표현 (2-12점)", min_value=2, max_value=12, value=7)
            
            total = content + organization + expression
            st.write(f"**총점: {total}점**")
            
            if st.form_submit_button("제출하기", type="primary"):
                # 결과 저장
                result = {
                    'question': st.session_state.current_question,
                    'content': content,
                    'organization': organization,
                    'expression': expression,
                    'total': total,
                    'correct_total': current_data['content_score'] + current_data['organization_score'] + current_data['expression_score']
                }
                st.session_state.practice2_results.append(result)
                
                # 피드백
                diff = abs(total - result['correct_total'])
                if diff <= 2:
                    st.success("🎉 매우 정확한 채점입니다!")
                elif diff <= 5:
                    st.info("👍 양호한 채점입니다.")
                else:
                    st.warning("💡 채점 기준을 다시 검토해보세요.")
                
                # 다음 문제로
                if st.session_state.current_question < 15:
                    if st.button("다음 문제 →", type="primary"):
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("결과 보기 →", type="primary"):
                        st.session_state.stage = 'results'
                        st.rerun()

def show_results():
    """결과 페이지"""
    st.title("🎉 연습 완료!")
    st.balloons()
    
    st.success(f"{st.session_state.user_name}님, 모든 연습을 완료하셨습니다!")
    
    # 결과 요약
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.practice1_results:
            correct = sum(1 for r in st.session_state.practice1_results if r['is_correct'])
            accuracy = (correct / 15) * 100
            st.metric("연습1 정답률", f"{accuracy:.1f}%")
    
    with col2:
        if st.session_state.practice2_results:
            avg_error = np.mean([abs(r['total'] - r['correct_total']) for r in st.session_state.practice2_results])
            st.metric("연습2 평균 오차", f"{avg_error:.1f}점")
    
    if st.button("🔄 다시 시작하기"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# 메인 실행
def main():
    # 사이드바
    st.sidebar.title("📊 진행 현황")
    if st.session_state.user_name:
        st.sidebar.success(f"👋 {st.session_state.user_name}님")
    
    if st.sidebar.button("🏠 처음으로"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # 단계별 페이지 표시
    if st.session_state
