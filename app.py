import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Session State) ---
# Wir initialisieren den Plan, falls er noch nicht existiert
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A": ["Kniebeugen", "Bankdrücken"],
        "Tag B": ["Kreuzheben", "Klimmzüge"]
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

# --- NAVIGATION ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: DAS GYM-INTERFACE (Dein aktueller Aufbau) ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        woche = st.selectbox("📅 Woche:", [f"Woche {i}" for i in range(1, 13)])
    with col_nav2:
        # Hier nutzen wir die Namen aus dem Planer
        selected_day = st.selectbox("📋 Tag wählen:", list(st.session_state.my_plan.keys()))

    current_exercises = st.session_state.my_plan[selected_day]
    st.markdown(f"## {selected_day}")
    st.divider()

    for i, ex in enumerate(current_exercises):
        st.subheader(f"{i+1}. {ex}")
        
        # Notizfelder
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_val = st.session_state.device_settings.get(ex, "")
            st.session_state.device_settings[ex] = st.text_input(f"⚙️ Einstellung (fest)", value=old_val, key=f"dev_{ex}")
        with c_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{ex}_{woche}")

        # Matrix
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        for s in range(1, 4):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[4].selectbox("p", [0, 1, 2], key=f"p_{ex}_{s}_{woche}", label_visibility="collapsed")
        st.divider()

# --- TAB 2: DER PLANER (Hier definierst du alles) ---
with tab_plan:
    st.header("Konfiguration deines Trainings")
    st.info("Hier kannst du deine Tage benennen und festlegen, welche Übungen du machst.")

    # 1. Tage verwalten
    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            # Tag umbenennen
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"rename_{day_key}")
            
            # Übungen dieses Tages (als kommagetrennte Liste zum schnellen Ändern)
            ex_list = st.session_state.my_plan[day_key]
            new_ex_str = st.text_area("Übungen (eine pro Zeile):", value="\n".join(ex_list), key=f"ex_edit_{day_key}")
            
            # Speichern-Logik für diesen Tag
            if st.button(f"Änderungen für {day_key} übernehmen"):
                # Alten Key löschen, neuen anlegen
                del st.session_state.my_plan[day_key]
                st.session_state.my_plan[new_day_name] = [e.strip() for e in new_ex_str.split("\n") if e.strip()]
                st.rerun()

    st.divider()
    if st.button("➕ Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = ["Übung 1"]
        st.rerun()
