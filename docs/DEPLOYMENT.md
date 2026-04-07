# 웹 앱 배포 가이드

## 로컬 실행 (내 컴퓨터에서)

### 1단계: 의존성 설치
```bash
cd /Users/taylor/income-growth/address-geo-analyzer
pip3 install -r requirements.txt
```

### 2단계: 앱 실행
```bash
streamlit run app.py
```

브라우저가 자동으로 열립니다 (http://localhost:8501)

---

## 온라인 배포 (친구에게 URL 공유)

### 옵션 A: Streamlit Community Cloud (무료, 추천)

**장점**: 완전 무료, 자동 배포, 친구에게 URL만 전달
**제한**: 공개 GitHub 저장소 필요

#### 1단계: GitHub에 푸시
```bash
cd /Users/taylor/income-growth/address-geo-analyzer
git remote add origin https://github.com/YOUR_USERNAME/address-geo-analyzer.git
git push -u origin main
```

#### 2단계: Streamlit Cloud 배포
1. [share.streamlit.io](https://share.streamlit.io) 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 저장소 선택: `YOUR_USERNAME/address-geo-analyzer`
5. Main file: `app.py`
6. "Deploy!" 클릭

**결과**: `https://your-username-address-geo-analyzer.streamlit.app`

---

### 옵션 B: Google Cloud Run (무료 티어)

**장점**: 비공개 가능, 커스텀 도메인
**제한**: 약간의 GCP 지식 필요

```bash
# Dockerfile 생성 (이미 준비됨)
gcloud run deploy address-geo-analyzer \
  --source . \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated
```

---

### 옵션 C: 친구 병원 컴퓨터에 직접 설치

**장점**: 인터넷 없이도 작동, 데이터 외부 유출 없음
**단점**: 친구가 컴퓨터 켤 때마다 실행해야 함

#### 전달 파일
```
address-geo-analyzer/
├── app.py
├── requirements.txt
├── start.sh              # 자동 실행 스크립트 (아래 참조)
└── README_INSTALL.txt    # 설치 가이드
```

#### start.sh (자동 실행 스크립트)
```bash
#!/bin/bash
cd "$(dirname "$0")"
pip3 install -r requirements.txt --quiet
streamlit run app.py
```

#### 사용법 (친구용)
1. 폴더를 다운로드
2. `start.sh` 더블클릭
3. 브라우저 열림 → 파일 업로드 → 분석 완료

---

## 권장 배포 방법

**비기술자 친구 + 월 1회 사용**
→ **옵션 A (Streamlit Cloud)** 추천

**이유:**
- URL만 전달하면 됨 (예: https://hospital-address.streamlit.app)
- 설치 불필요
- 항상 최신 버전
- 완전 무료

**유의사항:**
- GitHub 저장소는 공개 (코드 공개)
- 환자 데이터는 업로드 시에만 메모리에 있고 저장되지 않음
- HTTPS 암호화 통신

---

## 다음 단계

원하시는 배포 방법을 알려주시면:
1. GitHub 저장소 생성 도움
2. Streamlit Cloud 배포 진행
3. 또는 ZIP 파일로 패키징 (옵션 C)

어떤 방법으로 진행하시겠습니까?
