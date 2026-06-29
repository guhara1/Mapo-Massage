# 내부링크 강화 — 지역·역·테마 페이지 하단에 롱테일 관련 안내 블록을 생성한다.
#
# 지역끼리(area↔area), 역끼리(station↔station), 테마끼리의 교차 링크와
# 매거진 롱테일 글로의 연결을 한 곳에서 관리한다. build.py 가 페이지 경로를
# 보고 적절한 블록을 본문 끝에 주입한다. (페이지를 새로 만들지 않고 링크만 강화)

AREA_NAME = {
    "ahyeon-dong": "아현동", "gongdeok-dong": "공덕동", "dohwa-dong": "도화동",
    "yonggang-dong": "용강동", "daeheung-dong": "대흥동", "yeomni-dong": "염리동",
    "sinsu-dong": "신수동", "seogang-dong": "서강동", "seogyo-dong": "서교동",
    "hapjeong-dong": "합정동", "mangwon-dong": "망원동", "yeonnam-dong": "연남동",
    "seongsan-dong": "성산동", "sangam-dong": "상암동",
}

STATION_NAME = {
    "hongik-univ-station": "홍대입구역", "hapjeong-station": "합정역",
    "gongdeok-station": "공덕역", "mapo-station": "마포역",
    "mapo-gu-office-station": "마포구청역", "mangwon-station": "망원역",
    "sangsu-station": "상수역", "gwangheungchang-station": "광흥창역",
    "daeheung-station": "대흥역", "world-cup-stadium-station": "월드컵경기장역",
    "digital-media-city-station": "디지털미디어시티역", "sogang-univ-station": "서강대역",
    "sinchon-station": "신촌역", "ewha-womans-univ-station": "이대역",
    "ahyeon-station": "아현역", "aeogae-station": "애오개역",
}

THEME_NAME = {
    "swedish": "스웨디시", "lomilomi": "로미로미", "thai": "타이마사지",
    "chinese": "중국마사지", "aroma": "아로마테라피", "homecare": "홈케어",
    "hotel-style": "호텔식마사지", "foot": "발마사지", "sports": "스포츠·경락",
    "skincare": "스킨케어", "waxing": "왁싱", "couple": "커플 관리",
    "24hours": "24시간", "overnight": "수면 가능",
}

# 인접 대표 동 (실제 생활권 경계 기준)
AREA_NEIGHBORS = {
    "ahyeon-dong": ["yeomni-dong", "gongdeok-dong"],
    "gongdeok-dong": ["dohwa-dong", "yonggang-dong", "yeomni-dong"],
    "dohwa-dong": ["gongdeok-dong", "yonggang-dong"],
    "yonggang-dong": ["dohwa-dong", "gongdeok-dong"],
    "daeheung-dong": ["yeomni-dong", "sinsu-dong"],
    "yeomni-dong": ["daeheung-dong", "ahyeon-dong", "gongdeok-dong"],
    "sinsu-dong": ["seogang-dong", "daeheung-dong"],
    "seogang-dong": ["sinsu-dong", "seogyo-dong"],
    "seogyo-dong": ["hapjeong-dong", "yeonnam-dong", "seogang-dong"],
    "hapjeong-dong": ["seogyo-dong", "mangwon-dong"],
    "mangwon-dong": ["hapjeong-dong", "seongsan-dong"],
    "yeonnam-dong": ["seogyo-dong", "seongsan-dong"],
    "seongsan-dong": ["sangam-dong", "mangwon-dong"],
    "sangam-dong": ["seongsan-dong", "seongsan-dong"],
}

# 동 → 가까운 역, 어울리는 테마, 관련 매거진 글
AREA_STATION = {
    "ahyeon-dong": "ahyeon-station", "gongdeok-dong": "gongdeok-station",
    "dohwa-dong": "mapo-station", "yonggang-dong": "mapo-station",
    "daeheung-dong": "daeheung-station", "yeomni-dong": "ewha-womans-univ-station",
    "sinsu-dong": "sogang-univ-station", "seogang-dong": "gwangheungchang-station",
    "seogyo-dong": "hongik-univ-station", "hapjeong-dong": "hapjeong-station",
    "mangwon-dong": "mangwon-station", "yeonnam-dong": "hongik-univ-station",
    "seongsan-dong": "mapo-gu-office-station", "sangam-dong": "digital-media-city-station",
}

AREA_THEME = {
    "ahyeon-dong": "couple", "gongdeok-dong": "hotel-style", "dohwa-dong": "aroma",
    "yonggang-dong": "foot", "daeheung-dong": "thai", "yeomni-dong": "aroma",
    "sinsu-dong": "sports", "seogang-dong": "homecare", "seogyo-dong": "hotel-style",
    "hapjeong-dong": "couple", "mangwon-dong": "foot", "yeonnam-dong": "aroma",
    "seongsan-dong": "homecare", "sangam-dong": "sports",
}

# 역 → 가까운 역, 대표 동, 어울리는 테마
STATION_NEIGHBORS = {
    "hongik-univ-station": ["hapjeong-station", "sinchon-station"],
    "hapjeong-station": ["hongik-univ-station", "mangwon-station"],
    "gongdeok-station": ["mapo-station", "aeogae-station"],
    "mapo-station": ["gongdeok-station", "daeheung-station"],
    "mapo-gu-office-station": ["mangwon-station", "world-cup-stadium-station"],
    "mangwon-station": ["mapo-gu-office-station", "hapjeong-station"],
    "sangsu-station": ["hongik-univ-station", "gwangheungchang-station"],
    "gwangheungchang-station": ["sangsu-station", "daeheung-station"],
    "daeheung-station": ["gongdeok-station", "sogang-univ-station"],
    "world-cup-stadium-station": ["digital-media-city-station", "mapo-gu-office-station"],
    "digital-media-city-station": ["world-cup-stadium-station", "mapo-gu-office-station"],
    "sogang-univ-station": ["daeheung-station", "gwangheungchang-station"],
    "sinchon-station": ["ewha-womans-univ-station", "hongik-univ-station"],
    "ewha-womans-univ-station": ["ahyeon-station", "daeheung-station"],
    "ahyeon-station": ["ewha-womans-univ-station", "aeogae-station"],
    "aeogae-station": ["gongdeok-station", "ahyeon-station"],
}

STATION_AREA = {
    "hongik-univ-station": "seogyo-dong", "hapjeong-station": "hapjeong-dong",
    "gongdeok-station": "gongdeok-dong", "mapo-station": "dohwa-dong",
    "mapo-gu-office-station": "seongsan-dong", "mangwon-station": "mangwon-dong",
    "sangsu-station": "seogyo-dong", "gwangheungchang-station": "sinsu-dong",
    "daeheung-station": "daeheung-dong", "world-cup-stadium-station": "sangam-dong",
    "digital-media-city-station": "sangam-dong", "sogang-univ-station": "sinsu-dong",
    "sinchon-station": "daeheung-dong", "ewha-womans-univ-station": "yeomni-dong",
    "ahyeon-station": "ahyeon-dong", "aeogae-station": "gongdeok-dong",
}

STATION_THEME = {
    "hongik-univ-station": "hotel-style", "hapjeong-station": "couple",
    "gongdeok-station": "hotel-style", "mapo-station": "swedish",
    "mapo-gu-office-station": "homecare", "mangwon-station": "foot",
    "sangsu-station": "aroma", "gwangheungchang-station": "thai",
    "daeheung-station": "thai", "world-cup-stadium-station": "sports",
    "digital-media-city-station": "hotel-style", "sogang-univ-station": "sports",
    "sinchon-station": "thai", "ewha-womans-univ-station": "aroma",
    "ahyeon-station": "couple", "aeogae-station": "swedish",
}

# 테마 → 함께 보면 좋은 테마 2개 + 관련 매거진
THEME_RELATED = {
    "swedish": ["aroma", "lomilomi"], "lomilomi": ["swedish", "aroma"],
    "thai": ["sports", "homecare"], "chinese": ["sports", "thai"],
    "aroma": ["swedish", "overnight"], "homecare": ["swedish", "thai"],
    "hotel-style": ["aroma", "couple"], "foot": ["sports", "swedish"],
    "sports": ["thai", "foot"], "skincare": ["aroma", "waxing"],
    "waxing": ["skincare", "aroma"], "couple": ["swedish", "hotel-style"],
    "24hours": ["overnight", "swedish"], "overnight": ["aroma", "24hours"],
}

# 테마·지역 성격에 맞는 매거진 롱테일 글
THEME_MAGAZINE = {
    "swedish": ("swedish-vs-thai", "스웨디시 vs 타이마사지 비교 가이드"),
    "lomilomi": ("swedish-vs-thai", "오일 마사지 비교 가이드"),
    "thai": ("swedish-vs-thai", "타이마사지와 스웨디시 차이 비교"),
    "chinese": ("neck-shoulder-care", "어깨·목 결림 풀리는 관리 가이드"),
    "aroma": ("sleep-and-massage", "수면과 마사지의 관계"),
    "homecare": ("first-time-guide", "출장마사지 처음 이용 가이드"),
    "hotel-style": ("first-time-guide", "출장마사지 처음 이용 가이드"),
    "foot": ("post-workout-timing", "운동 후 회복 마사지 타이밍"),
    "sports": ("post-workout-timing", "운동 후 마사지 언제 받을까"),
    "skincare": ("first-time-guide", "처음 이용자가 묻는 10가지"),
    "waxing": ("first-time-guide", "처음 이용자가 묻는 10가지"),
    "couple": ("parents-gift", "부모님 선물·대리 예약 가이드"),
    "24hours": ("sleep-and-massage", "자기 전 마사지로 잠 바꾸기"),
    "overnight": ("sleep-and-massage", "수면과 마사지의 관계"),
}

AREA_MAGAZINE = {
    "ahyeon-dong": ("parents-gift", "부모님 선물·대리 예약 가이드"),
    "gongdeok-dong": ("first-time-guide", "출장마사지 처음 이용 가이드"),
    "dohwa-dong": ("parents-gift", "부모님 선물·대리 예약 가이드"),
    "yonggang-dong": ("post-workout-timing", "운동 후 회복 마사지 타이밍"),
    "daeheung-dong": ("neck-shoulder-care", "어깨·목 결림 관리 가이드"),
    "yeomni-dong": ("sleep-and-massage", "수면과 마사지의 관계"),
    "sinsu-dong": ("neck-shoulder-care", "거북목 어깨·목 결림 가이드"),
    "seogang-dong": ("first-time-guide", "출장마사지 처음 이용 가이드"),
    "seogyo-dong": ("first-time-guide", "출장마사지 처음 이용 가이드"),
    "hapjeong-dong": ("swedish-vs-thai", "스웨디시 vs 타이마사지 비교"),
    "mangwon-dong": ("post-workout-timing", "운동 후 회복 마사지 타이밍"),
    "yeonnam-dong": ("sleep-and-massage", "수면과 마사지의 관계"),
    "seongsan-dong": ("parents-gift", "부모님 선물·대리 예약 가이드"),
    "sangam-dong": ("post-workout-timing", "운동 후 회복 마사지 타이밍"),
}


def _li(href, text):
    return f'<li><a href="{href}">{text}</a></li>'


def render_area_related(slug):
    name = AREA_NAME[slug]
    items = []
    # 인접 지역 (롱테일 앵커)
    for n in AREA_NEIGHBORS.get(slug, []):
        items.append(_li(f"/mapo-gu/{n}/", f"{AREA_NAME[n]} 출장마사지·홈타이 안내"))
    # 가까운 역
    st = AREA_STATION.get(slug)
    if st:
        items.append(_li(f"/mapo-gu/stations/{st}/", f"{STATION_NAME[st]} 인근 방문 마사지 안내"))
    # 어울리는 테마 (롱테일)
    th = AREA_THEME.get(slug)
    if th:
        items.append(_li(f"/themes/{th}/", f"{name}에서 많이 찾는 {THEME_NAME[th]} 안내"))
    # 관련 매거진
    mg = AREA_MAGAZINE.get(slug)
    if mg:
        items.append(_li(f"/magazine/{mg[0]}/", mg[1]))
    # 코스·예약
    items.append(_li("/courses/", f"{name} 방문 코스·요금 안내"))
    items.append(_li("/reservation/", f"{name} 출장마사지 예약 방법"))
    return _wrap(f"{name} 주변 함께 보면 좋은 안내", items)


def render_station_related(slug):
    name = STATION_NAME[slug]
    items = []
    for n in STATION_NEIGHBORS.get(slug, []):
        items.append(_li(f"/mapo-gu/stations/{n}/", f"{STATION_NAME[n]} 인근 방문 마사지 안내"))
    ar = STATION_AREA.get(slug)
    if ar:
        items.append(_li(f"/mapo-gu/{ar}/", f"{AREA_NAME[ar]} 출장마사지·홈타이 안내"))
    th = STATION_THEME.get(slug)
    if th:
        items.append(_li(f"/themes/{th}/", f"{name} 인근에서 많이 찾는 {THEME_NAME[th]} 안내"))
    items.append(_li("/courses/", f"{name} 방문 코스·요금 안내"))
    items.append(_li("/reservation/", f"{name} 출장마사지 예약 방법"))
    return _wrap(f"{name} 주변 함께 보면 좋은 안내", items)


def render_theme_related(slug):
    name = THEME_NAME[slug]
    items = []
    for n in THEME_RELATED.get(slug, []):
        items.append(_li(f"/themes/{n}/", f"{THEME_NAME[n]} 방문 관리 안내"))
    mg = THEME_MAGAZINE.get(slug)
    if mg:
        items.append(_li(f"/magazine/{mg[0]}/", mg[1]))
    items.append(_li("/courses/", f"{name} 코스 구성·시간 안내"))
    items.append(_li("/mapo-gu/", f"{name} 방문 가능 지역 안내"))
    items.append(_li("/reservation/", f"{name} 예약 방법 안내"))
    return _wrap(f"{name}와 함께 보면 좋은 안내", items)


def _wrap(title, items):
    return (
        '<nav class="related-links" aria-label="관련 안내">'
        f'<p class="related-title">{title}</p>'
        f'<ul class="related-grid">{"".join(items)}</ul>'
        '</nav>'
    )
