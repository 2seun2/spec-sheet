import streamlit as st
import pandas as pd

# 1. 모바일 최적화 설정
st.set_page_config(
    page_title="TV Spec Analyzer", 
    layout="centered", # 모바일은 중앙 집중형이 보기 편함
    initial_sidebar_state="collapsed" # 모바일 화면 확보를 위해 사이드바 숨김
)

# 모바일 전용 CSS 주입 (글자 크기 및 버튼 크기 조정)
st.markdown("""
    <style>
    .main { font-size: 14px; }
    button { height: 3em !important; width: 100% !important; }
    .stDataFrame { width: 100% !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("📱 경쟁사 TV 분석 Tool")
st.caption("제품기획자용 모바일 대시보드")

# 2. 모바일 친화적 입력창
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        brand = st.text_input("제조사", value="삼성전자")
    with col2:
        year = st.selectbox("연도", ["2026", "2025"])

if st.button("🔍 실시간 데이터 스캔"):
    with st.spinner("최신 정보를 수집 중..."):
        # 샘플 데이터 (실제 운영 시 API 연동 구간)
        data = [
            {"모델": "QNC900", "Inch": "85", "패널": "NeoQLED 8K", "Spec": "144Hz, Gen3 AI"},
            {"모델": "QNC90", "Inch": "75", "패널": "NeoQLED 4K", "Spec": "144Hz, Gen2 AI"},
            {"모델": "The Frame", "Inch": "65", "패널": "QLED", "Spec": "Matte, 120Hz"}
        ]
        df = pd.DataFrame(data)

        # 3. 계층 구조 시각화 (모바일은 '탭' 방식이 훨씬 편합니다)
        st.subheader("📁 라인업 카테고리")
        tab1, tab2, tab3 = st.tabs(["85인치", "75인치", "65인치"])
        
        with tab1:
            st.info("**모델:** QNC900\n\n**화질:** 8K Mini-LED\n\n**핵심:** AI 업스케일링 3세대")
        with tab2:
            st.info("**모델:** QNC90\n\n**화질:** 4K Mini-LED\n\n**핵심:** 게이밍 퍼포먼스")
        with tab3:
            st.info("**모델:** The Frame\n\n**화질:** 4K QLED\n\n**핵심:** 디자인 가전")

        # 4. 비교 표 (모바일에서는 가로 스크롤이 생기므로 필요한 열만 노출)
        st.subheader("📊 상세 사양 매트릭스")
        st.write("💡 가로로 밀어서 전체 사양 확인")
        st.dataframe(df, use_container_width=True)

        # 5. 하단 액션 버튼
        st.divider()
        st.download_button(
            label="📄 분석 결과 CSV 저장",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name=f"TV_Report.csv",
            mime='text/csv'
        )

# 6. 기획자 전용 메모 (안드로이드 키보드 입력 대응)
st.subheader("📝 분석 메모")
note = st.text_area("현장에서 느낀 인사이트를 기록하세요", placeholder="예: LG OLED 대비 밝기가 개선됨...")
if note:
    st.success("메모가 임시 저장되었습니다.")
