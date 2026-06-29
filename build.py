#!/usr/bin/env python3
"""간다 GO — 마포 출장마사지·홈타이 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import datetime
import email.utils
import html
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.site import (BASE_URL, BRAND, INDEXNOW_KEY, NAV, PHONE, PHONE_DISPLAY)
from content.reviews_data import agg_for, reviews_for
from content import related as REL

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000
BUILD_DATE = datetime.date.today().isoformat()


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def _abs(path: str) -> str:
    return BASE_URL.rstrip("/") + "/" + path.lstrip("/")


def _ld(obj) -> str:
    return ('<script type="application/ld+json">\n'
            + json.dumps(obj, ensure_ascii=False, indent=2)
            + "\n</script>\n")


def _review_objs(key, n=3):
    out = []
    for author, rating, body in reviews_for(key, n):
        out.append({
            "@type": "Review",
            "reviewRating": {"@type": "Rating", "ratingValue": str(rating),
                             "bestRating": "5", "worstRating": "1"},
            "author": {"@type": "Person", "name": author},
            "reviewBody": body,
        })
    return out


def _agg_obj(key):
    a = agg_for(key)
    return {"@type": "AggregateRating", "ratingValue": a["ratingValue"],
            "reviewCount": a["reviewCount"], "bestRating": "5", "worstRating": "1"}


def build_breadcrumb_ld(page, canonical):
    crumbs = page.get("breadcrumb") or []
    if not crumbs:
        return ""
    items = [{"@type": "ListItem", "position": 1, "name": "홈", "item": _abs("")}]
    pos = 2
    for label, href in crumbs:
        item = _abs(href) if href else canonical
        items.append({"@type": "ListItem", "position": pos, "name": label, "item": item})
        pos += 1
    return _ld({"@context": "https://schema.org", "@type": "BreadcrumbList",
                "itemListElement": items})


def build_service_ld(page, canonical):
    """지역·역·테마 페이지에 Service + 평점 + 후기(+ 테마는 가격 Offer) 스키마를 부여한다."""
    path = page["path"]
    h1 = page["h1"]
    desc = page["desc"]
    m_area = re.fullmatch(r"mapo-gu/([a-z\-]+-dong)/", path)
    m_station = re.fullmatch(r"mapo-gu/stations/([a-z\-]+)/", path)
    m_theme = re.fullmatch(r"themes/([a-z0-9\-]+)/", path)

    if m_area:
        name = REL.AREA_NAME[m_area.group(1)]
        area_served = {"@type": "Place", "name": f"서울특별시 마포구 {name}"}
        svc_name = f"{name} 출장마사지·홈타이"
    elif m_station:
        name = REL.STATION_NAME[m_station.group(1)]
        area_served = {"@type": "Place", "name": f"서울특별시 마포구 {name} 인근"}
        svc_name = f"{name} 인근 출장마사지·홈타이"
    elif m_theme:
        name = REL.THEME_NAME[m_theme.group(1)]
        area_served = {"@type": "AdministrativeArea", "name": "서울특별시 마포구"}
        svc_name = f"마포 {name} 방문 관리"
    else:
        return ""

    obj = {
        "@context": "https://schema.org",
        "@type": "Service",
        "name": svc_name,
        "serviceType": "출장마사지·홈타이 방문 관리",
        "description": desc,
        "url": canonical,
        "provider": {
            "@type": "HealthAndBeautyBusiness",
            "@id": _abs("") + "#business",
            "name": BRAND,
            "telephone": PHONE,
            "url": _abs(""),
        },
        "areaServed": area_served,
        "aggregateRating": _agg_obj(path),
        "review": _review_objs(path),
    }
    if m_theme:
        obj["offers"] = {
            "@type": "Offer",
            "priceCurrency": "KRW",
            "price": "90000",
            "priceSpecification": {
                "@type": "PriceSpecification",
                "minPrice": "90000", "maxPrice": "180000", "priceCurrency": "KRW",
            },
            "availability": "https://schema.org/InStock",
            "url": canonical,
        }
    return _ld(obj)


def build_schema(page, canonical):
    return build_breadcrumb_ld(page, canonical) + build_service_ld(page, canonical)


def build_related(page) -> str:
    path = page["path"]
    m_area = re.fullmatch(r"mapo-gu/([a-z\-]+-dong)/", path)
    m_station = re.fullmatch(r"mapo-gu/stations/([a-z\-]+)/", path)
    m_theme = re.fullmatch(r"themes/([a-z0-9\-]+)/", path)
    if m_area:
        return REL.render_area_related(m_area.group(1))
    if m_station and m_station.group(1) in REL.STATION_NAME:
        return REL.render_station_related(m_station.group(1))
    if m_theme and m_theme.group(1) in REL.THEME_NAME:
        return REL.render_theme_related(m_theme.group(1))
    return ""


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 페이지 유형별 구조화 데이터(JSON-LD) — 빵부스러기 + 서비스·평점·후기
    schema_ld = build_schema(page, canonical)
    extra_head = extra_head + schema_ld

    # 본문 끝 내부링크 강화 블록(롱테일 교차 링크)
    related_html = build_related(page)

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<link rel="alternate" type="application/rss+xml" title="{BRAND} 매거진" href="{BASE_URL}/rss.xml">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}/assets/og-image.png">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">G</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 마포구 전지역 방문 관리 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {body}
      {related_html}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">마포구 전지역 방문 출장마사지·홈타이 안내 사이트입니다. 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 마포구 전지역</span>
      </address>
    </div>
    <nav class="footer-col" aria-label="서비스 안내">
      <p class="footer-title">서비스</p>
      <ul>
        <li><a href="/massage/">마포 출장마사지</a></li>
        <li><a href="/mapo-gu/">지역별 안내</a></li>
        <li><a href="/mapo-gu/stations/">지하철역별 안내</a></li>
        <li><a href="/themes/">테마별 안내</a></li>
        <li><a href="/courses/">코스안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/reservation/">예약안내</a></li>
        <li><a href="/guide/">이용가이드</a></li>
        <li><a href="/reviews/">이용 후기</a></li>
        <li><a href="/support/">고객센터</a></li>
        <li><a href="/support/#faq">자주 묻는 질문</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">정책</p>
      <ul>
        <li><a href="/about/">운영자 소개</a></li>
        <li><a href="/support/privacy/">개인정보처리방침</a></li>
        <li><a href="/support/terms/">이용약관</a></li>
        <li><a href="/guide/#hygiene">위생·안전 기준</a></li>
        <li><a href="/guide/#prohibited">금지행위 안내</a></li>
        <li><a href="/support/#biz">제휴·기업 문의</a></li>
      </ul>
    </nav>
  </div>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {BRAND}. All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="https://t.me/googleseolab" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_urls = []

    for page in PAGES:
        path = page["path"]  # "" 또는 "mapo-gu/gongdeok-dong/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            sitemap_urls.append(path)
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    # sitemap.xml — lastmod·changefreq·priority 로 우선순위와 신선도를 명시해
    # 검색엔진이 핵심 페이지를 더 빠르게 식별·재크롤하도록 한다.
    def _sm_meta(path):
        hubs = {"", "massage/", "mapo-gu/", "mapo-gu/stations/", "themes/",
                "courses/", "reservation/", "magazine/", "reviews/", "guide/", "support/"}
        if path == "":
            return "daily", "1.0"
        if path in hubs:
            return "weekly", "0.9"
        if path.startswith("magazine/"):
            return "weekly", "0.7"
        if path.startswith("mapo-gu/") or path.startswith("themes/"):
            return "weekly", "0.8"
        return "monthly", "0.6"

    rows = []
    for path in sitemap_urls:
        cf, pr = _sm_meta(path)
        loc = BASE_URL.rstrip("/") + "/" + path
        rows.append(
            f"  <url><loc>{loc}</loc><lastmod>{BUILD_DATE}</lastmod>"
            f"<changefreq>{cf}</changefreq><priority>{pr}</priority></url>"
        )
    urls = "\n".join(rows)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            f"{urls}\n</urlset>\n"
        )

    # rss.xml — 매거진 아티클 피드 (네이버 서치어드바이저 RSS 제출용)
    posts = sorted(
        (p for p in PAGES if p.get("date")),
        key=lambda p: p["date"], reverse=True,
    )
    now_rfc822 = email.utils.format_datetime(
        datetime.datetime.now(datetime.timezone.utc))
    items = []
    for p in posts:
        link = BASE_URL.rstrip("/") + "/" + p["path"]
        pub = email.utils.format_datetime(datetime.datetime(
            *map(int, p["date"].split("-")), 9, 0,
            tzinfo=datetime.timezone(datetime.timedelta(hours=9))))
        items.append(
            "  <item>\n"
            f"    <title>{html.escape(p['h1'])}</title>\n"
            f"    <link>{link}</link>\n"
            f"    <guid isPermaLink=\"true\">{link}</guid>\n"
            f"    <description>{html.escape(p['desc'])}</description>\n"
            f"    <pubDate>{pub}</pubDate>\n"
            "  </item>"
        )
    with open(os.path.join(ROOT, "rss.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">\n'
            "<channel>\n"
            f"  <title>{html.escape(BRAND)} — 마포 출장마사지·홈타이 매거진</title>\n"
            f"  <link>{BASE_URL}/</link>\n"
            "  <description>마포구 방문 관리 이용 가이드와 마사지 정보 매거진</description>\n"
            "  <language>ko</language>\n"
            f"  <lastBuildDate>{now_rfc822}</lastBuildDate>\n"
            f'  <atom:link href="{BASE_URL}/rss.xml" rel="self" type="application/rss+xml"/>\n'
            + "\n".join(items) + "\n"
            "</channel>\n</rss>\n"
        )

    # IndexNow 인증 키 파일 (Bing·Naver 즉시 색인 통보용)
    with open(os.path.join(ROOT, f"{INDEXNOW_KEY}.txt"), "w", encoding="utf-8") as f:
        f.write(INDEXNOW_KEY)

    # robots.txt — 주요 검색엔진 크롤러 명시 허용 + 사이트맵 위치 고지.
    #   Googlebot(구글), Yeti(네이버), Daum(다음/카카오), bingbot(빙)
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: Googlebot\nAllow: /\n\n"
            "User-agent: Yeti\nAllow: /\n\n"
            "User-agent: Daum\nAllow: /\n\n"
            "User-agent: bingbot\nAllow: /\n\n"
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {BASE_URL.rstrip('/')}/sitemap.xml\n"
            f"Sitemap: {BASE_URL.rstrip('/')}/rss.xml\n"
        )

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_urls)} in sitemap.")


if __name__ == "__main__":
    build()
