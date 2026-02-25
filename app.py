import streamlit as st
import json
import os

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# Name der Speicherdatei
DB_FILE = "trainingsplan.json"

# --- SPEICHER-FUNKTIONEN ---
def save_data():
    data = {
        "my_plan": st.session_state.my_plan,
        "cycle_weeks": st.session_state.cycle_weeks,
        "device_settings": st.session_state.device_settings
    }
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_data():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                st.session_state.my_plan = data.get("my_plan", {})
                st.session_state.cycle_weeks = data.get("cycle_weeks", 12)
                st.session_state.device_settings = data.get("device_settings", {})
            return True
        except Exception:
            return False
    return False

# --- INITIALISIERUNG ---
if 'my_plan' not in st.session_state:
    if not load_data():
        # Fallback-Daten, falls keine Datei existiert
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
        st.session_state.device_settings = {}
        st.session_state.cycle_weeks = 12

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", options=wochen_liste, key="select_woche")
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen, key="select_tag")

    if selected_day in st.session_state.my_plan:
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

            # Matrix Zeilen
            for s in range(1, sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[2].number_input("r", value=10, step=1, key=f"r_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[4].selectbox("p", options=[0, 1, 2], key=f"p_{name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            st.divider()
    else:
        st.warning("Bitte wähle einen gültigen Tag im Planer aus.")

# --- TAB 2: PLANER ---
with tab_plan:
    st.header("Konfiguration")
    
    # Master-Speicher-Button
    if st.button("💾 PLAN DAUERHAFT SPEICHERN", use_container_width=True, type="primary"):
        save_data()
        st.success(f"Erfolgreich in '{DB_FILE}' gespeichert!")

    st.divider()
    
    new_cycle = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=52, value=st.session_state.cycle_weeks, key="cycle_input")
    if new_cycle != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_cycle
        st.rerun()
    
    st.divider()

    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=False):
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"rename_{day_key}")
            
            current_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in current_ex_list])
            new_ex_names = st.text_area("Übungen (eine pro Zeile):", value=ex_names_only, key=f"ex_edit_{day_key}")
            
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            updated_data = []
            
            st.write("**Individuelle Sätze pro Übung:**")
            for n in temp_names:
                default_s = 3
                for old_ex in current_ex_list:
                    if old_ex["name"] == n:
                        default_s = old_ex["sets"]
                
                s_val = st.number_input(f"Sätze für {n}:", min_value=1, max_value=15, value=int(default_s), key=f"s_edit_{day_key}_{n}")
                updated_data.append({"name": n, "sets": s_val})
            
            c_save, c_del = st.columns(2)
            if c_save.button(f"Übernehmen", key=f"save_btn_{day_key}"):
                if new_day_name != day_key:
                    st.session_state.my_plan.pop(day_key)
                st.session_state.my_plan[new_day_name] = updated_data
                st.rerun()
                
            if c_del.button(f"🗑️ Tag löschen", key=f"del_btn_{day_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(day_key)
                    st.rerun()
                else:
                    st.error("Mindestens ein Tag muss bestehen bleiben.")

    st.divider()
    if st.button("➕ Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Übung 1", "sets": 3}]
        st.rerun()
