import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="TV Spec Analyzer (Gemini)", layout="centered")

# 2. API 키 입력 (사이드바)
with st.sidebar:
    st.title("⚙️ 설정")
    # 키가 없을 경우를 대비해 세션 상태나 Secrets 활용 권장
    google_api_key = st.text_input("Gemini API Key", type="password")
    st.info("[API 키 발급처](https://aistudio.google.com/app/apikey)")

st.title("📺 Gemini 실시간 TV 비교기")
st.caption("제조사와 인치를 선택하면 AI가 최신 모델을 추천합니다.")

# 3. 모델 리스트 가져오기 함수 (보안 및 예외처리 강화)
def get_model_list(brand, inch, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # 모델명을 'models/gemini-1.5-flash'로 명확히 지정 (v1beta 이슈 해결)
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        
        prompt = f"{brand}의 {inch}인치 최신 TV 모델명(2025-2026) 딱 3개만 콤마(,)로 구분해서 알려줘. 다른 설명은 생략해."
        
        # 안전한 호출을 위해 generation_config 추가
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                candidate_count=1,
                max_output_tokens=100,
                temperature=0.7
            )
        )
        
        # 결과 텍스트 정제
        raw_text = response.text.replace('\n', '').replace('*', '').strip()
        return [m.strip() for m in raw_text.split(',')]
        
    except Exception as e:
        # 에러 발생 시 상세 메시지를 반환하여 디버깅 지원
        return [f"에러: {str(e)}"]



# 4. 단계별 모델 선택 섹션
selected_models = []

# API 키가 입력되었을 때만 작동하도록 제어
if not google_api_key:
    st.warning("왼쪽 사이드바에서 Gemini API Key를 먼저 입력해주세요!")
else:
    for i in range(1, 4):
        with st.expander(f"📍 모델 {i} 선택", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                brand = st.selectbox(f"제조사 ({i})", ["삼성전자", "LG전자", "소니", "TCL"], key=f"brand_{i}")
            with col2:
                inch = st.selectbox(f"인치 ({i})", ["98", "85", "77", "65", "55", "43"], key=f"inch_{i}")
            
            # 모델 리스트 호출
            options = get_model_list(brand, inch, google_api_key)
            
            if "에러:" in options[0]:
                st.error(f"데이터를 가져오지 못했습니다. 원인: {options[0]}")
            else:
                selected_m = st.radio(f"상세 모델 ({i})", options, key=f"radio_{i}")
                selected_models.append(selected_m)

    st.divider()

    # 5. 최종 비교 실행
    if st.button("🚀 선택 모델 정밀 비교 시작"):
        if len(selected_models) == 3:
            with st.spinner("Gemini가 상세 사양을 분석 중입니다..."):
                try:
                    genai.configure(api_key=google_api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash-latest')
                    compare_prompt = f"""
                    다음 3개 TV 모델의 스펙 비교표를 만들어줘: {', '.join(selected_models)}
                    항목: 해상도, 패널유형, 최대밝기, 프로세서, 주사율, HDMI버전, 에너지효율.
                    마지막에 기획자 관점의 짧은 평을 추가해줘. 마크다운 표 형식을 사용해.
                    """
                    final_res = model.generate_content(compare_prompt)
                    st.markdown(final_res.text)
                except Exception as e:
                    st.error(f"비교 분석 중 오류 발생: {e}")
        else:
            st.error("모든 모델을 선택 완료해주세요.")
