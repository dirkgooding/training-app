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

# --- TABS FÜR DIE TRENNUNG ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer"])

# --- TAB 1: DAS TRAINING (Deine Basis) ---
with tab_train:
    st.title("🏋️ Trainings-Steuerung")

    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        woche = st.selectbox("📅 Wähle die Woche:", options=[f"Woche {i}" for i in range(1, 13)], index=0)
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
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
            s_cols[4].selectbox("p", options=[0, 1, 2], key=f"p_{ex}_{s}_{woche}", label_visibility="collapsed", format_func=lambda x: f"Schmerz: {x}")
        st.divider()

    if st.button("✅ Trainingstag abschließen", use_container_width=True):
        st.balloons()
        st.success(f"Daten für {selected_day} ({woche}) gesichert!")

# --- TAB 2: DER PLANER (Neu ausgelagert) ---
with tab_plan:
    st.header("⚙️ Trainingsplan-Konfiguration")
    st.write("Hier kannst du deine Tage umbenennen und die Übungen anpassen.")
    
    # Bearbeitung der bestehenden Tage
    for day_name in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_name}"):
            # Name ändern
            new_name = st.text_input("Name des Tages", value=day_name, key=f"edit_name_{day_name}")
            
            # Übungen ändern
            current_exs = st.session_state.my_plan[day_name]
            new_exs_text = st.text_area("Übungen (eine pro Zeile)", value="\n".join(current_exs), key=f"edit_exs_{day_name}")
            
            if st.button("Speichern", key=f"save_{day_name}"):
                # Update Plan
                updated_exs = [e.strip() for e in new_exs_text.split("\n") if e.strip()]
                # Falls Name geändert wurde: Alten Eintrag löschen, neuen hinzufügen
                if new_name != day_name:
                    del st.session_state.my_plan[day_name]
                st.session_state.my_plan[new_name] = updated_exs
                st.rerun()
    
    st.divider()
    if st.button("➕ Neuen Tag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = ["Übung 1"]
        st.rerun()
