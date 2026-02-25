import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSTRUKTUR INITIALISIEREN ---
# Jeder Tag ist eine Liste aus Dictionaries: [{"name": "Übung", "sets": 3}, ...]
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A": [
            {"name": "Kniebeugen", "sets": 3},
            {"name": "Bankdrücken", "sets": 3}
        ],
        "Tag B": [
            {"name": "Kreuzheben", "sets": 3},
            {"name": "Klimmzüge", "sets": 3}
        ]
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 12

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", wochen_liste)
    with col_nav2:
        selected_day = st.selectbox("📋 Tag wählen:", list(st.session_state.my_plan.keys()))

    current_exercises = st.session_state.my_plan[selected_day]
    st.markdown(f"## {selected_day}")
    st.divider()

    for i, ex_data in enumerate(current_exercises):
        name = ex_data["name"]
        sets = ex_data["sets"]
        
        st.subheader(f"{i+1}. {name}")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_val = st.session_state.device_settings.get(name, "")
            st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_val, key=f"dev_{name}_{selected_day}")
        with c_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{name}_{woche}_{selected_day}")

        # Matrix Header
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        # Matrix Zeilen (Individuell pro Übung)
        for s in range(1, sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1,
