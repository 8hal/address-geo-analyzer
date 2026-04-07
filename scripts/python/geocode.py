"""
address-geo-analyzer: 주소 지오코딩 스크립트 (Postcodify 기반)

사용법:
    python geocode.py <input_csv_or_excel_path>

예시:
    python geocode.py ../data/raw/patients_2024Q1.csv
    python geocode.py ../data/raw/patients_2024Q1.xlsx

출력:
    - ../data/processed/geocoded_YYYYMMDD_HHMMSS.csv
"""

import sys
import pandas as pd
from datetime import datetime
import requests
import time

# Postcodify 무료 API (API 키 불필요)
POSTCODIFY_API_URL = "http://api.poesis.kr/post/search.php"

# 위경도 변환용 Kakao Local API (선택사항)
KAKAO_GEOCODE_URL = "https://dapi.kakao.com/v2/local/search/address.json"


def geocode_address(address: str) -> dict:
    """
    도로명 주소를 지오코딩하여 동, 아파트명 추출 (Postcodify)
    
    Args:
        address: 도로명 주소
        
    Returns:
        {
            "address": 원본 주소,
            "postcode": 우편번호,
            "dong": 동 이름,
            "building": 건물명(아파트명),
            "jibun": 지번 주소
        }
    """
    params = {"q": address, "v": "2.1"}
    
    try:
        response = requests.get(POSTCODIFY_API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data.get("count", 0) > 0 and data.get("results"):
            result = data["results"][0]
            addr = result.get("address", {})
            
            # 지번 주소에서 동 이름 추출 (예: "신동 818")
            jibun = addr.get("old", "")
            dong = jibun.split()[0] if jibun else ""
            
            # 아파트명 추출
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
        print(f"❌ 오류: {address} - {e}")
        return {
            "address": address,
            "postcode": "",
            "dong": "",
            "building": "",
            "jibun": ""
        }


def main():
    if len(sys.argv) < 2:
        print("사용법: python geocode.py <input_csv_or_excel_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    print(f"📂 입력 파일: {input_path}")
    
    # 파일 형식에 따라 읽기 (CSV 또는 엑셀)
    if input_path.endswith(".csv"):
        df = pd.read_csv(input_path)
    elif input_path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(input_path)
    else:
        print("❌ 지원하지 않는 파일 형식입니다. (.csv, .xlsx, .xls만 가능)")
        sys.exit(1)
    
    if "주소" not in df.columns:
        print("❌ '주소' 컬럼이 없습니다. 컬럼명을 확인하세요.")
        print(f"현재 컬럼: {df.columns.tolist()}")
        sys.exit(1)
    
    print(f"📊 총 {len(df)}건의 주소 처리 시작")
    print(f"🌐 API: Postcodify (무료, API 키 불필요)")
    
    results = []
    for idx, row in df.iterrows():
        address = row["주소"]
        result = geocode_address(address)
        results.append(result)
        
        if (idx + 1) % 5 == 0:
            print(f"진행 중... {idx + 1}/{len(df)}")
        
        time.sleep(0.15)  # API 요청 제한 방지 (권장: 초당 7건)
    
    # 결과 저장
    output_df = pd.DataFrame(results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 절대 경로로 저장 (스크립트 위치 기준)
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "../..")
    output_path = os.path.join(project_root, "data/processed", f"geocoded_{timestamp}.csv")
    
    output_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    
    print(f"\n✅ 완료! 저장 위치: {output_path}")
    print(f"📊 성공: {output_df['dong'].notna().sum()}건 (동 정보)")
    print(f"🏠 아파트: {output_df[output_df['building'] != ''].shape[0]}건")
    print("\n📋 동별 집계 (상위 5개):")
    print(output_df["dong"].value_counts().head(5))


if __name__ == "__main__":
    main()
