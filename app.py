import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Strong Pain Coach", layout="wide")

# --- INITIALIZATION ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4

def_prog = {
    "type": "Linear (Weight Only)", 
    "inc_weight": 1.25, "inc_reps": 1, "inc_sec": 5, 
    "freq_inc": 1, "freq_del": 2,
    "min_reps": 8, "max_reps": 12, "glob_sets": 3, "glob_reps": 10
}

if 'my_plan' not in st.session_state: 
    st.session_state.my_plan = {
        "Day 1": [
            {"name": "Test 1", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}, 
            {"name": "Test 2", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10], "progression": def_prog.copy()}
        ]
    }
if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan, tab_data, tab_calendar = st.tabs([
    "Training", "Planner", "Data Management", "History"
])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("Select Week:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Week {x+1}")
        w_label = f"Week {w_idx + 1}"
    with col_nav2:
        selected_day = st.selectbox("Select Day:", options=list(st.session_state.my_plan.keys()), key="train_day_sel")

    if selected_day in st.session_state.my_plan:
        for i, ex in enumerate(st.session_state.my_plan[selected_day]):
            c_sets = ex["sets"][w_idx] if w_idx < len(ex["sets"]) else ex["sets"][-1]
            c_reps = ex["reps"][w_idx] if w_idx < len(ex["reps"]) else ex["reps"][-1]
            
            st.subheader(f"{i+1}. {ex['name']} ({c_sets} Sets | Goal: {c_reps})")
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                st.session_state.device_settings[ex['name']] = st.text_input(f"Setup", value=st.session_state.device_settings.get(ex['name'], ""), key=f"dev_{ex['name']}_{selected_day}")
            with c_n2: st.text_input(f"Note", key=f"note_{ex['name']}_{w_label}_{selected_day}")

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
    new_w = st.number_input("Cycle Duration (Weeks):", 1, 12, st.session_state.cycle_weeks)
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit Day: {d_key}", expanded=True):
            new_dn = st.text_input("Rename Day:", value=d_key, key=f"ren_{d_key}")
            if new_dn != d_key and new_dn.strip() != "":
                st.session_state.my_plan[new_dn] = st.session_state.my_plan.pop(d_key)
                st.rerun()
            
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises (one per line):", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                st.markdown(f"#### {n}")
                match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                o_prog = match["progression"].copy() if match else def_prog.copy()
                
                prog_options = ["Linear (Weight Only)", "Double Progression (Weight & Reps)", "Reps Only", "Time (Seconds)", "EXPERT (Variable Matrix)"]
                p_type = st.selectbox("Progression Model", prog_options, index=prog_options.index(o_prog["type"]) if o_prog["type"] in prog_options else 0, key=f"ptype_{d_key}_{n}")
                
                n_sets, n_reps = [], []
                
                if p_type == "EXPERT (Variable Matrix)":
                    st.caption("Weekly Volume Matrix")
                    w_cols = st.columns(st.session_state.cycle_weeks)
                    for w in range(st.session_state.cycle_weeks):
                        old_s = match["sets"][w] if (match and w < len(match["sets"])) else 3
                        old_r = match["reps"][w] if (match and w < len(match["reps"])) else 10
                        s_v = w_cols[w].number_input(f"W{w+1} Sets", 1, 15, int(old_s), key=f"es_{d_key}_{n}_{w}")
                        r_v = w_cols[w].number_input(f"W{w+1} Goal", 1, 300, int(old_r), key=f"er_{d_key}_{n}_{w}")
                        n_sets.append(s_v); n_reps.append(r_v)
                else:
                    c1, c2, c3 = st.columns(3)
                    g_s = c1.number_input("Sets (Cycle Default)", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                    
                    if p_type == "Double Progression (Weight & Reps)":
                        min_r = c2.number_input("Minimum Reps", 1, 300, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{n}")
                        max_r = c3.number_input("Maximum Reps", 1, 300, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{n}")
                        o_prog.update({"glob_sets": g_s, "min_reps": min_r, "max_reps": max_r, "glob_reps": max_r})
                    else:
                        g_r = c2.number_input("Goal (Reps/Sec)", 1, 300, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{n}")
                        o_prog.update({"glob_sets": g_s, "glob_reps": g_r})
                    
                    n_sets = [g_s] * st.session_state.cycle_weeks
                    n_reps = [o_prog.get("glob_reps", 10)] * st.session_state.cycle_weeks

                with st.expander("⚙️ Logic & Increments"):
                    l1, l2 = st.columns(2)
                    if "Weight" in p_type or "EXPERT" in p_type: 
                        o_prog["inc_weight"] = l1.number_input("Weight added after Success", 0.0, 50.0, float(o_prog.get("inc_weight", 1.25)), 1.25, key=f"iw_{d_key}_{n}")
                    if "Rep" in p_type: 
                        o_prog["inc_reps"] = l1.number_input("Reps added after Success", 0, 20, int(o_prog.get("inc_reps", 1)), 1, key=f"ir_{d_key}_{n}")
                    if "Time" in p_type: 
                        o_prog["inc_sec"] = l1.number_input("Seconds added after Success", 0, 100, int(o_prog.get("inc_sec", 5)), 1, key=f"is_{d_key}_{n}")
                    
                    o_prog["freq_inc"] = l2.number_input("Successful Weeks until Increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = l2.number_input("Failed Weeks until Deload", 1, 10, int(o_prog["freq_del"]), key=f"fd_{d_key}_{n}")

                o_prog["type"] = p_type
                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            
            st.session_state.my_plan[d_key] = upd_data
            if st.button("Delete Day", key=f"del_day_{d_key}"):
                if len(st.session_state.my_plan) > 1: st.session_state.my_plan.pop(d_key); st.rerun()

    if st.button("Add New Training Day"):
        st.session_state.my_plan[f"Day {len(st.session_state.my_plan)+1}"] = [{"name": "New Exercise", "sets": [3]*st.session_state.cycle_weeks, "reps": [10]*st.session_state.cycle_weeks, "progression": def_prog.copy()}]
        st.rerun()

# --- TAB 3 & 4: DATA & HISTORY ---
with tab_data:
    st.header("Data Management")
    if st.session_state.training_logs:
        df = pd.DataFrame([{"Date": v["ts"], "Week": k.split("_")[0], "Day": k.split("_")[1], "Exercise": k.split("_")[2], "Set": k.split("_")[3], "Weight": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]} for k,v in st.session_state.training_logs.items() if v["done"]])
        if not df.empty: st.download_button("Download CSV", df.to_csv(index=False, sep=";"), "training.csv", "text/csv"); st.dataframe(df)

with tab_calendar:
    st.header("History")
    if st.session_state.training_logs:
        for k, v in sorted(st.session_state.training_logs.items()):
            if v["done"]: st.write(f"{v['ts']} - {k.replace('_',' ')}: {v['kg']}kg x {v['r']}")
