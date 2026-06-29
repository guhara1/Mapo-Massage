#!/usr/bin/env python3
"""구글 색인 제출 스크립트 — Search Console 사이트맵 제출 + Indexing API 통보.

구글은 IndexNow에 참여하지 않으며, 과거의 사이트맵 핑 엔드포인트
(google.com/ping?sitemap=...)는 2023년 6월 지원 종료 후 폐기되었다.
현재 공식적으로 동작하는 자동화 경로는 두 가지다.

  1. Search Console API 사이트맵 제출 (sitemaps.submit)
     — 폐기된 핑의 공식 대체. 어떤 사이트든 정책상 안전하다.
  2. Indexing API (urlNotifications.publish)
     — 구글 공식 정책상 JobPosting·BroadcastEvent 페이지 전용.
       일반 페이지 제출은 정책 위반으로 무시되거나 불이익이 있을 수 있어
       기본 비활성화한다. (--indexing-api 플래그로만 동작)

준비:
  1. Google Cloud 프로젝트 생성 → 'Search Console API'(및 필요 시
     'Web Search Indexing API') 사용 설정
  2. 서비스 계정 생성 → JSON 키 다운로드
  3. Search Console 속성(https://mapo-massage.netlify.app/)에
     서비스 계정 이메일을 '소유자'로 추가
  4. pip install google-auth requests

사용법:
  export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
  python3 scripts/submit_google.py                     # 사이트맵 제출(권장)
  python3 scripts/submit_google.py --indexing-api URL  # Indexing API(전용 페이지만)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from content.site import BASE_URL

SITE = BASE_URL.rstrip("/") + "/"
CREDS_PATH = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")


def _session(scopes):
    try:
        import google.auth.transport.requests
        import requests
        from google.oauth2 import service_account
    except ImportError:
        sys.exit("필요 패키지가 없습니다: pip install google-auth requests")
    if not CREDS_PATH or not os.path.exists(CREDS_PATH):
        sys.exit("GOOGLE_APPLICATION_CREDENTIALS 환경변수에 서비스 계정 JSON 경로를 지정하세요.")
    creds = service_account.Credentials.from_service_account_file(
        CREDS_PATH, scopes=scopes)
    creds.refresh(google.auth.transport.requests.Request())
    s = requests.Session()
    s.headers["Authorization"] = f"Bearer {creds.token}"
    return s


def submit_sitemaps():
    """Search Console API로 sitemap.xml·rss.xml 을 제출한다 (핑의 공식 대체)."""
    s = _session(["https://www.googleapis.com/auth/webmasters"])
    from urllib.parse import quote
    for feed in ("sitemap.xml", "rss.xml"):
        feed_url = SITE + feed
        api = (f"https://www.googleapis.com/webmasters/v3/sites/"
               f"{quote(SITE, safe='')}/sitemaps/{quote(feed_url, safe='')}")
        r = s.put(api, timeout=30)
        ok = "성공" if r.status_code in (200, 204) else f"실패 HTTP {r.status_code}: {r.text[:120]}"
        print(f"사이트맵 제출 {feed_url} → {ok}")


def submit_indexing_api(urls):
    """Indexing API URL 통보 — JobPosting/BroadcastEvent 페이지 전용(정책 주의)."""
    s = _session(["https://www.googleapis.com/auth/indexing"])
    api = "https://indexing.googleapis.com/v3/urlNotifications:publish"
    for u in urls:
        r = s.post(api, json={"url": u, "type": "URL_UPDATED"}, timeout=30)
        ok = "성공" if r.status_code == 200 else f"실패 HTTP {r.status_code}: {r.text[:120]}"
        print(f"Indexing API {u} → {ok}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--indexing-api":
        if not args[1:]:
            sys.exit("--indexing-api 뒤에 제출할 URL을 지정하세요.")
        print("주의: Indexing API는 구글 정책상 채용공고·라이브방송 페이지 전용입니다.")
        submit_indexing_api(args[1:])
    else:
        submit_sitemaps()
