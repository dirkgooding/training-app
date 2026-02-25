import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# --- 1. DER TRAININGSPLAN (Das Herzstück) ---
# Hier definieren wir, welche Übungen zu welchem Tag gehören
TRAINING_PLAN = {
    "Tag A (Unterkörper)": ["Kniebeugen", "Beinstrecker", "Wadenheben"],
    "Tag B (Oberkörper)": ["Bankdrücken", "Rudern", "Schulterdrücken"],
    "Tag C (Full Body)": ["Kreuzheben", "Klimmzüge", "Dips"]
}

st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")
st.title("🏋️ Dein Trainingsplan")

# --- 2. SESSION STARTEN ---
if 'active_session' not in st.session_state:
    selected_day = st.selectbox("Welchen Tag trainierst du heute?", list(TRAINING_PLAN.keys()))
    if st.button("Training starten"):
        st.session_state.active_session = selected_day
        st.session_state.current_exercise_idx = 0
        st.rerun()

# --- 3. DURCHFÜHRUNG ---
if 'active_session' in st.session_state:
    current_day = st.session_state.active_session
    exercises = TRAINING_PLAN[current_day]
    current_idx = st.session_state.current_exercise_idx
    
    if current_idx < len(exercises):
        current_ex = exercises[current_idx]
        st.subheader(f"Übung {current_idx + 1}/{len(exercises)}: {current_ex}")
        
        # Log-Bereich für diese spezifische Übung
        with st.form(f"form_{current_ex}"):
            col1, col2 = st.columns(2)
            w = col1.number_input("KG", value=20.0, step=1.25)
            r = col2.number_input("Reps", value=10, step=1)
            p = st.select_slider("Schmerz", options=[0, 1, 2])
            
            if st.form_submit_button("Satz beendet"):
                # (Hier käme der SQLite Speicher-Befehl hin)
                st.toast(f"Satz für {current_ex} gespeichert!")
        
        # Navigation zur nächsten Übung
        if st.button("Nächste Übung →"):
            st.session_state.current_exercise_idx += 1
            st.rerun()
    else:
        st.success("🎉 Training beendet!")
        if st.button("Session schließen"):
            del st.session_state.active_session
            st.rerun()
