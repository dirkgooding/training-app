import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_gsheets import GSheetsConnection

# --- APP SETUP ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")
st.title("🏋️ Strong-Pain-Coach")

# Deine verifizierte ID
SHEET_ID = "1mOj0cocT5AD2FPPrgHrMosaG-p3BeX0Agmd0aoAhKEs"

# Verbindung initialisieren
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
def get_data():
    try:
        # Versuch, die Daten zu laden
        df_s = conn.read(worksheet="Settings", ttl=0)
        df_l = conn.read(worksheet="Log", ttl=0)
        return df_l, df_s, None
    except Exception as e:
        # Falls es schiefgeht: Testdaten als Fallback
        test_settings = pd.DataFrame({"Exercise": ["Kniebeugen", "Bankdrücken"]})
        return pd.DataFrame(), test_settings, str(e)

df_log, df_settings, error_msg = get_data()

# --- UI LOGIK ---
if error_msg:
    st.error(f"⚠️ Verbindungsproblem: {error_msg}")
    st.info("Wir nutzen gerade Test-Daten. Prüfe deine Secrets in Streamlit!")

if not df_settings.empty:
    exercise = st.selectbox("Wähle Übung", df_settings["Exercise"].tolist())
    
    with st.form("log_form"):
        col1, col2 = st.columns(2)
        w = col1.number_input("Gewicht (kg)", value=20.0, step=1.25)
        r = col2.number_input("Reps", value=10, step=1)
        p = st.select_slider("Schmerz (0=OK, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            st.success(f"Log-Versuch für {exercise}: {w}kg x {r}")
            # Hier versuchen wir zu speichern
            try:
                new_row = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Exercise": exercise, "Weight": w, "Reps": r, "Pain": p}])
                updated = pd.concat([df_log, new_row], ignore_index=True)
                conn.update(worksheet="Log", data=updated)
                st.balloons()
            except:
                st.warning("Speichern im Sheet fehlgeschlagen. Prüfe die Editor-Rechte!")
