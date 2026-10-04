import os

import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


# =========================================================
# CONFIGURATION
# =========================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "https://cloud-based-vehicle-data-storage.onrender.com"
)

LOGIN_URL = f"{API_BASE_URL}/login"
VEHICLES_URL = f"{API_BASE_URL}/vehicles"

USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Vehicle Telemetry Dashboard",
    page_icon="🚗",
    layout="wide"
)


# =========================================================
# AUTHENTICATION
# =========================================================

def get_access_token():
    login_data = {
        "username": USERNAME,
        "password": PASSWORD
    }

    try:
        response = requests.post(
            LOGIN_URL,
            data=login_data,
            timeout=15
        )

        if response.status_code == 200:
            return response.json().get(
                "access_token"
            )

        return None

    except requests.exceptions.RequestException:
        return None


def get_auth_headers():
    if "access_token" not in st.session_state:
        st.session_state.access_token = (
            get_access_token()
        )

    if not st.session_state.access_token:
        return None

    return {
        "Authorization": (
            f"Bearer {st.session_state.access_token}"
        )
    }


def authenticated_get(url):
    headers = get_auth_headers()

    if not headers:
        return None

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=15
        )

        # Refresh token if authentication expired.
        if response.status_code == 401:

            st.session_state.access_token = (
                get_access_token()
            )

            headers = get_auth_headers()

            if not headers:
                return response

            response = requests.get(
                url,
                headers=headers,
                timeout=15
            )

        return response

    except requests.exceptions.RequestException:
        return None


# =========================================================
# PAGE HEADER
# =========================================================

st.title(
    "🚗 Vehicle Telemetry Monitoring Dashboard"
)

st.caption(
    "Cloud-Based Vehicle Data Storage & Analytics Platform"
)

st.caption(
    f"Backend: {API_BASE_URL}"
)

st.divider()


# =========================================================
# CHECK AUTHENTICATION
# =========================================================

if "access_token" not in st.session_state:
    st.session_state.access_token = (
        get_access_token()
    )


if not st.session_state.access_token:

    st.error(
        "❌ Unable to authenticate with the FastAPI backend."
    )

    st.info(
        "Check the API URL and authentication "
        "environment variables."
    )

    st.stop()


# =========================================================
# FETCH VEHICLES
# =========================================================

vehicles_response = authenticated_get(
    VEHICLES_URL
)


if vehicles_response is None:

    st.error(
        "❌ Cannot connect to the FastAPI backend."
    )

    st.stop()


if vehicles_response.status_code != 200:

    st.error(
        f"❌ Unable to load vehicles. "
        f"Backend returned "
        f"{vehicles_response.status_code}."
    )

    st.stop()


vehicles = vehicles_response.json()


if not vehicles:

    st.warning(
        "⚠️ No vehicles are registered in the system."
    )

    st.stop()


# =========================================================
# VEHICLE SELECTION
# =========================================================

st.subheader("🚘 Vehicle Selection")


vehicle_options = {}

for vehicle in vehicles:

    display_name = (
        f'{vehicle["vehicle_id"]} — '
        f'{vehicle["manufacturer"]} '
        f'{vehicle["model"]} '
        f'({vehicle["year"]})'
    )

    vehicle_options[display_name] = vehicle


selected_vehicle_name = st.selectbox(
    "Select Vehicle",
    options=list(vehicle_options.keys())
)


selected_vehicle = vehicle_options[
    selected_vehicle_name
]


vehicle_id = selected_vehicle["id"]


# =========================================================
# VEHICLE INFORMATION
# =========================================================

st.subheader("🚘 Vehicle Information")


info_col1, info_col2, info_col3, info_col4 = (
    st.columns(4)
)


with info_col1:

    st.metric(
        "Vehicle ID",
        selected_vehicle["vehicle_id"]
    )


with info_col2:

    st.metric(
        "Manufacturer",
        selected_vehicle["manufacturer"]
    )


with info_col3:

    st.metric(
        "Model",
        selected_vehicle["model"]
    )


with info_col4:

    st.metric(
        "Year",
        selected_vehicle["year"]
    )


st.divider()


# =========================================================
# FETCH VEHICLE DATA
# =========================================================

telemetry_response = authenticated_get(
    f"{API_BASE_URL}/telemetry/{vehicle_id}"
)

analytics_response = authenticated_get(
    f"{API_BASE_URL}/analytics/{vehicle_id}"
)

alerts_response = authenticated_get(
    f"{API_BASE_URL}/alerts/{vehicle_id}"
)


# =========================================================
# CHECK TELEMETRY
# =========================================================

if telemetry_response is None:

    st.error(
        "❌ Could not retrieve telemetry data."
    )

    st.stop()


if telemetry_response.status_code == 404:

    st.error(
        "❌ Vehicle not found."
    )

    st.stop()


if telemetry_response.status_code != 200:

    st.error(
        f"❌ Telemetry request failed. "
        f"Status code: "
        f"{telemetry_response.status_code}"
    )

    st.stop()


telemetry_data = telemetry_response.json()


# =========================================================
# GET ALERTS
# =========================================================

if (
    alerts_response is not None
    and alerts_response.status_code == 200
):

    alerts = alerts_response.json()

else:

    alerts = []


# =========================================================
# VEHICLE STATUS
# =========================================================

critical_alerts = [
    alert
    for alert in alerts
    if alert.get("severity") == "CRITICAL"
]


warning_alerts = [
    alert
    for alert in alerts
    if alert.get("severity") == "WARNING"
]


if critical_alerts:

    vehicle_status = "🔴 Critical"

elif warning_alerts:

    vehicle_status = "🟠 Warning"

else:

    vehicle_status = "🟢 Normal"


# =========================================================
# STATUS + ALERT SUMMARY
# =========================================================

st.subheader("🚦 Vehicle Status")


status_col1, status_col2, status_col3, status_col4 = (
    st.columns(4)
)


with status_col1:

    st.metric(
        "Current Status",
        vehicle_status
    )


with status_col2:

    st.metric(
        "Total Alerts",
        len(alerts)
    )


with status_col3:

    st.metric(
        "Warnings",
        len(warning_alerts)
    )


with status_col4:

    st.metric(
        "Critical Alerts",
        len(critical_alerts)
    )


st.divider()


# =========================================================
# NO TELEMETRY DATA
# =========================================================

if not telemetry_data:

    st.warning(
        "⚠️ No telemetry data found for this vehicle."
    )

    if alerts:

        st.subheader("🚨 Vehicle Alerts")

        alerts_df = pd.DataFrame(alerts)

        st.dataframe(
            alerts_df,
            use_container_width=True,
            hide_index=True
        )

    st.stop()


# =========================================================
# CREATE DATAFRAME
# =========================================================

df = pd.DataFrame(
    telemetry_data
)


df["timestamp"] = pd.to_datetime(
    df["timestamp"]
)


# Sort oldest → newest.
df = df.sort_values(
    "timestamp"
).reset_index(
    drop=True
)


# =========================================================
# CHART DATA
# =========================================================

chart_df = df.tail(
    100
).copy()


chart_df["reading_number"] = range(
    1,
    len(chart_df) + 1
)


# =========================================================
# ANALYTICS
# =========================================================

if (
    analytics_response is not None
    and analytics_response.status_code == 200
):

    analytics = analytics_response.json()

else:

    analytics = {
        "total_records": len(df),
        "average_speed": 0,
        "maximum_speed": 0,
        "average_rpm": 0,
        "maximum_temperature": 0,
        "minimum_fuel": 0,
        "average_battery_voltage": 0
    }


# =========================================================
# VEHICLE OVERVIEW
# =========================================================

st.subheader("📊 Vehicle Overview")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Telemetry Records",
        analytics.get(
            "total_records",
            len(df)
        )
    )


with col2:

    st.metric(
        "Average Speed",
        f'{analytics.get("average_speed", 0)} km/h'
    )


with col3:

    st.metric(
        "Maximum Speed",
        f'{analytics.get("maximum_speed", 0)} km/h'
    )


with col4:

    st.metric(
        "Max Engine Temperature",
        f'{analytics.get("maximum_temperature", 0)} °C'
    )


st.divider()


# =========================================================
# VEHICLE HEALTH KPIs
# =========================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Average RPM",
        f'{analytics.get("average_rpm", 0)}'
    )


with col2:

    st.metric(
        "Minimum Fuel",
        f'{analytics.get("minimum_fuel", 0)}%'
    )


with col3:

    st.metric(
        "Average Battery",
        f'{analytics.get("average_battery_voltage", 0)} V'
    )


with col4:

    st.metric(
        "Total Alerts",
        len(alerts)
    )


st.divider()


# =========================================================
# VEHICLE SPEED
# =========================================================

st.subheader("📈 Vehicle Speed")


speed_chart = px.line(
    chart_df,
    x="reading_number",
    y="speed",
    markers=True,
    title="Speed — Last 100 Readings",
    hover_data={
        "reading_number": True,
        "speed": ":.2f",
        "timestamp": True
    }
)


speed_chart.update_layout(
    xaxis_title="Reading Number",
    yaxis_title="Speed (km/h)",
    hovermode="x unified"
)


speed_chart.update_traces(
    line=dict(width=2),
    marker=dict(size=5)
)


st.plotly_chart(
    speed_chart,
    use_container_width=True
)


# =========================================================
# ENGINE PARAMETERS
# =========================================================

st.subheader("⚙️ Engine Parameters")


col1, col2 = st.columns(2)


# ---------------------------------------------------------
# ENGINE RPM
# ---------------------------------------------------------

with col1:

    rpm_chart = px.line(
        chart_df,
        x="reading_number",
        y="engine_rpm",
        markers=True,
        title="Engine RPM — Last 100 Readings",
        hover_data={
            "reading_number": True,
            "engine_rpm": ":.2f",
            "timestamp": True
        }
    )


    rpm_chart.update_layout(
        xaxis_title="Reading Number",
        yaxis_title="RPM",
        hovermode="x unified"
    )


    rpm_chart.update_traces(
        line=dict(width=2),
        marker=dict(size=4)
    )


    st.plotly_chart(
        rpm_chart,
        use_container_width=True
    )


# ---------------------------------------------------------
# ENGINE TEMPERATURE
# ---------------------------------------------------------

with col2:

    temperature_chart = px.line(
        chart_df,
        x="reading_number",
        y="engine_temperature",
        markers=True,
        title="Engine Temperature — Last 100 Readings",
        hover_data={
            "reading_number": True,
            "engine_temperature": ":.2f",
            "timestamp": True
        }
    )


    temperature_chart.update_layout(
        xaxis_title="Reading Number",
        yaxis_title="Temperature (°C)",
        hovermode="x unified"
    )


    temperature_chart.update_traces(
        line=dict(width=2),
        marker=dict(size=4)
    )


    st.plotly_chart(
        temperature_chart,
        use_container_width=True
    )


# =========================================================
# VEHICLE HEALTH
# =========================================================

st.subheader("🔋 Vehicle Health")


col1, col2 = st.columns(2)


# ---------------------------------------------------------
# FUEL
# ---------------------------------------------------------

with col1:

    fuel_chart = px.line(
        chart_df,
        x="reading_number",
        y="fuel_level",
        markers=True,
        title="Fuel Level — Last 100 Readings",
        hover_data={
            "reading_number": True,
            "fuel_level": ":.2f",
            "timestamp": True
        }
    )


    fuel_chart.update_layout(
        xaxis_title="Reading Number",
        yaxis_title="Fuel (%)",
        hovermode="x unified"
    )


    fuel_chart.update_traces(
        line=dict(width=2),
        marker=dict(size=4)
    )


    st.plotly_chart(
        fuel_chart,
        use_container_width=True
    )


# ---------------------------------------------------------
# BATTERY
# ---------------------------------------------------------

with col2:

    battery_chart = px.line(
        chart_df,
        x="reading_number",
        y="battery_voltage",
        markers=True,
        title="Battery Voltage — Last 100 Readings",
        hover_data={
            "reading_number": True,
            "battery_voltage": ":.2f",
            "timestamp": True
        }
    )


    battery_chart.update_layout(
        xaxis_title="Reading Number",
        yaxis_title="Voltage (V)",
        hovermode="x unified"
    )


    battery_chart.update_traces(
        line=dict(width=2),
        marker=dict(size=4)
    )


    st.plotly_chart(
        battery_chart,
        use_container_width=True
    )


# =========================================================
# ALERTS
# =========================================================

st.subheader("🚨 Vehicle Alerts")


if alerts:

    alerts_df = pd.DataFrame(
        alerts
    )


    if "timestamp" in alerts_df.columns:

        alerts_df["timestamp"] = (
            pd.to_datetime(
                alerts_df["timestamp"]
            )
        )


        alerts_df = alerts_df.sort_values(
            "timestamp",
            ascending=False
        )


    preferred_columns = [
        "id",
        "vehicle_id",
        "telemetry_id",
        "alert_type",
        "severity",
        "message",
        "timestamp"
    ]


    available_columns = [
        column
        for column in preferred_columns
        if column in alerts_df.columns
    ]


    alerts_df = alerts_df[
        available_columns
    ]


    st.dataframe(
        alerts_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "✅ No alerts detected for this vehicle."
    )


# =========================================================
# LATEST TELEMETRY
# =========================================================

st.subheader("📡 Latest Telemetry")


latest_data = (
    df.sort_values(
        "timestamp",
        ascending=False
    )
    .head(10)
)


st.dataframe(
    latest_data,
    use_container_width=True,
    hide_index=True
)


# =========================================================
# DATABASE INFORMATION
# =========================================================

st.divider()


col1, col2 = st.columns(2)


with col1:

    st.caption(
        f"📊 Total telemetry records stored: "
        f"{len(df)}"
    )


with col2:

    st.caption(
        f"📈 Charts displaying latest "
        f"{min(100, len(df))} readings"
    )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "Cloud-Based Vehicle Data Storage & Analytics Platform "
    "| FastAPI + PostgreSQL + Streamlit"
)