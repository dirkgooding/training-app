import streamlit as st

# 'wide' für optimale Smartphone-Darstellung
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Initialisierung) ---
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

# Neu: Einstellbare Zyklus-Dauer (Standard 12)
if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 12

# --- TABS FÜR DIE TRENNUNG ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer"])

# --- TAB 1: DAS TRAINING (Deine gewohnte Basis) ---
with tab_train:
    st.title("🏋️ Trainings-Steuerung")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        # Dynamische Wochenanzahl basierend auf Planer-Einstellung
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Wähle die Woche:", options=wochen_liste, index=0)
    with col_nav2:
        selected_day = st.selectbox("📋 Welchen Tag heute?", options=list(st.session_state.my_plan.keys()), index=0)

    st.markdown(f"## {selected_day} <small>({woche})</small>", unsafe_allow_html=True)
    st.divider()

    current_exercises = st.session_state.my_plan[selected_day]

    for i, ex in enumerate(current_exercises):
        col_h, col_m = st.columns([8, 2])
