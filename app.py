import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Session State) ---
# Wir passen die Struktur minimal an, um die Anzahl der Sätze pro Tag zu speichern
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

    # Daten für den gewählten Tag abrufen
    day_data = st.session_state.my_plan[selected_day]
    current_exercises = day_data["exercises"]
    num_sets = day_data["sets"]

    st.markdown(f"## {selected_day}")
    st.divider()

    for i, ex in enumerate(current_exercises):
        st.subheader(f"{i+1}. {ex}")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_val = st.session_state.device_settings.get(ex, "")
            st.session_state.device_settings[ex] = st.text_input(f"⚙️ Einstellung (fest)", value=old_val, key=f"dev_{ex}")
        with c_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{ex}_{woche}")

        # Matrix
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        for s in range(1, num_sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[4].selectbox("p", [0, 1, 2], key=f"p_{ex}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
        st.divider()

# --- TAB 2: DER PLANER ---
with tab_plan:
    st.header("Konfiguration deines Trainings")
    
    st.subheader("📅 Zyklus-Dauer")
    new_weeks = st.number_input("Wie viele Wochen soll ein Zyklus dauern?", min_value=1, max_value=52, value=st.session_state.cycle_weeks)
    if new_weeks != st.session_state.cycle_weeks
