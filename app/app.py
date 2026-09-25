import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(page_title="Traffic Congestion Predictor", page_icon="🚦")

# Load the trained model and the exact column structure it expects
model = joblib.load("models/final_model.pkl")
X_train_columns = pd.read_csv("data/processed/X_train.csv", nrows=0).columns.tolist()

st.title("🚦 Traffic Congestion Predictor")
st.write("Predicts congestion on I-94 westbound (Minneapolis–St Paul) from expected conditions.")

# --- Inputs ---
day = st.selectbox("Day of week", ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
hour = st.slider("Hour of day (0–23)", 0, 23, 8)
is_holiday = st.checkbox("Is this a holiday?")

temp_celsius = st.slider("Temperature (°C)", -30, 40, 10)
rain = st.slider("Rainfall in the last hour (mm)", 0.0, 60.0, 0.0)
snow = st.slider("Snowfall in the last hour (mm)", 0.0, 1.0, 0.0)
clouds = st.slider("Cloud cover (%)", 0, 100, 50)
weather = st.selectbox("General weather condition",
    ['Clear', 'Clouds', 'Rain', 'Drizzle', 'Thunderstorm', 'Snow', 'Mist', 'Fog', 'Haze', 'Other'])

if st.button("Predict Congestion"):
    # --- Derive the same engineered features Phase 6 created ---
    is_weekend = 1 if day in ['Saturday', 'Sunday'] else 0
    peak_hours = [6, 7, 8, 14, 15, 16, 17]
    is_peak_hour = 1 if (hour in peak_hours and is_weekend == 0) else 0
    hour_sin = np.sin(2 * np.pi * hour / 24)
    hour_cos = np.cos(2 * np.pi * hour / 24)
    temp_kelvin = temp_celsius + 273.15

    # --- Build a row matching the model's exact expected columns ---
    input_row = pd.DataFrame(0, index=[0], columns=X_train_columns)

    input_row['temp'] = temp_kelvin
    input_row['rain_1h'] = rain
    input_row['snow_1h'] = snow
    input_row['clouds_all'] = clouds
    input_row['is_weekend'] = is_weekend
    input_row['is_holiday'] = int(is_holiday)
    input_row['is_peak_hour'] = is_peak_hour
    input_row['hour_sin'] = hour_sin
    input_row['hour_cos'] = hour_cos

    day_col = f'day_of_week_{day}'
    if day_col in input_row.columns:
        input_row[day_col] = 1

    weather_col = f'weather_main_grouped_{weather}'
    if weather_col in input_row.columns:
        input_row[weather_col] = 1

    # --- Predict ---
    prediction = model.predict(input_row)[0]
    probabilities = model.predict_proba(input_row)[0]
    prob_dict = dict(zip(model.classes_, probabilities))

    category_order = ['Low', 'Medium', 'High', 'Very High']
    prob_df = pd.DataFrame({
        'Congestion Level': category_order,
        'Probability': [prob_dict[c] for c in category_order]
    })

    st.subheader(f"Predicted congestion: **{prediction}**")
    st.bar_chart(prob_df.set_index('Congestion Level'))

    st.write("### Input summary")
    st.write(f"- **Day:** {day} ({'Weekend' if is_weekend else 'Weekday'})")
    st.write(f"- **Hour:** {hour}:00 {'— Peak hour' if is_peak_hour else ''}")
    st.write(f"- **Holiday:** {'Yes' if is_holiday else 'No'}")
    st.write(f"- **Weather:** {weather}, {temp_celsius}°C, {rain}mm rain, {snow}mm snow, {clouds}% cloud cover")