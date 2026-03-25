
import streamlit as st
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import torch
import torch.nn as nn
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from statsmodels.tsa.seasonal import seasonal_decompose

# ══════════════════════════════════════════════════════════════
#  한글 폰트 설정 (크로스 플랫폼 호환)
# ══════════════════════════════════════════════════════════════
import platform

if platform.system() == "Darwin":
    plt.rcParams["font.family"] = "AppleGothic"
elif platform.system() == "Windows":
    plt.rcParams["font.family"] = "Malgun Gothic"
else:
    # Linux (Streamlit Cloud 등) — 기본 sans-serif 폰트 사용
    plt.rcParams["font.family"] = "DejaVu Sans"

plt.rcParams["axes.unicode_minus"] = False

# ══════════════════════════════════════════════════════════════
#  LSTM 모델 구조 정의
# ══════════════════════════════════════════════════════════════
class LSTMPredictor(nn.Module):
    def __init__(self, input_size=1, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.fc(out[:, -1, :])

# ══════════════════════════════════════════════════════════════
#  페이지 설정
# ══════════════════════════════════════════════════════════════
st.set_page_config(page_title="🤖 AI Weather Dashboard", layout="wide")
st.title("🤖 AI-Powered Weather Dashboard")
st.caption("5주차 대시보드 + AI 모델 예측 (Streamlit Cloud 배포 버전)")

# ══════════════════════════════════════════════════════════════
#  합성 데이터 기반 모델 학습 (캐싱 — 앱 재시작 전까지 1회만 실행)
# ══════════════════════════════════════════════════════════════
@st.cache_resource
def train_models():
    """
    합성 기온 데이터를 생성하고 Linear Regression / LSTM 모델을 학습합니다.
    모델 파일(.pkl, .pt) 없이도 앱이 동작하도록 인라인 학습합니다.
    """
    # ─── 합성 데이터 생성 (01_linear_regression.py, 02_lstm_inference.py와 동일) ───
    np.random.seed(42)
    n_days = 500
    trend = np.linspace(0, 2, n_days)
    seasonality = 15 * np.sin(np.arange(n_days) * 2 * np.pi / 365.25 - np.pi / 2)
    noise = np.random.normal(0, 3, n_days)
    temperatures = 15 + trend + seasonality + noise

    trained = {}

    # ─── 1) Linear Regression ───
    day_nums = np.arange(n_days).reshape(-1, 1)
    lr_model = LinearRegression()
    lr_model.fit(day_nums, temperatures)
    trained["Linear Regression"] = lr_model

    # ─── 2) LSTM ───
    scaler = MinMaxScaler(feature_range=(0, 1))
    temps_scaled = scaler.fit_transform(temperatures.reshape(-1, 1)).flatten()

    window = 30
    X_seq, y_seq = [], []
    for i in range(len(temps_scaled) - window):
        X_seq.append(temps_scaled[i : i + window])
        y_seq.append(temps_scaled[i + window])
    X_seq = np.array(X_seq)
    y_seq = np.array(y_seq)

    X_tensor = torch.FloatTensor(X_seq).unsqueeze(-1)
    y_tensor = torch.FloatTensor(y_seq).unsqueeze(-1)

    lstm_model = LSTMPredictor()
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.001)

    lstm_model.train()
    for epoch in range(50):
        optimizer.zero_grad()
        output = lstm_model(X_tensor)
        loss = criterion(output, y_tensor)
        loss.backward()
        optimizer.step()

    lstm_model.eval()
    trained["LSTM"] = (lstm_model, scaler)

    return trained

# 학습 실행 (캐싱됨)
with st.spinner("모델 학습 중... (최초 1회만 실행됩니다)"):
    models = train_models()

# ══════════════════════════════════════════════════════════════
#  날씨 데이터 로드 (Open-Meteo API)
# ══════════════════════════════════════════════════════════════
@st.cache_data
def load_weather_data(city, start, end):
    cities = {
        "Seoul": {"lat": 37.566, "lon": 126.978},
        "Busan": {"lat": 35.1028, "lon": 129.0403},
        "Jeju": {"lat": 33.5097, "lon": 126.5219}
    }
    coords = cities.get(city, cities["Seoul"])
    url = f"https://archive-api.open-meteo.com/v1/archive?latitude={coords['lat']}&longitude={coords['lon']}&start_date={start}&end_date={end}&daily=temperature_2m_max&timezone=auto"

    res = requests.get(url)
    if res.status_code != 200: return pd.DataFrame()
    data = res.json()
    if "daily" not in data: return pd.DataFrame()

    dates = data["daily"]["time"]
    temps = data["daily"]["temperature_2m_max"]
    df = pd.DataFrame({"temperature": temps}, index=pd.to_datetime(dates)).dropna()
    return df

# ─── 사이드바 ───
st.sidebar.header("⚙️ Prediction Settings")
city = st.sidebar.selectbox("City", ["Seoul", "Busan", "Jeju"])
start_date = st.sidebar.date_input("Start Date", pd.Timestamp.today() - pd.Timedelta(days=365))
end_date = st.sidebar.date_input("End Date", pd.Timestamp.today() - pd.Timedelta(days=5))

forecast_days = st.sidebar.slider("Forecast Horizon (days)", 1, 30, 7)
show_confidence = st.sidebar.checkbox("Show Confidence Interval", value=True)

available_models = list(models.keys())
model_type = st.sidebar.radio("Model", available_models)

df = load_weather_data(city, str(start_date), str(end_date))
if df.empty:
    st.error("데이터 로드 실패 — Open-Meteo API 응답 오류")
    st.stop()

# ══════════════════════════════════════════════════════════════
#  예측 로직 (Test Split 시뮬레이션 및 미래 예측)
# ══════════════════════════════════════════════════════════════
split_idx = int(len(df) * 0.8)
train_data = df.iloc[:split_idx]
test_data = df.iloc[split_idx:]
test_dates = test_data.index
actual_test = test_data["temperature"].values

future_dates = pd.date_range(df.index[-1] + pd.Timedelta(days=1), periods=forecast_days, freq="D")

if model_type == "Linear Regression":
    model = models["Linear Regression"]
    X_test = np.arange(split_idx, len(df)).reshape(-1, 1)
    pred_test = model.predict(X_test)

    X_future = np.arange(len(df), len(df) + forecast_days).reshape(-1, 1)
    pred_future = model.predict(X_future)

elif model_type == "LSTM":
    model, scaler = models["LSTM"]
    window = 30

    # Test 기간 예측 (슬라이딩 윈도우)
    temps_scaled = scaler.transform(df["temperature"].values.reshape(-1, 1)).flatten()
    pred_test_scaled = []

    with torch.no_grad():
        for i in range(split_idx, len(df)):
            x_seq = temps_scaled[i - window : i]
            if len(x_seq) < window:
                pred_test_scaled.append(temps_scaled[i])
                continue
            x_tensor = torch.FloatTensor(x_seq).unsqueeze(0).unsqueeze(-1)
            pred = model(x_tensor).item()
            pred_test_scaled.append(pred)

    pred_test = scaler.inverse_transform(np.array(pred_test_scaled).reshape(-1, 1)).flatten()

    # 미래 예측 (Auto-regressive)
    current_seq = temps_scaled[-window:].tolist()
    pred_future_scaled = []

    with torch.no_grad():
        for _ in range(forecast_days):
            x_tensor = torch.FloatTensor(current_seq).unsqueeze(0).unsqueeze(-1)
            pred = model(x_tensor).item()
            pred_future_scaled.append(pred)
            current_seq.append(pred)
            current_seq.pop(0)

    pred_future = scaler.inverse_transform(np.array(pred_future_scaled).reshape(-1, 1)).flatten()

# 성능 지표
rmse = np.sqrt(mean_squared_error(actual_test, pred_test))
r2 = r2_score(actual_test, pred_test)
mae = mean_absolute_error(actual_test, pred_test)

# ══════════════════════════════════════════════════════════════
#  KPI & Tabs 렌더링
# ══════════════════════════════════════════════════════════════
c1, c2, c3 = st.columns(3)
c1.metric("Latest Temp", f"{df['temperature'].iloc[-1]:.1f}°C")
c2.metric("Change", f"{df['temperature'].diff().iloc[-1]:+.1f}°C")
c3.metric(f"AI ({model_type}) Forecast", f"{pred_future[-1]:.1f}°C")

st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["Temperature Trend", "AI Prediction", "Decomposition", "Raw Data"])

with tab1:
    st.subheader(f"{city} — Historical Temperature")
    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, df["temperature"], label="Temp", color="black")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(alpha=0.3)
    ax.legend()
    st.pyplot(fig)

with tab2:
    st.subheader(f"AI Model Prediction: {model_type}")

    m1, m2, m3 = st.columns(3)
    m1.metric("RMSE", f"{rmse:.4f}")
    m2.metric("R²", f"{r2:.4f}")
    m3.metric("MAE", f"{mae:.4f}")

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.plot(train_data.index, train_data["temperature"], label="Train", alpha=0.3, color="blue")
    ax.plot(test_dates, actual_test, label="Actual (Test)", color="green", linewidth=2)
    ax.plot(test_dates, pred_test, label=f"Predicted ({model_type})", color="red", linestyle="--")

    ax.plot(future_dates, pred_future, label=f"Forecast ({forecast_days}d)", color="purple", marker="o")

    if show_confidence:
        std = np.std(actual_test - pred_test)
        ax.fill_between(future_dates, pred_future - 1.96*std, pred_future + 1.96*std, alpha=0.15, color="purple", label="95% CI")

    ax.legend(fontsize=10)
    ax.set_title(f"{city} Temperature Forecast ({model_type})")
    ax.set_ylabel("Temperature (°C)")
    ax.grid(alpha=0.3)
    st.pyplot(fig)

    with st.expander("Prediction Comparison Table"):
        comp = pd.DataFrame({
            "Date": test_dates, "Actual": actual_test, "Predicted": pred_test,
            "Error": actual_test - pred_test,
            "Error %": ((actual_test - pred_test) / actual_test * 100)
        })
        st.dataframe(comp.style.format({
            "Actual": "{:.1f}°C", "Predicted": "{:.1f}°C", "Error": "{:.1f}°C", "Error %": "{:.2f}%"
        }))

with tab3:
    st.subheader("Time Series Decomposition")
    res = seasonal_decompose(df["temperature"], period=30)
    res.plot()
    st.pyplot(plt.gcf())

with tab4:
    st.subheader("Raw Data")
    st.dataframe(df)

