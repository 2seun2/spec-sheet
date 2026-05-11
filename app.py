import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 및 모바일 UI 설정
st.set_page_config(page_title="TV Spec Analyzer (Gemini)", layout="centered")

# 사이드바에 Gemini API 키 입력
with st.sidebar:
    st.title("⚙️ 설정")
    google_api_key = st.text_input("Gemini API Key", type="password")
    st.info("[Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료 키를 발급받을 수 있습니다.")

st.title("📺 Gemini 실시간 TV 비교기")
st.caption("제조사와 인치를 선택하면 AI가 최신 모델을 추천하고 스펙을 비교합니다.")

# 2. Gemini 설정 및 데이터 추출 함수
def get_gemini_response(prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

# 3. 단계별 모델 선택 섹션
selected_models = []

for i in range(1, 4):
    with st.expander(f"📍 모델 {i} 선택", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            brand = st.selectbox(f"제조사 ({i})", ["삼성전자", "LG전자", "소니", "TCL"], key=f"brand_{i}")
        with col2:
            inch = st.selectbox(f"인치 ({i})", ["98", "85", "77", "65", "55", "43"], key=f"inch_{i}")
        
        if google_api_key:
            try:
                # 모델 리스트 가져오기
                list_prompt = f"{brand}의 {inch}인치 최신 TV 모델(2025-2026) 중 대중적인 모델명 3개만 콤마(,)로 구분해서 나열해줘."
                model_raw = get_gemini_response(list_prompt, google_api_key)
                options = [m.strip() for m in model_raw.split(',')]
                
                selected_m = st.radio(f"상세 모델 ({i})", options, key=f"radio_{i}")
                selected_models.append(selected_m)
            except Exception as e:
                st.error("모델 리스트를 불러오는데 실패했습니다.")
        else:
            st.warning("API 키를 입력해주세요.")

st.divider()

# 4. 최종 비교 실행
if st.button("🚀 선택 모델 정밀 비교 시작"):
    if len(selected_models) == 3 and google_api_key:
        with st.spinner("Gemini가 실시간 데이터를 분석 중입니다..."):
            try:
                compare_prompt = f"""
                다음 3개 TV 모델의 모든 상세 사양을 비교하는 마크다운 표를 만들어줘:
                1. {selected_models[0]}
                2. {selected_models[1]}
                3. {selected_models[2]}
                
                - 항목: 해상도, 패널(QD-OLED/Mini-LED 등), 피크 밝기(nits), 프로세서명, 주사율, HDMI 버전, 에너지효율.
                - 마지막에 제품기획자 관점에서 각 모델의 '시장 경쟁력'을 1문장씩 요약해줘.
                - 정보가 불확실하면 '확인중'으로 표기해.
                """
                
                final_report = get_gemini_response(compare_prompt, google_api_key)
                st.markdown(final_report)
                st.success("분석 완료!")
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
    else:
        st.error("API 키 입력 및 모델 선택을 완료해주세요.")

# 5. 모바일 최적화 푸터
st.divider()
st.caption("Powered by Gemini 1.5 Flash | 기획자 전용 모바일 분석툴")
