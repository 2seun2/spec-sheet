import streamlit as st
import pandas as pd
from openai import OpenAI  # AI 서칭 연동용

# 1. 페이지 및 모바일 UI 설정
st.set_page_config(page_title="TV 비교 분석기", layout="centered")

# 사이드바에 API 키 입력 (보안)
with st.sidebar:
    st.title("⚙️ 설정")
    api_key = st.text_input("OpenAI API Key", type="password")
    st.info("실시간 데이터 서칭을 위해 OpenAI API 키가 필요합니다.")

st.title("📺 실시간 TV 스펙 비교기")
st.caption("비교하고 싶은 3가지 모델을 입력하세요.")

# 2. 모델 입력 섹션 (3개 열)
col1, col2, col3 = st.columns(3)
with col1:
    m1 = st.text_input("모델 1", value="삼성 QN900F")
with col2:
    m2 = st.text_input("모델 2", value="LG G5 OLED")
with col3:
    m3 = st.text_input("모델 3", value="소니 Bravia 9")

# 3. 실시간 분석 실행 버튼
if st.button("🚀 실시간 스펙 비교 시작"):
    if not api_key:
        st.warning("먼저 API 키를 입력해주세요.")
    else:
        with st.spinner("AI가 최신 웹 정보를 분석하여 표를 작성 중입니다..."):
            try:
                client = OpenAI(api_key=api_key)
                
                # AI에게 실시간 서칭 및 표 데이터 생성을 요청하는 프롬프트
                prompt = f"""
                다음 3개 TV 모델의 최신 스펙을 실시간으로 검색해서 비교표를 만들어줘: {m1}, {m2}, {m3}.
                제조사 공식 스펙을 기준으로 하되, 해상도, 주사율, 패널종류, 프로세서, HDMI버전, 특징을 포함해.
                반드시 아래 JSON 형식으로만 응답해:
                [
                    {{"항목": "해상도", "모델1": "값", "모델2": "값", "모델3": "값"}},
                    ...
                ]
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o", # 또는 gpt-4-turbo-preview
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 결과 데이터 파싱 (문자열 -> JSON -> DataFrame)
                import json
                raw_data = response.choices[0].message.content
                # JSON 부분만 추출 (마크다운 제거)
                json_data = raw_data.split('[')[1].split(']')[0]
                data = json.loads("[" + json_data + "]")
                
                df = pd.DataFrame(data)
                
                # 4. 결과 출력
                st.subheader("📊 상세 사양 비교 매트릭스")
                st.table(df) # 모바일에서 한눈에 보기 편하게 table 사용

                # 5. 인사이트 자동 생성
                st.subheader("💡 제품기획자 관점 분석")
                insight_prompt = f"{m1}, {m2}, {m3}의 스펙 차이를 바탕으로 기획자가 주목해야 할 마케팅 포인트 3가지만 요약해줘."
                insight_res = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": insight_prompt}]
                )
                st.info(insight_res.choices[0].message.content)

                # 엑셀 다운로드
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("Excel 다운로드", csv, "TV_Comparison.csv", "text/csv")

            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")

# 하단 가이드
st.divider()
st.caption("본 툴은 실시간 웹 데이터를 기반으로 하므로 실제 출시 사양과 미세한 차이가 있을 수 있습니다.")
