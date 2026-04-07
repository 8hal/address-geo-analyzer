# 빠른 시작 가이드

## 1분 안에 시작하기

### 1단계: 의존성 설치
```bash
cd /Users/taylor/income-growth/address-geo-analyzer
pip3 install -r requirements.txt
```

### 2단계: 주소 데이터 준비
CSV 또는 엑셀 파일을 `data/raw/` 폴더에 넣으세요.

**필수 형식:**
- 컬럼명: `주소` (정확히 이 이름)
- 예시:
  ```
  주소
  경기도 화성시 동탄구 동탄신리천로8길 15
  경기도 화성시 동탄구 동탄순환대로19길 59
  ```

### 3단계: 실행
```bash
cd scripts/python

# 주소 분석
python3 geocode.py ../../data/raw/your_file.csv

# 리포트 생성 (방금 생성된 파일명 사용)
python3 visualize.py ../../data/processed/geocoded_20260407_*.csv

# HTML 리포트 열기
open ../../data/output/report_*.html
```

## 결과물 확인

### geocoded_*.csv (data/processed/)
```csv
address,postcode,dong,building,jibun
경기도 화성시 동탄구 동탄신리천로8길 15,18494,신동,동탄2엘에이치40단지,신동 818
```

### report_*.html (data/output/)
- 요약 통계 (총 환자 수, 동 수, 아파트 수)
- 동별 환자 분포 (상위 20개)
- 아파트별 환자 분포 (상위 20개)

## 문제 해결

### "주소 컬럼이 없습니다" 오류
→ 엑셀/CSV 파일의 첫 줄에 `주소` 컬럼이 있는지 확인

### API 호출 실패
→ 인터넷 연결 확인 (Postcodify는 외부 API)

### pandas 설치 오류
```bash
pip3 install --upgrade pip
pip3 install pandas requests openpyxl
```

## API 키 발급 불필요!
Postcodify는 무료 API로 별도 가입/키 발급 없이 바로 사용 가능합니다.
