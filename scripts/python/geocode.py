"""
address-geo-analyzer: 주소 지오코딩 스크립트

사용법:
    python geocode.py <input_excel_path>

예시:
    python geocode.py ../data/raw/patients_2024Q1.xlsx

출력:
    - ../data/processed/geocoded_YYYYMMDD_HHMMSS.csv
"""

import sys
import pandas as pd
from datetime import datetime
import requests
import time
import os

# Kakao API 키 (환경변수 또는 .env 파일)
KAKAO_API_KEY = os.getenv("KAKAO_API_KEY", "YOUR_API_KEY_HERE")


def geocode_address(address: str) -> dict:
    """
    도로명 주소를 지오코딩하여 위경도, 동, 아파트명 추출
    
    Args:
        address: 도로명 주소
        
    Returns:
        {
            "address": 원본 주소,
            "lat": 위도,
            "lng": 경도,
            "dong": 동 이름,
            "building": 건물명(아파트명)
        }
    """
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {"Authorization": f"KakaoAK {KAKAO_API_KEY}"}
    params = {"query": address}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data["documents"]:
            doc = data["documents"][0]
            return {
                "address": address,
                "lat": doc["y"],
                "lng": doc["x"],
                "dong": doc["address"].get("region_3depth_name", ""),
                "building": doc["address_name"].split()[-1] if "아파트" in doc["address_name"] else ""
            }
        else:
            return {"address": address, "lat": None, "lng": None, "dong": "", "building": ""}
    
    except Exception as e:
        print(f"❌ 오류: {address} - {e}")
        return {"address": address, "lat": None, "lng": None, "dong": "", "building": ""}


def main():
    if len(sys.argv) < 2:
        print("사용법: python geocode.py <input_excel_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    print(f"📂 입력 파일: {input_path}")
    
    # 엑셀 읽기 (주소 컬럼명 가정: "주소")
    df = pd.read_excel(input_path)
    
    if "주소" not in df.columns:
        print("❌ '주소' 컬럼이 없습니다. 컬럼명을 확인하세요.")
        sys.exit(1)
    
    print(f"📊 총 {len(df)}건의 주소 처리 시작")
    
    results = []
    for idx, row in df.iterrows():
        address = row["주소"]
        result = geocode_address(address)
        results.append(result)
        
        if (idx + 1) % 10 == 0:
            print(f"진행 중... {idx + 1}/{len(df)}")
        
        time.sleep(0.1)  # API 요청 제한 방지
    
    # 결과 저장
    output_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"../data/processed/geocoded_{timestamp}.csv"
    output_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print(f"✅ 완료! 저장 위치: {output_path}")
    print(f"📊 성공: {output_df['lat'].notna().sum()}건 / 총 {len(output_df)}건")


if __name__ == "__main__":
    main()
