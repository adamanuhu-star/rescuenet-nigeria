# ================= DASHBOARD =================
elif menu == "Dashboard":

    st.subheader("📊 Incident Dashboard")

    data = load_reports()

    if not data.empty:

        # ---------- TABLE ----------
        st.dataframe(data)

        # ---------- DOWNLOAD ----------
        csv_file = data.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download Reports",
            csv_file,
            "reports.csv",
            "text/csv"
        )

        st.divider()

        # ---------- LIVE MAP ----------
        st.subheader("🗺️ Live Incident Map")

        # Default Nigeria center
        m = folium.Map(location=[9.0820, 8.6753], zoom_start=6)

        # Add markers
        for i, row in data.iterrows():
            folium.Marker(
                location=[row["Latitude"], row["Longitude"]],
                popup=f"""
                🚨 {row['Incident']}<br>
                🏢 {row['Agency']}<br>
                📝 {row['Description']}
                """,
                icon=folium.Icon(color="red", icon="info-sign")
            ).add_to(m)

        # Display map
        st_folium(m, width=800, height=500)

    else:
        st.warning("No reports yet")
