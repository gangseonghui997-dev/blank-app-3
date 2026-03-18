import streamlit as st
from datetime import date, time
from korean_lunar_calendar import KoreanLunarCalendar

st.set_page_config(
    page_title="🌸 몽글몽글 만세력 🌸",
    page_icon="🌸",
    layout="centered"
)

# ---------------------------
# 기본 데이터
# ---------------------------
STEMS = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
BRANCHES = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

ELEMENTS = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수",
    "자": "수", "해": "수",
    "인": "목", "묘": "목",
    "사": "화", "오": "화",
    "진": "토", "술": "토", "축": "토", "미": "토",
    "신": "금", "유": "금",
}

YINYANG = {
    "갑": "양", "병": "양", "무": "양", "경": "양", "임": "양",
    "을": "음", "정": "음", "기": "음", "신": "음", "계": "음",
    "자": "양", "인": "양", "진": "양", "오": "양", "신": "양", "술": "양",
    "축": "음", "묘": "음", "사": "음", "미": "음", "유": "음", "해": "음",
}

TEN_GODS = {
    "비견": "나와 쏙 빼닮은 단짝 친구 👯‍♀️",
    "겁재": "지기 싫어! 불타는 경쟁심 🔥",
    "식신": "냠냠 맛있는 거 먹고 신나게 놀기 🍰",
    "상관": "통통 튀는 아이디어 뱅크 ✨",
    "편재": "앗싸! 생각지도 못한 용돈 💸",
    "정재": "차곡차곡 모으는 알뜰살뜰 저금통 🐷",
    "편관": "으쌰으쌰! 책임감 넘치는 대장님 👑",
    "정관": "바른 생활 사나이/어린이 🌟",
    "편인": "엉뚱발랄 4차원 상상력 🎈",
    "정인": "따뜻한 엄마 품처럼 포근함 🧸",
}

TEN_GOD_TABLE = {
    "갑": {"갑": "비견", "을": "겁재", "병": "식신", "정": "상관", "무": "편재", "기": "정재", "경": "편관", "신": "정관", "임": "편인", "계": "정인"},
    "을": {"갑": "겁재", "을": "비견", "병": "상관", "정": "식신", "무": "정재", "기": "편재", "경": "정관", "신": "편관", "임": "정인", "계": "편인"},
    "병": {"갑": "편인", "을": "정인", "병": "비견", "정": "겁재", "무": "식신", "기": "상관", "경": "편재", "신": "정재", "임": "편관", "계": "정관"},
    "정": {"갑": "정인", "을": "편인", "병": "겁재", "정": "비견", "무": "상관", "기": "식신", "경": "정재", "신": "편재", "임": "정관", "계": "편관"},
    "무": {"갑": "편관", "을": "정관", "병": "편인", "정": "정인", "무": "비견", "기": "겁재", "경": "식신", "신": "상관", "임": "편재", "계": "정재"},
    "기": {"갑": "정관", "을": "편관", "병": "정인", "정": "편인", "무": "겁재", "기": "비견", "경": "상관", "신": "식신", "임": "정재", "계": "편재"},
    "경": {"갑": "편재", "을": "정재", "병": "편관", "정": "정관", "무": "편인", "기": "정인", "경": "비견", "신": "겁재", "임": "식신", "계": "상관"},
    "신": {"갑": "정재", "을": "편재", "병": "정관", "정": "편관", "무": "정인", "기": "편인", "경": "겁재", "신": "비견", "임": "상관", "계": "식신"},
    "임": {"갑": "식신", "을": "상관", "병": "편재", "정": "정재", "무": "편관", "기": "정관", "경": "편인", "신": "정인", "임": "비견", "계": "겁재"},
    "계": {"갑": "상관", "을": "식신", "병": "정재", "정": "편재", "무": "정관", "기": "편관", "경": "정인", "신": "편인", "임": "겁재", "계": "비견"},
}

HOUR_STEM_START = {
    "갑": "갑", "기": "갑",
    "을": "병", "경": "병",
    "병": "무", "신": "무",
    "정": "경", "임": "경",
    "무": "임", "계": "임",
}

HOUR_BRANCH_TABLE = [
    ((23, 0), (23, 59), "자"),
    ((0, 0), (0, 59), "자"),
    ((1, 0), (2, 59), "축"),
    ((3, 0), (4, 59), "인"),
    ((5, 0), (6, 59), "묘"),
    ((7, 0), (8, 59), "진"),
    ((9, 0), (10, 59), "사"),
    ((11, 0), (12, 59), "오"),
    ((13, 0), (14, 59), "미"),
    ((15, 0), (16, 59), "신"),
    ((17, 0), (18, 59), "유"),
    ((19, 0), (20, 59), "술"),
    ((21, 0), (22, 59), "해"),
]

def strip_unit(text: str) -> str:
    return text.replace("년", "").replace("월", "").replace("일", "").replace("(윤)", "").replace("(윤월)", "").strip()

def split_ganji(kor_gapja: str):
    parts = kor_gapja.split()
    if len(parts) < 3:
        raise ValueError(f"간지 문자열 파싱 실패: {kor_gapja}")
    return strip_unit(parts[0]), strip_unit(parts[1]), strip_unit(parts[2])

def get_hour_branch(hour: int, minute: int) -> str:
    total = hour * 60 + minute
    for (sh, sm), (eh, em), branch in HOUR_BRANCH_TABLE:
        start = sh * 60 + sm
        end = eh * 60 + em
        if start <= end:
            if start <= total <= end:
                return branch
        else:
            if total >= start or total <= end:
                return branch
    return "자"

def get_hour_stem(day_stem: str, hour_branch: str) -> str:
    start_stem = HOUR_STEM_START[day_stem]
    start_idx = STEMS.index(start_stem)
    branch_idx = BRANCHES.index(hour_branch)
    return STEMS[(start_idx + branch_idx) % 10]

def get_hour_ganji(day_stem: str, hour: int, minute: int) -> str:
    hour_branch = get_hour_branch(hour, minute)
    hour_stem = get_hour_stem(day_stem, hour_branch)
    return hour_stem + hour_branch

def get_ten_god(day_stem: str, other_stem: str) -> str:
    return TEN_GOD_TABLE.get(day_stem, {}).get(other_stem, "-")

def analyze_ohang(pillars):
    counts = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    for pillar in pillars:
        stem = pillar[0]
        branch = pillar[1]
        counts[ELEMENTS[stem]] += 1
        counts[ELEMENTS[branch]] += 1
    return counts

def dominant_elements(counts):
    max_val = max(counts.values())
    min_val = min(counts.values())
    strong = [k for k, v in counts.items() if v == max_val]
    weak = [k for k, v in counts.items() if v == min_val]
    return strong, weak

def safe_set_solar(calendar_obj, y, m, d):
    ok = calendar_obj.setSolarDate(y, m, d)
    if not ok:
        raise ValueError("지원 범위를 벗어난 날짜이거나 잘못된 날짜입니다.")
    return calendar_obj

def get_full_saju(y: int, m: int, d: int, hour: int, minute: int):
    calendar = KoreanLunarCalendar()
    safe_set_solar(calendar, y, m, d)

    gapja_kor = calendar.getGapJaString()
    year_ganji, month_ganji, day_ganji = split_ganji(gapja_kor)
    hour_ganji = get_hour_ganji(day_ganji[0], hour, minute)

    return {
        "solar_date": calendar.SolarIsoFormat(),
        "lunar_date": calendar.LunarIsoFormat(),
        "is_intercalation": calendar.isIntercalation,
        "year_pillar": year_ganji,
        "month_pillar": month_ganji,
        "day_pillar": day_ganji,
        "hour_pillar": hour_ganji,
        "gapja_kor": gapja_kor,
    }

def get_today_saju():
    today = date.today()
    calendar = KoreanLunarCalendar()
    safe_set_solar(calendar, today.year, today.month, today.day)
    _, _, day_ganji = split_ganji(calendar.getGapJaString())
    return day_ganji

def make_summary(saju):
    day_stem = saju["day_pillar"][0]
    year_stem = saju["year_pillar"][0]
    month_stem = saju["month_pillar"][0]
    hour_stem = saju["hour_pillar"][0]

    year_tg = get_ten_god(day_stem, year_stem)
    month_tg = get_ten_god(day_stem, month_stem)
    hour_tg = get_ten_god(day_stem, hour_stem)

    pillars = [
        saju["year_pillar"],
        saju["month_pillar"],
        saju["day_pillar"],
        saju["hour_pillar"],
    ]
    counts = analyze_ohang(pillars)
    strong, weak = dominant_elements(counts)

    day_element = ELEMENTS[day_stem]
    day_yinyang = YINYANG[day_stem]

    summary = f"""
🌷 **나의 주인공 에너지는 {day_stem}({day_element}, {day_yinyang})**이에요!

- 🐣 **태어난 해의 요정 ({year_tg})**: {TEN_GODS.get(year_tg, "-")}
- 🐥 **태어난 달의 요정 ({month_tg})**: {TEN_GODS.get(month_tg, "-")}
- 🦉 **태어난 시간의 요정 ({hour_tg})**: {TEN_GODS.get(hour_tg, "-")}

🎨 오행 팔레트를 보면 **{", ".join(strong)} 기운이 뿜뿜!** 넘치구요,  
조금 더 챙겨주면 좋은 기운은 **{", ".join(weak)}**이랍니다.
"""
    return summary, counts

st.title("🌸 몽글몽글 만세력 🌸")
st.info("🎂 생년월일과 출생 시간을 입력해 주세요!")

with st.form("saju_form"):
    birth_date = st.date_input(
        "생년월일",
        value=date(1995, 1, 1),
        min_value=date(1000, 2, 13),
        max_value=date(2050, 12, 31),
        format="YYYY-MM-DD",
    )
    birth_time = st.time_input(
        "출생 시간",
        value=time(12, 0),
        step=60,
    )
    submitted = st.form_submit_button("사주 보기")

if submitted:
    try:
        saju = get_full_saju(
            birth_date.year, birth_date.month, birth_date.day,
            birth_time.hour, birth_time.minute
        )

        summary_text, ohang_counts = make_summary(saju)

        st.success("만세력 계산이 완료되었습니다.")
        st.write(saju)
        st.markdown(summary_text)
        st.write(ohang_counts)

    except Exception as e:
        st.error(f"오류가 발생했습니다: {e}")
