import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Session State) ---
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
        woche = st.selectbox("📅 Woche:", [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)])
    with col_nav2:
        selected_day = st.selectbox("📋 Tag wählen:", list(st.session_state.my_plan.keys()))

    current_data = st.session_state.my_plan[selected_day]
    current_exercises = current_data["exercises"]
    num_sets = current_data["sets"] # Dynamische Anzahl der Sets

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

        # Nutzt jetzt die im Planer eingestellte Anzahl an Sets
        for s in range(1, num_sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[4].selectbox("p", [0, 1, 2], key=f"p_{ex}_{s}_{woche}", label_visibility="collapsed")
        st.divider()

# --- TAB 2: DER PLANER ---
with tab_plan:
    st.header("Konfiguration deines Trainings")
    
    st.subheader("📅 Zyklus-Dauer")
    new_weeks = st.number_input("Wie viele Wochen soll ein Zyklus dauern?", min_value=1, max_value=52, value=st.session_state.cycle_weeks)
    if new_weeks != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_weeks
        st.rerun()
    st.divider()

    st.info("Hier kannst du deine Tage benennen, Sätze festlegen und Übungen definieren.")

    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            # Tag umbenennen
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"rename_{day_key}")
            
            # NEU: Sätze für diesen Tag festlegen
            current_sets = st.session_state.my_plan[day_key]["sets"]
            new_sets = st.number_input(f"Anzahl Sätze pro Übung ({day_key}):", min_value=1, max_value=10, value=current_sets, key=f"sets_edit_{day_key}")
            
            # Übungen dieses Tages
            ex_list = st.session_state.my_plan[day_key]["exercises"]
            new_ex_str = st.text_area("Übungen (eine pro Zeile):", value="\
