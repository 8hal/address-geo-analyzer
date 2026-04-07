# Streamlit Cloud 배포 가이드 (단계별)

## 1단계: GitHub 계정 확인

GitHub 계정이 있나요?
- 있음 → 2단계로
- 없음 → [github.com/join](https://github.com/join) 가입 (무료)

## 2단계: 새 저장소 생성

### 방법 A: GitHub 웹사이트
1. [github.com/new](https://github.com/new) 접속
2. Repository name: `address-geo-analyzer`
3. Description: "병원 환자 주소 분석 도구"
4. **Public** 선택 (Streamlit Cloud 무료 사용 조건)
5. "Create repository" 클릭

### 방법 B: GitHub CLI (gh 명령)
```bash
gh repo create address-geo-analyzer --public --description "병원 환자 주소 분석 도구"
```

## 3단계: 로컬 코드 푸시

```bash
cd /Users/taylor/income-growth/address-geo-analyzer

# 리모트 추가 (YOUR_USERNAME을 본인 GitHub ID로 변경)
git remote add origin https://github.com/YOUR_USERNAME/address-geo-analyzer.git

# 푸시
git push -u origin main
```

## 4단계: Streamlit Cloud 배포

1. [share.streamlit.io](https://share.streamlit.io) 접속
2. "Sign in with GitHub" 클릭
3. "New app" 클릭
4. 설정:
   - **Repository**: `YOUR_USERNAME/address-geo-analyzer`
   - **Branch**: `main`
   - **Main file path**: `app.py`
5. "Deploy!" 클릭

⏱️ 배포 시간: 약 2~3분

## 5단계: URL 확인

배포 완료 후 URL 생성:
```
https://YOUR_USERNAME-address-geo-analyzer-XXXX.streamlit.app
```

이 URL을 친구에게 전달하면 됩니다!

## 트러블슈팅

### "requirements.txt not found"
→ 저장소 루트에 requirements.txt가 있는지 확인

### "Module not found"
→ requirements.txt에 모든 의존성 포함 확인

### 앱이 느려요
→ 정상입니다. 무료 티어는 sleep 후 첫 로드 시 느림 (30초)

### 앱이 자동 종료돼요
→ 무료 티어는 7일간 접속 없으면 sleep
→ 다시 접속하면 자동 재시작

## 무료 제한사항

- **스토리지**: 1GB
- **메모리**: 1GB RAM
- **동시 사용자**: 제한 없음
- **sleep**: 7일간 미접속 시
- **개수**: 무제한

병원 용도로는 충분합니다!
