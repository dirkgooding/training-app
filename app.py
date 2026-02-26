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
        st.session_state.reduce_sets_deload = st.checkbox("Reduce number of sets by 50%", value=st.session_state.reduce_sets_deload)

    st.divider()

    for d_key in list(st.session_state.my_plan.keys()):
        st.subheader(d_key)
        with st.expander(f"Edit Setup for {d_key}", expanded=True):
            new_dn = st.text_input("Rename Day", d_key, key=f"ren_{d_key}")
            
            if new_dn != d_key and new_dn.strip() != "":
                if new_dn in st.session_state.my_plan:
                    st.error(f"The name '{new_dn}' already exists. Please choose a unique name.")
                else:
                    st.session_state.my_plan[new_dn] = st.session_state.my_plan.pop(d_key)
                    st.rerun()
                
            if st.button("Delete Day", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()
            
            ex_txt = "\n".join([e["name"] for e in st.session_state.my_plan[d_key]])
            new_ex_txt = st.text_area("Exercises for this day (one per line):", value=ex_txt, key=f"edit_exs_{d_key}")
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            
            upd_data = []
            for n in names:
                with st.container(border=True):
                    st.markdown(f"**Exercise: {n}**")
                    match = next((e for e in st.session_state.my_plan[d_key] if e["name"] == n), None)
                    o_prog = match["progression"].copy() if match else def_prog_weight.copy()
                    
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
                        c1, c2, c3, c4 = st.columns(4)
                        g_s = c1.number_input("Sets per session", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                        
                        # Dynamisches Startwert-Feld (NEU)
                        if p_type in ["Linear Weight", "Double Progression"]:
                            o_prog["start_weight"] = c2.number_input("Starting Weight (kg)", 0.0, 500.0, float(o_prog.get("start_weight", 20.0)), step=1.25, format="%.2f", key=f"sw_{d_key}_{n}")
                        elif "Time" in p_type:
                            o_prog["start_time"] = c2.number_input("Starting Time (sec)", 0, 3600, int(o_prog.get("start_time", 30)), step=5, key=f"st_{d_key}_{n}")
                        elif "Reps" in p_type:
                            o_prog["start_reps"] = c2.number_input("Starting Reps", 0, 300, int(o_prog.get("start_reps", 8)), step=1, key=f"sr_{d_key}_{n}")
                        
                        # Ziel-Felder
                        if p_type == "Double Progression":
                            o_prog["min_reps"] = c3.number_input("Minimum Reps", 1, 300, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{n}")
                            o_prog["max_reps"] = c4.number_input("Maximum Reps", 1, 300, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{n}")
                            n_reps = [o_prog["max_reps"]] * st.session_state.cycle_weeks
                        else:
                            u_label = "Target time (sec)" if "Time" in p_type else "Target reps"
                            o_prog["glob_reps"] = c3.number_input(u_label, 1, 300, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{n}")
                            n_reps = [o_prog["glob_reps"]] * st.session_state.cycle_weeks
                        
                        if match and len(match["sets"]) == st.session_state.cycle_weeks:
                            n_sets = match["sets"]
                        else:
                            n_sets = [g_s] * st.session_state.cycle_weeks
                        o_prog["glob_sets"] = g_s

                    # Progression fields directly visible
                    l1, l2 = st.columns(2)
                    if "Time" in p_type:
                        inc_label, inc_step = "Time increment (sec)", 5.0
                    elif "Reps" in p_type:
                        inc_label, inc_step = "Reps increment", 1.0
                    else:
                        inc_label, inc_step = "Weight increment", 0.25
                    
                    o_prog["inc_weight"] = l1.number_input(inc_label, 0.0, 300.0, float(o_prog.get("inc_weight", 1.25)), inc_step, format="%.2f", key=f"iw_{d_key}_{n}")
                    o_prog["freq_inc"] = l2.number_input("Success weeks for increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = l2.number_input("Failed weeks for deload", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fd_{d_key}_{n}")

                    o_prog["type"] = p_type
                    upd_data.append({"name": n, "sets": n_sets, "reps": n_reps, "progression": o_prog})
            st.session_state.my_plan[d_key] = upd_data
        st.divider()

    if st.button("Add New Training Day"):
        st.session_state.my_plan[f"Day {len(st.session_state.my_plan)+1}"] = []
        st.rerun()
