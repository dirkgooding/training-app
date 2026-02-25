import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- UI SETUP ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# --- DATABASE CONNECTION ---
# Wir nutzen die stabilste Verbindungsmethode
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # Laden der Tabellen ohne Cache
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        return df_l, df_s
    except Exception as e:
        # Falls die Tabelle komplett leer ist (keine Spaltenköpfe), 
        # erstellen wir leere Datenrahmen, damit die App nicht abstürzt
        return pd.DataFrame(), pd.DataFrame()

df_log, df_settings = load_data()

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

# Check ob Daten da sind
if not df_settings.empty and "Exercise" in df_settings.columns:
    exercise = st.selectbox("Wähle Übung", df_settings['Exercise'].tolist())
    
    with st.form("log_form"):
        st.subheader(f"Training loggen")
        w = st.number_input("Gewicht (kg)", value=10.0, step=0.25)
        r = st.number_input("Wiederholungen", value=10, step=1)
        p = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": exercise, "Weight": w, "Reps": r, "Pain": p
            }])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert! 🎉")
            st.balloons()
else:
    st.warning("⚠️ Bitte trage in dein Google Sheet im Reiter 'Settings' in die erste Zeile 'Exercise' ein und darunter deine erste Übung.")
    st.info("Die App braucht mindestens eine Übung, um zu starten.")
