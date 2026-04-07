# address-geo-analyzer

> 병원 환자 주소 데이터를 지오코딩하여 지도 기반 통계 제공

## 📋 개요

| 항목 | 내용 |
|------|------|
| **목적** | 동탄 병원 환자 도로명 주소를 동/아파트 단위로 변환하고 지도 시각화 |
| **데이터 소스** | 병원 EMR 시스템 (주소 엑셀 추출) |
| **고객** | 친구 (동탄 병원 원장) |
| **상태** | 🚧 개발 중 |

## 📁 프로젝트 구조

```
address-geo-analyzer/
├── README.md
├── data/               # 데이터 파일
│   ├── raw/            # 원본 데이터
│   └── processed/      # 가공 데이터
├── sql/                # BigQuery 쿼리
│   ├── analysis/       # 분석 쿼리
│   └── views/          # 뷰 생성
├── scripts/            # 분석 스크립트
│   ├── python/         # Python 스크립트
│   └── shell/          # Shell 스크립트
├── reports/            # 분석 보고서
└── docs/               # 문서
```

## 🔧 사용 방법

### 방법 1: 웹 앱 (추천 ⭐)

```bash
# 간단 실행
./start.sh              # Mac/Linux
start.bat               # Windows

# 또는 수동 실행
streamlit run app.py
```

브라우저에서 자동 실행 → 파일 업로드 → 결과 확인

### 방법 2: 명령줄 스크립트

```bash
cd scripts/python

# 주소 분석
python3 geocode.py ../../data/raw/sample_addresses.csv

# 리포트 생성
python3 visualize.py ../../data/processed/geocoded_*.csv

# HTML 리포트 열기
open ../../data/output/report_*.html
```

**API 키 발급 불필요** - Postcodify 무료 API 사용

## 📊 주요 기능

### ✅ 웹 앱 (비기술자용)
- [x] 드래그 앤 드롭 파일 업로드
- [x] 원클릭 분석 실행
- [x] 실시간 진행률 표시
- [x] 동별/아파트별 차트
- [x] CSV 결과 다운로드

### Phase 1: 배치 분석 (완료)
- [x] 도로명 주소 → 동/아파트명 변환 (Postcodify 무료 API)
- [x] HTML 통계 리포트 생성
- [x] 동별/아파트별 순위 집계

### Phase 2: 지도 시각화 (선택사항)
- [ ] Kakao Maps API 연동 (위경도 좌표 필요)
- [ ] 히트맵 시각화

### Phase 3: 시스템 연동 (미정)
- [ ] EMR 시스템 필드 추가 자문
- [ ] 배치 데이터 보강 스크립트

## 📝 관련 문서

- [빠른 시작 (웹 앱)](./docs/QUICKSTART.md)
- [배포 가이드](./docs/DEPLOYMENT.md)
- [요구사항 상세](./docs/REQUIREMENTS.md)
- [설치 가이드 (비기술자용)](./README_INSTALL.txt)

---

**프로젝트 그룹**: income-growth (cos_find 하왕수님과 동일 인맥)
