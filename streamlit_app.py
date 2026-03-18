import streamlit as st
from datetime import date

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
    "text": "#3A3440"
}

# -----------------------------
# Custom CSS (입력창 제거 포함)
# -----------------------------
st.markdown(f"""
<style>
    .stApp {{
        background: linear-gradient(180deg, {COLORS["bg"]}, white);
    }}

    /* 🔥 모든 기본 입력 UI 제거 */
    div[data-testid="stTextInput"],
    div[data-testid="stDateInput"],
    div[data-testid="stTimeInput"],
    div[data-testid="stSelectbox"] {{
        display: none;
    }}

    .title {{
        text-align: center;
        font-size: 2.3rem;
        font-weight: 800;
        color: {COLORS["accent"]};
        margin-bottom: 20px;
    }}

    .card {{
        background: rgba(255,255,255,0.75);
        padding: 25px;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }}

    .soft {{
        background: {COLORS["card"]};
        padding: 18px;
        border-radius: 16px;
        margin-top: 10px;
    }}

    .fortune {{
        background: {COLORS["accent"]};
        color: white;
        padding: 20px;
        border-radius: 20px;
        margin-top: 15px;
    }}

    .btn button {{
        background: {COLORS["accent"]};
        color: white;
        border-radius: 12px;
        height: 50px;
        font-size: 16px;
        font-weight: bold;
        border: none;
    }}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# 데이터
# -----------------------------
elements = ["목", "화", "토", "금", "수"]

fortunes = [
    "차분하게 정리하면 좋은 결과가 생기는 날입니다.",
    "사람과의 관계에서 좋은 흐름이 들어옵니다.",
    "집중력이 높아져 중요한 일을 해결하기 좋아요.",
    "예상치 못한 기회가 들어올 수 있습니다.",
    "노력한 만큼 결과가 보이는 날입니다.",
    "가볍게 즐기면 좋은 일이 생깁니다.",
    "휴식과 재정비가 필요한 날입니다."
]

# -----------------------------
# 제목
# -----------------------------
st.markdown("<div class='title'>🔮 오늘의 사주</div>", unsafe_allow_html=True)

# -----------------------------
# 버튼만 사용 (입력 UI 제거됨)
# -----------------------------
if st.button("오늘 운세 보기", use_container_width=True):

    today = date.today()
    seed = today.day

    element = elements[seed % 5]
    fortune = fortunes[seed % 7]

    # -----------------------------
    # 결과 UI
    # -----------------------------
    st.markdown("<div class='card'>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class='soft'>
        오늘의 기운은 <b>{element}</b> 입니다.<br><br>
        오늘은 흐름을 거스르기보다 자연스럽게 따라가는 것이 중요합니다.
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class='fortune'>
        <b>오늘의 운세</b><br><br>
        {fortune}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# 설명
# -----------------------------
st.markdown("""
<div style='text-align:center; font-size:0.9rem; color:#666; margin-top:30px;'>
간단한 사주 흐름을 기반으로 한 오늘의 운세입니다.
</div>
""", unsafe_allow_html=True)
