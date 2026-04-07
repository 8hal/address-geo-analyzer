# 환자 주소 분석기

병원 환자 주소(도로명) → 동/아파트 분석 + 통계 시각화

🌐 **웹 데모**: [여기에 Streamlit Cloud URL 입력]

## 빠른 시작

### 웹 브라우저에서 (권장)

위 웹 데모 링크 클릭 → 파일 업로드 → 분석 시작

### 로컬 설치

```bash
# 1. 저장소 클론
git clone https://github.com/YOUR_USERNAME/address-geo-analyzer.git
cd address-geo-analyzer

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 실행
streamlit run app.py
```

또는 간단 실행:
- Mac: `./start.sh`
- Windows: `start.bat`

## 주요 기능

✅ 도로명 주소 → 동/아파트명 자동 변환  
✅ 동별 환자 분포 (아파트 목록 포함)  
✅ 아파트별 통계 (동 정보 포함)  
✅ 차트 시각화  
✅ CSV 결과 다운로드  

**API 키 불필요** - Postcodify 무료 API 사용

## 기술 스택

- **백엔드**: Python 3.9+
- **웹 프레임워크**: Streamlit
- **데이터 처리**: pandas
- **지오코딩**: Postcodify API (무료)

## 라이선스

MIT License

## 문의

문광명 (PM, Hyperconnect)
