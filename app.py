import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- SETUP ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# --- DATABASE SETUP (Lokal) ---
def init_db():
    conn = sqlite3.connect('training.db')
    c = conn.cursor()
    # Tabelle für das Log erstellen, falls sie nicht existiert
    c.execute('''CREATE TABLE IF NOT EXISTS log 
                 (date TEXT, exercise TEXT, weight REAL, reps INTEGER, rir INTEGER, pain INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- UI ---
st.title("🏋️ Strong-Pain-Coach (Lokal)")

# Da wir kein Google Sheet mehr haben, definieren wir die Übungen direkt hier im Code
exercises = ["Kniebeugen", "Bankdrücken", "Kreuzheben", "Tibialis Curl", "Beinstrecker"]
selected_exercise = st.selectbox("Wähle Übung", exercises)

with st.form("training_form"):
    col1, col2, col3 = st.columns(3)
    w = col1.number_input("KG", value=20.0, step=1.25)
    r = col2.number_input("Reps", value=10, step=1)
    rir = col3.number_input("RIR", value=2, step=1)
    
    p = st.select_slider("Schmerz (0=OK, 2=Stopp)", options=[0, 1, 2])
    
    if st.form_submit_button("Speichern"):
        conn = sqlite3.connect('training.db')
        c = conn.cursor()
        c.execute("INSERT INTO log VALUES (?, ?, ?, ?, ?, ?)", 
                  (datetime.now().strftime("%Y-%m-%d"), selected_exercise, w, r, rir, p))
        conn.commit()
        conn.close()
        st.success(f"Erfolgreich lokal gespeichert! 🎉")
        st.balloons()

# --- DATEN ANZEIGEN ---
if st.checkbox("Bisherige Trainings anzeigen"):
    conn = sqlite3.connect('training.db')
    df = pd.read_sql_query("SELECT * FROM log ORDER BY date DESC", conn)
    conn.close()
    st.dataframe(df)
