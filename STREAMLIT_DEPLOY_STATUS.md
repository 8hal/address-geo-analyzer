# Streamlit Cloud 배포 진행

## ✅ 완료된 단계

### 1. GitHub 저장소 생성 ✓
- **계정**: 8hal
- **저장소**: https://github.com/8hal/address-geo-analyzer
- **브랜치**: main
- **상태**: Public (Streamlit Cloud 무료 조건)

### 2. 코드 푸시 ✓
- 총 10개 커밋 푸시 완료
- app.py (Streamlit 앱)
- requirements.txt (의존성)
- 모든 문서 포함

## 🚀 다음 단계: Streamlit Cloud 배포

### 자동 배포 (추천)

아래 링크를 클릭하면 자동으로 배포 설정 화면이 열립니다:

**배포 링크**: https://share.streamlit.io/deploy?repository=8hal/address-geo-analyzer&branch=main&mainModule=app.py

### 수동 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. "Sign in with GitHub" 클릭 (8hal 계정)
3. "New app" 클릭
4. 설정:
   - **Repository**: `8hal/address-geo-analyzer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. "Deploy!" 클릭

⏱️ 배포 시간: 약 2~3분

## 📱 예상 결과

배포 완료 후 URL:
```
https://8hal-address-geo-analyzer-XXXX.streamlit.app
```

또는

```
https://address-geo-analyzer-XXXX.streamlit.app
```

이 URL을 친구에게 전달하시면 됩니다!

## 🎯 친구 전달 메시지 (배포 후)

```
[환자 주소 분석기]

웹 주소: https://YOUR_APP_URL.streamlit.app

사용법:
1. 위 링크 클릭
2. 환자 주소 엑셀 파일 업로드 (컬럼명: "주소")
3. "분석 시작" 버튼 클릭
4. 결과 확인 후 다운로드

문의: 문광명 (연락처)
```

## ⚠️ 주의사항

1. **GitHub 계정 권한**: Streamlit Cloud가 8hal 저장소 접근 권한 요청 → "승인" 클릭
2. **첫 배포**: 2~3분 소요 (정상)
3. **Sleep 모드**: 7일간 미접속 시 자동 sleep (재접속 시 30초 내 재시작)

## 다음 작업

1. 위 배포 링크 클릭
2. 배포 완료 대기 (2~3분)
3. URL 확인
4. 테스트 (샘플 파일 업로드)
5. 친구에게 URL 전달
