# address-geo-analyzer

> 병원 환자 주소 데이터를 지오코딩하여 지도 기반 통계 제공

## 📋 개요

| 항목 | 내용 |
|------|------|
| **목적** | 병원 환자 주소 데이터를 지오코딩하여 지도 기반 통계 제공 |
| **데이터 소스** | BigQuery (`hc-bi-project`) |
| **상태** | 🚧 분석 중 |

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

## 🔧 실행 방법

```bash
# Python 스크립트 실행
python scripts/python/analysis.py

# Shell 스크립트 실행
./scripts/shell/fetch-data.sh
```

## 📊 주요 분석

- [ ] 분석 1
- [ ] 분석 2
- [ ] 분석 3

## 📝 관련 문서

- [분석 보고서](./reports/)
- [쿼리 가이드](./docs/)

---

문의: #moderation_qna 또는 ticket bot
