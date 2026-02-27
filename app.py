import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Strong Pain Coach", layout="wide")

# --- INITIALIZATION ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'deload_strategy' not in st.session_state: st.session_state.deload_strategy = "No automatic deload"
if 'deload_intensity' not in st.session_state: st.session_state.deload_intensity = 50
if 'reduce_sets_deload' not in st.session_state: st.session_state.reduce_sets_deload = False
if 'rest_defaults' not in st.session_state: st.session_state.rest_defaults = {}

# Standard Progression Templates
def_prog_weight = {
    "type": "Linear Weight", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "min_reps": 8, "max_reps": 12, "glob_sets": 3, "glob_reps": 10,
    "start_weight": 20.0
}

def_prog_reps = {**def_prog_weight, "type": "Linear Reps", "inc_weight": 1.0, "start_reps": 8}
def_prog_time = {**def_prog_weight, "type": "Linear Time", "inc_weight": 5.0, "start_time": 30}
def_prog_double = {**def_prog_weight, "type": "Double Progression"}
def_prog_expert = {**def_prog_weight, "type": "Expert Mode"} 

# Initialize plan with test exercises
if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [
            {"name": "Linear Weight Exercise", "sets": [3]*12, "reps": [10]*12, "progression": def_prog_weight.copy()}, 
            {"name": "Linear Reps Exercise", "sets": [3]*12, "reps": [8]*12, "progression": def_prog_reps.copy()}
        ], 
        "Day 2": [
            {"name": "Linear Time Exercise", "sets": [3]*12, "reps": [30]*12, "progression": def_prog_time.copy()}, 
            {"name": "Double Progression Exercise", "sets": [3]*12, "reps": [12]*12, "progression": def_prog_double.copy()}
        ]
    }

if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- WARMUP INITIALIZATION ---
if "warmup_routines" not in st.session_state:
    st.session_state.warmup_routines = {
        "Standard Warmup": [
            {"percent": 50, "reps": 10},
            {"percent": 70, "reps": 5},
            {"percent": 90, "reps": 2},
        ]
    }

# --- TABS ---
tab_work, tab_prog, tab_progr, tab_pain, tab_warm, tab_rest, tab_data, tab_hist = st.tabs([
    "Workouts", "Program", "Progression", "Pain Management", "Warmups", "Rest Timer", "Data", "History"
])

# --- TAB 1: WORKOUTS ---
with tab_work:
    c_nav1, c_nav2 = st.columns(2)
    with c_nav1:
        w_idx = st.selectbox("Select Week:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Week {x+1}")
        w_label = f"Week {w_idx + 1}"
    with c_nav2:
        selected_day = st.selectbox("Select Day:", options=list(st.session_state.my_plan.keys()))

    if selected_day in st.session_state.my_plan:
        for i, ex in enumerate(st.session_state.my_plan[selected_day]):
            c_sets = ex["sets"][w_idx] if w_idx < len(ex["sets"]) else ex["sets"][-1]
            c_reps = ex["reps"][w_idx] if w_idx < len(ex["reps"]) else ex["reps"][-1]
            p_type = ex["progression"].get("type", "Linear Weight")
            
            st.subheader(f"{i+1}. {ex['name']} ({c_sets} Sets | Goal: {c_reps})")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.session_state.device_settings[ex['name']] = st.text_input("Exercise Settings and Machine Setup", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2:
                st.text_input("Note", key=f"note_{ex['name']}_{w_label}_{selected_day}")

            cols = st.columns([1, 1, 1, 1, 1, 1, 1])
            cols[0].caption("Set")
            cols[1].caption("Weight")
            cols[2].caption("Time/Reps")
            cols[3].caption("RIR")
            cols[4].caption("Pain")
            cols[5].caption("Rest")
            cols[6].caption("Done")

            start_w = ex["progression"].get("start_weight", 20.0)

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 1, 1, 1, 1, 1, 1])
                l_key = f"{w_label}_{selected_day}_{ex['name']}_{s}"
                default_rest = st.session_state.rest_defaults.get(f"{ex['name']}_sets", "1:30")
                cur_l = st.session_state.training_logs.get(l_key, {"kg": start_w, "r": c_reps, "rir": 2, "p": 0, "rest": default_rest, "done": False, "type": str(s), "ts": ""})
                
                s_type_options = [str(s), "𝘞", "𝘋", "𝘍", "𝘙/𝘗", "𝘔"]
                r_type = s_cols[0].selectbox("Type", s_type_options, index=s_type_options.index(cur_l.get("type", str(s))) if cur_l.get("type") in s_type_options else 0, key=f"type_{l_key}", label_visibility="collapsed")
                
                is_w_disabled = p_type in ["Linear Time", "Linear Reps"]
                r_kg = s_cols[1].number_input("W", value=float(cur_l["kg"]), step=0.25, format="%.2f", key=f"w_{l_key}", label_visibility="collapsed", disabled=is_w_disabled)
                
                if "Time" in p_type:
                    r_r = s_cols[2].number_input("T", value=int(cur_l["r"]), step=5, key=f"r_{l_key}", label_visibility="collapsed")
                else:
                    r_r = s_cols[2].number_input("R", value=int(cur_l["r"]), step=1, key=f"r_{l_key}", label_visibility="collapsed")
                
                r_rir = s_cols[3].number_input("RIR", 0, 10, int(cur_l["rir"]), key=f"rir_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("P", [0, 1, 2], index=int(cur_l["p"]), key=f"p_{l_key}", label_visibility="collapsed")
                r_rest = s_cols[5].text_input("Res", value=cur_l.get("rest", default_rest), key=f"rest_{l_key}", label_visibility="collapsed")
                r_done = s_cols[6].checkbox("OK", value=cur_l["done"], key=f"done_{l_key}", label_visibility="collapsed")
                
                ts = datetime.now().strftime("%Y-%m-%d %H:%M") if r_done and not cur_l["done"] else (cur_l["ts"] if r_done else "")
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p, "rest": r_rest, "done": r_done, "type": r_type, "ts": ts}
            
            if st.button("+ Add Set", key=f"add_{ex['name']}_{w_label}"):
                st.session_state.my_plan[selected_day][i]["sets"][w_idx] += 1
                st.rerun()
            st.divider()

# --- TAB 3: PROGRESSION ---
with tab_progr:
    st.header("Exercise Progression Setup")
    for d_key in st.session_state.my_plan:
        with st.expander(f"Progression Details for {d_key}"):
            for i, ex in enumerate(st.session_state.my_plan[d_key]):
                with st.container(border=True):
                    st.markdown(f"**{ex['name']}**")

                    # Warmup Dropdown
                    warmup_options = ["None"] + list(st.session_state.warmup_routines.keys())
                    current_warmup = ex.get("warmup_routine", "None")

                    selected_warmup = st.selectbox(
                        "Warmup Routine",
                        warmup_options,
                        index=warmup_options.index(current_warmup) if current_warmup in warmup_options else 0,
                        key=f"warmup_{d_key}_{ex['name']}"
                    )

                    ex["warmup_routine"] = selected_warmup

                    o_prog = ex["progression"]
                    prog_options = ["Linear Weight", "Linear Reps", "Linear Time", "Double Progression", "Expert Mode"]
                    p_type = st.selectbox(
                        "Progression Model",
                        prog_options,
                        index=prog_options.index(o_prog["type"]) if o_prog["type"] in prog_options else 0,
                        key=f"ptype_{d_key}_{ex['name']}"
                    )
