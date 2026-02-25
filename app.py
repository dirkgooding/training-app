import streamlit as st
import pandas as pd

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DATENSTRUKTUR (Planung & Persistenz)
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

# Speicher für Geräte-Einstellungen (bleibt immer gleich)
if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

st.title("🏋️ Trainings-Dashboard")

# --- OBERSTE EBENE: DIE WOCHE ---
col_w1, col_w2 = st.columns(2)
with col_w1:
    woche = st.selectbox("📅 Trainingswoche", [f"Woche {i}" for i in range(1, 9)])
with col_w2:
    selected_day = st.selectbox("📋 Trainingstag", list(st.session_state.my_plan.keys()))

current_exercises = st.session_state.my_plan[selected_day]

st.markdown(f"### {woche} - {selected_day}")
st.divider()

# --- DAS DASHBOARD ---
for i, ex in enumerate(current_exercises):
    
    # Header & Sortierung
    col_header, col_move = st.columns([7, 3])
    with col_header:
        st.subheader(f"{i+1}. {ex}")
    with col_move:
        up_col, down_col = st.columns(2)
        if up_col.button("▲", key=f"btn_up_{i}") and i > 0:
            current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
            st.rerun()
        if down_col.button("▼", key=f"btn_down_{i}") and i < len(current_exercises)-1:
            current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
            st.rerun()

    # --- DIE ZWEI NOTIZFELDER ---
    col_note1, col_note2 = st.columns(2)
    with col_note1:
        # Persistente Einstellung (Gerät)
        old_setting = st.session_state.device_settings.get(ex, "")
        new_setting = st.text_input(f"⚙️ Geräte-Einstellung ({ex})", value=old_setting, key=f"device_{ex}")
        st.session_state.device_settings[ex] = new_setting
    with col_note2:
        # Session Notiz (nur für heute)
        st.text_input(f"📝 Notiz für heute", key=f"note_today_{ex}_{woche}")

    # --- DIE SATZ-MATRIX ---
    cols = st.columns([1, 2, 2, 2, 3])
    cols[0].write("**Set**")
    cols[1].write("**KG**")
    cols[2].write("**Reps**")
    cols[3].write("**RIR**")
    cols[4].write("**Pain**")

    for s in range(1, 4):
        s_cols = st.columns([1, 2, 2, 2, 3])
        s_cols[0].write(f"#{s}")
        s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[4].select_slider("p", options=[0, 1, 2], key=f"p_{ex}_{s}_{woche}", label_visibility="collapsed")
    
    st.divider()

# Abschluss
if st.button("✅ Training beenden & Woche speichern", use_container_width=True):
    st.balloons()
    st.success(f"{selected_day} der {woche} wurde erfolgreich geloggt!")
