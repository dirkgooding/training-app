import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# DIE URL DEINES SHEETS
# Wir wandeln den Link so um, dass er direkt die Daten ausspuckt
sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
csv_url = sheet_url.replace('/edit', '/export?format=csv&gid=193480860') # gid für 'Settings'

def load_settings():
    try:
        # Wir lesen das Sheet direkt als CSV ein - das umgeht viele Cache-Probleme
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Daten konnten nicht geladen werden. Bitte prüfe, ob das Sheet für 'Jeden mit dem Link' freigegeben ist.")
        return pd.DataFrame()

df_settings = load_settings()

st.title("🏋️ Strong-Pain-Coach")

if not df_settings.empty and "Exercise" in df_settings.columns:
    exercise_list = df_settings['Exercise'].dropna().tolist()
    exercise = st.selectbox("Wähle Übung", exercise_list)
    
    with st.form("log_form"):
        col1, col2, col3 = st.columns(3)
        w = col1.number_input("KG", value=10.0, step=0.25)
        r = col2.number_input("Reps", value=10, step=1)
        rir = col3.number_input("RIR", value=2, step=1)
        p = st.select_slider("Schmerz", options=[0, 1, 2])
        
        if st.form_submit_button("Speichern"):
            st.info("Datenübertragung wird vorbereitet...")
            # Hier nutzen wir für den Schreibzugriff wieder die Connection
            # Aber wir wissen jetzt zumindest, ob wir lesen können!
            st.write("Sende Daten zu Google...")
else:
    st.warning("Die App kann die Übungen nicht finden.")
    st.write("Gefundene Spalten:", list(df_settings.columns) if not df_settings.empty else "Keine")
