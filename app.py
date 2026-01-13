import streamlit as st
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from datetime import datetime

# ----------------------------------
# Page Configuration
# ----------------------------------
st.set_page_config(
    page_title="Smart Home Energy Prediction",
    page_icon="⚡",
    layout="wide"
)

# ----------------------------------
# Styling (UI polish)
# ----------------------------------
st.markdown("""
<style>
body {
    background-color: #F4F6F8;
}
.block-container {
    padding-top: 1rem;
}
.card {
    background-color: white;
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ----------------------------------
# Load Model
# ----------------------------------
model = joblib.load("energy_model.pkl")

# ----------------------------------
# Session Storage
# ----------------------------------
if "records" not in st.session_state:
    st.session_state.records = []

# ----------------------------------
# Title
# ----------------------------------
st.markdown("""
<h1 style='text-align:center;color:#2C3E50;'>⚡ Smart Home Energy Consumption Prediction</h1>
<p style='text-align:center;color:#555;font-size:18px;'>
Predictive Analytics for Smarter Household Energy Management
</p>
<hr>
""", unsafe_allow_html=True)

# ----------------------------------
# Inputs
# ----------------------------------
st.subheader("🔧 Enter Household & Weather Details")

c1, c2, c3 = st.columns(3)

with c1:
    date = st.date_input("📅 Date", value=datetime.today())
    tavg = st.number_input("🌡 Avg Temperature (°C)", -10.0, 45.0, 20.0)
    prcp = st.number_input("🌧 Precipitation (mm)", 0.0, 100.0, 10.0)

with c2:
    wspd = st.number_input("💨 Wind Speed (km/h)", 0.0, 120.0, 10.0)
    sub1 = st.number_input("🍳 Kitchen (kWh)", 0.0, 50.0, 2.0)
    sub2 = st.number_input("🧺 Laundry (kWh)", 0.0, 50.0, 2.0)

with c3:
    sub3 = st.number_input("🚿 Water / AC (kWh)", 0.0, 100.0, 20.0)

# ----------------------------------
# Feature Engineering
# ----------------------------------
year, month, day = date.year, date.month, date.day

input_data = {
    "Year": year,
    "Month": month,
    "Day": day,
    "Is_Summer": int(month in [6,7,8]),
    "Is_Winter": int(month in [12,1,2]),
    "tavg": tavg,
    "tmin": tavg - 3,
    "tmax": tavg + 3,
    "prcp": prcp,
    "wspd": wspd,
    "wdir": 180.0,
    "pres": 1013.0,
    "Sub_metering_1": sub1,
    "Sub_metering_2": sub2,
    "Sub_metering_3": sub3,
    "Voltage": 230.0,
    "Global_intensity": sub1 + sub2 + sub3,
    "Global_reactive_power": 0.1,
    "Lag_1": sub1 + sub2 + sub3,
    "Lag_60": (sub1 + sub2 + sub3) * 0.95,
    "Temp_ActivePower": tavg * (sub1 + sub2 + sub3)
}

X_input = pd.DataFrame([input_data])[model.feature_names_in_]

# ----------------------------------
# Predict Button
# ----------------------------------
if st.button("⚡ Predict Energy Consumption"):
    prediction = float(model.predict(X_input)[0])

    # Consumption level
    if prediction < 50:
        level = "🟢 Low"
    elif prediction < 90:
        level = "🟡 Medium"
    else:
        level = "🔴 High"

    # Save record
    st.session_state.records.append({
        "Date": date.strftime("%Y-%m-%d"),
        "Avg Temp (°C)": tavg,
        "Precipitation (mm)": prcp,
        "Wind Speed (km/h)": wspd,
        "Kitchen (kWh)": sub1,
        "Laundry (kWh)": sub2,
        "Water/AC (kWh)": sub3,
        "Predicted Energy (kW)": round(prediction, 2),
        "Level": level
    })

    # Output
    st.metric("🔌 Predicted Energy Consumption (kW)", f"{prediction:.2f}")
    st.markdown(f"### Consumption Level: **{level}**")

    st.subheader("📊 Current Input Analysis")

    g1, g2 = st.columns(2)

    # Graph 1 (SMALL)
    with g1:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.bar(
            ["Temp", "Wind", "Kitchen", "Laundry", "Water"],
            [tavg, wspd, sub1, sub2, sub3]
        )
        ax.set_title("Input Overview")
        st.pyplot(fig)

    # Graph 2 (SMALL)
    with g2:
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.pie(
            [sub1, sub2, sub3],
            labels=["Kitchen", "Laundry", "Water/AC"],
            autopct="%1.1f%%"
        )
        ax.set_title("Energy Distribution")
        st.pyplot(fig)

# ----------------------------------
# Show Previous Predictions
# ----------------------------------
if st.button("📋 Show Previous Predictions"):
    if st.session_state.records:
        df = pd.DataFrame(st.session_state.records)
        st.subheader("📋 All Recorded Predictions")
        st.dataframe(df, use_container_width=True, height=350)
    else:
        st.info("No predictions yet.")

# ----------------------------------
# Compare With Previous
# ----------------------------------
if st.button("📊 Compare with Previous"):
    if len(st.session_state.records) >= 2:
        df = pd.DataFrame(st.session_state.records)

        prev = df.iloc[-2]["Predicted Energy (kW)"]
        curr = df.iloc[-1]["Predicted Energy (kW)"]

        left, right = st.columns([1, 2])

        with left:
            fig, ax = plt.subplots(figsize=(4, 3))
            ax.bar(["Previous", "Current"], [prev, curr])
            ax.set_title("Prediction Comparison")
            ax.set_ylabel("kW")
            st.pyplot(fig)

        with right:
            st.dataframe(df, use_container_width=True, height=300)
    else:
        st.warning("At least two predictions are required.")

# ----------------------------------
# Footer
# ----------------------------------
st.markdown("""
<hr>
<p style='text-align:center;color:gray;'>
"Energy efficiency is intelligent living." ⚡
</p>
""", unsafe_allow_html=True)
