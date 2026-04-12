import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from twilio.rest import Client

# =========================
# PAGE CONFIG
# =========================
st.set_page_config(page_title="RescueNet Nigeria 🇳🇬", layout="wide")

st.title("🚨 RescueNet Nigeria 🇳🇬")

# =========================
# SESSION STATE
# =========================
if "lat" not in st.session_state:
    st.session_state.lat = None
    st.session_state.lon = None

# =========================
# INCIDENT → AGENCY MAP
# =========================
AGENCY_MAP = {
    "Road Accident": "FRSC",
    "Fire Outbreak": "Fire Service",
    "Flood": "NEMA",
    "Kidnapping": "Police",
    "Critical National Asset Vandalism": "NSCDC"
}

# =========================
# SAVE REPORT
# =========================
def save_report(lat, lon, incident, agency, description):
    df = pd.DataFrame([{
        "lat": lat,
        "lon": lon,
        "incident": incident,
        "agency": agency,
        "description": description
    }])

    try:
        old = pd.read_csv("reports.csv")
        df = pd.concat([old, df], ignore_index=True)
    except:
        pass

    df.to_csv("reports.csv", index=False)

# =========================
# SEND SMS
# =========================
def send_sms(incident, agency, description, lat, lon):
    try:
        client = Client(
            st.secrets["TWILIO_SID"],
            st.secrets["TWILIO_AUTH_TOKEN"]
        )

        message = f"""🚨 RescueNet Nigeria 🇳🇬
Incident: {incident}
Agency: {agency}
Location: {lat}, {lon}

Details:
{description}
"""

        client.messages.create(
            body=message,
            from_=st.secrets["TWILIO_PHONE"],
            to=st.secrets["ALERT_PHONE"]
        )

        return True

    except Exception as e:
        return str(e)

# =========================
# SIDEBAR MENU
# =========================
menu = st.sidebar.selectbox("Menu", ["Report Incident", "Dashboard"])

# =========================
# REPORT PAGE
# =========================
if menu == "Report Incident":

    st.subheader("📍 Select Location")

    # Map
    m = folium.Map(location=[9.08, 8.67], zoom_start=6)
    m.add_child(folium.LatLngPopup())

    map_data = st_folium(m, height=400, width=700)

    if map_data and map_data.get("last_clicked"):
        st.session_state.lat = map_data["last_clicked"]["lat"]
        st.session_state.lon = map_data["last_clicked"]["lng"]

        st.success(f"Location selected: {st.session_state.lat}, {st.session_state.lon}")

    # Form
    st.subheader("📝 Incident Details")

    incident = st.selectbox("Select Incident", list(AGENCY_MAP.keys()))
    agency = AGENCY_MAP[incident]

    st.info(f"Responsible Agency: {agency}")

    description = st.text_area("Describe the situation")

    # Uploads
    image = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])
    video = st.file_uploader("Upload Video", type=["mp4"])

    # Submit
    if st.button("🚀 Submit Report"):

        if st.session_state.lat is not None:

            save_report(
                st.session_state.lat,
                st.session_state.lon,
                incident,
                agency,
                description
            )

            sms_status = send_sms(
                incident,
                agency,
                description,
                st.session_state.lat,
                st.session_state.lon
            )

            if sms_status == True:
                st.success("✅ Report sent successfully + SMS alert delivered")
            else:
                st.warning(f"Report saved, but SMS failed: {sms_status}")

            if image:
                st.image(image)

            if video:
                st.video(video)

        else:
            st.error("❌ Please select location on the map")

# =========================
# DASHBOARD
# =========================
elif menu == "Dashboard":

    st.subheader("📊 Live Incident Dashboard")

    try:
        df = pd.read_csv("reports.csv")

        m = folium.Map(location=[9.08, 8.67], zoom_start=6)

        for _, row in df.iterrows():
            folium.Marker(
                [row["lat"], row["lon"]],
                popup=f"{row['incident']} - {row['agency']}"
            ).add_to(m)

        st_folium(m, height=500, width=900)

        st.dataframe(df)

    except:
        st.warning("No reports available yet")
