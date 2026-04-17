import streamlit as st
import pandas as pd
from datetime import datetime
import hashlib
import urllib.parse
import sqlite3

# -----------------------------
# DATABASE INIT
# -----------------------------
conn = sqlite3.connect("rescuenet.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident TEXT,
    agency TEXT,
    description TEXT,
    lat REAL,
    lon REAL,
    user TEXT,
    time TEXT
)
""")

conn.commit()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="RescueNet Nigeria 🇳🇬", layout="wide")
st.title("🚨 RescueNet Nigeria 🇳🇬")

# -----------------------------
# PASSWORD HASH
# -----------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# -----------------------------
# AUTH FUNCTIONS
# -----------------------------
def create_user(username, password, role="user"):
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
              (username, hash_password(password), role))
    conn.commit()

def login_user(username, password):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    return c.fetchone()

# -----------------------------
# INCIDENT MAP
# -----------------------------
AGENCY_MAP = {
    "Road Accident": "FRSC",
    "Fire Outbreak": "Fire Service",
    "Flood": "NEMA",
    "Kidnapping": "Police",
    "Critical Asset Vandalism": "NSCDC"
}

AGENCY_PHONES = {
    "FRSC": "+234XXXXXXXXXX",
    "Fire Service": "+234XXXXXXXXXX",
    "NEMA": "+234XXXXXXXXXX",
    "Police": "+234XXXXXXXXXX",
    "NSCDC": "+234XXXXXXXXXX"
}

def send_alert(incident, agency, desc, lat, lon):
    to_number = AGENCY_PHONES.get(agency)

    message = f"""🚨 RescueNet Nigeria 🇳🇬
Incident: {incident}
Agency: {agency}
Location: {lat}, {lon}

Details:
{desc}
"""

    encoded = urllib.parse.quote(message)

    return {
        "whatsapp": f"https://wa.me/{to_number.replace('+','')}?text={encoded}",
        "call": f"tel:{to_number}"
    }

# -----------------------------
# SESSION STATE
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# -----------------------------
# AUTH UI
# -----------------------------
if not st.session_state.user:

    menu = st.sidebar.selectbox("Menu", ["Login", "Signup"])

    if menu == "Signup":
        st.subheader("Create Account")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Sign Up"):
            if user and pwd:
                create_user(user, pwd)
                st.success("Account created! Login now")
            else:
                st.warning("Enter username and password")

    elif menu == "Login":
        st.subheader("Login")

        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")

        if st.button("Login"):
            result = login_user(user, pwd)

            if result:
                st.session_state.user = result
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid credentials")

# -----------------------------
# MAIN APP
# -----------------------------
else:

    username = st.session_state.user[1]
    role = st.session_state.user[3]

    st.sidebar.write(f"👤 {username} ({role})")

    if st.sidebar.button("Logout"):
        st.session_state.user = None
        st.rerun()

    menu = st.sidebar.selectbox("Menu", ["Report Incident", "Dashboard"])

    # =============================
    # REPORT INCIDENT
    # =============================
    if menu == "Report Incident":

        st.subheader("📍 Report Emergency")

        col1, col2 = st.columns(2)

        with col1:
            incident = st.selectbox("Select Incident", list(AGENCY_MAP.keys()))
            agency = AGENCY_MAP[incident]

            st.info(f"🚑 Assigned Agency: {agency}")

            desc = st.text_area("Describe incident")

        with col2:
            lat = st.number_input("Latitude", value=9.0820)
            lon = st.number_input("Longitude", value=8.6753)

            st.map(pd.DataFrame({"lat": [lat], "lon": [lon]}), zoom=6)

        if st.button("🚨 Submit Report"):

            if not desc:
                st.warning("Please describe the incident")
            else:
                c.execute("""
                INSERT INTO reports (incident, agency, description, lat, lon, user, time)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (incident, agency, desc, lat, lon, username,
                      datetime.now().strftime("%Y-%m-%d %H:%M")))

                conn.commit()

                links = send_alert(incident, agency, desc, lat, lon)

                st.success("✅ Report submitted!")

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown(f"[📲 WhatsApp Alert]({links['whatsapp']})")

                with col2:
                    st.markdown(f"[📞 Call Agency]({links['call']})")

    # =============================
    # DASHBOARD
    # =============================
    elif menu == "Dashboard":

        st.subheader("📊 Admin Dashboard" if role == "admin" else "📊 My Reports")

        # ADMIN VIEW
        if role == "admin":

            tab1, tab2 = st.tabs(["📁 Reports", "👥 Users"])

            # REPORTS
            with tab1:
                df = pd.read_sql("SELECT * FROM reports", conn)

                if df.empty:
                    st.info("No reports yet")
                else:
                    st.dataframe(df, use_container_width=True)
                    st.map(df)

                    report_id = st.number_input("Report ID to delete", step=1)

                    if st.button("Delete Report"):
                        c.execute("DELETE FROM reports WHERE id=?", (report_id,))
                        conn.commit()
                        st.success("Report deleted")
                        st.rerun()

            # USERS
            with tab2:
                users_df = pd.read_sql("SELECT id, username, role FROM users", conn)
                st.dataframe(users_df, use_container_width=True)

                user_id = st.number_input("User ID to delete", step=1)

                if user_id == st.session_state.user[0]:
                    st.warning("You cannot delete yourself")
                else:
                    if st.button("Delete User"):
                        c.execute("DELETE FROM users WHERE id=?", (user_id,))
                        conn.commit()
                        st.success("User deleted")
                        st.rerun()

        # NORMAL USER
        else:
            df = pd.read_sql(f"SELECT * FROM reports WHERE user='{username}'", conn)

            if df.empty:
                st.info("No reports yet")
            else:
                st.dataframe(df, use_container_width=True)
                st.map(df)
