import streamlit as st
import pandas as pd

# 'wide' sorgt dafür, dass die Zeilen auf dem Handy nicht zu schmal werden
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DEIN TRAININGSPLAN (Das Herzstück)
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

st.title("🏋️ Trainings-Einheit")

# 2. TAG WÄHLEN
selected_day = st.selectbox("Welcher Tag steht an?", list(st.session_state.my_plan.keys()))
current_exercises = st.session_state.my_plan[selected_day]

st.markdown("---")

# 3. DAS DASHBOARD (Alles permanent offen)
# Wir nutzen ein Formular für die GESAMTE Seite, damit du am Ende alles mit einem Klick speicherst
with st.form("overall_workout"):
    
    for i, ex in enumerate(current_exercises):
        # Header für die Übung mit Sortier-Buttons daneben
        col_header, col_move = st.columns([7, 3])
        
        with col_header:
            st.subheader(f"{i+1}. {ex}")
        
        with col_move:
            up, down = st.columns(2)
            # Buttons zum Verschieben der Reihenfolge
            if up.form_submit_button("▲"):
                if i > 0:
                    current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
                    st.rerun()
            if down.form_submit_button("▼"):
                if i
