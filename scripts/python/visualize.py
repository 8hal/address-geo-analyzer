"""
address-geo-analyzer: 지도 시각화 스크립트

사용법:
    python visualize.py <geocoded_csv_path>

예시:
    python visualize.py ../data/processed/geocoded_20240315_120000.csv

출력:
    - ../data/output/map_20240315_120000.html
"""

import sys
import pandas as pd
import folium
from folium.plugins import HeatMap
from datetime import datetime


def create_heatmap(df: pd.DataFrame, output_path: str):
    """
    지오코딩된 데이터를 히트맵으로 시각화
    
    Args:
        df: 지오코딩 결과 DataFrame (lat, lng 필수)
        output_path: HTML 저장 경로
    """
    # 유효한 좌표만 필터링
    valid_df = df.dropna(subset=["lat", "lng"])
    
    if len(valid_df) == 0:
        print("❌ 유효한 좌표 데이터가 없습니다.")
        return
    
    # 중심 좌표 계산 (평균)
    center_lat = valid_df["lat"].astype(float).mean()
    center_lng = valid_df["lng"].astype(float).mean()
    
    # 지도 생성
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=13,
        tiles="OpenStreetMap"
    )
    
    # 히트맵 데이터
    heat_data = [[row["lat"], row["lng"]] for _, row in valid_df.iterrows()]
    HeatMap(heat_data, radius=15, blur=20, max_zoom=13).add_to(m)
    
    # 동별 집계 마커 (상위 5개)
    dong_counts = valid_df["dong"].value_counts().head(5)
    for dong, count in dong_counts.items():
        dong_df = valid_df[valid_df["dong"] == dong]
        dong_lat = dong_df["lat"].astype(float).mean()
        dong_lng = dong_df["lng"].astype(float).mean()
        
        folium.Marker(
            location=[dong_lat, dong_lng],
            popup=f"<b>{dong}</b><br>환자 수: {count}명",
            icon=folium.Icon(color="blue", icon="info-sign")
        ).add_to(m)
    
    # 저장
    m.save(output_path)
    print(f"✅ 지도 생성 완료: {output_path}")


def create_statistics(df: pd.DataFrame):
    """
    동/아파트별 통계 출력
    """
    print("\n📊 동별 환자 수 (상위 10개)")
    print(df["dong"].value_counts().head(10))
    
    print("\n🏠 아파트별 환자 수 (상위 10개)")
    building_counts = df[df["building"] != ""]["building"].value_counts().head(10)
    print(building_counts)


def main():
    if len(sys.argv) < 2:
        print("사용법: python visualize.py <geocoded_csv_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    print(f"📂 입력 파일: {input_path}")
    
    # CSV 읽기
    df = pd.read_csv(input_path)
    
    # 통계 출력
    create_statistics(df)
    
    # 지도 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"../data/output/map_{timestamp}.html"
    create_heatmap(df, output_path)


if __name__ == "__main__":
    main()
