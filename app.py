import streamlit as st
import pandas as pd
import json

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A": [{"name": "Kniebeugen", "sets": [3, 3, 3, 3]}, {"name": "Bankdrücken", "sets": [3, 3, 3, 3]}],
        "Tag B": [{"name": "Kreuzheben", "sets": [3, 3, 3, 3]}, {"name": "Klimmzüge", "sets": [3, 3, 3, 3]}]
    }

if 'training_logs' not in st.session_state:
    st.session_state.training_logs = {}

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 4

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Excel-Export"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_idx = st.selectbox("📅 Woche wählen:", range(st.session_state.cycle_weeks), 
                                  format_func=lambda x: f"Woche {x+1}")
        woche_label = f"Woche {wochen_idx + 1}"
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen)

    if selected_day in st.session_state.my_plan:
        current_exercises = st.session_state.my_plan[selected_day]
        st.markdown(f"## {selected_day} - {woche_label}")
        st.divider()

        for i, ex_data in enumerate(current_exercises):
            name = ex_data["name"]
            sets_list = ex_data["sets"]
            # Sicherstellung, dass die Liste lang genug ist
            current_sets = sets_list[wochen_idx] if wochen_idx < len(sets_list) else sets_list[-1]
            
            st.subheader(f"{i+1}. {name} ({current_sets} Sätze)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"📝 Notiz", key=f"note_{name}_{woche_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

            for s in range(1, current_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                log_key = f"{woche_label}_{selected_day}_{name}_{s}"
                cur_log = st.session_state.training_logs.get(log_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
                
                res_kg = s_cols[1].number_input("kg", value=float(cur_log["kg"]), step=1.25, key=f"w_{log_key}", label_visibility="collapsed")
                res_r = s_cols[2].number_input("r", value=int(cur_log["r"]), step=1, key=f"r_{log_key}", label_visibility="collapsed")
                res_rir = s_cols[3].number_input("rir", value=int(cur_log["rir"]), step=1, key=f"rir_{log_key}", label_visibility="collapsed")
                res_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(cur_log["p"]), key=f"p_{log_key}", label_visibility="collapsed")
                st.session_state.training_logs[log_key] = {"kg": res_kg, "r": res_r, "rir": res_rir, "p": res_p}
            st.divider()

# --- TAB 2: PLANER (VOLLSTÄNDIG) ---
with tab_plan:
    st.header("📊 Daten-Verwaltung")
    # CSV Export
    if st.session_state.training_logs:
        export_list = []
        for k, v in st.session_state.training_logs.items():
            p = k.split("_")
            if len(p) >= 4:
                export_list.append({"Woche": p[0], "Tag": p[1], "Übung": p[2], "Satz": p[3], "KG": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        csv = pd.DataFrame(export_list).to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button("📥 Excel-Export (CSV)", data=csv, file_name="training.csv", mime="text/csv")

    st.divider()
    st.header("⚙️ Konfiguration")
    
    new_c = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_c != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_c
        st.rerun()

    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"ren_{day_key}")
            
            cur_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in cur_ex_list])
            new_ex_names = st.text_area("Übungen (eine pro Zeile):", value=ex_names_only, key=f"edit_{day_key}")
            
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            updated_data = []
            
            for n in temp_names:
                st.write(f"**Sätze pro Woche für: {n}**")
                # Finde vorhandene Satz-Liste oder erstelle neue
                old_sets = [3] * st.session_state.cycle_weeks
                for old_ex in cur_ex_list:
                    if old_ex["name"] == n:
                        old_sets = old_ex["sets"]
                
                # Spalten für jede Woche
                w_cols = st.columns(st.session_state.cycle_weeks)
                new_sets_list = []
                for w in range(st.session_state.cycle_weeks):
                    val = old_sets[w] if w < len(old_sets) else old_sets[-1]
                    s_val = w_cols[w].number_input(f"W{w+1}", 1, 10, int(val), key=f"s_{day_key}_{n}_{w}")
                    new_sets_list.append(s_val)
                
                updated_data.append({"name": n
