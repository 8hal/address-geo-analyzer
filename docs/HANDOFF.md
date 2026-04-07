# 친구 전달 가이드

## 3가지 전달 방법

### 🌟 방법 1: URL 공유 (가장 추천!)

**Streamlit Cloud 무료 배포**

1. GitHub에 코드 푸시 (공개 저장소)
2. Streamlit Cloud에서 배포
3. 친구에게 URL만 전달

**장점:**
- 설치 불필요
- 브라우저에서 바로 사용
- 자동 업데이트
- 완전 무료

**URL 예시:** `https://hospital-address-analyzer.streamlit.app`

**진행 여부:** 원하시면 지금 바로 배포해드립니다!

---

### 📦 방법 2: ZIP 파일 전달

**로컬 설치 패키지**

```bash
# ZIP 파일 생성
cd /Users/taylor/income-growth
zip -r address-geo-analyzer.zip address-geo-analyzer/ \
  -x "*.git*" -x "*__pycache__*" -x "*.pyc" \
  -x "data/raw/*" -x "data/processed/*" -x "data/output/*"
```

**포함 파일:**
- app.py (웹 앱)
- start.sh / start.bat (자동 실행)
- README_INSTALL.txt (설치 가이드)
- requirements.txt (라이브러리 목록)

**친구 작업:**
1. ZIP 압축 해제
2. start.sh (Mac) 또는 start.bat (Windows) 더블클릭
3. 브라우저 자동 실행

**단점:**
- Python 설치 필요
- 초회 실행 시 라이브러리 설치 (30초~1분)

---

### 📧 방법 3: 이메일/카톡 전달

**간단 공유**

1. 위 ZIP 파일을 이메일/카톡으로 전송
2. README_INSTALL.txt 내용을 메시지로 요약 전달

**메시지 예시:**
```
[환자 주소 분석기]

첨부 파일 압축 해제 후
Mac: start.sh 더블클릭
Windows: start.bat 더블클릭

브라우저 열리면 파일 업로드 → 분석 시작 버튼만 누르면 됩니다.

문제 있으면 연락주세요!
```

---

## 💡 추천 순서

**비기술자 + 월 1회 사용**
1. **방법 1 (URL)** 시도 (10분)
   → 실패 시
2. **방법 2 (ZIP)** 백업 (5분)

**근거:**
- 방법 1이 가장 쉽지만 GitHub 계정 필요
- 방법 2는 확실하지만 Python 설치 필요
- 두 가지 모두 준비하면 안전

---

## 다음 단계

어떤 방법으로 진행하시겠습니까?

**A) Streamlit Cloud 배포 (추천)**
→ GitHub 저장소 생성 도움

**B) ZIP 파일 생성**
→ 지금 바로 패키징

**C) 둘 다**
→ URL + ZIP 백업

**D) 테스트 먼저**
→ 내 컴퓨터에서 start.sh 실행해보기
