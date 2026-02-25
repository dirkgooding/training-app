import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'my_plan' not in st.session_state: st.session_state.my_plan = {"Tag 1": [{"name": "Test 1", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}, {"name": "Test 2", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}], "Tag 2": [{"name": "Test 3", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}, {"name": "Test 4", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}]}
if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan, tab_data, tab_calendar = st.tabs(["Training", "Planer", "Daten-Verwaltung", "Historie"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("Woche wählen:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Woche {x+1}")
        w_label = f"Woche {w_idx + 1}"
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("Tag wählen:", options=tag_namen)

    if selected_day in st.session_state.my_plan:
        current_exercises = st.session_state.my_plan[selected_day]
        st.markdown(f"## {selected_day} - {w_label}")
        st.divider()

        for i, ex_data in enumerate(current_exercises):
            name = ex_data["name"]
            sets_list = ex_data.get("sets", [3] * st.session_state.cycle_weeks)
            reps_list = ex_data.get("reps", [10] * st.session_state.cycle_weeks)
            
            if not isinstance(sets_list, list): sets_list = [sets_list] * st.session_state.cycle_weeks
            if not isinstance(reps_list, list): reps_list = [reps_list] * st.session_state.cycle_weeks
            
            c_sets = sets_list[w_idx] if w_idx < len(sets_list) else sets_list[-1]
            c_reps = reps_list[w_idx] if w_idx < len(reps_list) else reps_list[-1]
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sätze | Ziel: {c_reps} Reps)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"Notiz", key=f"note_{name}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": c_reps, "rir": 2, "p": 0})
                
                r_kg = s_cols[1].number_input("kg", value=float(cur_l.get("kg", 20.0)), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("r", value=int(cur_l.get("r", c_reps)), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("rir", value=int(cur_l.get("rir", 2)), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(cur_l.get("p", 0)), key=f"p_in_{l_key}", label_visibility="collapsed")
                
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p}
            st.divider()

# --- TAB 2: PLANER ---
with tab_plan:
    st.header("Konfiguration")
    
    new_w = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {d_key}", expanded=True):
            new_name = st.text_input("Name des Tages:", value=d_key, key=f"ren_{d_key}")
            
            # Auto-Save für den Namen (lädt die Seite sofort neu)
            if new_name != d_key and new_name.strip() != "":
                st.session_state.my_plan[new_name] = st.session_state.my_plan.pop(d_key)
                st.rerun()
                
            cur_exs = st.session_state.my_plan[d_key]
            ex_txt = "\n".join([e["name"] for e in cur_exs])
            new_ex_txt = st.text_area("Übungen (eine pro Zeile):", value=ex_txt, key=f"edit_{d_key}")
            
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            upd_data = []
            
            for n in names:
                st.write(f"**Sätze & Reps für: {n}**")
                o_sets = [3] * st.session_state.cycle_weeks
                o_reps = [10] * st.session_state.cycle_weeks
                for e in cur_exs:
                    if e["name"] == n:
                        if "sets" in e and isinstance(e["sets"], list): o_sets = e["sets"]
                        elif "sets" in e: o_sets = [e["sets"]] * st.session_state.cycle_weeks
                        if "reps" in e and isinstance(e["reps"], list): o_reps = e["reps"]
                        elif "reps" in e: o_reps = [e["reps"]] * st.session_state.cycle_weeks
                
                w_cols = st.columns(st.session_state.cycle_weeks)
                n_sets = []
                n_reps = []
                for w in range(st.session_state.cycle_weeks):
                    v_s = o_sets[w] if w < len(o_sets) else o_sets[-1]
                    v_r = o_reps[w] if w < len(o_reps) else
