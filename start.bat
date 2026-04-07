@echo off
REM 환자 주소 분석기 자동 실행 스크립트 (Windows)

echo ========================================
echo   환자 주소 분석기
echo ========================================
echo.

REM Python 확인
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python이 설치되어 있지 않습니다.
    echo     https://www.python.org/downloads/ 에서 다운로드하세요.
    pause
    exit /b 1
)

echo [√] Python 확인 완료
echo.

REM 의존성 설치
echo [*] 필요한 라이브러리 설치 중...
pip install -r requirements.txt --quiet --user

if %errorlevel% neq 0 (
    echo [X] 라이브러리 설치 실패
    pause
    exit /b 1
)

echo [√] 라이브러리 설치 완료
echo.
echo [*] 웹 브라우저가 자동으로 열립니다...
echo     (안 열리면 http://localhost:8501 을 직접 여세요)
echo.
echo [!] 이 창을 닫으면 앱이 종료됩니다.
echo.

REM Streamlit 실행
streamlit run app.py
if %errorlevel% neq 0 (
    python -m streamlit run app.py
)

pause
