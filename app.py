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


MAP_HEIGHT = 700

CARTO_TILES = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
CARTO_ATTR  = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>'


def count_to_color(count, min_c, max_c):
    """환자 수 → 색상 (연파랑 → 노랑 → 진빨강)"""
    if max_c == min_c:
        return "#74b9ff"
    ratio = (count - min_c) / (max_c - min_c)
    if ratio < 0.5:
        t = ratio * 2
        r = int(116 + t * (253 - 116))
        g = int(185 + t * (203 - 185))
        b = int(255 + t * (110 - 255))
    else:
        t = (ratio - 0.5) * 2
        r = int(253 + t * (214 - 253))
        g = int(203 + t * (48  - 203))
        b = int(110 + t * (49  - 110))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_legend(min_count, max_count):
    return f"""
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;
                background:white;padding:12px 16px;border-radius:10px;
                border:1px solid #ddd;font-size:12px;
                box-shadow:2px 2px 6px rgba(0,0,0,0.15);min-width:140px;">
        <b>환자 수</b>
        <div style="margin-top:8px;">
            <div style="width:110px;height:14px;border-radius:7px;
                background:linear-gradient(to right,#74b9ff,#fdcb6e,#d63031);
                border:1px solid #ccc;"></div>
            <div style="display:flex;justify-content:space-between;
                        width:110px;margin-top:3px;color:#555;">
                <span>{min_count}명</span><span>{max_count}명</span>
            </div>
        </div>
    </div>
    """


def render_map(result_df: pd.DataFrame):
    """Folium 지도 렌더링 (히트맵 / 버블 / 라벨 3가지 뷰)"""
    valid = result_df.dropna(subset=["lat", "lng"])
    if len(valid) == 0:
        st.warning("⚠️ 위경도 데이터가 없습니다. Kakao API 키를 설정해주세요.")
        return

    center_lat = valid["lat"].mean()
    center_lng = valid["lng"].mean()

    # 아파트별 집계
    building_groups = (
        valid[valid["building"] != ""]
        .groupby(["building", "dong"])
        .agg(count=("address", "count"), lat=("lat", "mean"), lng=("lng", "mean"))
        .reset_index()
        .sort_values("count", ascending=False)
    )
    min_count = int(building_groups["count"].min()) if len(building_groups) > 0 else 1
    max_count = int(building_groups["count"].max()) if len(building_groups) > 0 else 1

    # ────────── 탭 ──────────
    tab_heat, tab_bubble, tab_label = st.tabs(["🔥 히트맵", "⭕ 버블맵", "🏷️ 라벨맵"])

    # ── 1. 히트맵 ──────────────────────────────────────────────
    with tab_heat:
        st.caption("밀집 지역을 색상 강도로 표현합니다.")
        m = folium.Map(location=[center_lat, center_lng], zoom_start=14,
                       tiles=CARTO_TILES, attr=CARTO_ATTR)
        heat_data = [[float(r["lat"]), float(r["lng"])] for _, r in valid.iterrows()]
        HeatMap(heat_data, radius=30, blur=20, min_opacity=0.4).add_to(m)
        st_folium(m, use_container_width=True, height=MAP_HEIGHT, key="tab_heat",
                  returned_objects=[])

    # ── 2. 버블맵 ──────────────────────────────────────────────
    with tab_bubble:
        st.caption("원 클릭 → 아파트 정보 팝업 | 원 크기 = 환자 수")
        m2 = folium.Map(location=[center_lat, center_lng], zoom_start=14,
                        tiles=CARTO_TILES, attr=CARTO_ATTR)

        for _, row in building_groups.iterrows():
            count    = int(row["count"])
            building = row["building"]
            dong     = row["dong"]
            color    = count_to_color(count, min_count, max_count)
            radius   = 18 + (count - min_count) * 10

            # CircleMarker + popup (클릭시 정보 표시)
            folium.CircleMarker(
                location=[row["lat"], row["lng"]],
                radius=radius,
                color="#fff",
                weight=2.5,
                fill=True,
                fill_color=color,
                fill_opacity=0.88,
                tooltip=folium.Tooltip(
                    f"<b>{building}</b><br>동: {dong}<br>👤 {count}명",
                    sticky=True
                ),
                popup=folium.Popup(
                    f"<b style='font-size:14px'>{building}</b><br>"
                    f"📍 동: {dong}<br>"
                    f"👤 환자 수: <b>{count}명</b>",
                    max_width=240
                )
            ).add_to(m2)

            # 숫자 라벨 (pointer-events:none → 클릭이 CircleMarker로 통과)
            folium.Marker(
                location=[row["lat"], row["lng"]],
                icon=folium.DivIcon(
                    html=f"""<div style="
                        pointer-events:none;
                        width:{radius*2}px;height:{radius*2}px;
                        line-height:{radius*2}px;
                        text-align:center;font-weight:bold;
                        font-size:{max(12, radius)}px;
                        color:#fff;text-shadow:0 1px 3px rgba(0,0,0,0.6);
                    ">{count}</div>""",
                    icon_size=(radius * 2, radius * 2),
                    icon_anchor=(radius, radius)
                )
            ).add_to(m2)

        m2.get_root().html.add_child(folium.Element(make_legend(min_count, max_count)))
        st_folium(m2, use_container_width=True, height=MAP_HEIGHT, key="tab_bubble",
                  returned_objects=[])

    # ── 3. 라벨맵 ──────────────────────────────────────────────
    with tab_label:
        st.caption("기본 반투명 | hover/클릭 시 선명하게")
        m3 = folium.Map(location=[center_lat, center_lng], zoom_start=15,
                        tiles=CARTO_TILES, attr=CARTO_ATTR)

        for _, row in building_groups.iterrows():
            count    = int(row["count"])
            building = row["building"]
            dong     = row["dong"]
            color    = count_to_color(count, min_count, max_count)
            # 긴 이름 축약
            short    = building[:13] + "…" if len(building) > 13 else building

            label_html = f"""
            <div style="
                background:{color};
                color:#fff;
                padding:3px 8px;
                border-radius:10px;
                font-size:10px;
                font-weight:bold;
                white-space:nowrap;
                border:1.5px solid rgba(255,255,255,0.8);
                box-shadow:1px 1px 4px rgba(0,0,0,0.25);
                text-align:center;
                line-height:1.5;
                opacity:0.4;
                transition:opacity 0.2s ease;
                cursor:pointer;
            "
            onmouseover="this.style.opacity='1'"
            onmouseout="this.style.opacity='0.4'"
            onclick="this.style.opacity='1'">
                {short} ({dong})<br>
                <span style="font-size:11px;">👤 {count}명</span>
            </div>"""

            folium.Marker(
                location=[row["lat"], row["lng"]],
                icon=folium.DivIcon(
                    html=label_html,
                    icon_size=(170, 44),
                    icon_anchor=(85, 22)
                ),
                popup=folium.Popup(
                    f"<b style='font-size:14px'>{building}</b><br>"
                    f"📍 동: {dong}<br>"
                    f"👤 환자 수: <b>{count}명</b>",
                    max_width=240
                )
            ).add_to(m3)

        m3.get_root().html.add_child(folium.Element(make_legend(min_count, max_count)))
        st_folium(m3, use_container_width=True, height=MAP_HEIGHT, key="tab_label",
                  returned_objects=[])


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
