import streamlit as st
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(page_title="Strong Pain Coach", layout="wide")

# --- INITIALIZATION ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'expert_mode' not in st.session_state: st.session_state.expert_mode = False

# Standard Progression Values
def_prog = {
    "type": "Linear (Weight Only)", 
    "inc_weight": 1.25, 
    "inc_reps": 0, 
    "inc_sec": 0, 
    "freq_inc": 1, 
    "freq_del": 2,
    "base_reps": 8,
    "target_reps": 12,
    "glob_sets": 3
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
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sets | Goal: {c_reps} Reps/Sec)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"Exercise Setup", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"Note", key=f"note_{name}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3, 1])
            cols[0].caption("Set"); cols[1].caption("Weight"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain"); cols[5].caption("Done")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3, 1])
                s_cols[0].write(f"**{s}**")
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": c_reps, "rir": 2, "p": 0, "done": False, "ts": ""})
                
                r_kg = s_cols[1].number_input("Weight", value=float(cur_l.get("kg", 20.0)), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("Reps", value=int(cur_l.get("r", c_reps)), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("RIR", value=int(cur_l.get("rir", 2)), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("Pain", options=[0, 1, 2], index=int(cur_l.get("p", 0)), key=f"p_in_{l_key}", label_visibility="collapsed")
                r_done = s_cols[5].checkbox("Done", value=cur_l.get("done", False), key=f"done_in_{l_key}", label_visibility="collapsed")
                
                ts = cur_l.get("ts", "")
                if r_done and not cur_l.get("done", False):
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                elif not r_done:
                    ts = ""
                
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p, "done": r_done, "ts": ts}
            st.divider()

# --- TAB 2: PLANNER ---
with tab_plan:
    st.header("Configuration")
    
    col_cfg1, col_cfg2 = st.columns(2)
    new_w = col_cfg1.number_input("Cycle Duration (Weeks):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    st.session_state.expert_mode = col_cfg2.checkbox("Expert Mode: Variable Sets per Week", value=st.session_state.expert_mode)
    
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Edit: {d_key}", expanded=True):
            new_name = st.text_input("Day Name:", value=d_key, key=f"ren_{d_key}")
            
            if new_name != d_key and new_name.strip() != "":
                if new_name not in st.session_state.my_plan:
                    st.session_state.my_plan[new_name] = st.session_state.my_plan.pop(d_key)
                    st.rerun()
                
            cur_exs = st.session_state.my_plan[d_key]
            ex_txt = "\n".join([e["name"] for e in cur_exs])
            new_ex_txt = st.text_area("Exercises (one per line):", value=ex_txt, key=f"edit_{d_key}")
            
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            upd_data = []
            
            for n in names:
                st.write(f"**Setup: {n}**")
                o_sets = [3] * st.session_state.cycle_weeks
                o_reps = [10] * st.session_state.cycle_weeks
                o_prog = def_prog.copy()
                
                for e in cur_exs:
                    if e["name"] == n:
                        if "sets" in e and isinstance(e["sets"], list): o_sets = e["sets"]
                        elif "sets" in e: o_sets = [e["sets"]] * st.session_state.cycle_weeks
                        if "reps" in e and isinstance(e["reps"], list): o_reps = e["reps"]
                        elif "reps" in e: o_reps = [e["reps"]] * st.session_state.cycle_weeks
                        if "progression" in e: o_prog = e["progression"]

                type_options = ["Linear (Weight Only)", "Double Progression (Weight & Reps)", "Reps Only", "Time (Seconds)"]
                current_type = o_prog.get("type", "Linear (Weight Only)")
                p_type = st.selectbox("Progression Model", type_options, index=type_options.index(current_type), key=f"ptype_{d_key}_{n}")
                
                n_sets = []
                n_reps = []
                is_double = p_type in ["Double Progression (Weight & Reps)", "Reps Only"]
                
                if is_double and not st.session_state.expert_mode:
                    col_s, col_br, col_tr = st.columns(3)
                    n_sets_glob = col_s.number_input("Sets", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gsets_{d_key}_{n}")
                    n_base = col_br.number_input("Base Reps", 1, 300, int(o_prog.get("base_reps", 8)), key=f"br_{d_key}_{n}")
                    n_target = col_tr.number_input("Target Reps", 1, 300, int(o_prog.get("target_reps", 12)), key=f"tr_{d_key}_{n}")
                    
                    n_sets = [n_sets_glob] * st.session_state.cycle_weeks
                    n_reps = [n_target] * st.session_state.cycle_weeks
                    o_prog.update({"glob_sets": n_sets_glob, "base_reps": n_base, "target_reps": n_target})
                else:
                    # Individual week input with full labels
                    w_cols = st.columns(st.session_state.cycle_weeks)
                    label_type = "Sec Goal" if p_type == "Time (Seconds)" else "Rep Goal"
                    for w in range(st.session_state.cycle_weeks):
                        v_s = o_sets[w] if w < len(o_sets) else o_sets[-1]
                        v_r = o_reps[w] if w < len(o_reps) else o_reps[-1]
                        s_v = w_cols[w].number_input(f"Week {w+1} Sets", 1, 15, int(v_s), key=f"s_{d_key}_{n}_{w}")
                        r_v = w_cols[w].number_input(f"Week {w+1} {label_type}", 1, 300, int(v_r), key=f"r_{d_key}_{n}_{w}")
                        n_sets.append(s_v)
                        n_reps.append(r_v)
                    
                    if is_double:
                        c_br, c_tr = st.columns(2)
                        o_prog["base_reps"] = c_br.number_input("Base Reps (Algorithm Info)", 1, 300, int(o_prog.get("base_reps", 8)), key=f"br_exp_{d_key}_{n}")
                        o_prog["target_reps"] = c_tr.number_input("Target Reps (Algorithm Info)", 1, 300, int(o_prog.get("target_reps", 12)), key=f"tr_exp_{d_key}_{n}")

                with st.expander(f"⚙️ Increments & Deload for {n}"):
                    p_col1, p_col2, p_col3 = st.columns(3)
                    i_kg = o_prog.get("inc_weight", 1.25)
                    i_r = o_prog.get("inc_reps", 1)
                    i_sec = o_prog.get("inc_sec", 5)

                    if p_type == "Linear (Weight Only)":
                        i_kg = p_col1.number_input("Weight Increment", 0.0, 50.0, float(i_kg), step=1.25, key=f"pkg_{d_key}_{n}")
                    elif p_type == "Double Progression (Weight & Reps)":
                        i_kg = p_col1.number_input("Weight Increment", 0.0, 50.0, float(i_kg), step=1.25, key=f"pkg_{d_key}_{n}")
                        i_r = p_col2.number_input("Rep Increment", 0, 20, int(i_r), step=1, key=f"prep_{d_key}_{n}")
                    elif p_type == "Reps Only":
                        i_r = p_col1.number_input("Rep Increment", 0, 20, int(i_r), step=1, key=f"prep_{d_key}_{n}")
                    else:
                        i_sec = p_col1.number_input("Time Increment", 0, 100, int(i_sec), step=1, key=f"psec_{d_key}_{n}")
                        
                    f_col1, f_col2 = st.columns(2)
                    f_inc = f_col1.number_input("Increase Frequency (Weeks)", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"finc_{d_key}_{n}")
                    f_del = f_col2.number_input("Deload Frequency (Failures)", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fdel_{d_key}_{n}")
                    
                    o_prog.update({"type": p_type, "inc_weight": i_kg, "inc_reps": i_r, "inc_sec": i_sec, "freq_inc": f_inc, "freq_del": f_del})

                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
                st.divider()
            
            st.session_state.my_plan[d_key] = upd_data
            if st.button("Delete Day", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

    st.divider()
    if st.button("Add New Training Day"):
        st.session_state.my_plan["New Day"] = [{"name": "New Exercise", "sets": [3] * st.session_state.cycle_weeks, "reps": [10] * st.session_state.cycle_weeks, "progression": def_prog.copy()}]
        st.rerun()

# --- TAB 3 & 4 (Unchanged logic) ---
with tab_data:
    st.header("Data Import & Export")
    uploaded_csv = st.file_uploader("Upload CSV Import", type=["csv"])
    if uploaded_csv is not None and st.button("Confirm Import"):
        try:
            df_i = pd.read_csv(uploaded_csv, sep=";")
            for _, row in df_i.iterrows():
                l_key = f"{row['Week']}_{row['Day']}_{row['Exercise']}_{row['Set']}"
                st.session_state.training_logs[l_key] = {"kg": float(row["Weight"]), "r": int(row["Reps"]), "rir": int(row["RIR"]), "p": int(row["Pain"]), "done": True, "ts": str(row["Date"])}
            st.success("Import successful!"); st.rerun()
        except Exception as e: st.error(f"Error: {e}")
    if st.session_state.training_logs:
        exp_list = [{"Date": v.get("ts", ""), "Week": k.split("_")[0], "Day": k.split("_")[1], "Exercise": k.split("_")[2], "Set": k.split("_")[3], "Weight": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]} for k, v in st.session_state.training_logs.items() if v.get("done")]
        if exp_list:
            df = pd.DataFrame(exp_list)
            st.download_button("Download CSV Export", data=df.to_csv(index=False, sep=";", encoding="utf-8-sig"), file_name="training_export.csv", mime="text/csv")
            st.dataframe(df, use_container_width=True)

with tab_calendar:
    st.header("Training History")
    if st.session_state.training_logs:
        hist_list = [{"Date": v.get("ts", ""), "Week": k.split("_")[0], "Day": k.split("_")[1], "Exercise": k.split("_")[2], "Set": k.split("_")[3], "Weight": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]} for k, v in st.session_state.training_logs.items() if v.get("done")]
        if hist_list:
            df_hist = pd.DataFrame(hist_list)
            for w in sorted(df_hist["Week"].unique()):
                with st.expander(f"View: {w}"):
                    df_w = df_hist[df_hist["Week"] == w]
                    for d in sorted(df_w["Day"].unique()):
                        st.markdown(f"**{d}**"); st.dataframe(df_w[df_w["Day"] == d][["Date", "Exercise", "Set", "Weight", "Reps", "RIR", "Pain"]], use_container_width=True, hide_index=True)
