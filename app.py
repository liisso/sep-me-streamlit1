import streamlit as st
import pandas as pd
import os
from datetime import datetime

def load_student_texts():
    samples = []
    # grade 폴더
    grade_files = sorted([f for f in os.listdir("data/grade") if f.endswith('.txt')])
    for filename in grade_files:
        with open(f"data/grade/{filename}", encoding='utf-8') as f:
            lines = f.read().split('\n')
        if len(lines) < 6:
            continue
        file_id = int(lines[0].strip())
        correct_grade = int(lines[1].strip())
        content_score = int(lines[2].strip())
        organization_score = int(lines[3].strip())
        expression_score = int(lines[4].strip())
        student_text = '\n'.join(lines[5:]).strip()
        if not student_text:
            continue
        samples.append({
            'file_id': file_id,
            'text': student_text,
            'correct_grade': correct_grade,
            'content_score': content_score,
            'organization_score': organization_score,
            'expression_score': expression_score,
            'type': 'grade',
            'filename': filename
        })
    # score 폴더
    score_files = sorted([f for f in os.listdir("data/score") if f.endswith('.txt')])
    for filename in score_files:
        with open(f"data/score/{filename}", encoding='utf-8') as f:
            lines = f.read().split('\n')
        if len(lines) < 6:
            continue
        file_id = int(lines[0].strip())
        correct_grade = int(lines[1].strip())
        content_score = int(lines[2].strip())
        organization_score = int(lines[3].strip())
        expression_score = int(lines[4].strip())
        student_text = '\n'.join(lines[5:]).strip()
        if not student_text:
            continue
        samples.append({
            'file_id': file_id,
            'text': student_text,
            'correct_grade': correct_grade,
            'content_score': content_score,
            'organization_score': organization_score,
            'expression_score': expression_score,
            'type': 'score',
            'filename': filename
        })
    return samples

def show_practice(samples, practice_type):
    st.header("✏️ 학생 글 채점 연습")
    data = [s for s in samples if s['type'] == practice_type]
    for idx, sample in enumerate(data, 1):
        st.markdown(f"### 문제 {idx}: {sample['filename']} (문제번호: {sample['file_id']})")
        st.markdown(
            f"<div style='background:#f8f9fa;padding:1rem;border-radius:10px;white-space:pre-wrap'>{sample['text']}</div>",
            unsafe_allow_html=True
        )
        if practice_type == 'grade':
            grade = st.radio(
                "등급을 선택하세요",
                options=[1,2,3,4,5],
                format_func=lambda x: f"{x}등급",
                key=f"grade_{idx}"
            )
            if st.button(f"정답 확인_{idx}"):
                st.success(f"정답: {sample['correct_grade']}등급")
                img_path = f"data/f_grade/{sample['file_id']}.png"
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"피드백 이미지: {sample['file_id']}.png")
                else:
                    st.info("피드백 이미지가 없습니다.")
        else:
            st.write("내용/조직/표현 점수를 입력하세요.")
            content = st.number_input("내용(3-18)", 3, 18, key=f"content_{idx}")
            org = st.number_input("조직(2-12)", 2, 12, key=f"org_{idx}")
            expr = st.number_input("표현(2-12)", 2, 12, key=f"expr_{idx}")
            if st.button(f"정답 확인_{idx}"):
                st.success(
                    f"정답: 내용 {sample['content_score']} / 조직 {sample['organization_score']} / 표현 {sample['expression_score']}"
                )
                img_path = f"data/f_score/{sample['file_id']}.png"
                if os.path.exists(img_path):
                    st.image(img_path, caption=f"피드백 이미지: {sample['file_id']}.png")
                else:
                    st.info("피드백 이미지가 없습니다.")

def main():
    st.set_page_config(page_title="SEP ME ver.6", layout="wide")
    st.title("SEP ME - 학생 글 채점 연습")
    st.sidebar.title("설정")
    practice_type = st.sidebar.radio(
        "연습 유형 선택", ("등급 맞추기", "점수 맞추기")
    )
    samples = load_student_texts()
    if practice_type == "등급 맞추기":
        show_practice(samples, "grade")
    else:
        show_practice(samples, "score")

if __name__ == "__main__":
    main()
