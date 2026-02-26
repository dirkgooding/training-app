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
        "Day 1": [{"name": "Squats", "sets": [3]*4, "reps": [10]*4, "progression": def_prog_weight.copy()}],
        "Day 2": [{"name": "Bench Press", "sets": [3]*4, "reps": [10]*4, "progression": def_prog_weight.copy()}]
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
            
            unit = "Sec" if "Time" in p_type else "Reps"
            st.subheader(f"{i+1}. {ex['name']} ({c_sets} Sets | Goal: {c_reps} {unit})")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.session_state.device_settings[ex['name']] = st.text_input(f"Settings", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2:
                st.text_input(f"Note", key=f"note_{ex['name']}_{w_label}_{selected_day}")

            # 7-SPALTEN-RASTER: Ausgeglichene Gewichtung
            cols = st.columns([1.2, 2, 2, 1.5, 1.2, 1.5, 1])
            cols[0].caption("Set")
            cols[1].caption("Weight")
            cols[2].caption("Time" if "Time" in p_type else "Reps")
            cols[3].caption("RIR")
            cols[4].caption("Pain")
            cols[5].caption("Rest")
            cols[6].caption("Done")

            start_w = ex["progression"].get("start_weight", 20.0)

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1.2, 2, 2, 1.5, 1.2, 1.5, 1])
                l_key = f"{w_label}_{selected_day}_{ex['name']}_{s}"
                
                # Default Rest aus dem Rest Timer Tab ziehen
                default_rest = st.session_state.rest_defaults.get(ex["name"], "1:30")
                cur_l = st.session_state.training_logs.get(l_key, {"kg": start_w, "r": c_reps, "rir": 2, "p": 0, "rest": default_rest, "done": False, "type": str(s), "ts": ""})
                
                # Spalte 0: Set Type (Unicode Kursiv)
                s_type_options = [str(s), "𝘞", "𝘋", "𝘍", "𝘙/𝘗", "𝘔"]
                r_type = s_cols[0].selectbox("Type", s_type_options, index=s_type_options.index(cur_l.get("type", str(s))) if cur_l.get("type") in s_type_options else 0, key=f"type_{l_key}", label_visibility="collapsed")
                
                # Spalte 1: Weight (Disabled bei Time/Reps)
                is_disabled = p_type in ["Linear Time", "Linear Reps"]
                r_kg = s_cols[1].number_input("Weight", value=float(cur_l["kg"]), step=0.25, format="%.2f", key=f"w_{l_key}", label_visibility="collapsed", disabled=is_disabled)
                
                # Spalte 2: Reps / Time
                if "Time" in p_type:
                    r_r = s_cols[2].number_input("Time", value=int(cur_l["r"]), step=5, key=f"r_{l_key}", label_visibility="collapsed")
                else:
                    r_r = s_cols[2].number_input("Reps", value=int(cur_l["r"]), step=1, key=f"r_{l_key}", label_visibility="collapsed")
                
                # Spalte 3-6: RIR, Pain, Rest, Done
                r_rir = s_cols[3].number_input("RIR", 0, 10, int(cur_l["rir"]), key=f"rir_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("Pain", [0, 1, 2], index=int(cur_l["p"]), key=f"p_{l_key}", label_visibility="collapsed")
                r_rest = s_cols[5].text_input("Rest", value=cur_l.get("rest", default_rest), key=f"rest_{l_key}", label_visibility="collapsed")
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

# --- TAB 3: PROGRESSION ---
with tab_progr:
    st.header("Exercise Progression Setup")
    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Setup {d_key}", expanded=True):
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
                    
                    c1, c2, c3 = st.columns(3)
                    g_s = c1.number_input("Sets", 1, 15, 3, key=f"gs_{d_key}_{n}")
                    
                    if p_type == "Double Progression":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, 20.0, key=f"sw_{d_key}_{n}")
                        o_prog["max_reps"] = c3.number_input("Max Reps", 1, 100, 12, key=f"mr_{d_key}_{n}")
                    elif p_type == "Linear Weight":
                        o_prog["start_weight"] = c2.number_input("Start Weight", 0.0, 500.0, 20.0, key=f"sw_{d_key}_{n}")
                        o_prog["glob_reps"] = c3.number_input("Target Reps", 1, 100, 10, key=f"gr_{d_key}_{n}")
                    
                    o_prog["type"] = p_type
                    n_sets = [g_s] * st.session_state.cycle_weeks
                    n_reps = [o_prog.get("glob_reps", 10)] * st.session_state.cycle_weeks
                    upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            st.session_state.my_plan[d_key] = upd_data

# --- TAB 4: WARMUPS ---
with tab_warm:
    st.header("Warmup Configuration")
    st.info("Hier kannst du bald deine Aufwärmroutinen definieren.")

# --- TAB 5: REST TIMER ---
with tab_rest:
    st.header("Rest Timer Settings")
    all_ex = set()
    for day in st.session_state.my_plan:
        for ex in st.session_state.my_plan[day]:
            all_ex.add(ex["name"])
    
    for ex_name in sorted(list(all_ex)):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{ex_name}**")
        st.session_state.rest_defaults[ex_name] = col2.text_input("Default Rest", value=st.session_state.rest_defaults.get(ex_name, "1:30"), key=f"res_{ex_name}")

# --- TAB 6 & 7: DATA & HISTORY ---
with tab_data:
    st.header("Data Management")
    if st.session_state.training_logs:
        df = pd.DataFrame([{"Set": k, **v} for k, v in st.session_state.training_logs.items() if v["done"]])
        st.dataframe(df)

with tab_hist:
    st.header("History")
    for k, v in sorted(st.session_state.training_logs.items(), reverse=True):
        if v["done"]:
            st.write(f"**{v['ts']}** - {k}: {v['kg']}kg x {v['r']} (Type: {v['type']})")
