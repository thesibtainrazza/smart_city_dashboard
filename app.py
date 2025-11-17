# app.py
import streamlit as st
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Smart City IoT Dashboard", layout="wide", initial_sidebar_state="expanded")

# -----------------------
# Helper / Utility funcs
# -----------------------
def clean_columns(cols):
    # remove bad encoding, normalize names
    cols = cols.str.replace("Â", "", regex=False)
    cols = cols.str.replace("µ", "u", regex=False)
    cols = cols.str.replace("³", "3", regex=False)
    cols = cols.str.replace(" ", "", regex=False)  # optional: remove spaces in column names for stability
    # but we will also keep a display mapping
    return cols

def human_col_map(col):
    # Returns nicer display label for cleaned column names
    mapping = {
        "Timestamp": "Timestamp",
        "City": "City",
        "Temperature(°C)": "Temperature(°C)",
        "Temperature(°C)".replace(" ", ""): "Temperature(°C)",
        "Temperature(°C)".replace(" ", ""): "Temperature(°C)",
    }
    return mapping.get(col, col)

def aqi_status(aqi):
    # returns (label, color)
    if aqi <= 50:
        return "Good", "#2ECC71"
    if aqi <= 100:
        return "Moderate", "#F1C40F"
    if aqi <= 200:
        return "Unhealthy", "#E67E22"
    if aqi <= 300:
        return "Very Unhealthy", "#E74C3C"
    return "Hazardous", "#8E44AD"

def ensure_numeric_cols(df):
    # convert common sensor columns to numeric safely
    for c in df.columns:
        # attempt numeric conversion if object dtype
        if df[c].dtype == object:
            try:
                df[c] = pd.to_numeric(df[c], errors='ignore')
            except Exception:
                pass
    return df

# -----------------------
# Load Data
# -----------------------
@st.cache_data
def load_data():
    # assumes data.csv is present in the working directory
    df = pd.read_csv("data.csv")
    return df

try:
    df = load_data()
except FileNotFoundError:
    st.error("data.csv not found. Please place your exported data.csv in the app folder.")
    st.stop()

# Clean column names for consistent access
orig_cols = df.columns.copy()
df.columns = clean_columns(df.columns)

# Map cleaned column names to the internal keys we'll use (flexible)
# Common cleaned names we expect:
# e.g. "PM2.5(ug/m3)" might become "PM2.5(ug/m3)" but with no spaces above logic may remove spaces
# we'll search for best matching columns:
def find_col(possible_names):
    for name in possible_names:
        if name in df.columns:
            return name
    return None

col_timestamp = find_col(["Timestamp", "timestamp", "Time", "Datetime"])
col_city = find_col(["City", "city"])
col_temp = find_col(["Temperature(°C)", "Temperature(°C)".replace(" ", ""), "Temperature"])
col_humidity = find_col(["Humidity(%)", "Humidity"])
col_aqi = find_col(["AQI", "Aqi", "aqi"])
col_pm25 = find_col(["PM2.5(ug/m3)", "PM2.5(ug/m3)".replace(" ", ""), "PM25", "PM2_5"])
col_pm10 = find_col(["PM10(ug/m3)", "PM10", "PM10(ug/m3)".replace(" ", "")])
col_co = find_col(["CO(ppm)", "CO(ppm)".replace(" ", ""), "CO"])
col_no2 = find_col(["NO2(ppm)", "NO2"])
col_wind = find_col(["WindSpeed(km/h)", "Wind Speed(km/h)", "WindSpeed", "Wind"])

# If timestamp exists, make sure it's datetime
if col_timestamp:
    try:
        df[col_timestamp] = pd.to_datetime(df[col_timestamp])
    except:
        # try infer
        df[col_timestamp] = pd.to_datetime(df[col_timestamp], errors='coerce')

# Ensure numeric columns are numeric
df = ensure_numeric_cols(df)

# If city column exists and lat/lon missing, create approximate coordinates
# We'll map known city names to approximate coords; add jitter for markers.
city_coords = {
    "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Mumbai": (19.0760, 72.8777),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639)
}

# Add lat/lon if not already present
if "lat" not in df.columns and "lon" not in df.columns and col_city:
    lats = []
    lons = []
    for c in df[col_city].astype(str):
        base = city_coords.get(c.split()[0], (0,0))
        # jitter so multiple sensors show distinct points
        jitter = (random.uniform(-0.02, 0.02), random.uniform(-0.02, 0.02))
        if base == (0,0):
            lats.append(np.nan)
            lons.append(np.nan)
        else:
            lats.append(base[0] + jitter[0])
            lons.append(base[1] + jitter[1])
    df["lat"] = lats
    df["lon"] = lons

# -----------------------
# Sidebar - Filters
# -----------------------
st.sidebar.header("🔎 Filters & Controls")

# City filter
if col_city:
    cities = df[col_city].dropna().unique().tolist()
    selected_city = st.sidebar.selectbox("Select city", ["All"] + sorted(cities))
else:
    selected_city = "All"

# Weather filter (if exists)
weather_col = find_col(["Weather", "weather"])
if weather_col:
    weathers = df[weather_col].dropna().unique().tolist()
    selected_weather = st.sidebar.multiselect("Weather", options=weathers, default=weathers)
else:
    selected_weather = None

# Date range filter
if col_timestamp:
    min_date = df[col_timestamp].min()
    max_date = df[col_timestamp].max()
    date_range = st.sidebar.date_input("Date range", value=(min_date.date(), max_date.date()))
else:
    date_range = None

# AQI slider
if col_aqi:
    min_aqi = int(df[col_aqi].min(skipna=True))
    max_aqi = int(df[col_aqi].max(skipna=True))
    aqi_slider = st.sidebar.slider("AQI Range", min_value=0, max_value=500, value=(min_aqi, max_aqi))
else:
    aqi_slider = (0, 500)

# Live simulation toggle & speed
simulate_live = st.sidebar.checkbox("Enable live simulation", value=False)
sim_delay = st.sidebar.slider("Simulation delay (sec)", 0.2, 2.0, 1.0, step=0.2)

# Reset / Refresh button
if st.sidebar.button("Reset filters"):
    # trivial hack: reload the page
    st.experimental_rerun()

# -----------------------
# Apply filters to dataframe
# -----------------------
df_filtered = df.copy()

if selected_city != "All" and col_city:
    df_filtered = df_filtered[df_filtered[col_city] == selected_city]

if selected_weather and weather_col:
    if len(selected_weather) > 0:
        df_filtered = df_filtered[df_filtered[weather_col].isin(selected_weather)]

if date_range and col_timestamp:
    start_date, end_date = date_range
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    df_filtered = df_filtered[(df_filtered[col_timestamp] >= start_dt) & (df_filtered[col_timestamp] <= end_dt)]

if col_aqi:
    df_filtered = df_filtered[(df_filtered[col_aqi] >= aqi_slider[0]) & (df_filtered[col_aqi] <= aqi_slider[1])]

# -----------------------
# Top KPIs & AQI Status
# -----------------------
st.markdown("## Overview")

kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

# Current AQI (last record in filtered df)
try:
    current_aqi = int(df_filtered[col_aqi].dropna().iloc[-1])
except Exception:
    current_aqi = None

if current_aqi is not None:
    status_text, status_color = aqi_status(current_aqi)
    kpi_col1.metric("Current AQI", current_aqi, delta=None)
    # show color box and status
    kpi_col2.markdown(f"**AQI Status:** <span style='color:{status_color};font-weight:bold'>{status_text}</span>", unsafe_allow_html=True)
else:
    kpi_col1.metric("Current AQI", "N/A")
    kpi_col2.write("AQI Status: N/A")

# PM2.5 and PM10 averages if columns are present
if col_pm25:
    pm25_avg = round(df_filtered[col_pm25].dropna().astype(float).mean(), 2)
    kpi_col3.metric("PM2.5 Avg (ug/m3)", pm25_avg)
else:
    kpi_col3.metric("PM2.5 Avg", "N/A")

if col_pm10:
    pm10_avg = round(df_filtered[col_pm10].dropna().astype(float).mean(), 2)
    kpi_col4.metric("PM10 Avg (ug/m3)", pm10_avg)
else:
    kpi_col4.metric("PM10 Avg", "N/A")

# Alert box for hazardous AQI
if current_aqi is not None and current_aqi > 200:
    st.error(f"⚠️ Hazardous AQI detected ({current_aqi}) — immediate action recommended!")

# -----------------------
# Main layout: charts & map
# -----------------------
left_col, right_col = st.columns((2,1))

with left_col:
    st.subheader("Interactive Sensor Trends")

    # Time-series selector
    numeric_candidates = df_filtered.select_dtypes(include=[np.number]).columns.tolist()
    # short friendly names for dropdown, but use column keys
    trend_options = numeric_candidates.copy()
    if not trend_options:
        st.info("No numeric columns available to chart.")
    else:
        # Default choose AQI if available, else first numeric
        default_trend = col_aqi if col_aqi in trend_options else trend_options[0]
        selected_trends = st.multiselect("Select metrics to plot (time-series)", options=trend_options, default=[default_trend])

        # Build time-series figure using Plotly
        if col_timestamp:
            fig_ts = go.Figure()
            for metric in selected_trends:
                # Ensure metric exists
                y = df_filtered[metric]
                x = df_filtered[col_timestamp]
                fig_ts.add_trace(go.Scatter(x=x, y=y, mode="lines+markers", name=metric))
            fig_ts.update_layout(title="Time-series: Selected Metrics", xaxis_title="Time", yaxis_title="Value", template="plotly_white")
            st.plotly_chart(fig_ts, use_container_width=True)
        else:
            st.info("No timestamp column available for time-series charts.")

    st.markdown("---")

    # Scatter matrix / relationship chart (Plotly)
    st.subheader("Feature Relationships")
    if len(numeric_candidates) >= 2:
        x_axis = st.selectbox("X-axis", options=numeric_candidates, index=0)
        y_axis = st.selectbox("Y-axis", options=numeric_candidates, index=1)
        color_by = col_city if col_city else None

        fig_scatter = px.scatter(df_filtered, x=x_axis, y=y_axis, color=color_by, hover_data=df_filtered.columns.tolist(), title=f"{y_axis} vs {x_axis}")
        st.plotly_chart(fig_scatter, use_container_width=True)
    else:
        st.info("Add more numeric columns to enable scatter plots.")

    st.markdown("---")

    # Correlation heatmap (Plotly)
    st.subheader("Correlation Heatmap")
    numeric_df = df_filtered.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        corr = numeric_df.corr()
        fig_corr = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Matrix")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("No numeric data to compute correlation.")

with right_col:
    st.subheader("Spatial View & Latest Sensors")

    # Map of sensors (if lat/lon present)
    if "lat" in df_filtered.columns and "lon" in df_filtered.columns and not df_filtered["lat"].isna().all():
        # small table of latest readings and a map
        latest = df_filtered.sort_values(by=col_timestamp if col_timestamp else df_filtered.columns[0]).tail(10)
        st.dataframe(latest[[col_city, col_aqi] + ([col_pm25] if col_pm25 else []) + (["lat","lon"] if "lat" in latest.columns else [])].rename(columns=lambda x: x))
        st.map(df_filtered[["lat","lon"]].dropna())
    else:
        st.info("No coordinates available for map. Add lat/lon or let app auto-generate by city.")

    st.markdown("---")
    st.subheader("Summary Statistics")
    st.write(numeric_df.describe().T)

# -----------------------
# Live simulation (Plotly streaming-like)
# -----------------------
if simulate_live:
    st.subheader("Live Simulation — Real-time Chart")
    sim_col = st.container()
    # build a small dataframe to append to for simulation
    sim_df = pd.DataFrame(columns=["time", "AQI", "PM2.5", "Temperature"])
    # seed with last N rows if available
    try:
        seed = df_filtered.tail(10)
        if col_timestamp and col_aqi:
            for idx, row in seed.iterrows():
                sim_df = sim_df.append({
                    "time": row[col_timestamp],
                    "AQI": row[col_aqi],
                    "PM2.5": row[col_pm25] if col_pm25 in df_filtered.columns else np.nan,
                    "Temperature": row[col_temp] if col_temp in df_filtered.columns else np.nan
                }, ignore_index=True)
    except Exception:
        pass

    # live plot initial
    fig_live = go.Figure()
    fig_live.add_trace(go.Scatter(x=sim_df["time"], y=sim_df["AQI"], mode="lines+markers", name="AQI"))
    fig_live.add_trace(go.Scatter(x=sim_df["time"], y=sim_df["PM2.5"], mode="lines+markers", name="PM2.5"))
    fig_live.update_layout(title="Live Sensor Stream", xaxis_title="Time", yaxis_title="Value", template="plotly_white")

    live_plot = st.plotly_chart(fig_live, use_container_width=True)

    # append simulated points for N iterations
    for i in range(30):
        new_time = datetime.now()
        new_aqi = random.randint(40, 320)
        new_pm25 = random.randint(10, 200) if col_pm25 else np.nan
        new_temp = round(random.uniform(18, 34), 2) if col_temp else np.nan

        sim_df = sim_df.append({"time": new_time, "AQI": new_aqi, "PM2.5": new_pm25, "Temperature": new_temp}, ignore_index=True)

        fig_live = go.Figure()
        fig_live.add_trace(go.Scatter(x=sim_df["time"], y=sim_df["AQI"], mode="lines+markers", name="AQI"))
        fig_live.add_trace(go.Scatter(x=sim_df["time"], y=sim_df["PM2.5"], mode="lines+markers", name="PM2.5"))
        fig_live.update_layout(title="Live Sensor Stream", xaxis_title="Time", yaxis_title="Value", template="plotly_white")

        live_plot.plotly_chart(fig_live, use_container_width=True)
        time.sleep(sim_delay)

    st.success("Simulation finished.")

# -----------------------
# Footer / credits
# -----------------------
st.markdown("---")
st.markdown("Made by **Mohd. Sibtain Raza** — Smart City Dashboard | IoT | Real-time Data Visualization")
