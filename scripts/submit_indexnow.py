#!/usr/bin/env python3
"""IndexNow 제출 스크립트 — 빙·네이버 등 참여 엔진에 URL 변경을 즉시 통보한다.

api.indexnow.org 한 곳에 제출하면 참여 검색엔진(Bing, Naver, Yandex, Seznam 등)
전체에 공유된다. 구글은 IndexNow 미참여이므로 scripts/submit_google.py 를 사용한다.

사용법:
  python3 scripts/submit_indexnow.py            # sitemap.xml 의 모든 URL 제출
  python3 scripts/submit_indexnow.py URL [URL]  # 특정 URL만 제출 (글 발행 직후)

표준 라이브러리만 사용한다. 키 파일({키}.txt)은 build.py 가 사이트 루트에
자동 생성하므로 배포만 되어 있으면 별도 준비가 필요 없다.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from content.site import BASE_URL, INDEXNOW_KEY

ENDPOINT = "https://api.indexnow.org/indexnow"
HOST = BASE_URL.split("//", 1)[1].rstrip("/")


def sitemap_urls():
    with open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8") as f:
        return re.findall(r"<loc>(.*?)</loc>", f.read())


def submit(urls):
    payload = {
        "host": HOST,
        "key": INDEXNOW_KEY,
        "keyLocation": f"{BASE_URL}/{INDEXNOW_KEY}.txt",
        "urlList": urls[:10000],
    }
    req = urllib.request.Request(
        ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as res:
            print(f"IndexNow 응답: HTTP {res.status} — {len(urls)}개 URL 제출 완료")
    except urllib.error.HTTPError as e:
        print(f"IndexNow 오류: HTTP {e.code} {e.reason}")
        print("  422 = 키 파일 미배포/URL-호스트 불일치, 403 = 키 불일치 가능성")
        sys.exit(1)


if __name__ == "__main__":
    urls = sys.argv[1:] or sitemap_urls()
    if not urls:
        sys.exit("제출할 URL이 없습니다. 먼저 python3 build.py 를 실행하세요.")
    submit(urls)
