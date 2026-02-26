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

def_prog_linear = {
    "type": "Linear Weight", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "min_reps": 8, "max_reps": 12, "glob_sets": 3, "glob_reps": 10
}

if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [
            {"name": "Linear Weight Exercise", "sets": [3]*4, "reps": [10]*4, "progression": def_prog_linear.copy()}, 
            {"name": "Linear Reps Exercise", "sets": [3]*4, "reps": [10]*4, "progression": {**def_prog_linear, "type": "Linear Reps"}}
        ], 
        "Day 2": [
            {"name": "Linear Time Exercise", "sets": [3]*4, "reps": [10]*4, "progression": {**def_prog_linear, "type": "Linear Time"}}, 
            {"name": "Double Progression Exercise", "sets": [3]*4, "reps": [10]*4, "progression": {**def_prog_linear, "type": "Double Progression"}}
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
                st.session_state.device_settings[ex['name']] = st.text_input(f"Exercise & Equipment Settings", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2:
                st.text_input(f"Note", key=f"note_{ex['name']}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3, 1])
            cols[0].caption("Set")
            cols[1].caption("Weight")
            cols[2].caption("Reps")
            cols[3].caption("RIR")
            cols[4].caption("Pain")
            cols[5].caption("Done")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3, 1])
                l_key = f"{w_label}_{selected_day}_{ex['name']}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": c_reps, "rir": 2, "p": 0, "done": False, "ts": ""})
                
                s_cols[0].write(f"{s}")
                r_kg = s_cols[1].number_input("Weight", value=float(cur_l["kg"]), step=0.25, format="%.2f", key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("Reps", value=int(cur_l["r"]), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("RIR", value=int(cur_l["rir"]), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("Pain", options=[0, 1, 2], index=int(cur_l["p"]), key=f"p_in_{l_key}", label_visibility="collapsed")
                r_done = s_cols[5].checkbox("Done", value=cur_l["done"], key=f"done_in_{l_key}", label_visibility="collapsed")
                
                ts = datetime.now().strftime("%Y-%m-%d %H:%M") if r_done and not cur_l["done"] else (cur_l["ts"] if r_done else "")
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p, "done": r_done, "ts": ts}
            st.divider()

# --- TAB 2: PLANNER ---
with tab_plan:
    st.header("Training Cycle Configuration")
    st.markdown("Set the duration of your training cycle and decide how to handle the deload.")
    
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.session_state.cycle_weeks = st.number_input("Number of weeks for this training cycle", 1, 12, st.session_state.cycle_weeks)
    with row1_col2:
        strategies = ["No automatic deload", "Use last week of cycle as deload", "Add deload week after cycle"]
        st.session_state.deload_strategy = st.selectbox("Select deload strategy", strategies, index=strategies.index(st.session_state.deload_strategy))
    
    row2_col1, row2_col2 = st.columns(2)
    with row2_col1:
        st.session_state.deload_intensity = st.slider("Percentage of training weight for deload week (%)", 50, 100, st.session_state.deload_intensity, step=10)
    with row2_col2:
        st.write("") 
        st.session_state.reduce_sets_deload = st.checkbox("Reduce number of sets by 50%", value=st.session_state.reduce_sets_deload, help="Halving the sets further reduces training volume to maximize recovery while maintaining movement quality.")

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit Day: {d_key}", expanded=True):
            new_dn = st.text_input("Rename Day", d_key, key=f"ren_{d_key}")
            if st.button("Delete Day", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

            if new_dn != d_key and new_dn.strip() != "":
                st.session_state.my_plan[new_dn] = st.session_state.my_plan.pop(d_key)
                st.rerun()
            
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises for this day:", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                st.markdown(f"---")
                st.markdown(f"#### Setup: {n}")
                match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                o_prog = match["progression"].copy() if match else def_prog_linear.copy()
                
                prog_options = ["Linear Weight", "Linear Reps", "Linear Time", "Double Progression", "Expert Matrix"]
                p_type = st.selectbox("Choose your progression model", prog_options, index=prog_options.index(o_prog["type"]) if o_prog["type"] in prog_options else 0, key=f"ptype_{d_key}_{n}")
                
                n_sets, n_reps = [], []
                
                if p_type == "Expert Matrix":
                    st.caption("Weekly Volume Matrix")
                    w_cols = st.columns(st.session_state.cycle_weeks)
                    for w in range(st.session_state.cycle_weeks):
                        old_s = match["sets"][w] if (match and w < len(match["sets"])) else 3
                        old_r = match["reps"][w] if (match and w < len(match["reps"])) else 10
                        s_v = w_cols[w].number_input(f"W{w+1} sets", 1, 15, int(old_s), key=f"es_{d_key}_{n}_{w}")
                        r_v = w_cols[w].number_input(f"W{w+1} Goal", 1, 300, int(old_r), key=f"er_{d_key}_{n}_{w}")
                        n_sets.append(s_v); n_reps.append(r_v)
                else:
                    c1, c2, c3 = st.columns(3)
                    g_s = c1.number_input("Number of sets for this training cycle", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                    if p_type == "Double Progression":
                        o_prog["min_reps"] = c2.number_input("Minimum Reps", 1, 300, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{n}")
                        o_prog["max_reps"] = c3.number_input("Maximum Reps", 1, 300, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{n}")
                        n_reps = [o_prog["max_reps"]] * st.session_state.cycle_weeks
                    else:
                        u_label = "Set your target time (in seconds, e.g. 90 = 1:30)" if "Time" in p_type else "Set your target reps"
                        o_prog["glob_reps"] = c2.number_input(u_label, 1, 300, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{n}")
                        n_reps = [o_prog["glob_reps"]] * st.session_state.cycle_weeks
                    
                    if match and len(match["sets"]) == st.session_state.cycle_weeks:
                        n_sets = match["sets"]
                    else:
                        n_sets = [g_s] * st.session_state.cycle_weeks
                    o_prog["glob_sets"] = g_s

                with st.expander("Progression logic and increments"):
                    l1, l2 = st.columns(2)
                    # Dynamische Labels und Steps für Zeit vs Gewicht
                    inc_label = "Time increment (sec)" if "Time" in p_type else "Weight increment"
                    inc_step = 5.0 if "Time" in p_type else 0.25
                    
                    o_prog["inc_weight"] = l1.number_input(inc_label, 0.0, 300.0, float(o_prog.get("inc_weight", 1.25)), inc_step, format="%.2f", key=f"iw_{d_key}_{n}")
                    o_prog["freq_inc"] = l2.number_input("Success weeks for increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = l2.number_input("Failed weeks for deload", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fd_{d_key}_{n}")

                o_prog["type"] = p_type
                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            st.session_state.my_plan[d_key] = upd_data

    if st.button("Add New Training Day"):
        st.session_state.my_plan[f"Day {len(st.session_state.my_plan)+1}"] = []
        st.rerun()

# --- TAB 3: DATA MANAGEMENT ---
with tab_data:
    st.header("Data Management")
    has_data = False
    if st.session_state.training_logs:
        log_list = []
        for k, v in st.session_state.training_logs.items():
            if v.get("done"):
                parts = k.split("_")
                log_list.append({"Date": v["ts"], "Week": parts[0], "Day": parts[1], "Exercise": parts[2], "Set": parts[3], "Weight": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        if log_list:
            has_data = True
            df = pd.DataFrame(log_list)
            st.download_button("Download CSV", df.to_csv(index=False, sep=";"), "training.csv", "text/csv")
            st.dataframe(df, use_container_width=True)
    if not has_data:
        st.info("No training data recorded yet.")

# --- TAB 4: HISTORY ---
with tab_calendar:
    st.header("History")
    history_items = [k for k, v in st.session_state.training_logs.items() if v.get("done")]
    if history_items:
        for k in sorted(history_items, reverse=True):
            v = st.session_state.training_logs[k]
            st.write(f"**{v['ts']}** - {k.replace('_',' ')}: {v['kg']}kg x {v['r']} (Pain: {v['p']})")
    else:
        st.info("No history available yet.")
