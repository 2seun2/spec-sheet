import streamlit as st
import pandas as pd
import google.generativeai as genai

# 1. 페이지 설정
st.set_page_config(page_title="TV Spec Analyzer (Gemini)", layout="centered")

# 2. API 키 설정 (보안상 사이드바 권장)
# 기획자님이 방금 알려주신 키를 사이드바에 넣으시면 작동합니다.
google_api_key = st.sidebar.text_input("Gemini API Key", type="password")

st.title("📺 Gemini 실시간 TV 비교기")
st.caption("제조사와 인치를 선택하면 AI가 최신 모델을 추천합니다.")

# 3. 모델 리스트 가져오기 함수 (안정성 강화 버전)
def get_model_list(brand, inch, api_key):
    try:
        genai.configure(api_key=api_key)
        
        # [핵심 수정] 모델 이름에서 'models/'를 빼고 'gemini-1.5-flash'만 사용하거나 
        # 최신 라이브러리 규격인 GenerativeModel 직접 호출 방식을 사용합니다.
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"{brand}의 {inch}인치 TV 모델명(2025-2026) 딱 3개만 콤마(,)로 구분해서 알려줘. 다른 설명은 절대 하지마."
        
        # API 호출
        response = model.generate_content(prompt)
        
        # 결과 텍스트 정제
        raw_text = response.text.replace('\n', '').replace('*', '').strip()
        models = [m.strip() for m in raw_text.split(',') if m.strip()]
        
        return models if models else ["검색된 모델 없음"]
        
    except Exception as e:
        # 에러 발생 시 원인을 명확히 출력
        return [f"연결 오류: {str(e)}"]

# 4. 단계별 모델 선택 섹션
selected_models = []

if not google_api_key:
    st.warning("왼쪽 사이드바에 API 키를 입력해주세요!")
else:
    for i in range(1, 4):
        with st.expander(f"📍 모델 {i} 선택", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                brand = st.selectbox(f"제조사 ({i})", ["삼성전자", "LG전자", "소니", "TCL"], key=f"brand_{i}")
            with col2:
                inch = st.selectbox(f"인치 ({i})", ["98", "85", "77", "65", "55", "43"], key=f"inch_{i}")
            
            # API 호출 결과 확인
            options = get_model_list(brand, inch, google_api_key)
            
            if "연결 오류:" in options[0]:
                st.error(f"데이터를 가져오지 못했습니다. (원인: {options[0]})")
            else:
                selected_m = st.radio(f"상세 모델 ({i})", options, key=f"radio_{i}")
                selected_models.append(selected_m)

    st.divider()

    # 5. 최종 비교 실행
    if st.button("🚀 선택 모델 정밀 비교 시작"):
        if len(selected_models) == 3:
            with st.spinner("Gemini가 상세 사양을 분석 중입니다..."):
                try:
                    model = genai.GenerativeModel('gemini-1.5-flash')
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
            st.error("3개의 모델을 모두 선택해 주세요.")
