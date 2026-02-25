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
        # Laden der Tabellen und direktes Entfernen von Leerzeichen in den Spaltennamen
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        
        if df_s is not None:
            df_s.columns = df_s.columns.str.strip() # Entfernt Leerzeichen wie "Exercise "
        if df_l is not None:
            df_l.columns = df_l.columns.str.strip()
            
        return df_l, df_s
    except Exception as e:
        st.error(f"Verbindung zum Sheet fehlgeschlagen: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_log, df_settings = load_data()

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

# Diagnose-Hilfe (nur sichtbar wenn es nicht klappt)
if df_settings.empty:
    st.error("Die Tabelle 'Settings' wurde als leer eingelesen.")
    st.info("Checke bitte, ob der Reiter in Google Sheets exakt 'Settings' heißt.")
elif "Exercise" not in df_settings.columns:
    st.error(f"Spalte 'Exercise' nicht gefunden. Vorhanden sind: {list(df_settings.columns)}")
else:
    # --- REGULÄRES INTERFACE ---
    exercise_list = df_settings['Exercise'].dropna().unique().tolist()
    exercise = st.selectbox("Wähle Übung", exercise_list)
    
    with st.form("log_form"):
        st.subheader(f"Training loggen")
        col1, col2, col3 = st.columns(3)
        w = col1.number_input("KG", value=10.0, step=0.25)
        r = col2.number_input("Reps", value=10, step=1)
        rir = col3.number_input("RIR", value=2, step=1)
        
        p = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": exercise, "Weight": w, "Reps": r, "RIR": rir, "Pain": p
            }])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert! 🎉")
