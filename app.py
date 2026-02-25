import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# Deine spezifische Sheet ID
SHEET_ID = "1mOj0cocT5AD2FPPrgHrMosaG-p3BeX0Agmd0aoAhKEs"

# URLs für den direkten Lese-Zugriff (Robusteste Methode)
# Wir nutzen GID 766773450 für Settings, falls das dein Tab ist
SETTINGS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Settings"
LOG_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Log"

# Verbindung für das SCHREIBEN (Speichern)
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        # 1. Settings lesen (für die Übungsauswahl)
        df_s = pd.read_csv(SETTINGS_URL)
        df_s.columns = df_s.columns.str.strip()
        
        # 2. Log lesen (um neue Daten anzuhängen)
        df_l = conn.read(worksheet="Log", ttl=0)
        return df_l, df_s
    except Exception as e:
        st.error(f"Verbindungsfehler: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_log, df_settings = load_data()

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

if not df_settings.empty and "Exercise" in df_settings.columns:
    # Übungsauswahl aus der Spalte 'Exercise'
    exercises = df_settings['Exercise'].dropna().unique().tolist()
    selected_exercise = st.selectbox("Wähle Übung", exercises)
    
    with st.form("log_form"):
        st.subheader(f"Training: {selected_exercise}")
        col1, col2, col3 = st.columns(3)
        
        weight = col1.number_input("KG", value=20.0, step=1.25)
        reps = col2.number_input("Reps", value=10, step=1)
        rir = col3.number_input("RIR", value=2, step=1)
        
        pain = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            new_data = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": selected_exercise,
                "Weight": weight,
                "Reps": reps,
                "RIR": rir,
                "Pain": pain
            }])
            
            # Update via gsheets connection
            updated_log = pd.concat([df_log, new_data], ignore_index=True)
            conn.update(worksheet="Log", data=updated_log)
            
            st.success("Erfolgreich gespeichert! 🎉")
            st.balloons()
else:
    st.warning("Keine Übungen gefunden. Prüfe, ob der Reiter 'Settings' heißt und eine Spalte 'Exercise' hat.")
