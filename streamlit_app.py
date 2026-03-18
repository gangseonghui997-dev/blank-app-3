from __future__ import annotations

from datetime import date, datetime, time
import sys
import unittest

try:
    import streamlit as st  # type: ignore
except ModuleNotFoundError:
    st = None


# -----------------------------
# 기본 설정
# -----------------------------
ELEMENTS = {
    "목": {"emoji": "🌳", "desc": "성장, 배려, 확장"},
    "화": {"emoji": "🔥", "desc": "열정, 표현, 추진력"},
    "토": {"emoji": "🪨", "desc": "안정, 균형, 현실감"},
    "금": {"emoji": "⚔️", "desc": "원칙, 결단, 정리"},
    "수": {"emoji": "💧", "desc": "지혜, 유연함, 감수성"},
}

STEMS = [
    ("갑", "목"), ("을", "목"),
    ("병", "화"), ("정", "화"),
    ("무", "토"), ("기", "토"),
    ("경", "금"), ("신", "금"),
    ("임", "수"), ("계", "수"),
]

BRANCHES = [
    ("자", "수"), ("축", "토"), ("인", "목"), ("묘", "목"),
    ("진", "토"), ("사", "화"), ("오", "화"), ("미", "토"),
    ("신", "금"), ("유", "금"), ("술", "토"), ("해", "수"),
]

ELEMENT_RELATION = {
    "목": {"same": "목", "support": "수", "output": "화", "wealth": "토", "control": "금"},
    "화": {"same": "화", "support": "목", "output": "토", "wealth": "금", "control": "수"},
    "토": {"same": "토", "support": "화", "output": "금", "wealth": "수", "control": "목"},
    "금": {"same": "금", "support": "토", "output": "수", "wealth": "목", "control": "화"},
    "수": {"same": "수", "support": "금", "output": "목", "wealth": "화", "control": "토"},
}

PERSONALITY_TEXT = {
    "목": "따뜻하고 성장 지향적이며 사람과 함께 나아가는 힘이 강합니다.",
    "화": "표현력이 좋고 분위기를 밝게 만드는 에너지가 있습니다.",
    "토": "신중하고 안정감을 주며 중심을 잘 잡는 편입니다.",
    "금": "원칙이 분명하고 판단력이 좋으며 정리 능력이 뛰어납니다.",
    "수": "섬세하고 유연하며 생각이 깊은 편입니다.",
}

JOB_TEXT = {
    "목": "기획, 교육, 상담, 브랜드, 인사처럼 사람과 성장에 연결된 일이 잘 맞습니다.",
    "화": "마케팅, 영업, 콘텐츠, 방송, 강연처럼 표현과 전달이 중요한 분야가 어울립니다.",
    "토": "운영, 관리, 부동산, 재무, 행정처럼 안정성과 책임감이 필요한 일이 잘 맞습니다.",
    "금": "전략, 법률, 데이터, 품질관리, 금융처럼 기준과 정확성이 필요한 분야가 좋습니다.",
    "수": "연구, 기획, IT, 분석, 글쓰기처럼 사고력과 정보 활용이 필요한 분야가 잘 맞습니다.",
}

LOVE_TEXT = {
    "목": "관계에서 함께 성장하는 느낌을 중요하게 생각합니다.",
    "화": "감정 표현이 중요한 편이며 따뜻한 반응에서 힘을 얻습니다.",
    "토": "안정적이고 믿을 수 있는 관계를 선호합니다.",
    "금": "예의와 기준이 잘 맞는 관계에서 편안함을 느낍니다.",
    "수": "대화가 잘 통하고 정서적으로 연결되는 관계를 중요하게 생각합니다.",
}

HEALTH_TEXT = {
    "목": "무리해서 앞으로만 나아가기보다 생활 리듬을 일정하게 유지하는 것이 중요합니다.",
    "화": "에너지가 급격히 오르내릴 수 있어 휴식과 수면 균형을 챙기면 좋습니다.",
    "토": "과로와 스트레스를 쌓아두지 말고 꾸준한 루틴으로 몸을 돌보는 것이 좋습니다.",
    "금": "완벽주의로 긴장이 쌓일 수 있어 가볍게 푸는 습관이 도움이 됩니다.",
    "수": "생각이 많아지면 피로가 누적되기 쉬워 충분한 휴식이 필요합니다.",
}

GOOD_TIPS = {
    "목": ["새로운 것을 배우는 시간 만들기", "산책이나 자연 속에서 머리 식히기", "주변 사람과 목표를 나누기"],
    "화": ["감정을 건강하게 표현하기", "몸을 움직이며 에너지 발산하기", "무리한 일정 줄이기"],
    "토": ["생활 루틴 일정하게 유지하기", "한 번에 너무 많은 책임 지지 않기", "정리된 공간 만들기"],
    "금": ["완벽보다 균형을 우선하기", "중요한 기준을 글로 정리하기", "휴식도 일정에 포함하기"],
    "수": ["혼자 정리하는 시간 확보하기", "기록하며 생각 정리하기", "정보 과부하 피하기"],
}


# -----------------------------
# 계산 함수
# -----------------------------
def get_year_pillar(year: int) -> dict[str, str]:
    stem = STEMS[(year - 4) % 10]
    branch = BRANCHES[(year - 4) % 12]
    return {
        "stem_kr": stem[0],
        "stem_el": stem[1],
        "branch_kr": branch[0],
        "branch_el": branch[1],
    }


def get_month_element(month: int) -> str:
    if not 1 <= month <= 12:
        raise ValueError("month must be between 1 and 12")
    if month in [2, 3]:
        return "목"
    if month in [4, 5]:
        return "화"
    if month in [6, 7, 8]:
        return "토"
    if month in [9, 10]:
        return "금"
    return "수"



def get_hour_element(hour: int) -> str:
    if not 0 <= hour <= 23:
        raise ValueError("hour must be between 0 and 23")
    if 5 <= hour < 9:
        return "목"
    if 9 <= hour < 13:
        return "화"
    if 13 <= hour < 17:
        return "토"
    if 17 <= hour < 21:
        return "금"
    return "수"



def get_day_master(year: int, month: int, day: int) -> str:
    idx = (year + month + day) % 5
    return ["목", "화", "토", "금", "수"][idx]



def score_elements(year: int, month: int, day: int, hour: int):
    scores = {k: 0 for k in ELEMENTS.keys()}

    year_pillar = get_year_pillar(year)
    scores[year_pillar["stem_el"]] += 2
    scores[year_pillar["branch_el"]] += 1

    month_el = get_month_element(month)
    hour_el = get_hour_element(hour)
    day_master = get_day_master(year, month, day)

    scores[month_el] += 2
    scores[hour_el] += 1
    scores[day_master] += 3

    return scores, day_master, year_pillar, month_el, hour_el



def get_main_trait(scores: dict[str, int]) -> str:
    return max(scores, key=scores.get)



def get_balance_comment(scores: dict[str, int]) -> str:
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    strongest = sorted_items[0][0]
    weakest = sorted_items[-1][0]
    return (
        f"전체적으로 **{strongest} 기운**이 강하게 보이고, "
        f"상대적으로 **{weakest} 기운**은 보완이 필요해 보입니다. "
        f"강한 장점은 살리고 부족한 부분은 생활 습관과 환경으로 채워가면 좋습니다."
    )



def get_relation_summary(day_master: str) -> dict[str, str]:
    rel = ELEMENT_RELATION[day_master]
    return {
        "나와 같은 기운": rel["same"],
        "나를 도와주는 기운": rel["support"],
        "내가 표현하는 기운": rel["output"],
        "재물 감각과 연결": rel["wealth"],
        "나를 다잡는 기운": rel["control"],
    }



def build_result(name: str, birth_date: date, birth_time: time) -> dict:
    year = birth_date.year
    month = birth_date.month
    day = birth_date.day
    hour = birth_time.hour

    scores, day_master, year_pillar, month_el, hour_el = score_elements(year, month, day, hour)
    main_trait = get_main_trait(scores)
    rel_summary = get_relation_summary(day_master)

    return {
        "name": name or "사용자",
        "scores": scores,
        "day_master": day_master,
        "year_pillar": year_pillar,
        "month_element": month_el,
        "hour_element": hour_el,
        "main_trait": main_trait,
        "relation_summary": rel_summary,
        "balance_comment": get_balance_comment(scores),
        "personality_text": PERSONALITY_TEXT[main_trait],
        "love_text": LOVE_TEXT[main_trait],
        "job_text": JOB_TEXT[main_trait],
        "health_text": HEALTH_TEXT[main_trait],
        "tips": GOOD_TIPS[main_trait],
    }



def render_cli_fallback() -> None:
    print("[안내] streamlit 모듈이 설치되어 있지 않아 콘솔 모드로 실행합니다.\n")
    demo_result = build_result(
        name="홍길동",
        birth_date=date(1995, 5, 15),
        birth_time=time(9, 30),
    )
    print(f"이름: {demo_result['name']}")
    print(f"핵심 기운: {demo_result['main_trait']}")
    print(f"일간: {demo_result['day_master']}")
    print(f"연주: {demo_result['year_pillar']['stem_kr']}{demo_result['year_pillar']['branch_kr']}")
    print(demo_result["balance_comment"])
    print("\n성격:", demo_result["personality_text"])
    print("연애:", demo_result["love_text"])
    print("직업:", demo_result["job_text"])
    print("건강:", demo_result["health_text"])
    print("추천 팁:")
    for tip in demo_result["tips"]:
        print(f"- {tip}")
    print("\n실제 웹앱으로 실행하려면 streamlit을 설치한 뒤 아래 명령을 사용하세요.")
    print("pip install streamlit")
    print("streamlit run saju_streamlit_app.py")



def render_streamlit_app() -> None:
    assert st is not None

    st.set_page_config(
        page_title="사주 풀이 사이트",
        page_icon="🔮",
        layout="wide",
    )

    st.markdown(
        """
        <style>
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }
        .sub-text {
            color: #666;
            font-size: 1rem;
            margin-bottom: 1rem;
        }
        .card {
            padding: 1.2rem;
            border-radius: 18px;
            background: #f8f9ff;
            border: 1px solid #e8ebff;
            margin-bottom: 1rem;
        }
        .small-card {
            padding: 0.9rem;
            border-radius: 14px;
            background: #ffffff;
            border: 1px solid #ececec;
            height: 100%;
        }
        .pill {
            display: inline-block;
            padding: 0.35rem 0.7rem;
            border-radius: 999px;
            background: #eef2ff;
            margin: 0.15rem;
            font-size: 0.9rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="main-title">🔮 쉬운 사주 풀이</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-text">생년월일과 태어난 시간을 입력하면, 복잡한 용어 대신 쉬운 말로 성향과 운의 흐름을 보여줍니다.</div>',
        unsafe_allow_html=True,
    )

    with st.expander("이 서비스 안내", expanded=True):
        st.info(
            "이 예제는 **입문용 사주 사이트 데모**입니다. 전문 만세력 계산이 아니라, "
            "오행 균형과 성향을 보기 쉽게 보여주는 구조로 만들어졌습니다. "
            "실서비스로 발전시키려면 실제 사주 계산 로직(API 또는 만세력 라이브러리)으로 교체하면 됩니다."
        )

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### 1) 기본 정보 입력")
        name = st.text_input("이름", placeholder="예: 홍길동")
        birth_date = st.date_input(
            "생년월일",
            value=datetime(1995, 5, 15),
            min_value=datetime(1950, 1, 1),
            max_value=datetime(2035, 12, 31),
        )
        birth_time = st.time_input("태어난 시간", value=datetime.strptime("09:30", "%H:%M").time())
        st.radio("성별", ["여성", "남성", "선택 안 함"], horizontal=True)

    with right:
        st.markdown("### 2) 원하는 풀이 선택")
        show_personality = st.checkbox("성격/기질", value=True)
        show_love = st.checkbox("연애/인간관계", value=True)
        show_job = st.checkbox("직업/재물", value=True)
        show_health = st.checkbox("건강/생활습관", value=True)
        show_balance = st.checkbox("오행 균형", value=True)

    analyze = st.button("사주 풀이 보기", use_container_width=True)

    if analyze:
        result = build_result(name=name, birth_date=birth_date, birth_time=birth_time)

        st.success(f"{result['name']}님의 사주 풀이 결과를 정리했어요.")
        st.markdown("## 한눈에 보는 결과")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="card">
                    <h4>핵심 기운</h4>
                    <h2>{ELEMENTS[result['main_trait']]['emoji']} {result['main_trait']}</h2>
                    <p>{ELEMENTS[result['main_trait']]['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.markdown(
                f"""
                <div class="card">
                    <h4>일간(나를 나타내는 기운)</h4>
                    <h2>{ELEMENTS[result['day_master']]['emoji']} {result['day_master']}</h2>
                    <p>성향의 중심축으로 해석합니다.</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c3:
            st.markdown(
                f"""
                <div class="card">
                    <h4>연주 참고</h4>
                    <h2>{result['year_pillar']['stem_kr']}{result['year_pillar']['branch_kr']}</h2>
                    <p>{result['year_pillar']['stem_el']} · {result['year_pillar']['branch_el']} 기운</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        if show_personality:
            st.markdown("## 성격 / 기질")
            st.markdown(
                f"""
                <div class="card">
                    <b>{result['name']}</b>의 중심 기운은 <b>{result['day_master']}</b>이며,
                    전반적으로 <b>{result['main_trait']}</b>의 성향이 두드러집니다.<br><br>
                    {result['personality_text']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if show_love:
            st.markdown("## 연애 / 인간관계")
            st.markdown(
                f"""
                <div class="card">
                    {result['love_text']}<br><br>
                    인간관계에서는 <b>{ELEMENT_RELATION[result['day_master']]['support']}</b> 기운을 가진 사람이나 환경이
                    안정감을 주는 편으로 볼 수 있습니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

        if show_job:
            st.markdown("## 직업 / 재물")
            st.markdown(
                f"""
                <div class="card">
                    {result['job_text']}<br><br>
                    재물과 연결되는 기운은 <b>{ELEMENT_RELATION[result['day_master']]['wealth']}</b>입니다.
                    즉, {ELEMENT_RELATION[result['day_master']]['wealth']}의 특성을 살리는 방식으로 돈의 흐름을 만들면 유리합니다.
                </div>
                """,
                unsafe_allow_html=True,
            )

        if show_health:
            st.markdown("## 건강 / 생활 습관")
            st.markdown(
                f"""
                <div class="card">
                    {result['health_text']}
                </div>
                """,
                unsafe_allow_html=True,
            )

        if show_balance:
            st.markdown("## 오행 균형")
            cols = st.columns(5)
            for idx, (el, score) in enumerate(result['scores'].items()):
                with cols[idx]:
                    st.metric(f"{ELEMENTS[el]['emoji']} {el}", score)

            st.progress(min(sum(result['scores'].values()) / 12, 1.0))
            st.write(result['balance_comment'])

            st.markdown("### 관계 해석 키워드")
            rel_cols = st.columns(len(result['relation_summary']))
            for idx, (k, v) in enumerate(result['relation_summary'].items()):
                with rel_cols[idx]:
                    st.markdown(
                        f"""
                        <div class="small-card">
                            <b>{k}</b><br>
                            {v}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("## 일상에서 이렇게 활용해 보세요")
        tips_html = "".join([f'<span class="pill">{tip}</span>' for tip in result['tips']])
        st.markdown(f'<div class="card">{tips_html}</div>', unsafe_allow_html=True)

        st.caption(
            "안내: 현재 버전은 보기 쉽고 이해하기 쉬운 데모용 사주 앱입니다. "
            "정확한 사주 명식 계산(연주/월주/일주/시주)과 대운·세운 분석이 필요하면 전문 계산 로직을 연동해 고도화할 수 있습니다."
        )
    else:
        st.markdown("---")
        st.markdown("### 이렇게 보이게 만들었어요")
        st.write("- 입력이 단순합니다: 이름, 생년월일, 시간만 넣으면 됩니다.")
        st.write("- 결과가 어렵지 않습니다: 성격, 연애, 직업, 건강으로 나눠서 보여줍니다.")
        st.write("- 사주를 잘 몰라도 이해할 수 있도록 쉬운 표현으로 구성했습니다.")
        st.write("- 나중에 실제 만세력 API를 연결하면 서비스 수준으로 확장할 수 있습니다.")

    st.markdown("---")
    st.caption("Made with Streamlit · 입문용 사주 풀이 UI 예제")


class TestSajuLogic(unittest.TestCase):
    def test_get_month_element(self):
        self.assertEqual(get_month_element(2), "목")
        self.assertEqual(get_month_element(5), "화")
        self.assertEqual(get_month_element(7), "토")
        self.assertEqual(get_month_element(10), "금")
        self.assertEqual(get_month_element(12), "수")

    def test_get_hour_element(self):
        self.assertEqual(get_hour_element(6), "목")
        self.assertEqual(get_hour_element(10), "화")
        self.assertEqual(get_hour_element(14), "토")
        self.assertEqual(get_hour_element(18), "금")
        self.assertEqual(get_hour_element(23), "수")

    def test_invalid_month_raises(self):
        with self.assertRaises(ValueError):
            get_month_element(13)

    def test_invalid_hour_raises(self):
        with self.assertRaises(ValueError):
            get_hour_element(24)

    def test_score_elements_total(self):
        scores, day_master, year_pillar, month_el, hour_el = score_elements(1995, 5, 15, 9)
        self.assertEqual(sum(scores.values()), 9)
        self.assertIn(day_master, ELEMENTS)
        self.assertIn(month_el, ELEMENTS)
        self.assertIn(hour_el, ELEMENTS)
        self.assertIn(year_pillar["stem_el"], ELEMENTS)

    def test_build_result_has_required_keys(self):
        result = build_result("홍길동", date(1995, 5, 15), time(9, 30))
        required_keys = {
            "name", "scores", "day_master", "year_pillar", "month_element",
            "hour_element", "main_trait", "relation_summary", "balance_comment",
            "personality_text", "love_text", "job_text", "health_text", "tips"
        }
        self.assertTrue(required_keys.issubset(result.keys()))
        self.assertEqual(result["name"], "홍길동")


if __name__ == "__main__":
    if "--test" in sys.argv:
        unittest.main(argv=[sys.argv[0]])
    elif st is None:
        render_cli_fallback()
    else:
        render_streamlit_app()
else:
    if st is not None:
        render_streamlit_app()
