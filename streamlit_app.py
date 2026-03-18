import streamlit as st
from datetime import date, datetime
import sxtwl

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="오늘의 사주",
    page_icon="🔮",
    layout="centered"
)

# -----------------------------
# Color Palette
# -----------------------------
COLORS = {
    "bg": "#F2EAE0",
    "card": "#B4D3D9",
    "sub": "#BDA6CE",
    "accent": "#9B8EC7",
    "text": "#3A3440",
    "white": "#FFFFFF"
}

# -----------------------------
# CSS
# -----------------------------
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {COLORS["bg"]} 0%, #ffffff 100%);
        color: {COLORS["text"]};
    }}

    .main-title {{
        text-align: center;
        font-size: 2.2rem;
        font-weight: 800;
        color: {COLORS["accent"]};
        margin-bottom: 0.2rem;
    }}

    .sub-title {{
        text-align: center;
        font-size: 1rem;
        color: {COLORS["text"]};
        margin-bottom: 1.5rem;
    }}

    .card {{
        background: rgba(255,255,255,0.78);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
        border: 1px solid rgba(255,255,255,0.5);
        margin-bottom: 16px;
    }}

    .soft-card {{
        background: {COLORS["card"]};
        border-radius: 20px;
        padding: 18px;
        color: {COLORS["text"]};
        margin-bottom: 14px;
    }}

    .mini-card {{
        background: {COLORS["sub"]};
        border-radius: 18px;
        padding: 14px;
        color: white;
        text-align: center;
        font-weight: 700;
    }}

    .fortune-card {{
        background: {COLORS["accent"]};
        border-radius: 22px;
        padding: 20px;
        color: white;
        box-shadow: 0 10px 22px rgba(155,142,199,0.25);
    }}

    .section-title {{
        font-size: 1.15rem;
        font-weight: 800;
        margin-bottom: 10px;
        color: {COLORS["accent"]};
    }}

    .pill {{
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: {COLORS["bg"]};
        color: {COLORS["text"]};
        font-size: 0.88rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }}

    .notice {{
        font-size: 0.92rem;
        color: #5b5561;
        background: rgba(255,255,255,0.7);
        padding: 12px 16px;
        border-radius: 14px;
        border-left: 5px solid {COLORS["accent"]};
        margin-bottom: 16px;
    }}

    .stButton > button {{
        background: {COLORS["accent"]};
        color: white;
        border: none;
        border-radius: 14px;
        height: 48px;
        font-weight: 700;
        width: 100%;
    }}

    .stButton > button:hover {{
        border: none;
        color: white;
        opacity: 0.95;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Constants
# -----------------------------
GAN = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
ZHI = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

# sxtwl docs/examples use index arrays for Gan/Zhi values. :contentReference[oaicite:2]{index=2}

ZODIAC = ["쥐", "소", "호랑이", "토끼", "용", "뱀", "말", "양", "원숭이", "닭", "개", "돼지"]

GAN_ELEMENT = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수"
}

ZHI_ELEMENT = {
    "자": "수", "축": "토", "인": "목", "묘": "목",
    "진": "토", "사": "화", "오": "화", "미": "토",
    "신": "금", "유": "금", "술": "토", "해": "수"
}

ELEMENT_DESC = {
    "목": {
        "title": "성장형",
        "desc": "배움, 확장, 시작의 기운이 강합니다.",
        "tip": "계획을 세운 뒤 꾸준히 밀고 가면 좋습니다."
    },
    "화": {
        "title": "표현형",
        "desc": "열정, 표현력, 존재감이 강합니다.",
        "tip": "감정의 속도를 조금만 조절하면 더 좋습니다."
    },
    "토": {
        "title": "안정형",
        "desc": "균형감, 현실감, 신뢰가 강점입니다.",
        "tip": "혼자 다 떠안지 말고 분산하면 훨씬 편해집니다."
    },
    "금": {
        "title": "정리형",
        "desc": "판단력, 기준, 정돈 능력이 좋습니다.",
        "tip": "완벽하려 하기보다 유연함을 조금 더하면 좋습니다."
    },
    "수": {
        "title": "통찰형",
        "desc": "직감, 사고력, 흐름을 읽는 힘이 좋습니다.",
        "tip": "생각이 많아질 땐 글로 적으면 정리가 빨라집니다."
    }
}

DAY_MASTER_TEXT = {
    "갑": "큰 나무 같은 타입으로, 곧고 성장하려는 힘이 큽니다.",
    "을": "덩굴이나 화초 같은 타입으로, 섬세하고 유연한 감각이 좋습니다.",
    "병": "태양 같은 타입으로, 밝고 추진력이 강한 편입니다.",
    "정": "촛불 같은 타입으로, 섬세한 감성과 집중력이 돋보입니다.",
    "무": "큰 산 같은 타입으로, 중심을 잡고 버티는 힘이 좋습니다.",
    "기": "논밭의 흙 같은 타입으로, 실용적이고 배려가 자연스럽습니다.",
    "경": "원석이나 큰 쇠 같은 타입으로, 결단력과 원칙이 강합니다.",
    "신": "보석 같은 타입으로, 정교함과 미감, 세밀함이 강점입니다.",
    "임": "큰 바다 같은 타입으로, 스케일이 크고 사고가 넓습니다.",
    "계": "비나 안개 같은 타입으로, 조용하지만 깊은 통찰이 있습니다."
}

TODAY_MESSAGES = {
    0: {
        "overall": "정리와 준비에 좋은 흐름입니다.",
        "love": "강한 표현보다 진심 있는 한마디가 잘 통합니다.",
        "work": "중요한 결정 전 우선순위 정리에 좋습니다.",
        "money": "충동 소비보다 점검과 계획이 유리합니다."
    },
    1: {
        "overall": "사람운이 들어오는 날입니다.",
        "love": "먼저 다정하게 다가가면 흐름이 부드러워집니다.",
        "work": "혼자보다 협업에서 성과가 더 잘 납니다.",
        "money": "작은 혜택이나 유용한 정보를 얻기 쉽습니다."
    },
    2: {
        "overall": "집중력이 높아지는 날입니다.",
        "love": "말보다 신뢰를 보여주는 태도가 중요합니다.",
        "work": "문서, 공부, 분석성 업무에 좋습니다.",
        "money": "새 소비보다 관리와 절제가 유리합니다."
    },
    3: {
        "overall": "변화가 들어오는 날입니다.",
        "love": "단정적인 말투만 줄여도 관계가 편해집니다.",
        "work": "새 제안이나 아이디어를 시험해보기 좋습니다.",
        "money": "큰 결정은 한 번 더 검토하세요."
    },
    4: {
        "overall": "성과를 만들기 좋은 날입니다.",
        "love": "안정감 있는 태도가 관계운을 높입니다.",
        "work": "실행력이 살아나 결과가 잘 보입니다.",
        "money": "예정된 범위 안의 소비는 무난합니다."
    },
    5: {
        "overall": "가볍게 흐름을 타기 좋은 날입니다.",
        "love": "호감운이 올라오고 분위기가 부드럽습니다.",
        "work": "딱딱한 일보다 아이디어성 업무가 잘 맞습니다.",
        "money": "기분 소비만 조심하면 괜찮습니다."
    },
    6: {
        "overall": "회복과 재정비가 중요한 날입니다.",
        "love": "상대보다 내 마음을 먼저 돌보는 게 좋습니다.",
        "work": "다음 주 준비와 정리가 잘 맞습니다.",
        "money": "새 지출보다 점검과 절약이 유리합니다."
    }
}

# -----------------------------
# Helpers
# -----------------------------
def gz_to_korean(gz_obj):
    return GAN[gz_obj.tg] + ZHI[gz_obj.dz]

def get_saju_pillars(birth_date_obj, birth_time_obj):
    day = sxtwl.fromSolar(
        birth_date_obj.year,
        birth_date_obj.month,
        birth_date_obj.day
    )

    year_gz = day.getYearGZ()     # 입춘 기준
    month_gz = day.getMonthGZ()   # 절기 기준 월주
    day_gz = day.getDayGZ()
    hour_gz = day.getHourGZ(birth_time_obj.hour)

    return {
        "year": gz_to_korean(year_gz),
        "month": gz_to_korean(month_gz),
        "day": gz_to_korean(day_gz),
        "hour": gz_to_korean(hour_gz),
        "year_animal": ZODIAC[year_gz.dz],
        "day_master": GAN[day_gz.tg]
    }

def count_five_elements(pillars):
    counts = {"목": 0, "화": 0, "토": 0, "금": 0, "수": 0}
    chars = []
    for key in ["year", "month", "day", "hour"]:
        chars.extend(list(pillars[key]))

    for ch in chars:
        if ch in GAN_ELEMENT:
            counts[GAN_ELEMENT[ch]] += 1
        elif ch in ZHI_ELEMENT:
            counts[ZHI_ELEMENT[ch]] += 1
    return counts

def get_main_element(counts):
    return max(counts, key=counts.get)

def get_weak_element(counts):
    return min(counts, key=counts.get)

def get_today_fortune():
    return TODAY_MESSAGES[date.today().weekday()]

def get_lucky_color(element):
    mapping = {
        "목": "연두 / 그린 계열",
        "화": "코랄 / 핑크 계열",
        "토": "베이지 / 브라운 계열",
        "금": "화이트 / 실버 계열",
        "수": "네이비 / 블루 계열"
    }
    return mapping[element]

def get_lucky_numbers(pillars):
    seed = sum(ord(ch) for ch in pillars["day"] + pillars["month"])
    return [(seed % 9) + 1, ((seed + 3) % 9) + 1, ((seed + 6) % 9) + 1]

def pillar_summary(pillars, counts):
    day_master = pillars["day_master"]
    dominant = get_main_element(counts)
    weak = get_weak_element(counts)

    dm_text = DAY_MASTER_TEXT[day_master]
    dominant_info = ELEMENT_DESC[dominant]

    return {
        "day_master": day_master,
        "dm_text": dm_text,
        "dominant": dominant,
        "weak": weak,
        "dominant_title": dominant_info["title"],
        "dominant_desc": dominant_info["desc"],
        "tip": dominant_info["tip"]
    }

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='main-title'>🔮 오늘의 사주</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>사주팔자(년주·월주·일주·시주)와 오늘의 흐름을 쉽게 보기</div>", unsafe_allow_html=True)

st.markdown(
    "<div class='notice'>이 버전은 연주·월주·일주·시주를 계산합니다. 해석 문구는 쉽게 풀어쓴 입문형 설명이라서, 명리학 세부 해석 전체를 완전히 대체하지는 않습니다.</div>",
    unsafe_allow_html=True
)

# -----------------------------
# Input
# -----------------------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>1) 정보 입력</div>", unsafe_allow_html=True)

    with st.form("saju_form"):
        name = st.text_input("이름", placeholder="예: 지안")
        birth_date = st.date_input(
            "생년월일",
            value=date(1995, 1, 1),
            min_value=date(1900, 1, 1),
            max_value=date.today()
        )
        birth_time = st.time_input(
            "태어난 시간",
            value=datetime.strptime("12:00", "%H:%M").time()
        )
        submitted = st.form_submit_button("사주 보기")

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Result
# -----------------------------
if submitted:
    user_name = name.strip() if name.strip() else "당신"
    pillars = get_saju_pillars(birth_date, birth_time)
    counts = count_five_elements(pillars)
    summary = pillar_summary(pillars, counts)
    today = get_today_fortune()
    lucky_numbers = get_lucky_numbers(pillars)
    lucky_color = get_lucky_color(summary["dominant"])

    # 사주팔자
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>2) 사주팔자</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='mini-card'>년주<br><span style='font-size:1.35rem'>{pillars['year']}</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='mini-card'>월주<br><span style='font-size:1.35rem'>{pillars['month']}</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='mini-card'>일주<br><span style='font-size:1.35rem'>{pillars['day']}</span></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='mini-card'>시주<br><span style='font-size:1.35rem'>{pillars['hour']}</span></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='soft-card'>
            <b>{user_name}</b>님의 일간은 <b>{summary["day_master"]}</b>입니다.<br><br>
            {summary["dm_text"]}<br><br>
            전체 오행 흐름에서는 <b>{summary["dominant"]}</b> 기운이 강하게 보이고,
            상대적으로 <b>{summary["weak"]}</b> 기운은 보완 포인트로 볼 수 있습니다.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 오행
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>3) 오행 분포</div>", unsafe_allow_html=True)

    cols = st.columns(5)
    order = ["목", "화", "토", "금", "수"]
    for i, el in enumerate(order):
        with cols[i]:
            st.markdown(
                f"<div class='mini-card'>{el}<br><span style='font-size:1.35rem'>{counts[el]}</span></div>",
                unsafe_allow_html=True
            )

    st.markdown(
        f"""
        <div class='soft-card'>
            <b>주요 기운: {summary["dominant"]} ({summary["dominant_title"]})</b><br>
            {summary["dominant_desc"]}<br><br>
            <b>생활 팁</b><br>
            {summary["tip"]}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 오늘 운세
    st.markdown("<div class='fortune-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='color:white;'>4) 오늘의 운세</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style='line-height:1.8;'>
            <b>전체운</b><br>
            {today["overall"]}<br><br>
            <b>연애운</b><br>
            {today["love"]}<br><br>
            <b>일/학업운</b><br>
            {today["work"]}<br><br>
            <b>금전운</b><br>
            {today["money"]}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)

    # 행운 포인트
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>5) 오늘의 포인트</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <span class='pill'>띠: {pillars["year_animal"]}</span>
        <span class='pill'>일간: {summary["day_master"]}</span>
        <span class='pill'>행운 색상: {lucky_color}</span>
        <span class='pill'>행운 숫자: {lucky_numbers[0]}, {lucky_numbers[1]}, {lucky_numbers[2]}</span>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='soft-card'>
            오늘은 <b>{user_name}</b>님이 자신의 기본 리듬을 유지할수록 좋은 날입니다.
            특히 <b>{summary["dominant"]}</b> 기운의 장점을 살려,
            너무 많은 일을 한 번에 벌이기보다 <b>한 가지 중요한 일에 집중</b>하면 흐름이 좋아집니다.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
