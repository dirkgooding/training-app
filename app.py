import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Strong Pain Coach", layout="wide")

# --- INITIALIZATION ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'expert_mode' not in st.session_state: st.session_state.expert_mode = False

def_prog = {
    "type": "Linear (Weight Only)", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "base_reps": 8, "target_reps": 12, "glob_sets": 3
}

if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [
            {"name": "Test 1", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}, 
            {"name": "Test 2", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}
        ], 
        "Day 2": [
            {"name": "Test 3", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}, 
            {"name": "Test 4", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}
        ]
    }
if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan, tab_data, tab_calendar = st.tabs(["Training", "Planner", "Data Management", "History"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("Select Week:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Week {x+1}")
        w_label = f"Week {w_idx + 1}"
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("Select Day:", options=tag_namen)

    if selected_day in st.session_state.my_plan:
        current_exercises = st.session_state.my_plan[selected_day]
        for i, ex_data in enumerate(current_exercises):
            name = ex_data["name"]
            sets_list = ex_data.get("sets", [3] * st.session_state.cycle_weeks)
            reps_list = ex_data.get("reps", [10] * st.session_state.cycle_weeks)
            c_sets = sets_list[w_idx] if w_idx < len(sets_list) else sets_list[-1]
            c_reps = reps_list[w_idx] if w_idx < len(reps_list) else reps_list[-1]
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sets | Goal: {c_reps} Reps/Sec)")
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.session_state.device_settings[name] = st.text_input(f"Exercise Setup", value=st.session_state.device_settings.get(name, ""), key=f"dev_{name}_{selected_day}")
            with c_n2: st.text_input(f"Note", key=f"note_{name}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3, 1])
            cols[0].caption("Set"); cols[1].caption("Weight"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain"); cols[5].caption("Done")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3, 1])
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
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
    st.header("Configuration")
    col_cfg1, col_cfg2 = st.columns(2)
    new_w = col_cfg1.number_input("Cycle Duration (Weeks):", 1, 12, st.session_state.cycle_weeks)
    st.session_state.expert_mode = col_cfg2.checkbox("Expert Mode: Variable Sets per Week", st.session_state.expert_mode)
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit: {d_key}", expanded=True):
            new_day_name = st.text_input("Day Name:", value=d_key, key=f"ren_{d_key}")
            if new_day_name != d_key and new_day_name.strip() != "":
                st.session_state.my_plan[new_day_name] = st.session_state.my_plan.pop(d_key)
                st.rerun()
            
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises:", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                st.markdown(f"**Setup: {n}**")
                # Find existing data or use default
                match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                o_sets = match["sets"] if match else [3] * st.session_state.cycle_weeks
                o_reps = match["reps"] if match else [10] * st.session_state.cycle_weeks
                o_prog = match["progression"].copy() if match else def_prog.copy()

                type_options = ["Linear (Weight Only)", "Double Progression (Weight & Reps)", "Reps Only", "Time (Seconds)"]
                p_type = st.selectbox("Progression Model", type_options, index=type_options.index(o_prog["type"]), key=f"ptype_{d_key}_{n}")
                
                n_sets, n_reps = [], []
                is_double = p_type in ["Double Progression (Weight & Reps)", "Reps Only"]
                
                if is_double and not st.session_state.expert_mode:
                    c1, c2, c3 = st.columns(3)
                    g_s = c1.number_input("Sets", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                    b_r = c2.number_input("Base Reps", 1, 300, int(o_prog.get("base_reps", 8)), key=f"br_{d_key}_{n}")
                    t_r = c3.number_input("Target Reps", 1, 300, int(o_prog.get("target_reps", 12)), key=f"tr_{d_key}_{n}")
                    n_sets, n_reps = [g_s] * st.session_state.cycle_weeks, [t_r] * st.session_state.cycle_weeks
                    o_prog.update({"glob_sets": g_s, "base_reps": b_r, "target_reps": t_r})
                else:
                    w_cols = st.columns(st.session_state.cycle_weeks)
                    label = "Sec Goal" if p_type == "Time (Seconds)" else "Rep Goal"
                    for w in range(st.session_state.cycle_weeks):
                        s_v = w_cols[w].number_input(f"W{w+1} Sets", 1, 15, int(o_sets[w] if w < len(o_sets) else o_sets[-1]), key=f"s_{d_key}_{n}_{w}")
                        r_v = w_cols[w].number_input(f"W{w+1} {label}", 1, 300, int(o_reps[w] if w < len(o_reps) else o_reps[-1]), key=f"r_{d_key}_{n}_{w}")
                        n_sets.append(s_v); n_reps.append(r_v)
                    if is_double:
                        c1, c2 = st.columns(2)
                        o_prog["base_reps"] = c1.number_input("Base Reps", 1, 300, int(o_prog.get("base_reps", 8)), key=f"br_e_{d_key}_{n}")
                        o_prog["target_reps"] = c2.number_input("Target Reps", 1, 300, int(o_prog.get("target_reps", 12)), key=f"tr_e_{d_key}_{n}")

                with st.expander("⚙️ Increments & Deload"):
                    c1, c2 = st.columns(2)
                    if "Weight" in p_type: o_prog["inc_weight"] = c1.number_input("Weight Increment", 0.0, 50.0, float(o_prog["inc_weight"]), 1.25, key=f"iw_{d_key}_{n}")
                    if "Rep" in p_type: o_prog["inc_reps"] = c1.number_input("Rep Increment", 0, 20, int(o_prog["inc_reps"]), 1, key=f"ir_{d_key}_{n}")
                    if "Time" in p_type: o_prog["inc_sec"] = c1.number_input("Time Increment", 0, 100, int(o_prog["inc_sec"]), 1, key=f"is_{d_key}_{n}")
                    o_prog["freq_inc"] = c2.number_input("Increase Frequency", 1, 10, int(o_prog["freq_inc"]), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = c2.number_input("Deload Frequency", 1, 10, int(o_prog["freq_del"]), key=f"fd_{d_key}_{n}")
                
                o_prog["type"] = p_type
                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            
            st.session_state.my_plan[d_key] = upd_data
            if st.button("Delete Day", key=f"del_day_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

    if st.button("Add New Training Day"):
        st.session_state.my_plan[f"Day {len(st.session_state.my_plan)+1}"] = [{"name": "New Exercise", "sets": [3]*st.session_state.cycle_weeks, "reps": [10]*st.session_state.cycle_weeks, "progression": def_prog.copy()}]
        st.rerun()

# --- TAB 3: DATA & TAB 4: HISTORY (Simplified for Stability) ---
with tab_data:
    st.header("Data Management")
    if st.session_state.training_logs:
        df = pd.DataFrame([{"Date": v["ts"], "Week": k.split("_")[0], "Day": k.split("_")[1], "Exercise": k.split("_")[2], "Set": k.split("_")[3], "Weight": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]} for k,v in st.session_state.training_logs.items() if v["done"]])
        if not df.empty:
            st.download_button("Download CSV", df.to_csv(index=False, sep=";"), "training.csv", "text/csv")
            st.dataframe(df)

with tab_calendar:
    st.header("History")
    if st.session_state.training_logs:
        for k, v in st.session_state.training_logs.items():
            if v["done"]: st.write(f"{v['ts']} - {k.replace('_',' ')}: {v['kg']}kg x {v['r']}")
