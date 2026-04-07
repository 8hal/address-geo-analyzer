# Kakao Local API 설정 가이드

## 1. API 키 발급

1. [Kakao Developers](https://developers.kakao.com/) 접속
2. 로그인 후 "내 애플리케이션" 클릭
3. "애플리케이션 추가하기" 클릭
4. 앱 이름: `address-geo-analyzer` (임의)
5. 생성 후 "앱 키" 탭에서 **REST API 키** 복사

## 2. API 키 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:

```
KAKAO_API_KEY=your_rest_api_key_here
```

⚠️ **주의**: `.env` 파일은 Git에 커밋되지 않습니다 (.gitignore 등록됨)

## 3. API 사용량 제한

| 항목 | 제한 |
|------|------|
| 무료 할당량 | 300,000건/일 |
| 초당 요청 | 제한 없음 (권장: 10 QPS) |
| 주소 검색 정확도 | 도로명 주소 ~95%, 지번 주소 ~85% |

## 4. API 응답 예시

**요청**:
```
GET https://dapi.kakao.com/v2/local/search/address.json?query=경기 화성시 동탄순환대로 632
Authorization: KakaoAK {REST_API_KEY}
```

**응답**:
```json
{
  "documents": [
    {
      "address": {
        "region_1depth_name": "경기",
        "region_2depth_name": "화성시",
        "region_3depth_name": "반송동"
      },
      "address_name": "경기 화성시 반송동 123 OO아파트",
      "x": "127.0676",
      "y": "37.2236"
    }
  ]
}
```

## 5. 문제 해결

### API 키 오류 (401 Unauthorized)
- `.env` 파일 경로 확인
- API 키 복사 시 공백 포함 여부 확인

### 주소 검색 실패
- 도로명 주소 정확도 확인 (예: "OO로 123" vs "OO로123")
- 건물명 포함 여부 확인

### 사용량 초과
- [Kakao Developers 콘솔](https://developers.kakao.com/console/app)에서 사용량 확인
- 필요시 유료 플랜 전환 (월 10만건 추가: ~5,000원)

## 참고 문서

- [Kakao Local API 문서](https://developers.kakao.com/docs/latest/ko/local/dev-guide)
- [주소 검색 API](https://developers.kakao.com/docs/latest/ko/local/dev-guide#search-by-address)
