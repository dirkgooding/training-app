import streamlit as st

# 'wide' für optimale Smartphone-Darstellung
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Session State) ---
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

# Neu: Einstellung für die Anzahl der Wochen (Standard: 12)
if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 12

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer"])

# --- TAB 1: DAS TRAINING ---
with tab_train:
    st.title("🏋️ Trainings-Steuerung")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        # Die Wochen-Optionen passen sich jetzt dynamisch an den Planer an
        wochen_options = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Wähle die Woche:", options=wochen_options, index=0)
    with col_nav2:
        selected_day = st.selectbox("📋 Welchen Tag heute?", options=list(st.session_state.my_plan.keys()), index=0)

    st.markdown(f"## {selected_day} <small>({woche})</small>", unsafe_allow_html=True)
    st.divider()

    current_exercises = st.session_state.my_plan[selected_day]

    for i, ex in enumerate(current_exercises):
        col_h, col_m = st.columns([8, 2])
        col_h.subheader(f"{i+1}. {ex}")
        
        with col_m:
            up, down = st.columns(2)
            if up.button("▲", key=f"up_{ex}_{i}") and i > 0:
                current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
                st.rerun()
            if down.button("▼", key=f"down_{ex}_{i}") and i < len(current_exercises)-1:
                current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
                st.rerun()

        col_n1, col_n2 = st.columns(2)
        with col_n1:
            old_val = st.session_state.device_settings.get(ex, "")
            st.session_state.device_settings[ex] = st.text_input(f"⚙️ Einstellung (fest)", value=old_val, key=f"dev_{ex}")
        with col_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{ex}_{woche}")

        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        for s in range(1, 4):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25
