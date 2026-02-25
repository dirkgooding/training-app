import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# Wir fügen einen zufälligen Parameter hinzu, um den Cache zu umgehen
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # ttl=0 ist extrem wichtig, damit er NICHTS zwischenspeichert
        df_log = conn.read(worksheet="Log", ttl=0)
        df_settings = conn.read(worksheet="Settings", ttl=0)
        
        if df_settings is not None:
            df_settings.columns = df_settings.columns.str.strip()
        return df_log, df_settings
    except Exception as e:
        st.error(f"Technischer Fehler: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_log, df_settings = load_data()

st.title("🏋️ Strong-Pain-Coach")

# Wenn er es jetzt immer noch nicht sieht, lassen wir uns die Spalten anzeigen
if df_settings.empty:
    st.error("Die App sieht die Daten im Reiter 'Settings' noch nicht.")
    if st.button("Verbindung hart neu starten"):
        st.cache_data.clear()
        st.rerun()
else:
    exercise_list = df_settings['Exercise'].dropna().unique().tolist()
    exercise = st.selectbox("Wähle Übung", exercise_list)
    
    with st.form("log_form"):
        col1, col2, col3 = st.columns(3)
        w = col1.number_input("KG", value=10.0, step=0.25)
        r = col2.number_input("Reps", value=10, step=1)
        rir = col3.number_input("RIR", value=2, step=1)
        p = st.select_slider("Schmerz", options=[0, 1, 2])
        
        if st.form_submit_button("Speichern"):
            new_row = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Exercise": exercise, "Weight": w, "Reps": r, "RIR": rir, "Pain": p}])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert! 🎉")
