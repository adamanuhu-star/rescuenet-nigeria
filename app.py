import streamlit as st
import folium
from streamlit_folium import st_folium

# ---------------- PAGE ----------------
st.set_page_config(page_title="RescueNet Nigeria", layout="wide")

# ---------------- TITLE ----------------
st.markdown("<h1 style='text-align: center;'>🚨 RescueNet Nigeria 🇳🇬</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>AI-Powered Emergency Response System</p>", unsafe_allow_html=True)

st.divider()

# ---------------- SESSION ----------------
if "lat" not in st.session_state:
    st.session_state.lat = None
if "lon" not in st.session_state:
    st.session_state.lon = None

# ---------------- LAYOUT ----------------
col1, col2 = st.columns([1, 1])

# -------- LEFT: MAP --------
with col1:
    st.subheader("📍 Select Location")

    m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)

    map_data = st_folium(
        m,
        width=500,   # reduced size
        height=350,  # reduced height
        key="map"
    )

    if map_data and map_data.get("last_clicked"):
        st.session_state.lat = map_data["last_clicked"]["lat"]
        st.session_state.lon = map_data["last_clicked"]["lng"]

    if st.session_state.lat is not None:
        st.success(f"📍 {st.session_state.lat}, {st.session_state.lon}")
    else:
        st.warning("Click map to select location")

# -------- RIGHT: FORM --------
with col2:
    st.subheader("🚨 Report Incident")

    incident = st.selectbox("Incident Type", [
        "Road Accident",
        "Fire Outbreak",
        "Flood",
        "Kidnapping",
        "Critical National Asset Vandalism"
    ])

    # SMART ROUTING
    agency = ""
    agency_number = ""

    if incident == "Road Accident":
        agency = "🚧 FRSC"
        agency_number = "122"

    elif incident == "Fire Outbreak":
        agency = "🚒 Fire Service"
        agency_number = "112"

    elif incident == "Flood":
        agency = "🌊 NEMA"
        agency_number = "0800-ANEMA"

    elif incident == "Kidnapping":
        agency = "🚓 Police"
        agency_number = "112"

    elif incident == "Critical National Asset Vandalism":
        agency = "🛡️ NSCDC"
        agency_number = "0800-NSCDC"

    st.info(f"{agency} | 📞 {agency_number}")

    description = st.text_area("📝 Describe situation")
    uploaded_file = st.file_uploader("📸 Upload evidence")

    if st.button("🚀 Report Incident"):
        if st.session_state.lat is not None:
            st.success("✅ Report Sent Successfully")
            st.write(f"📍 Location: {st.session_state.lat}, {st.session_state.lon}")
            st.write(f"🚨 Agency: {agency}")
        else:
            st.error("⚠️ Select location first")

# ---------------- FOOTER ----------------
st.divider()
st.markdown("### 🚑 Emergency Contacts")

colA, colB, colC = st.columns(3)

with colA:
    st.write("🚓 Police: 112")
    st.write("🚧 FRSC: 122")

with colB:
    st.write("🚒 Fire: 112")
    st.write("🌊 NEMA: 0800-ANEMA")

with colC:
    st.write("🛡️ NSCDC: 0800-NSCDC")
