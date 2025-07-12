import streamlit as st
import random
import requests
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="논설문 평가 연습", layout="wide")

# --- 초기 세션 설정 ---
import time
for key in ["username", "mode", "submitted", "page", "current_text_grade", "current_text_score", "next_trigger"]:
    if key not in st.session_state:
        st.session_state[key] = None
st.session_state.page = st.session_state.page or "intro"

# --- 사이드바 ---
with st.sidebar:
    st.header("📌 진행 내역")
    st.write("사용자:", st.session_state.get("username", "(미입력)"))
    st.write("현재 모드:", st.session_state.get("mode", "등급 추정 연습"))
    current_text = st.session_state.get("current_text_grade") if st.session_state.mode == "등급 추정 연습" else st.session_state.get("current_text_score")
    st.write("현재 문항 번호:", current_text[0] if current_text else "(없음)")
    st.write("진행률:", f"{current_text[0]} / 15" if current_text else "(없음)")
    if st.button("◀ 이전 화면으로 이동"):
        st.session_state.page = "instructions"
        st.session_state.current_text_grade = None
        st.session_state.current_text_score = None
        st.session_state.submitted = False

# --- 유틸 함수 ---
def load_image_from_url(url):
    r = requests.get(url)
    if r.status_code == 200 and "image" in r.headers.get("Content-Type", ""):
        return BytesIO(r.content)
    return None

def load_texts_from_github(folder):
    base_url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/{folder}/"
    api_url = f"https://api.github.com/repos/liisso/sep-me-streamlit1/contents/data/{folder}"
    try:
        res = requests.get(api_url).json()
        return [r.text.splitlines() for f in res if f['name'].endswith('.txt') and (r := requests.get(base_url + f['name'])).status_code == 200]
    except:
        return []

if st.session_state.next_trigger:
    st.session_state.next_trigger = False
    st.experimental_rerun()

# --- 화면 렌더링 ---

# 결과 다운로드 기능
import pandas as pd
import io

if (
    (st.session_state.get("score_results") and st.session_state.get("current_text_score") and int(st.session_state.current_text_score[0]) == 15)
    or
    (st.session_state.get("grade_results") and st.session_state.get("current_text_grade") and int(st.session_state.current_text_grade[0]) == 15)
):
    df_score = pd.DataFrame(st.session_state.get("score_results", []))
    df_grade = pd.DataFrame(st.session_state.get("grade_results", []))

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
    summary_df = pd.DataFrame({
        "사용자명": [st.session_state.username],
        "등급 추정 소요 시간 (분:초)": [grade_time],
        "점수 추정 소요 시간 (분:초)": [score_time]
    })
    summary_df.to_excel(writer, index=False, sheet_name="연습 시간 요약")
    if not df_score.empty:
        df_score["총점 (정답)"] = df_score[["내용 점수 (정답)", "조직 점수 (정답)", "표현 점수 (정답)"]].sum(axis=1)
        df_score["총점 (입력)"] = df_score[["내용 점수 (입력)", "조직 점수 (입력)", "표현 점수 (입력)"]].sum(axis=1)
        df_score.to_excel(writer, index=False, sheet_name="점수 추정 결과")
    if not df_grade.empty:
        df_grade.to_excel(writer, index=False, sheet_name="등급 추정 결과")

    st.sidebar.download_button(
        label="📥 연습 결과 다운로드 (Excel)",
        data=buffer.getvalue(),
        file_name=f"{st.session_state.username}_평가결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# 결과 다운로드 기능
if st.session_state.get("score_results"):
    import pandas as pd
    import io
    df = pd.DataFrame(st.session_state.score_results)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="점수 추정 결과")
        writer.save()
    st.sidebar.download_button(
        label="📥 점수 결과 다운로드 (Excel)",
        data=buffer.getvalue(),
        file_name=f"{st.session_state.username}_점수결과.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
if st.session_state.page == "intro":
    st.title("✍️ 논설문 평가 연습 프로그램 (SEP ME Web Edition)")
    st.header("1단계: 사용자 정보 입력")
    name = st.text_input("이름을 입력하세요")
    agree = st.checkbox("입력한 이름으로 연습 결과가 저장됨에 동의합니다")
    if name and agree and st.button("다음 단계로 진행"):
    st.session_state.grade_start_time = None
    st.session_state.score_start_time = None
        st.session_state.username = name
        st.session_state.page = "instructions"

elif st.session_state.page == "instructions":
    st.title("📌 연습 안내 및 과제 확인")
    for label, url in {
        "쓰기 과제": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/assignment.png",
        "평가 기준": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/standard.png",
        "등급별 예시문": "https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/prompt.jpg"
    }.items():
        if (img := load_image_from_url(url)):
            st.image(img, caption=label)
    if st.button("다음으로", key="to_practice"):
        st.session_state.page = "practice"

elif st.session_state.page == "practice":
    st.title(f"✍️ 논설문 평가 연습 - {st.session_state.username}님")
    st.markdown("### 상위 인지 점검 리스트")
    st.markdown("""
    - ✅ 글의 **주제가 분명히** 드러났는가?
    - ✅ 자신의 **주장이 일관성 있게** 유지되었는가?
    - ✅ 제시한 **근거가 충분하고 타당한가?**
    - ✅ 글의 **구성과 전개가 자연스러운가?**
    - ✅ 문장 **표현이 명확하고 오류가 없는가?**
    """)

    mode = st.radio("연습 모드를 선택하세요", ["등급 추정 연습", "점수 추정 연습"])
    st.session_state.mode = mode

    if mode == "등급 추정 연습":
        if st.session_state.grade_start_time is None:
            st.session_state.grade_start_time = time.time()
        st.subheader("🎯 [연습1] 학생 글의 등급 추정하기")
        texts = [txt for txt in load_texts_from_github("grade") if txt[0].strip().isdigit() and 1 <= int(txt[0].strip()) <= 15]
        existing_ids = sorted(int(txt[0].strip()) for txt in texts if 1 <= int(txt[0].strip()) <= 15)
        st.sidebar.write(f"📂 불러온 문항 번호: {existing_ids}")
        if not st.session_state.current_text_grade:
            st.session_state.current_text_grade = next((txt for txt in sorted(texts, key=lambda x: int(x[0])) if int(txt[0]) == 1), None)
        sel = st.session_state.current_text_grade
        text_id, correct_grade, student_text = sel[0], int(sel[1]), "\n".join(sel[5:])

        st.markdown("#### 학생 글")
        st.markdown(f"<div style='background:white; color:black; padding:1rem; border-radius:6px; border:1px solid #ccc;'>{student_text}</div>", unsafe_allow_html=True)
        user_grade = st.radio("예상 등급을 선택하세요", [1, 2, 3, 4, 5], horizontal=True)

        if st.button("제출", key="submit_grade"):
        # 결과 저장 기능 (추후 확장 가능)
        # st.session_state.result_log.append({...})
            st.session_state.submitted = True
            if user_grade == correct_grade:
                st.success("✅ 정답입니다!")
            else:
                st.error("❌ 오답입니다.")
                url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/f_grade/{text_id.strip()}.png"
                if (img := load_image_from_url(url)):
                    st.image(img, caption="등급 평가 해설")
                else:
                    st.warning(f"이미지를 불러올 수 없습니다: {url}")

            # 등급 결과 저장
            if "grade_results" not in st.session_state:
                st.session_state.grade_results = []
            st.session_state.grade_results.append({
                "이름": st.session_state.username,
                "문항 번호": text_id,
                "등급 (정답)": correct_grade,
                "등급 (입력)": user_grade
            })

        if st.session_state.submitted and st.button("다음 문제로 이동", key="next_grade"):
            current_id = int(st.session_state.current_text_grade[0])
            next_text = next((txt for txt in sorted(texts, key=lambda x: int(x[0].strip())) if int(txt[0].strip()) == current_id + 1), None)
            if next_text:
                st.session_state.current_text_grade = next_text
                st.session_state.submitted = False
            else:
                st.warning("✅ 모든 문항을 완료했습니다. 처음부터 다시 시작하려면 '이전 화면으로 이동'을 누르세요.")

    elif mode == "점수 추정 연습":
        if st.session_state.score_start_time is None:
            st.session_state.score_start_time = time.time()
        st.subheader("🧩 [연습2] 내용·조직·표현 점수 추정하기")
        texts = [txt for txt in load_texts_from_github("scre") if len(txt) >= 6 and txt[0].strip().isdigit() and 1 <= int(txt[0].strip()) <= 15]
        existing_ids = sorted(int(txt[0].strip()) for txt in texts)
        st.sidebar.write(f"📂 불러온 문항 번호: {existing_ids}")
        if not st.session_state.current_text_score:
            st.session_state.current_text_score = next((txt for txt in sorted(texts, key=lambda x: int(x[0].strip())) if int(txt[0].strip()) == 1), None)
        sel = st.session_state.current_text_score
        text_id, a_c, a_o, a_e = sel[0], int(sel[2]), int(sel[3]), int(sel[4])
        student_text = "\n".join(sel[5:])

        st.markdown("#### 학생 글")
        st.markdown(f"<div style='background:white; color:black; padding:1rem; border-radius:6px; border:1px solid #ccc;'>{student_text}</div>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1: user_c = st.number_input("내용 점수 (3~18)", min_value=3, max_value=18, step=1)
        with col2: user_o = st.number_input("조직 점수 (2~12)", min_value=2, max_value=12, step=1)
        with col3: user_e = st.number_input("표현 점수 (2~12)", min_value=2, max_value=12, step=1)

        if st.button("제출", key="submit_score"):
        # 결과 저장 기능 (추후 확장 가능)
        # st.session_state.result_log.append({...})
            st.session_state.submitted = True
            msgs = []
            for label, user, ans in [("내용", user_c, a_c), ("조직", user_o, a_o), ("표현", user_e, a_e)]:
                if abs(user - ans) <= 1:
                    msgs.append(f"✅ {label} 점수: 정답")
                else:
                    msgs.append(f"❌ {label} 점수: 오답")
            for m in msgs: st.write(m)
            if all("정답" in m for m in msgs):
                st.success("🎉 모든 점수를 정확히 맞추셨습니다!")
            else:
                st.error("📌 일부 점수가 오답입니다. 해설 이미지를 참고하세요.")
                url = f"https://raw.githubusercontent.com/liisso/sep-me-streamlit1/refs/heads/main/data/f_score/{text_id.strip()}.png"
                if (img := load_image_from_url(url)):
                    st.image(img, caption="요소별 평가 해설")
                else:
                    st.warning(f"이미지를 불러올 수 없습니다: {url}")

        if st.session_state.submitted:
            # 결과 저장
            if "score_results" not in st.session_state:
                st.session_state.score_results = []
            st.session_state.score_results.append({
                "이름": st.session_state.username,
                "문항 번호": text_id,
                "내용 점수 (정답)": a_c,
                "내용 점수 (입력)": user_c,
                "조직 점수 (정답)": a_o,
                "조직 점수 (입력)": user_o,
                "표현 점수 (정답)": a_e,
                "표현 점수 (입력)": user_e,
            })

        if st.session_state.submitted and st.button("다음 문제로 이동", key="next_score"):
            current_id = int(st.session_state.current_text_score[0])
            next_text = next((txt for txt in sorted(texts, key=lambda x: int(x[0].strip())) if txt[0].strip().isdigit() and int(txt[0].strip()) == current_id + 1), None)
            if next_text:
                st.session_state.current_text_score = next_text
                st.session_state.submitted = False
            else:
                st.warning("✅ 모든 문항을 완료했습니다. 처음부터 다시 시작하려면 '이전 화면으로 이동'을 누르세요.")
