import streamlit as st

st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- 1. DATENSPEICHERUNG (Initialisierung) ---
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

# --- NAVIGATION ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: DAS TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", options=wochen_liste)
    with col_nav2:
        selected_day = st.selectbox("📋 Tag wählen:", options=list(st.session_state.my_plan.keys()))

    current_exercises = st.session_state.my_plan[selected_day]
    st.markdown(f"## {selected_day}")
    st.divider()

    for i, ex_data in enumerate(current_exercises):
        name = ex_data["name"]
        sets = int(ex_data["sets"])
        
        st.subheader(f"{i+1}. {name}")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_val = st.session_state.device_settings.get(name, "")
            st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_val, key=f"dev_{name}_{selected_day}")
        with c_n2:
            st.text_input(f"📝 Notiz {woche}", key=f"note_{name}_{woche}_{selected_day}")

        # Matrix Kopfzeile
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set")
        cols[1].caption("KG")
        cols[2].caption("Reps")
        cols[3].caption("RIR")
        cols[4].caption("Pain")

        # Dynamische Sätze pro Übung
        for s in range(1, sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[2].number_input("r", value=10, step=1, key=f"r_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            s_cols[4].selectbox("p", options=[0, 1, 2], key=f"p_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
        st.divider()

# --- TAB 2: DER PLANER ---
with tab_plan:
    st.header("Konfiguration")
    
    # Zyklus-Dauer
    new_cycle = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=52, value=st.session_state.cycle_weeks)
    if new_cycle != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_cycle
        st.rerun()
    
    st.divider()

    # Tage verwalten
    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"rename_{day_key}")
            
            # Übungen als Text laden
            current_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in current_ex_list])
            new_ex_names = st.text_area("Übungen (eine pro Zeile):", value=ex_names_only, key=f"ex_edit_{day_key}")
            
            # Übungsnamen verarbeiten
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            
            # Sätze für jede Übung einzeln festlegen
            updated_data = []
            st.write("**Sätze festlegen:**")
            for n in temp_names:
                # Alten Wert suchen oder Standard 3 setzen
                val_s = 3
                for old_ex in current_ex_list:
                    if old_ex["name"] == n:
                        val_s = old_ex["sets"]
                
                s_count = st.number_input(f"Sätze für {n}:", min_value=1, max_value=15, value=int(val_s), key=f"s_edit_{day_key}_{n}")
                updated_data.append({"name": n, "sets": s_count})
            
            c_save, c_del = st.columns(2)
            with c_save:
                if st.button(f"Speichern", key=f"save_btn_{day_key}"):
                    if new_day_name != day_key:
                        st.session_state.my_plan.pop(day_key)
                    st.session_state.my_plan[new_day_name] = updated_data
                    st.rerun()
            with col_del:
                if st.button(f"🗑️ Tag löschen", key=f"del_btn_{day_key}"):
                    st.session_state.my_plan.pop(day_key)
                    st.rerun()

    st.divider()
    if st.button("➕ Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Übung 1", "sets": 3}]
        st.rerun()
