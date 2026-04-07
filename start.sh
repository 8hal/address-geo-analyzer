#!/bin/bash
# 환자 주소 분석기 자동 실행 스크립트

echo "🏥 환자 주소 분석기를 시작합니다..."
echo ""

# 현재 스크립트 위치로 이동
cd "$(dirname "$0")"

# Python 3 확인
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3가 설치되어 있지 않습니다."
    echo "   https://www.python.org/downloads/ 에서 다운로드하세요."
    read -p "아무 키나 눌러 종료..."
    exit 1
fi

echo "✅ Python 확인 완료"

# 의존성 설치
echo "📦 필요한 라이브러리 설치 중..."
pip3 install -r requirements.txt --quiet --user

if [ $? -ne 0 ]; then
    echo "❌ 라이브러리 설치 실패"
    read -p "아무 키나 눌러 종료..."
    exit 1
fi

echo "✅ 라이브러리 설치 완료"
echo ""
echo "🌐 웹 브라우저가 자동으로 열립니다..."
echo "   (안 열리면 http://localhost:8501 을 직접 여세요)"
echo ""
echo "⚠️  이 창을 닫으면 앱이 종료됩니다."
echo ""

# Streamlit 실행
if command -v streamlit &> /dev/null; then
    streamlit run app.py
else
    python3 -m streamlit run app.py
fi
