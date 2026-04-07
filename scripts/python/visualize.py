"""
address-geo-analyzer: 주소 분석 리포트 생성 (Postcodify 기반)

사용법:
    python visualize.py <geocoded_csv_path>

예시:
    python visualize.py ../data/processed/geocoded_20240315_120000.csv

출력:
    - ../data/output/report_20240315_120000.html (통계 리포트)
    - 콘솔에 동별/아파트별 집계
"""

import sys
import pandas as pd
from datetime import datetime


def create_statistics_report(df: pd.DataFrame, output_path: str):
    """
    동/아파트별 통계를 HTML 리포트로 생성
    
    Args:
        df: 지오코딩 결과 DataFrame (dong, building 필수)
        output_path: HTML 저장 경로
    """
    # 동별 집계
    dong_counts = df["dong"].value_counts().head(20)
    
    # 아파트별 집계 (건물명이 있는 경우만)
    building_df = df[df["building"] != ""]
    building_counts = building_df["building"].value_counts().head(20)
    
    # HTML 생성
    html = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>환자 주소 분석 리포트</title>
    <style>
        body {{
            font-family: 'Malgun Gothic', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            margin: 0 0 10px 0;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        .card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #34495e;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ecf0f1;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .rank {{
            background: #3498db;
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: bold;
        }}
        .count {{
            font-size: 18px;
            font-weight: bold;
            color: #e74c3c;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .summary-box {{
            background: #ecf0f1;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .summary-number {{
            font-size: 36px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .summary-label {{
            color: #7f8c8d;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏥 환자 주소 분석 리포트</h1>
        <p class="subtitle">생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="card">
        <h2>📊 요약</h2>
        <div class="summary">
            <div class="summary-box">
                <div class="summary-number">{len(df)}</div>
                <div class="summary-label">총 환자 수</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{len(dong_counts)}</div>
                <div class="summary-label">고유 동 수</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{len(building_counts)}</div>
                <div class="summary-label">고유 아파트 수</div>
            </div>
            <div class="summary-box">
                <div class="summary-number">{building_df.shape[0]}</div>
                <div class="summary-label">아파트 거주자</div>
            </div>
        </div>
    </div>
    
    <div class="card">
        <h2>📍 동별 환자 분포 (상위 20개)</h2>
        <table>
            <thead>
                <tr>
                    <th>순위</th>
                    <th>동</th>
                    <th>환자 수</th>
                    <th>비율</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, (dong, count) in enumerate(dong_counts.items(), 1):
        pct = (count / len(df)) * 100
        html += f"""
                <tr>
                    <td><span class="rank">{idx}</span></td>
                    <td>{dong}</td>
                    <td class="count">{count}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
    
    <div class="card">
        <h2>🏠 아파트별 환자 분포 (상위 20개)</h2>
        <table>
            <thead>
                <tr>
                    <th>순위</th>
                    <th>아파트</th>
                    <th>환자 수</th>
                    <th>비율</th>
                </tr>
            </thead>
            <tbody>
"""
    
    for idx, (building, count) in enumerate(building_counts.items(), 1):
        pct = (count / len(building_df)) * 100 if len(building_df) > 0 else 0
        html += f"""
                <tr>
                    <td><span class="rank">{idx}</span></td>
                    <td>{building}</td>
                    <td class="count">{count}</td>
                    <td>{pct:.1f}%</td>
                </tr>
"""
    
    html += """
            </tbody>
        </table>
    </div>
</body>
</html>
"""
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"✅ HTML 리포트 생성 완료: {output_path}")


def print_statistics(df: pd.DataFrame):
    """
    동/아파트별 통계를 콘솔에 출력
    """
    print("\n" + "="*50)
    print("📊 동별 환자 수 (상위 10개)")
    print("="*50)
    dong_counts = df["dong"].value_counts().head(10)
    for dong, count in dong_counts.items():
        pct = (count / len(df)) * 100
        print(f"{dong:15s} {count:4d}명 ({pct:5.1f}%)")
    
    print("\n" + "="*50)
    print("🏠 아파트별 환자 수 (상위 10개)")
    print("="*50)
    building_df = df[df["building"] != ""]
    if len(building_df) > 0:
        building_counts = building_df["building"].value_counts().head(10)
        for building, count in building_counts.items():
            pct = (count / len(building_df)) * 100
            print(f"{building:30s} {count:4d}명 ({pct:5.1f}%)")
    else:
        print("아파트 정보가 없습니다.")


def main():
    if len(sys.argv) < 2:
        print("사용법: python visualize.py <geocoded_csv_path>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    print(f"📂 입력 파일: {input_path}")
    
    # CSV 읽기
    df = pd.read_csv(input_path)
    
    # 콘솔 통계 출력
    print_statistics(df)
    
    # HTML 리포트 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 절대 경로로 저장
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.join(script_dir, "../..")
    output_path = os.path.join(project_root, "data/output", f"report_{timestamp}.html")
    
    create_statistics_report(df, output_path)
    
    print(f"\n💡 브라우저에서 확인: open {output_path}")


if __name__ == "__main__":
    main()

