import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'my_plan' not in st.session_state:
    # Struktur jetzt: "sets" ist eine Liste, die so lang ist wie die Wochenanzahl
    st.session_state.my_plan = {
        "Tag A": [{"name": "Kniebeugen", "sets": [3, 3, 3, 3]}, {"name": "Bankdrücken", "sets": [3, 3, 3, 3]}],
    }

if 'training_logs' not in st.session_state:
    st.session_state.training_logs = {}

if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 4

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Excel-Export"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    wochen_idx = st.selectbox("📅 Woche wählen:", range(st.session_state.cycle_weeks), 
                              format_func=lambda x: f"Woche {x+1}")
    woche_label = f"Woche {wochen_idx + 1}"
    
    tag_namen = list(st.session_state.my_plan.keys())
    selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen)

    current_exercises = st.session_state.my_plan[selected_day]
    st.markdown(f"## {selected_day} - {woche_label}")

    for i, ex_data in enumerate(current_exercises):
        name = ex_data["name"]
        # Kern-Logik: Nimm die Satzanzahl spezifisch für die gewählte Woche
        # Falls die Liste zu kurz ist (wegen Zyklus-Änderung), nimm den letzten Wert
        sets_list = ex_data["sets"]
        current_sets = sets_list[wochen_idx] if wochen_idx < len(sets_list) else sets_list[-1]
        
        st.subheader(f"{i+1}. {name} ({current_sets} Sätze)")
        
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        for s in range(1, current_sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            log_key = f"{woche_label}_{selected_day}_{name}_{s}"
            current_log = st.session_state.training_logs.get(log_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
            
            res_kg = s_cols[1].number_input("kg", value=float(current_log["kg"]), step=1.25, key=f"w_{log_key}", label_visibility="collapsed")
            res_r = s_cols[2].number_input("r", value=int(current_log["r"]), step=1, key=f"r_{log_key}", label_visibility="collapsed")
            res_rir = s_cols[3].number_input("rir", value=int(current_log["rir"]), step=1, key=f"rir_{log_key}", label_visibility="collapsed")
            res_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(current_log["p"]), key=f"p_{log_key}", label_visibility="collapsed")
            st.session_state.training_logs[log_key] = {"kg": res_kg, "r": res_r, "rir": res_rir, "p": res_p}
        st.divider()

# --- TAB 2: PLANER (DIE NEUE WOCHENSTEUERUNG) ---
with tab_plan:
    st.header("⚙️ Trainingsplan-Konfiguration")
    
    new_cycle = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_cycle != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_cycle
        st.rerun()

    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"ren_{day_key}")
            
            current_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in current_ex_list])
            new_ex_names = st.text_area("Übungen (eine pro Zeile):", value=ex_names_only, key=f"edit_{day_key}")
            
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            updated_data = []
            
            for n in temp_names:
                st.markdown(f"**Satzplanung für: {n}**")
                # Finde alte Daten oder erstelle neue Liste mit Standard 3 Sätzen
                old_sets = [3] * st.session_state.cycle_weeks
                for old_ex in current_ex_list:
                    if old_ex["name"] == n:
                        old_sets = old_ex["sets"]
                
                # Dynamische Spalten für jede Woche
                week_cols = st.columns(st.session_state.cycle_weeks)
                new_sets_for_ex = []
                for w in range(st.session_state.cycle_weeks):
                    # Falls Zyklus verlängert wurde, nimm alten Wert oder 3
                    val = old_sets[w] if w < len(old_sets) else old_sets[-1]
                    s_val = week_cols[w].number_input(f"W{w+1}", min_value=1, max_value=10, value=int(val), key=f"s_{day_key}_{n}_{w}")
                    new_sets_for_ex.append(s_val)
                
                updated_data.append({"name": n, "sets": new_sets_for_ex})
                st.divider()
            
            if st.button("Speichern", key=f"btn_{day_key}"):
                if new_day_name != day_key: st.session_state.my_plan.pop(day_key)
                st.session_state.my_plan[new_day_name] = updated_data
                st.rerun()
