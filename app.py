"""
address-geo-analyzer: Streamlit 웹 앱

병원 원장님용 주소 분석 도구
- 파일 업로드 (CSV/엑셀)
- 동/아파트 통계 분석
- 지도 시각화 (Kakao API)
- 결과 다운로드
"""

import streamlit as st
import pandas as pd
import requests
import time
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="환자 주소 분석기",
    page_icon="🏥",
    layout="wide"
)

# API 설정
POSTCODIFY_API_URL = "http://api.poesis.kr/post/search.php"
KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"

# Kakao API 키: Streamlit Cloud secrets 또는 없으면 None
KAKAO_API_KEY = st.secrets.get("KAKAO_API_KEY", None) if hasattr(st, "secrets") else None


def geocode_postcodify(address: str) -> dict:
    """Postcodify: 동/아파트명 추출"""
    params = {"q": address, "v": "2.1"}
    try:
        response = requests.get(POSTCODIFY_API_URL, params=params, timeout=5)
        data = response.json()
        if data.get("count", 0) > 0 and data.get("results"):
            result = data["results"][0]
            addr = result.get("address", {})
            jibun = addr.get("old", "")
            dong = jibun.split()[0] if jibun else ""
            return {
                "postcode": result.get("code5", ""),
                "dong": dong,
                "building": addr.get("building", ""),
                "jibun": jibun
            }
    except Exception:
        pass
    return {"postcode": "", "dong": "", "building": "", "jibun": ""}


def geocode_kakao(address: str, api_key: str) -> dict:
    """Kakao Local API: 위경도 추출"""
    headers = {"Authorization": f"KakaoAK {api_key}"}
    params = {"query": address}
    try:
        response = requests.get(KAKAO_GEOCODE_URL, headers=headers, params=params, timeout=5)
        data = response.json()
        if data.get("documents"):
            doc = data["documents"][0]
            return {"lat": float(doc["y"]), "lng": float(doc["x"])}
    except Exception:
        pass
    return {"lat": None, "lng": None}


def process_addresses(df: pd.DataFrame) -> pd.DataFrame:
    """주소 데이터 처리 (Postcodify + Kakao 병합)"""
    if "주소" not in df.columns:
        st.error("❌ '주소' 컬럼이 없습니다. 파일을 확인해주세요.")
        return None

    use_map = KAKAO_API_KEY is not None
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()
    total = len(df)

    for idx, row in df.iterrows():
        address = str(row["주소"]).strip()

        # Postcodify: 동/아파트
        info = geocode_postcodify(address)

        # Kakao: 위경도 (키 있을 때만)
        coords = geocode_kakao(address, KAKAO_API_KEY) if use_map else {"lat": None, "lng": None}

        results.append({
            "address": address,
            "postcode": info["postcode"],
            "dong": info["dong"],
            "building": info["building"],
            "jibun": info["jibun"],
            "lat": coords["lat"],
            "lng": coords["lng"],
        })

        progress_bar.progress((idx + 1) / total)
        status_text.text(f"처리 중... {idx + 1}/{total}")
        time.sleep(0.15)

    progress_bar.empty()
    status_text.empty()
    return pd.DataFrame(results)


def render_map(result_df: pd.DataFrame):
    """Folium 지도 렌더링"""
    valid = result_df.dropna(subset=["lat", "lng"])
    if len(valid) == 0:
        st.warning("⚠️ 위경도 데이터가 없습니다. Kakao API 키를 설정해주세요.")
        return

    center_lat = valid["lat"].mean()
    center_lng = valid["lng"].mean()

    tab1, tab2 = st.tabs(["🔥 히트맵", "📍 마커"])

    CARTO_TILES = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
    CARTO_ATTR = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'

    # 히트맵
    with tab1:
        m = folium.Map(location=[center_lat, center_lng], zoom_start=14,
                       tiles=CARTO_TILES, attr=CARTO_ATTR)
        heat_data = [[row["lat"], row["lng"]] for _, row in valid.iterrows()]
        HeatMap(heat_data, radius=20, blur=25, min_opacity=0.4).add_to(m)
        st_folium(m, use_container_width=True, height=500)

    # 마커 (아파트별 클러스터)
    with tab2:
        m2 = folium.Map(location=[center_lat, center_lng], zoom_start=14,
                        tiles=CARTO_TILES, attr=CARTO_ATTR)
        cluster = MarkerCluster().add_to(m2)

        dong_colors = {}
        palette = ["blue", "red", "green", "purple", "orange", "darkred", "cadetblue"]
        for i, dong in enumerate(valid["dong"].unique()):
            dong_colors[dong] = palette[i % len(palette)]

        for _, row in valid.iterrows():
            building = row["building"] if row["building"] else "건물명 미확인"
            dong = row["dong"] if row["dong"] else "동 미확인"
            color = dong_colors.get(dong, "gray")
            folium.Marker(
                location=[row["lat"], row["lng"]],
                popup=folium.Popup(
                    f"<b>{building}</b><br>동: {dong}<br>주소: {row['address']}",
                    max_width=250
                ),
                tooltip=f"{dong} | {building}",
                icon=folium.Icon(color=color, icon="plus-sign")
            ).add_to(cluster)

        # 범례
        dong_legend = "".join([
            f"<li><span style='color:{c}'>●</span> {d}</li>"
            for d, c in dong_colors.items()
        ])
        legend_html = f"""
        <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                    background:white; padding:12px; border-radius:8px;
                    border:1px solid #ccc; font-size:13px;">
            <b>동 범례</b><ul style="margin:5px 0; padding-left:18px;">{dong_legend}</ul>
        </div>
        """
        m2.get_root().html.add_child(folium.Element(legend_html))
        st_folium(m2, use_container_width=True, height=500)


# ─────────── 메인 UI ───────────

st.title("🏥 환자 주소 분석기")
st.markdown("---")

# API 키 상태 표시
if KAKAO_API_KEY:
    st.success("✅ Kakao API 연동됨 — 지도 기능 사용 가능")
else:
    st.info("ℹ️ 현재 통계 분석만 가능합니다. Kakao API 키 등록 시 지도 기능이 활성화됩니다.")

st.markdown("""
### 📋 사용 방법
1. 환자 주소가 담긴 **CSV** 또는 **엑셀** 파일 업로드
2. 파일에 **'주소'** 컬럼 필수
3. "분석 시작" 버튼 클릭
4. 통계 / 지도 / CSV 다운로드

**예시 형식:**
```
주소
경기도 화성시 동탄구 동탄신리천로8길 15
경기도 화성시 동탄구 동탄순환대로19길 59
```
""")

st.markdown("---")

uploaded_file = st.file_uploader(
    "📂 파일 선택 (CSV 또는 엑셀)",
    type=["csv", "xlsx", "xls"],
    help="환자 주소가 담긴 파일을 선택하세요"
)

# 파일이 새로 업로드되면 이전 결과 초기화
if uploaded_file:
    if "last_file" not in st.session_state or st.session_state.last_file != uploaded_file.name:
        st.session_state.last_file = uploaded_file.name
        st.session_state.result_df = None

if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") else pd.read_excel(uploaded_file)
        st.success(f"✅ 파일 로드 완료: {len(df)}건의 데이터")

        with st.expander("📊 데이터 미리보기"):
            st.dataframe(df.head(10))

        if st.button("🚀 분석 시작", type="primary"):
            with st.spinner("주소 분석 중..."):
                st.session_state.result_df = process_addresses(df)

        # session_state에 결과가 있으면 계속 표시
        result_df = st.session_state.get("result_df", None)

        if result_df is not None:
            st.success("✅ 분석 완료!")

            # ── 요약 통계 ──
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("총 환자 수", len(result_df))
            with col2:
                st.metric("고유 동 수", result_df[result_df["dong"] != ""]["dong"].nunique())
            with col3:
                st.metric("아파트 거주자", result_df[result_df["building"] != ""].shape[0])
            with col4:
                rate = (result_df["dong"] != "").sum() / len(result_df) * 100
                st.metric("분석 성공률", f"{rate:.1f}%")

            st.markdown("---")

            # ── 탭 구성 ──
            tab_stat, tab_map = st.tabs(["📊 통계", "🗺️ 지도"])

            with tab_stat:
                st.subheader("📍 동별 환자 분포")
                dong_counts = result_df[result_df["dong"] != ""]["dong"].value_counts()
                st.bar_chart(dong_counts.head(10))

                st.markdown("### 🏘️ 동별 상세 현황")
                for dong in dong_counts.head(10).index:
                    dong_df = result_df[result_df["dong"] == dong]
                    dong_total = len(dong_df)
                    dong_pct = (dong_total / len(result_df)) * 100
                    with st.expander(f"**{dong}** - {dong_total}명 ({dong_pct:.1f}%)", expanded=True):
                        building_in_dong = dong_df[dong_df["building"] != ""]["building"].value_counts()
                        if len(building_in_dong) > 0:
                            st.markdown("**📌 아파트 분포:**")
                            for building, count in building_in_dong.items():
                                pct_in_dong = (count / dong_total) * 100
                                st.markdown(f"- {building}: **{count}명** ({pct_in_dong:.1f}%)")
                        else:
                            st.info("아파트 정보 없음 (단독주택 또는 오피스텔)")

                st.markdown("---")
                st.subheader("🏠 아파트별 환자 분포 (상위 20개)")
                building_df = result_df[result_df["building"] != ""]
                if len(building_df) > 0:
                    bwd = building_df.groupby(["building", "dong"]).size().reset_index(name="count")
                    bwd = bwd.sort_values("count", ascending=False).head(20)
                    st.dataframe(
                        bwd.rename(columns={"building": "아파트", "dong": "동", "count": "환자 수"}),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.info("아파트 정보가 없습니다.")

                st.markdown("---")
                with st.expander("📋 전체 결과 보기"):
                    st.dataframe(result_df)

            with tab_map:
                st.subheader("🗺️ 환자 분포 지도")
                if KAKAO_API_KEY:
                    render_map(result_df)
                else:
                    st.warning("⚠️ Kakao API 키가 필요합니다. 관리자에게 문의하세요.")

            # ── CSV 다운로드 ──
            st.markdown("---")
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

st.markdown("---")
st.caption("💡 문의: 문광명 PM | Postcodify + Kakao API 사용")
