import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="🇰🇷 한국 에너지 안보 분석", layout="wide")

st.title("🇰🇷 한국 중심 호르무즈 원유 의존도 & 미국 안보 기여 분석")

st.markdown("""
### 핵심 질문
- 한국은 호르무즈 해협에 얼마나 의존하는가?
- 미국의 해상안보 기여가 줄어들면 어떤 일이 발생하는가?
- 봉쇄 시 실제 공급 충격은 어느 정도인가?
""")

# -------------------------
# 한국 기본 데이터 (현실 반영 근사값)
# -------------------------
korea_data = {
    "total_import_mbpd": 2.7,        # 총 원유 수입
    "middle_east_ratio": 0.72,       # 중동 의존도
    "hormuz_ratio": 0.95,            # 중동 중 호르무즈 통과 비율
    "us_security": 85                # 미국 안보 기여도 (기본값)
}

# -------------------------
# 사용자 입력
# -------------------------
st.subheader("📊 시나리오 설정")

col1, col2, col3 = st.columns(3)

with col1:
    disruption = st.slider(
        "호르무즈 봉쇄 강도",
        0.0, 1.0, 1.0, 0.05,
        help="1.0 = 완전 봉쇄"
    )

with col2:
    us_security = st.slider(
        "미국 안보 기여도",
        0, 100, korea_data["us_security"],
        help="해상 보호 수준"
    )

with col3:
    buffer_power = st.slider(
        "안보 완충 효과",
        0.0, 1.0, 0.6,
        help="안보 기여가 실제 리스크 감소로 이어지는 정도"
    )

# -------------------------
# 계산
# -------------------------
total_import = korea_data["total_import_mbpd"]

# 호르무즈 의존 물량
hormuz_exposure = (
    total_import *
    korea_data["middle_east_ratio"] *
    korea_data["hormuz_ratio"]
)

# 충격 반영
gross_loss = hormuz_exposure * disruption

# 미국 완충
buffer_factor = 1 - (us_security / 100 * buffer_power)
net_loss = gross_loss * buffer_factor

# -------------------------
# 결과 표시
# -------------------------
st.subheader("📉 공급 충격 분석")

c1, c2, c3 = st.columns(3)

c1.metric("총 원유 수입", f"{total_import:.2f} mbpd")
c2.metric("호르무즈 의존 물량", f"{hormuz_exposure:.2f} mbpd")
c3.metric("실제 공급 손실", f"{net_loss:.2f} mbpd")

st.markdown("---")

# -------------------------
# 시나리오 비교
# -------------------------
st.subheader("📊 미국 안보 수준별 시나리오")

scenario_data = []

for sec in range(0, 101, 10):
    buffer = 1 - (sec / 100 * buffer_power)
    loss = gross_loss * buffer
    scenario_data.append({
        "미국 안보 기여도": sec,
        "공급 손실": loss
    })

df = pd.DataFrame(scenario_data)

# 그래프
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(df["미국 안보 기여도"], df["공급 손실"], marker="o")
ax.set_xlabel("미국 안보 기여도")
ax.set_ylabel("공급 손실 (mbpd)")
ax.set_title("미국 안보 수준에 따른 한국 공급 리스크 변화")

st.pyplot(fig)

# -------------------------
# 리스크 등급 평가
# -------------------------
st.subheader("🚨 리스크 평가")

if net_loss > 1.5:
    level = "🔴 매우 위험"
elif net_loss > 1.0:
    level = "🟠 위험"
elif net_loss > 0.5:
    level = "🟡 주의"
else:
    level = "🟢 안정"

st.markdown(f"### 현재 리스크 수준: **{level}**")

# -------------------------
# 해석
# -------------------------
st.subheader("🧠 해석")

st.markdown(f"""
- 한국은 약 **{hormuz_exposure:.2f} mbpd**를 호르무즈에 의존
- 봉쇄 시 최대 **{gross_loss:.2f} mbpd** 공급 충격 발생 가능
- 미국 안보 기여 반영 시 실제 손실은 **{net_loss:.2f} mbpd**

### 의미
- 한국은 구조적으로 **해상 chokepoint 리스크 국가**
- 미국 해군 존재는 **실질적인 에너지 보험 역할**
- 안보 약화 시 → 즉각적인 경제 충격으로 전이 가능
""")

# -------------------------
# 정책 인사이트
# -------------------------
st.subheader("📌 정책 인사이트")

st.markdown("""
### 1. 취약 구조
- 중동 + 호르무즈 집중 구조 → 단일 chokepoint 리스크

### 2. 미국 의존성
- 단순 군사 문제가 아니라 **에너지 안보 핵심 변수**

### 3. 대응 전략
- 원유 수입 다변화 (미국, 브라질, 아프리카)
- 전략비축유 확대
- LNG/재생에너지 전환
- 해상안보 협력 확대 (한미, 다국적 연합)
""")

st.markdown("---")
st.caption("※ 본 모델은 정책 시뮬레이션용 단순화 모델입니다.")
