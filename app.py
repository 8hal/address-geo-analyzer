"""
address-geo-analyzer: Streamlit 웹 앱

병원 원장님용 주소 분석 도구
- 파일 업로드 (CSV/엑셀)
- 자동 분석
- 결과 다운로드
"""

import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime
import io

# 페이지 설정
st.set_page_config(
    page_title="환자 주소 분석기",
    page_icon="🏥",
    layout="wide"
)

# Postcodify API
POSTCODIFY_API_URL = "http://api.poesis.kr/post/search.php"


def geocode_address(address: str) -> dict:
    """주소 지오코딩"""
    params = {"q": address, "v": "2.1"}
    
    try:
        response = requests.get(POSTCODIFY_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("count", 0) > 0 and data.get("results"):
            result = data["results"][0]
            addr = result.get("address", {})
            
            jibun = addr.get("old", "")
            dong = jibun.split()[0] if jibun else ""
            building = addr.get("building", "")
            
            return {
                "address": address,
                "postcode": result.get("code5", ""),
                "dong": dong,
                "building": building,
                "jibun": jibun
            }
        else:
            return {
                "address": address,
                "postcode": "",
                "dong": "",
                "building": "",
                "jibun": ""
            }
    
    except Exception as e:
        return {
            "address": address,
            "postcode": "",
            "dong": "",
            "building": "",
            "jibun": "",
            "error": str(e)
        }


def process_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """주소 데이터 처리"""
    if "주소" not in df.columns:
        st.error("❌ '주소' 컬럼이 없습니다. 파일을 확인해주세요.")
        return None
    
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total = len(df)
    
    for idx, row in df.iterrows():
        address = row["주소"]
        result = geocode_address(address)
        results.append(result)
        
        progress = (idx + 1) / total
        progress_bar.progress(progress)
        status_text.text(f"처리 중... {idx + 1}/{total}")
        
        time.sleep(0.15)  # API 제한 방지
    
    progress_bar.empty()
    status_text.empty()
    
    return pd.DataFrame(results)


# 메인 UI
st.title("🏥 환자 주소 분석기")
st.markdown("---")

st.markdown("""
### 📋 사용 방법
1. 환자 주소가 담긴 **CSV** 또는 **엑셀** 파일을 업로드하세요
2. 파일에는 반드시 **'주소'** 컬럼이 있어야 합니다
3. "분석 시작" 버튼을 클릭하세요
4. 결과를 확인하고 다운로드하세요

**예시 형식:**
```
주소
경기도 화성시 동탄구 동탄신리천로8길 15
경기도 화성시 동탄구 동탄순환대로19길 59
```
""")

st.markdown("---")

# 파일 업로드
uploaded_file = st.file_uploader(
    "📂 파일 선택 (CSV 또는 엑셀)",
    type=["csv", "xlsx", "xls"],
    help="환자 주소가 담긴 파일을 선택하세요"
)

if uploaded_file:
    try:
        # 파일 읽기
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        st.success(f"✅ 파일 로드 완료: {len(df)}건의 데이터")
        
        # 미리보기
        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(10))
        
        # 분석 시작 버튼
        if st.button("🚀 분석 시작", type="primary"):
            with st.spinner("주소 분석 중..."):
                result_df = process_addresses(df)
            
            if result_df is not None:
                st.success("✅ 분석 완료!")
                
                # 통계 요약
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("총 환자 수", len(result_df))
                
                with col2:
                    unique_dong = result_df[result_df["dong"] != ""]["dong"].nunique()
                    st.metric("고유 동 수", unique_dong)
                
                with col3:
                    building_count = result_df[result_df["building"] != ""].shape[0]
                    st.metric("아파트 거주자", building_count)
                
                with col4:
                    success_rate = (result_df["dong"] != "").sum() / len(result_df) * 100
                    st.metric("분석 성공률", f"{success_rate:.1f}%")
                
                st.markdown("---")
                
                # 동별 분포
                st.subheader("📍 동별 환자 분포")
                dong_counts = result_df["dong"].value_counts().head(10)
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.bar_chart(dong_counts)
                
                with col2:
                    for dong, count in dong_counts.items():
                        pct = (count / len(result_df)) * 100
                        st.metric(dong, f"{count}명 ({pct:.1f}%)")
                
                st.markdown("---")
                
                # 아파트별 분포
                st.subheader("🏠 아파트별 환자 분포")
                building_df = result_df[result_df["building"] != ""]
                if len(building_df) > 0:
                    building_counts = building_df["building"].value_counts().head(10)
                    
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.bar_chart(building_counts)
                    
                    with col2:
                        for building, count in building_counts.items():
                            pct = (count / len(building_df)) * 100
                            st.metric(building, f"{count}명 ({pct:.1f}%)")
                else:
                    st.info("아파트 정보가 없습니다.")
                
                st.markdown("---")
                
                # 상세 결과 테이블
                with st.expander("📋 상세 결과 보기"):
                    st.dataframe(result_df)
                
                # CSV 다운로드
                csv = result_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                st.download_button(
                    label="📥 결과 다운로드 (CSV)",
                    data=csv,
                    file_name=f"환자주소분석_{timestamp}.csv",
                    mime="text/csv",
                    type="primary"
                )
    
    except Exception as e:
        st.error(f"❌ 오류 발생: {e}")

# 푸터
st.markdown("---")
st.caption("💡 문의: 문광명 PM | Postcodify API 사용 (무료)")
