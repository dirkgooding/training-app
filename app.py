import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Initialisierung) ---
# Struktur angepasst, um die Anzahl der Sätze pro Tag zu speichern
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A": {"exercises": ["Kniebeugen", "Bankdrücken"], "sets": 3},
        "Tag B": {"exercises": ["Kreuzheben", "Klimmzüge"], "sets": 3}
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 12

# --- NAVIGATION ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: DAS GYM-INTERFACE ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", wochen_liste)
    with col_nav2:
        selected_day = st.selectbox("📋 Tag wählen:", list(st.session_state.my_plan.keys()))

    # Sicherer Zugriff auf die Daten des gewählten Tages
    day_data = st.session_state.my_plan[selected_day]
    current_exercises = day_data["exercises"]
    num_sets = day_data["sets"] # Hier wird die Menge der Sätze abgerufen

    st.markdown(f"## {selected_day}")
    st.divider()

    for i, ex in enumerate(current_exercises):
        st.subheader(f"{i+1}. {ex}")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_val = st.session_state.device_settings.get(ex, "")
            st.session_state.device_settings[ex] = st.text_input(f"⚙️ Einstellung (fest)", value=old_val, key=f"dev_{ex}")
        with c_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{ex}_{woche}_{selected_day}")

        # Matrix Kopfzeile
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        # Dynamische Anzahl an Sätzen basierend auf der Einstellung im Planer
        for s in range
