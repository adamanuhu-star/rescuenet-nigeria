import streamlit as st
import folium
from streamlit_folium import st_folium
import geocoder
import csv
import os
import pandas as pd

# ---------------- PAGE ----------------
st.set_page_config(page_title="RescueNet Nigeria", layout="wide")

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align: center;'>🚨 RescueNet Nigeria 🇳🇬</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>AI-Powered Emergency Response System</p>", unsafe_allow_html=True)

st.divider()

# ---------------- SAVE FUNCTION ----------------
def save_report(lat, lon, incident, agency, description):
    file_exists = os.path.isfile("reports.csv")

    with open("reports.csv", mode="a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["Latitude", "Longitude", "Incident", "Agency", "Description"])

        writer.writerow([lat, lon, incident, agency, description])

# ---------------- LOAD FUNCTION ----------------
def load_reports():
    if os.path.exists("reports.csv"):
        return pd.read_csv("reports.csv")
    else:
        return pd.DataFrame(columns=["Latitude", "Longitude", "Incident", "Agency", "Description"])

# ---------------- MENU ----------------
menu = st.sidebar.selectbox("Menu", ["Report Incident", "Dashboard"])

# ---------------- AUTO LOCATION ----------------
if "lat" not in st.session_state:
    try:
        g = geocoder.ip('me')
        if g.ok:
            st.session_state.lat = g.latlng[0]
            st.session_state.lon = g.latlng[1]
        else:
            st.session_state.lat = None
            st.session_state.lon = None
    except:
        st.session_state.lat = None
        st.session_state.lon = None

# ================= REPORT PAGE =================
if menu == "Report Incident":

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📍 Location")

        lat = st.session_state.lat if st.session_state.lat else 9.0820
        lon = st.session_state.lon if st.session_state.lon else 8.6753

        m = folium.Map(location=[lat, lon], zoom_start=10)

        map_data = st_folium(m, width=500, height=350)

        if map_data and map_data.get("last_clicked"):
            st.session_state.lat = map_data["last_clicked"]["lat"]
            st.session_state.lon = map_data["last_clicked"]["lng"]

        if st.session_state.lat:
            st.success(f"📍 {st.session_state.lat}, {st.session_state.lon}")
        else:
            st.warning("Select location")

    with col2:
        st.subheader("🚨 Report Incident")

        incident = st.selectbox("Incident Type", [
            "Road Accident",
            "Fire Outbreak",
            "Flood",
            "Kidnapping",
            "Critical National Asset Vandalism"
        ])

        agency = ""
        number = ""

        if incident == "Road Accident":
            agency = "FRSC"
            number = "122"
        elif incident == "Fire Outbreak":
            agency = "Fire Service"
            number = "112"
        elif incident == "Flood":
            agency = "NEMA"
            number = "0800-ANEMA"
        elif incident == "Kidnapping":
            agency = "Police"
            number = "112"
        elif incident == "Critical National Asset Vandalism":
            agency = "NSCDC"
            number = "0800-NSCDC"

        st.info(f"{agency} | 📞 {number}")

        description = st.text_area("Describe situation")

        if st.button("🚀 Report Incident"):
            if st.session_state.lat is not None:
                save_report(
                    st.session_state.lat,
                    st.session_state.lon,
                    incident,
                    agency,
                    description
                )
                st.success("✅ Report saved!")
            else:
                st.error("⚠️ Select location on map")

# ================= DASHBOARD =================
elif menu == "Dashboard":

    st.subheader("📊 Incident Dashboard")

    data = load_reports()

    if not data.empty:

        st.dataframe(data)

        csv_file = data
