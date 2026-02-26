import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Strong Pain Coach", layout="wide")

# --- INITIALIZATION ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4

# Standard-Logik für Expert Matrix (wird für die Initialisierung genutzt)
def_prog_expert = {
    "type": "Expert Matrix", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "min_reps": 8, "max_reps": 12, "glob_sets": 3, "glob_reps": 10
}

# WIEDERHERSTELLUNG DER GEWÜNSCHTEN STRUKTUR (Fixiert)
if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [
            {"name": "Test 1", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog_expert.copy()}, 
            {"name": "Test 2", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog_expert.copy()}
        ], 
        "Day 2": [
            {"name": "Test 3", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog_expert.copy()}, 
            {"name": "Test 4", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog_expert.copy()}
        ]
    }

if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan, tab_data, tab_calendar = st.tabs(["Training", "Planner", "Data", "History"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("Select Week:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Week {x+1}")
        w_label = f"Week {w_idx + 1}"
    with col_nav2:
        selected_day = st.selectbox("Select Day:", options=list(st.session_state.my_plan.keys()))

    if selected_day in st.session_state.my_plan:
        for i, ex in enumerate(st.session_state.my_plan[selected_day]):
            c_sets = ex["sets"][w_idx] if w_idx < len(ex["sets"]) else ex["sets"][-1]
            c_reps = ex["reps"][w_idx] if w_idx < len(ex["reps"]) else ex["reps"][-1]
            unit = "Sec" if "Time" in ex["progression"]["type"] else "Reps"
            
            st.subheader(f"{i+1}. {ex['name']} ({c_sets} Sets | Goal: {c_reps} {unit})")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.session_state.device_settings[ex['name']] = st.text_input(f"Setup {ex['name']}", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2:
                st.text_input(f"Note {ex['name']}", key=f"note_{ex['name']}_{w_label}_{selected_day}")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3, 1])
                l_key = f"{w_label}_{selected_day}_{ex['name']}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": c_reps, "rir": 2, "p": 0, "done": False, "ts": ""})
                
                r_kg = s_cols[1].number_input("W", value=float(cur_l["kg"]), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("R", value=int(cur_l["r"]), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("RIR", value=int(cur_l["rir"]), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("P", options=[0, 1, 2], index=int(cur_l["p"]), key=f"p_in_{l_key}", label_visibility="collapsed")
                r_done = s_cols[5].checkbox("D", value=cur_l["done"], key=f"done_in_{l_key}", label_visibility="collapsed")
                
                ts = datetime.now().strftime("%Y-%m-%d %H:%M") if r_done and not cur_l["done"] else (cur_l["ts"] if r_done else "")
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p, "done": r_done, "ts": ts}
            st.divider()

# --- TAB 2: PLANNER ---
with tab_plan:
    st.header("Cycle Configuration")
    st.session_state.cycle_weeks = st.number_input("Cycle Duration (Weeks):", 1, 12, st.session_state.cycle_weeks)

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit Day: {d_key}", expanded=True):
            col_d1, col_d2 = st.columns([3, 1])
            new_dn = col_d1.text_input("Rename Day", d_key, key=f"ren_{d_key}")
            if col_d2.button("🗑️ Delete Day", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

            if new_dn != d_key and new_dn.strip() != "":
                st.session_state.my_plan[new_dn] = st.session_state.my_plan.pop(d_key)
                st.rerun()
            
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises (one per line):", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                st.markdown(f"#### 🏋️ {n}")
                match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                o_prog = match["progression"].copy() if match else def_prog_expert.copy()
                
                prog_options = ["Linear Weight", "Linear Reps", "Linear Time", "Double Progression", "Expert Matrix"]
                p_type = st.selectbox("Model", prog_options, index=prog_options.index(o_prog["type"]) if o_prog["type"] in prog_options else 4, key=f"ptype_{d_key}_{n}")
                
                n_sets, n_reps = [], []
                
                if p_type == "Expert Matrix":
                    st.caption("Weekly Volume Matrix")
                    h_cols = st.columns(st.session_state.cycle_weeks)
                    w_cols = st.columns(st.session_state.cycle_weeks)
                    for w in range(st.session_state.cycle_weeks):
                        h_cols[w].markdown(f"<center><b>W{w+1}</b></center>", unsafe_allow_html=True)
                        old_s = match["sets"][w] if (match and w < len(match["sets"])) else 3
                        old_r = match["reps"][w] if (match and w < len(match["reps"])) else 10
                        s_v = w_cols[w].number_input(f"S", 1, 15, int(old_s), key=f"es_{d_key}_{n}_{w}", label_visibility="collapsed")
                        r_v = w_cols[w].number_input(f"G", 1, 300, int(old_r), key=f"er_{d_key}_{n}_{w}", label_visibility="collapsed")
                        n_sets.append(s_v); n_reps.append(r_v)
                else:
                    c1, c2, c3 = st.columns(3)
                    g_s = c1.number_input("Sets (Cycle Default)", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                    if p_type == "Double Progression":
                        o_prog["min_reps"] = c2.number_input("Minimum Reps", 1, 300, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{n}")
                        o_prog["max_reps"] = c3.number_input("Maximum Reps", 1, 300, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{n}")
                        n_reps = [o_prog["max_reps"]] * st.session_state.cycle_weeks
                    else:
                        unit_label = "Goal (Seconds)" if "Time" in p_type else "Goal (Reps)"
                        o_prog["glob_reps"] = c2.number_input(unit_label, 1, 300, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{n}")
                        n_reps = [o_prog["glob_reps"]] * st.session_state.cycle_weeks
                    n_sets = [g_s] * st.session_state.cycle_weeks
                    o_prog["glob_sets"] = g_s

                with st.expander("⚙️ Logic & Increments"):
                    l1, l2 = st.columns(2)
                    if any(x in p_type for x in ["Weight", "Double", "Expert"]): 
                        o_prog["inc_weight"] = l1.number_input("Weight added after Success", 0.0, 50.0, float(o_prog.get("inc_weight", 1.25)), 1.25, key=f"iw_{d_key}_{n}")
                    if "Reps" in p_type: 
                        o_prog["inc_reps"] = l1.number_input("Reps added after Success", 0, 20, int(o_prog.get("inc_reps", 1)), 1, key=f"ir_{d_key}_{n}")
                    if "Time" in p_type: 
                        o_prog["inc_sec"] = l1.number_input("Seconds added after Success", 0, 100, int(o_prog.get("inc_sec", 5)), 1, key=f"is_{d_key}_{n}")
                    
                    o_prog["freq_inc"] = l2.number_input("Successful Weeks until Increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = l2.number_input("Failed Weeks until Deload", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fd_{d_key}_{n}")

                o_prog["type"] = p_type
                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            st.session_state.my_plan[d_key] = upd_data
