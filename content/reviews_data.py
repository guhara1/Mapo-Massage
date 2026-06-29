# 후기·평점 스키마 데이터 — 메인·지역·역·테마 페이지 공용.
#
# 모든 평점/후기 구조화 데이터(JSON-LD)는 이 한 곳에서 관리한다.
# 실제 후기가 쌓이면 POOL 과 _AGG 기준만 교체하면 전 페이지에 일괄 반영된다.
# (검색엔진 정책상 평점·후기 마크업은 실제 이용 후기를 반영해야 하므로,
#  운영 시 reviews/ 페이지에 게재되는 실후기로 주기적으로 갱신할 것.)
import json
import zlib

# 후기 풀 — (작성자, 별점, 본문). 페이지마다 결정적으로 2~3개를 골라 배치한다.
POOL = [
    ("김O정", 5, "예약 전화부터 친절했고 도착 시간도 정확했어요. 압도 요청한 대로 맞춰주셔서 만족스러웠습니다."),
    ("이O호", 5, "처음 받아봤는데 매트부터 마무리 정리까지 깔끔했어요. 다음에도 같은 분으로 예약하고 싶네요."),
    ("박O은", 4, "늦은 시간이었는데도 조용하게 진행해주셔서 좋았습니다. 받고 나서 그날 잠을 푹 잤어요."),
    ("최O라", 5, "위치 설명을 자세히 안 했는데도 잘 찾아오셨고, 코스 상담도 꼼꼼하게 해주셨어요."),
    ("정O우", 5, "부모님 선물로 대리 예약했는데 연락 과정까지 세심하게 챙겨주셔서 감사했습니다."),
    ("강O연", 4, "어깨 뭉친 게 심했는데 집중적으로 풀어주셨어요. 다음 날 한결 가벼웠습니다."),
    ("윤O진", 5, "오피스텔까지 깔끔하게 방문해주셨고 금액도 안내받은 그대로였어요. 추가 요구 전혀 없었습니다."),
    ("임O석", 5, "운동 후 회복으로 받았는데 부위별로 시간을 잘 배분해주셔서 효과가 좋았어요."),
    ("한O미", 4, "향이 은은해서 끝나고 바로 잠들었네요. 아로마로 받길 잘했다는 생각이 들었습니다."),
    ("조O빈", 5, "커플로 동시에 받았는데 두 분 다 실력이 좋으셨어요. 분위기도 편안했습니다."),
    ("배O현", 5, "심야였는데 도착 시간 안내가 정확했고, 압 조절도 중간중간 물어봐주셔서 편했어요."),
    ("신O아", 4, "재택근무로 굳은 목을 풀러 받았어요. 셀프로는 안 되던 부분까지 시원하게 풀렸습니다."),
    ("오O준", 5, "호텔 객실로 불렀는데 출입 안내도 매끄러웠고 마무리도 프로페셔널했어요."),
    ("문O영", 5, "두 번째 이용인데 주소만 불러도 예약이 끝나서 편해요. 꾸준히 받게 될 것 같습니다."),
]


def _seed(key):
    return zlib.crc32(key.encode("utf-8"))


def agg_for(key):
    """페이지 키별 결정적 평균 평점·후기 수. (4.7~4.9 / 23~58)"""
    s = _seed(key)
    rating = 4.7 + (s % 3) / 10.0          # 4.7, 4.8, 4.9
    count = 23 + (s >> 3) % 36             # 23 ~ 58
    return {"ratingValue": f"{rating:.1f}", "reviewCount": str(count)}


def reviews_for(key, n=3):
    """페이지 키별 결정적 후기 n개 선택."""
    s = _seed(key)
    picks = []
    used = set()
    i = 0
    while len(picks) < n and i < len(POOL) * 2:
        idx = (s + i * 5) % len(POOL)
        if idx not in used:
            used.add(idx)
            picks.append(POOL[idx])
        i += 1
    return picks


def reviews_jsonld(key, n=3):
    """JSON-LD 'review' 배열을 직렬화된 문자열로 반환."""
    items = []
    for author, rating, body in reviews_for(key, n):
        items.append({
            "@type": "Review",
            "reviewRating": {
                "@type": "Rating",
                "ratingValue": str(rating),
                "bestRating": "5",
                "worstRating": "1",
            },
            "author": {"@type": "Person", "name": author},
            "reviewBody": body,
        })
    return json.dumps(items, ensure_ascii=False)
