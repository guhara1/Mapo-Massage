# 간다 GO — 마포 출장마사지·홈타이 안내 사이트

마포구 전지역 방문 관리(출장마사지·홈타이) 안내용 정적 사이트입니다.
예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함

```
build.py            # 빌드 스크립트 (레이아웃·글자수 검사·sitemap 생성)
content/
  site.py           # 상호·전화·BASE_URL·메뉴 구조
  main.py           # 메인 페이지 (+ LocalBusiness/FAQPage JSON-LD)
  areas.py          # 지역별: 마포구 허브 + 대표 동 14개
  stations.py       # 지하철역별: 허브 + 16개 역
  themes.py         # 테마별: 허브 + 14개 테마
  info.py           # 출장마사지 안내·코스·예약·가이드·후기·고객센터·약관
assets/             # CSS, 모바일 내비 JS
```

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드에 강제됨)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외
- 지역은 대표 동 14개만 (아현동·공덕동·도화동·용강동·대흥동·염리동·신수동·서강동·서교동·합정동·망원동·연남동·성산동·상암동) — 숫자 행정동 페이지 없음 (망원1·2동→망원동, 성산1·2동→성산동 통합)
- 역은 역 1개당 페이지 1개 — 환승역(홍대입구·공덕·합정·디지털미디어시티)도 URL 하나, 출구별 페이지 없음
- **지역+역+테마 조합 페이지 없음** (도어웨이 방지) — 테마는 독립 페이지로만 운영
- 상단/하위 메뉴와 푸터에 키워드·지역명·역명 대량 나열 없음
- 모든 페이지 본문은 페이지별 고유 작성 (지역명만 바꾼 복붙 없음)

## 색인 운영 (도메인: https://mapo-massage.netlify.app)

빌드 시 자동 생성: `sitemap.xml`(lastmod·changefreq·priority 포함) · `rss.xml`(매거진 피드) ·
`robots.txt`(Googlebot/Yeti/Daum/bingbot 명시 허용 + Sitemap 2줄) · IndexNow 키 파일.

### 최초 1회
1. **Google Search Console**: 속성 등록 → `sitemap.xml`·`rss.xml` 제출 →
   "URL 검사 → 색인 생성 요청"으로 메인·허브 페이지 우선 요청
2. **네이버 서치어드바이저**: 소유 확인(메인 메타 태그 등록됨) →
   사이트맵 `sitemap.xml` + RSS `rss.xml` 제출 → "웹 페이지 수집 요청"으로 메인 요청

### 콘텐츠 갱신 때마다
```bash
python3 build.py                          # lastmod·RSS 갱신
python3 scripts/submit_indexnow.py        # 빙·네이버 등 IndexNow 즉시 통보
python3 scripts/submit_google.py          # 구글 Search Console API 사이트맵 재제출
```
- IndexNow: 키 파일이 사이트 루트에 배포되므로 별도 준비 없음. 특정 URL만
  통보하려면 `python3 scripts/submit_indexnow.py <URL>`
- 구글: 핑 엔드포인트는 폐기되어 Search Console API 제출이 공식 경로.
  서비스 계정 설정은 `scripts/submit_google.py` 상단 주석 참고.
  Indexing API는 채용공고·라이브방송 전용이라 일반 페이지에는 쓰지 않는다.
