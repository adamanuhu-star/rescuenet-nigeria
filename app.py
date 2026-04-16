import streamlit as st
import pandas as pd
from datetime import datetime

# Optional imports (safe loading)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except:
    TWILIO_AVAILABLE = False

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="RescueNet Nigeria 🇳🇬", layout="wide")

st.title("🚨 RescueNet Nigeria 🇳🇬")

# -----------------------------
# INCIDENT → AGENCY MAP
# -----------------------------
AGENCY_MAP = {
    "Road Accident": "FRSC",
    "Fire Outbreak": "Fire Service",
    "Flood": "NEMA",
    "Kidnapping": "Police",
    "Critical Asset Vandalism": "NSCDC"
}

# -----------------------------
# GET PHONE PER AGENCY
# -----------------------------
def get_agency_phone(agency):
    try:
        if agency == "FRSC":
            return st.secrets.get("FRSC_PHONE")
        elif agency == "Fire Service":
            return st.secrets.get("FIRE_PHONE")
        elif agency == "NEMA":
            return st.secrets.get("NEMA_PHONE")
        elif agency == "Police":
            return st.secrets.get("POLICE_PHONE")
        elif agency == "NSCDC":
            return st.secrets.get("NSCDC_PHONE")
    except:
        return None

# -----------------------------
# SEND SMS FUNCTION
# -----------------------------
def send_sms(incident, agency, desc, lat, lon):

    if not TWILIO_AVAILABLE:
        return "Twilio not installed"

    try:
        sid = st.secrets.get("TWILIO_SID")
        token = st.secrets.get("TWILIO_AUTH_TOKEN")
        sender = st.secrets.get("TWILIO_PHONE")

        if not sid or not token or not sender:
            return "Missing Twilio config"

        client = Client(sid, token)

        to_number = get_agency_phone(agency)

        if not to_number:
            return f"No number for {agency}"

        msg = f"""🚨 RescueNet Nigeria 🇳🇬
Incident: {incident}
Agency: {agency}
Location: {lat}, {lon}

Details:
{desc}
"""

        client.messages.create(
            body=msg,
            from_=sender,
            to=to_number
        )

        return "sent"

    except Exception as e:
        return str(e)

# -----------------------------
# SESSION STORAGE
# -----------------------------
if "reports" not in st.session_state:
    st.session_state.reports = []

# -----------------------------
# MENU
# -----------------------------
menu = st.sidebar.selectbox("Menu", ["Report Incident", "Dashboard"])

# =============================
# REPORT PAGE
# =============================
if menu == "Report Incident":

    st.subheader("📍 Report Emergency")

    col1, col2 = st.columns(2)

    with col1:
        incident = st.selectbox("Select Incident", list(AGENCY_MAP.keys()))
        agency = AGENCY_MAP[incident]

        st.info(f"🚑 Assigned Agency: {agency}")

        desc = st.text_area("Describe incident")

        file = st.file_uploader("Upload Image/Video", type=["jpg", "png", "mp4"])

    with col2:
        st.markdown("### 📌 Select Location")

        lat = st.number_input("Latitude", value=9.0820)
        lon = st.number_input("Longitude", value=8.6753)

        st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=6)

    if st.button("🚨 Submit Report"):

        if not desc:
            st.warning("Please describe the incident")
        else:
            report = {
                "incident": incident,
                "agency": agency,
                "desc": desc,
                "lat": lat,
                "lon": lon,
                "time": datetime.now().strftime("%Y-%m-%d %H:%M")
            }

            st.session_state.reports.append(report)

            sms_status = send_sms(incident, agency, desc, lat, lon)

            if sms_status == "sent":
                st.success("✅ Report saved & sent to agency")
            else:
                st.warning(f"⚠ Report saved, but SMS failed: {sms_status}")

# =============================
# DASHBOARD
# =============================
elif menu == "Dashboard":

    st.subheader("📊 Live Incident Dashboard")

    if len(st.session_state.reports) == 0:
        st.info("No reports yet")
    else:
        df = pd.DataFrame(st.session_state.reports)

        st.dataframe(df, use_container_width=True)

        st.map(df.rename(columns={"lat": "lat", "lon": "lon"}))
