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
        # Laden der Tabellen ohne Cache (ttl=0)
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        return df_l, df_s
    except Exception as e:
        st.error("Verbindung fehlgeschlagen. Prüfe Secrets und Sheet-Freigabe.")
        st.stop()

df_log, df_settings = load_data()

# --- LOGIK: PROGRESSION ---
def calculate_next(exercise_name):
    # Standardwerte, falls keine Historie existiert
    if df_settings.empty or exercise_name not in df_settings['Exercise'].values:
        return 10.0, 10
        
    # Suche im Log nach dem letzten Eintrag
    if not df_log.empty:
        relevant_log = df_log[df_log['Exercise'] == exercise_name].copy()
        if not relevant_log.empty:
            relevant_log['Date'] = pd.to_datetime(relevant_log['Date'])
            last = relevant_log.sort_values(by='Date').iloc[-1]
            return float(last['Weight']), int(last['Reps'])
            
    return 10.0, 10 # Fallback

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

if not df_settings.empty:
    exercise = st.selectbox("Wähle Übung", df_settings['Exercise'].tolist())
    target_w, target_r = calculate_next(exercise)

    with st.form("log_form"):
        st.subheader(f"Ziel: {target_w} kg x {target_r}")
        c1, c2 = st.columns(2)
        w = c1.number_input("Gewicht", value=float(target_w), step=0.25)
        r = c2.number_input("Reps", value=int(target_r), step=1)
        p = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Speichern"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": exercise, "Weight": w, "Reps": r, "Pain": p
            }])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert! 🎉")
            st.balloons()
else:
    st.warning("Keine Übungen in 'Settings' gefunden.")
