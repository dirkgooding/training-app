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

def_prog_weight = {
    "type": "Linear Weight", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "min_reps": 8, "max_reps": 12, "glob_sets": 3, "glob_reps": 10,
    "start_weight": 20.0
}

if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [{"name": "Squats", "sets": [3]*12, "reps": [10]*12, "progression": def_prog_weight.copy()}],
        "Day 2": [{"name": "Bench Press", "sets": [3]*12, "reps": [10]*12, "progression": def_prog_weight.copy()}]
    }

if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_work, tab_prog, tab_progr, tab_warm, tab_rest, tab_data, tab_hist = st.tabs([
    "Workouts", "Programm", "Progression", "Warmups", "Rest Timer", "Data", "History"
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
                st.session_state.device_settings[ex['name']] = st.text_input(f"Settings", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2:
                st.text_input(f"Note", key=f"note_{ex['name']}_{w_label}_{selected_day}")

            # SYMMETRISCHES RASTER (1:1:1:1:1:1:1)
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
                default_rest = st.session_state.rest_defaults.get(ex["name"], "1:30")
                cur_l = st.session_state.training_logs.get(l_key, {"kg": start_w, "r": c_reps, "rir": 2, "p": 0, "rest": default_rest, "done": False, "type": str(s), "ts": ""})
                
                # Dropdown mit kursivem Warmup
                s_type_options = [str(s), "𝘞", "𝘋", "𝘍", "𝘙/𝘗", "𝘔"]
                r_type = s_cols[0].selectbox("Type", s_type_options, index=s_type_options.index(cur_l.get("type", str(s))) if cur_l.get("type") in s_type_options else 0, key=f"type_{l_key}", label_visibility="collapsed")
                
                # Weight Handling
                is_w_disabled = p_type in ["Linear Time", "Linear Reps"]
                r_kg = s_cols[1].number_input("W", value=float(cur_l["kg"]), step=0.25, format="%.2f", key=f"w_{l_key}", label_visibility="collapsed", disabled=is_w_disabled)
                
                # Reps/Time Handling
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

# --- TAB 2: PROGRAMM ---
with tab_prog:
    st.header("Programm Strategy")
    st.session_state.cycle_weeks = st.number_input("Cycle Duration (Weeks)", 1, 12, st.session_state.cycle_weeks)
    strategies = ["No automatic deload", "Use last week of cycle as deload", "Add deload week after cycle"]
    st.session_state.deload_strategy = st.selectbox("Deload Strategy", strategies, index=strategies.index(st.session_state.deload_strategy))
    st.session_state.deload_intensity = st.slider("Deload Intensity (%)", 50, 100, st.session_state.deload_intensity, 10)
    st.session_state.reduce_sets_deload = st.checkbox("Reduce sets by 50% during deload", st.session_state.reduce_sets_deload)

    st.divider()
    st.subheader("Manage Training Days")
    for d_key in list(st.session_state.my_plan.keys()):
        c1, c2 = st.columns([4, 1])
        new_dn = c1.text_input(f"Rename {d_key}", d_key, key=f"ren_{d_key}")
        if new_dn != d_key and new_dn.strip() != "":
            st.session_state.my_plan[new_dn] = st.session_state.my_plan.pop(d_key)
            st.rerun()
        if c2.button("Delete Day", key=f"del_{d_key}"):
            if len(st.session_state.my_plan) > 1:
                st.session_state.my_plan.pop(d_key)
                st.rerun()
    if st.button("Add New Training Day"):
        st.session_state.my_plan[f"Day {len(st.session_state.my_plan)+1}"] = []
        st.rerun()

# --- TAB 3: PROGRESSION ---
with tab_progr:
    st.header("Exercise Progression Setup")
    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit Setup for {d_key}", expanded=True):
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises (one per line):", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                with st.container(border=True):
                    st.markdown(f"**Exercise: {n}**")
                    match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                    o_prog = match["progression"].copy() if match else def_prog_weight.copy()
                    
                    p_type = st.selectbox("Progression Model", ["Linear Weight", "Linear Reps", "Linear Time", "Double Progression"], index=0, key=f"ptype_{d_key}_{n}")
                    
                    c1, c2, c3, c4 = st.columns(4)
                    g_s = c1.number_input("Sets", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                    
                    if p_type == "Double Progression":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), key=f"sw_{d_key}_{n}")
                        o_prog["min_reps"] = c3.number_input("Min Reps", 1, 100, 8, key=f"minr_{d_key}_{n}")
                        o_prog["max_reps"] = c4.number_input("Max Reps", 1, 100, 12, key=f"maxr_{d_key}_{n}")
                        n_reps = [o_prog["max_reps"]] * st.session_state.cycle_weeks
                    elif p_type == "Linear Weight":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), key=f"sw_{d_key}_{n}")
                        o_prog["glob_reps"] = c3.number_input("Target Reps", 1, 100, 10, key=f"gr_{d_key}_{n}")
                        n_reps = [o_prog["glob_reps"]] * st.session_state.cycle_weeks
                    elif p_type == "Linear Reps":
                        o_prog["start_reps"] = c2.number_input("Start Reps", 1, 100, 8, key=f"sr_{d_key}_{n}")
                        n_reps = [o_prog["start_reps"]] * st.session_state.cycle_weeks
                    elif p_type == "Linear Time":
                        o_prog["start_time"] = c2.number_input("Start Time (sec)", 1, 3600, 30, key=f"st_{d_key}_{n}")
                        n_reps = [o_prog["start_time"]] * st.session_state.cycle_weeks
                    
                    o_prog["type"] = p_type
                    o_prog["glob_sets"] = g_s
                    n_sets = [g_s] * st.session_state.cycle_weeks
                    upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            st.session_state.my_plan[d_key] = upd_data

# --- TAB 4: WARMUPS ---
with tab_warm:
    st.header("Warmup Configuration")
    st.info("Hier kannst du bald deine Aufwärmroutinen definieren.")

# --- TAB 5: REST TIMER ---
with tab_rest:
    st.header("Rest Timer Settings")
    for d_key, exercises in st.session_state.my_plan.items():
        for ex in exercises:
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{ex['name']}**")
            st.session_state.rest_defaults[ex['name']] = col2.text_input("Default Rest", value=st.session_state.rest_defaults.get(ex['name'], "1:30"), key=f"res_{ex['name']}")

# --- TAB 6: DATA ---
with tab_data:
    st.header("Data Management")
    log_data = [{"Key": k, **v} for k, v in st.session_state.training_logs.items() if v.get("done")]
    if log_data:
        st.dataframe(pd.DataFrame(log_data), use_container_width=True)
    else:
        st.info("No data recorded yet.")

# --- TAB 7: HISTORY ---
with tab_hist:
    st.header("History")
    has_history = any(v.get("done") for v in st.session_state.training_logs.values())
    if has_history:
        for k, v in sorted(st.session_state.training_logs.items(), reverse=True):
            if v.get("done"):
                st.write(f"**{v['ts']}** - {k.replace('_',' ')}: {v['kg']}kg x {v['r']} (Type: {v['type']})")
    else:
        st.info("No history available yet. Complete a set to see it here.")
