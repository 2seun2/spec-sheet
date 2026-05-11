import streamlit as st
import pandas as pd
from openai import OpenAI

# 1. 초기 설정
st.set_page_config(page_title="TV 비교 분석기", layout="centered")

# API 키 설정 (사이드바)
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password")

st.title("📺 맞춤형 TV 스펙 비교기")
st.caption("제조사/인치별 모델을 선택하여 정밀 비교를 진행하세요.")

# 2. 데이터 추출 함수 (AI 연동)
def get_model_list(brand, inch, api_key):
    client = OpenAI(api_key=api_key)
    prompt = f"{brand}의 {inch}인치 최신 TV 모델(2025-2026) 리스트를 3개만 찾아줘. 모델명과 핵심 사양 요약만 알려줘."
    # 실제 구현 시에는 JSON으로 받아 파싱하는 로직이 들어갑니다. 
    # 여기서는 구조를 보여드리기 위해 예시 데이터를 반환합니다.
    # API 연동 시 response = client.chat.completions.create(...) 사용
    return [f"{brand} {inch}인치 플래그십", f"{brand} {inch}인치 하이엔드", f"{brand} {inch}인치 보급형"]

# 3. 모델 선택 프로세스 (3개 모델 각각)
selected_models = []

for i in range(1, 4):
    st.subheader(f"📍 모델 {i} 선택")
    col1, col2 = st.columns(2)
    
    with col1:
        brand = st.selectbox(f"제조사 ({i})", ["삼성전자", "LG전자", "소니", "TCL"], key=f"brand_{i}")
    with col2:
        inch = st.selectbox(f"인치 ({i})", ["98", "85", "77", "65", "55"], key=f"inch_{i}")
    
    if api_key:
        # 제조사와 인치를 선택하면 해당 리스트를 가져옴
        model_options = get_model_list(brand, inch, api_key)
        selected_m = st.radio(f"상세 모델 선택 ({i})", model_options, key=f"model_select_{i}")
        selected_models.append(selected_m)
    else:
        st.warning("API 키를 입력하면 모델 리스트를 불러옵니다.")

st.divider()

# 4. 최종 비교 실행
if st.button("🚀 선택한 3개 모델 상세 비교 시작"):
    if len(selected_models) == 3:
        with st.spinner("전문 스펙 데이터를 수집하여 비교표를 작성 중입니다..."):
            client = OpenAI(api_key=api_key)
            compare_prompt = f"""
            다음 3개 모델의 모든 기술 사양을 비교표로 만들어줘:
            1. {selected_models[0]}
            2. {selected_models[1]}
            3. {selected_models[2]}
            
            항목은 해상도, 패널기술, 최대밝기(nits), 프로세서, HDR규격, HDMI단자, 전력효율을 포함해.
            마지막에 제품기획자 관점에서 '차별화 포인트'도 한줄씩 요약해줘.
            JSON 형식이 아닌 마크다운 표로 깔끔하게 보여줘.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": compare_prompt}]
            )
            
            st.markdown(response.choices[0].message.content)
            
            # 엑셀 변환을 위한 데이터 정리 (필요시 추가)
            st.success("비교 분석 완료!")
    else:
        st.error("3개의 모델을 모두 선택해주세요.")

# 5. 하단 메모
st.info("💡 팁: 모바일에서 화면을 가로로 돌리면 더 넓은 비교표를 볼 수 있습니다.")
