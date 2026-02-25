import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- UI SETUP ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Laden der Tabellen ohne Cache
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        return df_l, df_s
    except Exception as e:
        st.error("Verbindung fehlgeschlagen. Prüfe Secrets und Sheet-Freigabe.")
        st.stop()

df_log, df_settings = load_data()

# --- LOGIK & UI ---
st.title("🏋️ Strong-Pain-Coach")

if not df_settings.empty:
    exercise = st.selectbox("Übung wählen", df_settings['Exercise'].tolist())
    
    # Platzhalter für die Berechnung (vereinfacht für den Start)
    target_w, target_r = 10.0, 10 

    with st.form("log_form"):
        st.subheader(f"Ziel: {target_w} kg")
        w = st.number_input("Gewicht", value=float(target_w))
        r = st.number_input("Reps", value=int(target_r))
        p = st.select_slider("Schmerz (0-2)", options=[0, 1, 2])
        
        if st.form_submit_button("Speichern"):
            new_row = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Exercise": exercise, "Weight": w, "Reps": r, "Pain": p}])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert!")
else:
    st.warning("Keine Übungen in 'Settings' gefunden.")
