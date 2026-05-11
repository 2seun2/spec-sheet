import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="TV Spec Analyzer (Gemini)", layout="centered")

# 2. API 키 설정 (Secrets 우선, 없으면 사이드바)
google_api_key = st.sidebar.text_input("Gemini API Key", type="password")
if st.secrets.get("GOOGLE_API_KEY"):
    google_api_key = st.secrets["GOOGLE_API_KEY"]

st.title("📺 Gemini 실시간 TV 비교기")
st.caption("제조사와 인치를 선택하면 AI가 최신 모델을 추천합니다.")

# 3. 모델 리스트 가져오기 함수 (404 에러 방지 로직 적용)
def get_model_list(brand, inch, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # 모델명을 명확하게 지정 (404 models/gemini-1.5-flash 방지)
        # 만약 이래도 안되면 'gemini-1.5-flash'로 번갈아 테스트
        model = genai.GenerativeModel(model_name='gemini-1.5-flash')
        
        prompt = f"{brand}의 {inch}인치 TV 모델명(2025-2026) 딱 3개만 콤마(,)로 구분해서 알려줘. 다른 설명은 절대 하지마."
        
        # API 호출 (안전한 설정 추가)
        response = model.generate_content(prompt)
        
        # 결과 텍스트 정제
        raw_text = response.text.replace('\n', '').replace('*', '').strip()
        models = [m.strip() for m in raw_text.split(',') if m.strip()]
        
        return models if models else ["모델 정보를 찾을 수 없음"]
        
    except Exception as e:
        return [f"에러 발생: {str(e)}"]

# 4. 단계별 모델 선택 섹션
selected_models = []

if not google_api_key:
    st.warning("왼쪽 사이드바에 API 키를 입력하거나 Secrets에 등록해주세요.")
else:
    for i in range(1, 4):
        with st.expander(f"📍 모델 {i} 선택", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                brand = st.selectbox(f"제조사 ({i})", ["삼성전자", "LG전자", "소니", "TCL"], key=f"brand_{i}")
            with col2:
                inch = st.selectbox(f"인치 ({i})", ["98", "85", "77", "65", "55", "43"], key=f"inch_{i}")
            
            options = get_model_list(brand, inch, google_api_key)
            
            if "에러 발생:" in options[0]:
                st.error(f"데이터를 가져오지 못했습니다.\n{options[0]}")
            else:
                selected_m = st.radio(f"상세 모델 ({i})", options, key=f"radio_{i}")
                selected_models.append(selected_m)

    st.divider()

    # 5. 최종 비교 실행
    if st.button("🚀 선택 모델 정밀 비교 시작"):
        if len(selected_models) == 3:
            with st.spinner("Gemini가 상세 사양을 분석 중입니다..."):
                try:
                    model = genai.GenerativeModel(model_name='gemini-1.5-flash')
                    compare_prompt = f"""
                    다음 3개 TV 모델의 스펙 비교표를 만들어줘: {', '.join(selected_models)}
                    항목: 해상도, 패널유형, 최대밝기, 프로세서, 주사율, HDMI버전, 에너지효율.
                    마지막에 기획자 관점의 짧은 평을 추가해줘. 마크다운 표 형식을 사용해.
                    """
                    final_res = model.generate_content(compare_prompt)
                    st.markdown(final_res.text)
                except Exception as e:
                    st.error(f"비교 분석 중 오류 발생: {e}")
