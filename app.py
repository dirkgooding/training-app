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

# ---------------------------
# (TAB 1 und TAB 2 bleiben exakt wie bei dir)
# ---------------------------

# --- TAB 3: PROGRESSION ---
with tab_progr:
    st.header("Exercise Progression Setup")
    for d_key in st.session_state.my_plan:
        with st.expander(f"Progression Details for {d_key}"):
            for i, ex in enumerate(st.session_state.my_plan[d_key]):
                with st.container(border=True):
                    st.markdown(f"**{ex['name']}**")

                    # --- Warmup Dropdown ---
                    warmup_options = ["None"] + list(st.session_state.warmup_routines.keys())
                    current_warmup = ex.get("warmup_routine", "None")

                    selected_warmup = st.selectbox(
                        "Warmup Routine",
                        warmup_options,
                        index=warmup_options.index(current_warmup) if current_warmup in warmup_options else 0,
                        key=f"warmup_{d_key}_{ex['name']}"
                    )

                    ex["warmup_routine"] = selected_warmup
                    # --- End Warmup Dropdown ---

                    o_prog = ex["progression"]
                    prog_options = ["Linear Weight", "Linear Reps", "Linear Time", "Double Progression", "Expert Mode"]
                    p_type = st.selectbox(
                        "Progression Model",
                        prog_options,
                        index=prog_options.index(o_prog["type"]) if o_prog["type"] in prog_options else 0,
                        key=f"ptype_{d_key}_{ex['name']}"
                    )

                    c1, c2, c3, c4 = st.columns(4)
                    g_s = c1.number_input("Sets", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{ex['name']}")
                    
                    if p_type == "Double Progression":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), key=f"sw_{d_key}_{ex['name']}")
                        o_prog["min_reps"] = c3.number_input("Min Reps", 1, 100, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{ex['name']}")
                        o_prog["max_reps"] = c4.number_input("Max Reps", 1, 100, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{ex['name']}")
                    elif p_type == "Expert Mode":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), key=f"sw_{d_key}_{ex['name']}")
                        o_prog["min_reps"] = c3.number_input("Min Reps", 1, 100, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{ex['name']}")
                        o_prog["max_reps"] = c4.number_input("Max Reps", 1, 100, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{ex['name']}")
                    elif p_type == "Linear Weight":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), key=f"sw_{d_key}_{ex['name']}")
                        o_prog["glob_reps"] = c3.number_input("Target Reps", 1, 100, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{ex['name']}")
                    elif p_type == "Linear Reps":
                        o_prog["start_reps"] = c2.number_input("Start Reps", 1, 100, int(o_prog.get("start_reps", 8)), key=f"sr_{d_key}_{ex['name']}")
                    elif p_type == "Linear Time":
                        o_prog["start_time"] = c2.number_input("Start Time (sec)", 1, 3600, int(o_prog.get("start_time", 30)), key=f"st_{d_key}_{ex['name']}")

                    st.markdown("---")
                    l1, l2, l3 = st.columns(3)

                    if "Time" in p_type:
                        inc_label, inc_step = "Increase time by (sec)", 5.0
                    elif "Reps" in p_type:
                        inc_label, inc_step = "Increase reps by", 1.0
                    else:
                        inc_label, inc_step = "Increase weight by", 0.25

                    o_prog["inc_weight"] = l1.number_input(inc_label, 0.0, 300.0, float(o_prog.get("inc_weight", 1.25)), inc_step, format="%.2f", key=f"iw_{d_key}_{ex['name']}")
                    o_prog["freq_inc"] = l2.number_input("Success weeks for increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{ex['name']}")
                    o_prog["freq_del"] = l3.number_input("Failed weeks for deload", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fd_{d_key}_{ex['name']}")

                    o_prog["type"] = p_type
                    o_prog["glob_sets"] = g_s
                    st.session_state.my_plan[d_key][i]["progression"] = o_prog
