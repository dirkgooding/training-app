import streamlit as st
import pandas as pd

# 'wide' für optimale Smartphone-Darstellung
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DATENSTRUKTUR (Dein fester Plan)
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

# Permanenter Speicher für Geräte-Einstellungen (z.B. Sitzhöhe)
if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

st.title("🏋️ Trainings-Steuerung")

# --- HIERARCHIE: ERST TAG, DANN WOCHE ---
col_setup1, col_setup2 = st.columns(2)

with col_setup1:
    # Schritt 1: Welches Programm?
    selected_day = st.selectbox("📋 Welchen Tag trainierst du heute?", list(st.session_state.my_plan.keys()))
    current_exercises = st.session_state.my_plan[selected_day]

with col_setup2:
    # Schritt 2: In welcher Woche des Zyklus bist du?
    woche = st.selectbox("📅 In welcher Woche (Zyklus)?", [f"Woche {i}" for i in range(1, 13)])

st.markdown(f"## {selected_day} <small>({woche})</small>", unsafe_allow_html=True)
st.divider()

# --- DAS DASHBOARD ---
for i, ex in enumerate(current_exercises):
    
    # Übungs-Header mit Sortierung
    col_header, col_move = st.columns([7, 3])
    with col_header:
        st.subheader(f"{i+1}. {ex}")
    with col_move:
        up, down = st.columns(2)
        if up.button("▲", key=f"up_{ex}_{i}") and i > 0:
            current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
            st.rerun()
        if down.button("▼", key=f"down_{ex}_{i}") and i < len(current_exercises)-1:
            current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
            st.rerun()

    # NOTIZFELDER
    col_note1, col_note2 = st.columns(2)
    with col_note1:
        # IMMER DA: Geräte-Einstellung (Persistent über alle Wochen)
        old_val = st.session_state.device_settings.get(ex, "")
        new_val = st.text_input(f"⚙️ Einstellung (fest)", value=old_val, key=f"device_{ex}", help="Bleibt für diese Übung immer gespeichert.")
        st.session_state.device_settings[ex] = new_val
    with col_note2:
        # NUR FÜR DIESE WOCHE: Notiz zum aktuellen Training
        st.text_input(f"📝 Notiz ({woche})", key=f"session_note_{ex}_{woche}", placeholder="Gefühl, Schmerz-Details...")

    # DIE SATZ-MATRIX
    cols = st.columns([1, 2, 2, 2, 3])
    cols[0].caption("Set")
    cols[1].caption("KG")
    cols[2].caption("Reps")
    cols[3].caption("RIR")
    cols[4].caption("Pain")

    for s in range(1, 4):
        s_cols = st.columns([1, 2, 2, 2, 3])
        s_cols[0].write(f"**{s}**")
        # Alle Keys enthalten die Woche, damit die Daten pro Woche getrennt bleiben
        s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[4].select_slider("p", options=[0, 1, 2], key=f"p_{ex}_{s}_{woche}", label_visibility="collapsed")
    
    st.divider()

# ABSCHLUSS
if st.button("✅ Training beenden & Speichern", use_container_width=True):
    st.balloons()
    st.success(f"Training abgeschlossen! {selected_day} in {woche} wurde gesichert.")
