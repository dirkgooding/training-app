import streamlit as st
import pandas as pd

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide") # 'wide' für bessere Tabellen-Ansicht

# 1. DER TRAININGSPLAN
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"]
    }

st.title("🏋️ Trainings-Einheit")

# 2. TAG WÄHLEN
selected_day = st.selectbox("Welcher Tag steht an?", list(st.session_state.my_plan.keys()))
current_exercises = st.session_state.my_plan[selected_day]

st.markdown("---")

# 3. DAS DASHBOARD (Alles permanent sichtbar)
for i, ex in enumerate(current_exercises):
    # Container für jede Übung ohne Aufklapp-Funktion
    with st.container():
        col_header, col_move = st.columns([8, 2])
        
        with col_header:
            st.subheader(f"{i+1}. {ex}")
        
        with col_move:
            # Schnelle Sortierung
            up, down = st.columns(2)
            if up.button("▲", key=f"up_{ex}_{i}") and i > 0:
                current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
                st.rerun()
            if down.button("▼", key=f"down_{ex}_{i}") and i < len(current_exercises)-1:
                current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
                st.rerun()

        # Die Satz-Matrix (3 Sätze immer präsent)
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set")
        cols[1].caption("KG")
        cols[2].caption("Reps")
        cols[3].caption("RIR")
        cols[4].caption("Pain")

        for s in range(1, 4):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{
