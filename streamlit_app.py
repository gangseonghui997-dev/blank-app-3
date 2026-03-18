import streamlit as st
from datetime import date, datetime

# -----------------------------
# Page Config
# -----------------------------
st.set_page_config(
    page_title="오늘의 사주 한 장",
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
# Custom CSS
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
        background: rgba(255,255,255,0.72);
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
        font-weight: 600;
    }}

    .fortune-card {{
        background: {COLORS["accent"]};
        border-radius: 22px;
        padding: 20px;
        color: white;
        box-shadow: 0 10px 22px rgba(155,142,199,0.25);
    }}

    .section-title {{
        font-size: 1.2rem;
        font-weight: 700;
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
        font-size: 0.9rem;
        color: #5b5561;
        background: rgba(255,255,255,0.65);
        padding: 12px 16px;
        border-radius: 14px;
        border-left: 5px solid {COLORS["accent"]};
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Saju Data
# -----------------------------
heavenly_stems = ["갑", "을", "병", "정", "무", "기", "경", "신", "임", "계"]
earthly_branches = ["자", "축", "인", "묘", "진", "사", "오", "미", "신", "유", "술", "해"]

stem_elements = {
    "갑": "목", "을": "목",
    "병": "화", "정": "화",
    "무": "토", "기": "토",
    "경": "금", "신": "금",
    "임": "수", "계": "수"
}

branch_animals = {
    "자": "쥐", "축": "소", "인": "호랑이", "묘": "토끼",
    "진": "용", "사": "뱀", "오": "말", "미": "양",
    "신": "원숭이", "유": "닭", "술": "개", "해": "돼지"
}

element_traits = {
    "목": {
        "title": "성장형 에너지",
        "desc": "배움, 확장, 새로운 시작에 강한 흐름입니다.",
        "strength": "계획을 세우고 꾸준히 밀어붙일 때 강점이 살아나요.",
        "tip": "시작은 빠르지만 마무리 루틴을 함께 만들면 더 좋아요."
    },
    "화": {
        "title": "표현형 에너지",
        "desc": "열정, 매력, 드러나는 힘이 강한 편입니다.",
        "strength": "사람들 앞에서 자신의 생각을 보여줄 때 운이 열립니다.",
        "tip": "감정이 앞설 수 있으니 속도를 한 번 조절하면 더 안정적이에요."
    },
    "토": {
        "title": "안정형 에너지",
        "desc": "균형, 신뢰, 중심을 잡는 힘이 좋습니다.",
        "strength": "현실 감각과 책임감이 강해 주변에서 믿고 맡기기 쉬워요.",
        "tip": "너무 혼자 감당하지 말고 도움을 나누면 운이 더 부드럽게 흘러요."
    },
    "금": {
        "title": "정리형 에너지",
        "desc": "판단력, 기준, 정돈 능력이 돋보입니다.",
        "strength": "복잡한 상황에서 핵심을 빠르게 정리하는 힘이 있어요.",
        "tip": "완벽주의가 올라오면 유연함을 조금 더해보세요."
    },
    "수": {
        "title": "통찰형 에너지",
        "desc": "직감, 사고력, 흐름을 읽는 감각이 좋습니다.",
        "strength": "깊이 생각하고 본질을 파악하는 힘이 강해요.",
        "tip": "생각이 많아질 땐 기록하거나 대화로 풀면 훨씬 좋아집니다."
    }
}

daily_messages = {
    0: {
        "mood": "차분하게 출발하는 날",
        "overall": "무리해서 밀어붙이기보다 정리와 준비에 좋은 흐름입니다.",
        "love": "감정을 크게 표현하기보다 진심 있는 한마디가 더 효과적이에요.",
        "work": "중요한 결정보다 우선순위 정리가 잘 맞습니다.",
        "money": "충동 지출보다 점검과 계획이 유리해요."
    },
    1: {
        "mood": "사람운이 살아나는 날",
        "overall": "대화와 협업에서 좋은 기회가 생길 수 있어요.",
        "love": "먼저 다정하게 말을 걸면 분위기가 부드러워집니다.",
        "work": "혼자보다 함께할 때 성과가 더 잘 납니다.",
        "money": "작은 혜택이나 뜻밖의 정보가 들어올 수 있어요."
    },
    2: {
        "mood": "집중력이 좋아지는 날",
        "overall": "해야 할 일을 깊게 파고들기 좋은 흐름입니다.",
        "love": "감정보다 신뢰를 보여주는 태도가 더 중요해요.",
        "work": "중요 업무, 문서 정리, 공부운이 괜찮습니다.",
        "money": "불필요한 소비를 줄이면 만족감이 커져요."
    },
    3: {
        "mood": "변화가 들어오는 날",
        "overall": "예상 밖 일정이나 제안이 생길 수 있어 유연함이 중요해요.",
        "love": "오해를 줄이려면 단정적인 말투를 피하는 게 좋습니다.",
        "work": "새로운 아이디어를 시험해보기 좋아요.",
        "money": "큰 결정은 한 번 더 확인하고 진행하세요."
    },
    4: {
        "mood": "성과를 만들기 좋은 날",
        "overall": "꾸준히 해온 일이 눈에 띄기 시작하는 흐름입니다.",
        "love": "관계에서는 안정감과 배려가 포인트예요.",
        "work": "실행력이 높아져 결과를 내기 좋습니다.",
        "money": "계획한 범위 안의 소비는 무난합니다."
    },
    5: {
        "mood": "가볍게 즐기기 좋은 날",
        "overall": "긴장감을 조금 내려놓고 사람들과 흐름을 타기 좋아요.",
        "love": "분위기가 좋아지고 호감운이 올라옵니다.",
        "work": "딱딱한 일보다 아이디어성 업무가 잘 맞아요.",
        "money": "기분 소비가 늘 수 있으니 예산만 정해두세요."
    },
    6: {
        "mood": "회복과 재정비의 날",
        "overall": "휴식, 정리, 나를 돌보는 데 집중하면 좋은 날입니다.",
        "love": "억지로 맞추기보다 내 마음을 먼저 살피는 게 중요해요.",
        "work": "재충전이 우선이고, 다음 주 준비가 잘 맞습니다.",
        "money": "새 지출보다 점검과 절약이 유리합니다."
    }
}

# -----------------------------
# Functions
# -----------------------------
def get_year_ganzhi(year: int):
    stem = heavenly_stems[(year - 4) % 10]
    branch = earthly_branches[(year - 4) % 12]
    return stem, branch

def get_today_fortune():
    weekday = date.today().weekday()
    return daily_messages[weekday]

def get_lucky_numbers(birth_year: int):
    base = sum(map(int, str(birth_year)))
    return [(base % 9) + 1, ((base + 3) % 9) + 1, ((base + 6) % 9) + 1]

def get_lucky_color(element: str):
    mapping = {
        "목": "연두빛 / 자연색",
        "화": "분홍빛 / 따뜻한 색",
        "토": "베이지 / 브라운",
        "금": "화이트 / 실버",
        "수": "네이비 / 블루"
    }
    return mapping[element]

def build_simple_saju_interpretation(year: int):
    stem, branch = get_year_ganzhi(year)
    element = stem_elements[stem]
    animal = branch_animals[branch]
    trait = element_traits[element]

    summary = f"{stem}{branch}년생으로, 기본 기운은 '{element}'에 가까워요."
    nature = f"{animal}의 이미지처럼 상황을 읽고 자기 방식으로 움직이려는 성향이 있습니다."

    return {
        "stem": stem,
        "branch": branch,
        "animal": animal,
        "element": element,
        "summary": summary,
        "nature": nature,
        "trait": trait
    }

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='main-title'>🔮 오늘의 사주 한 장</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='sub-title'>쉽게 보는 사주 성향 + 오늘 운세</div>",
    unsafe_allow_html=True
)

st.markdown(
    "<div class='notice'>이 앱은 이해하기 쉬운 입문형 사주 서비스입니다. "
    "정통 사주처럼 절기 기준의 정밀 계산이 아니라, 연도 기반 성향 해석과 오늘의 흐름을 중심으로 보여줍니다.</div>",
    unsafe_allow_html=True
)

# -----------------------------
# Input
# -----------------------------
with st.container():
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>1) 내 정보 입력</div>", unsafe_allow_html=True)

    name = st.text_input("이름", placeholder="예: 홍길동")
    birth_date = st.date_input(
        "생년월일",
        value=date(1995, 1, 1),
        min_value=date(1950, 1, 1),
        max_value=date.today()
    )
    birth_time = st.time_input("태어난 시간 (선택)", value=datetime.strptime("12:00", "%H:%M").time())
    gender = st.selectbox("성별 (선택)", ["선택 안 함", "여성", "남성"])

    run = st.button("오늘의 사주 보기", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Result
# -----------------------------
if run:
    saju = build_simple_saju_interpretation(birth_date.year)
    today = get_today_fortune()
    lucky_numbers = get_lucky_numbers(birth_date.year)
    lucky_color = get_lucky_color(saju["element"])

    user_name = name if name.strip() else "당신"

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>2) 기본 사주 성향</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='soft-card'>
            <b>{user_name}</b>님의 기본 기운은 <b>{saju["stem"]}{saju["branch"]}</b>,
            띠는 <b>{saju["animal"]}</b>, 오행은 <b>{saju["element"]}</b>입니다.
        </div>
        """,
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"<div class='mini-card'>천간<br><span style='font-size:1.4rem'>{saju['stem']}</span></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='mini-card'>지지<br><span style='font-size:1.4rem'>{saju['branch']}</span></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='mini-card'>오행<br><span style='font-size:1.4rem'>{saju['element']}</span></div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class='soft-card'>
            <b>{saju["trait"]["title"]}</b><br><br>
            • {saju["summary"]}<br>
            • {saju["nature"]}<br>
            • {saju["trait"]["desc"]}<br><br>
            <b>강점</b><br>
            {saju["trait"]["strength"]}<br><br>
            <b>한 줄 조언</b><br>
            {saju["trait"]["tip"]}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='fortune-card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title' style='color:white;'>3) 오늘의 운세</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div style='font-size:1.1rem; font-weight:700; margin-bottom:10px;'>
            오늘의 분위기: {today["mood"]}
        </div>
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

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>4) 오늘의 행운 포인트</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <span class='pill'>행운 색상: {lucky_color}</span>
        <span class='pill'>행운 숫자: {lucky_numbers[0]}, {lucky_numbers[1]}, {lucky_numbers[2]}</span>
        <span class='pill'>추천 키워드: 정리, 균형, 대화</span>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <div class='soft-card'>
            오늘은 <b>{user_name}</b>님이 너무 복잡하게 생각하기보다,
            <b>한 가지 중요한 일에 집중</b>할수록 흐름이 좋아지는 날입니다.
            작은 선택 하나를 안정적으로 끝내는 것이 큰 행운으로 이어질 수 있어요.
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("</div>", unsafe_allow_html=True)
