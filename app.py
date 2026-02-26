# --- DYNAMISCHE EINGABEMASKE IM PLANNER ---
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
                        g_s = c1.number_input("Sets per session", 1, 15, int(o_prog.get("glob_sets", 3)), key=f"gs_{d_key}_{n}")
                        
                        if p_type == "Double Progression":
                            o_prog["min_reps"] = c2.number_input("Minimum Reps", 1, 300, int(o_prog.get("min_reps", 8)), key=f"minr_{d_key}_{n}")
                            o_prog["max_reps"] = c3.number_input("Maximum Reps", 1, 300, int(o_prog.get("max_reps", 12)), key=f"maxr_{d_key}_{n}")
                            n_reps = [o_prog["max_reps"]] * st.session_state.cycle_weeks
                        else:
                            # Dynamisches Label für das Ziel-Feld
                            if "Time" in p_type:
                                u_label = "Target time (sec)"
                            else:
                                u_label = "Target reps"
                            
                            o_prog["glob_reps"] = c2.number_input(u_label, 1, 300, int(o_prog.get("glob_reps", 10)), key=f"gr_{d_key}_{n}")
                            n_reps = [o_prog["glob_reps"]] * st.session_state.cycle_weeks
                        
                        if match and len(match["sets"]) == st.session_state.cycle_weeks:
                            n_sets = match["sets"]
                        else:
                            n_sets = [g_s] * st.session_state.cycle_weeks
                        o_prog["glob_sets"] = g_s

                    # --- DYNAMISCHE INCREMENTS ---
                    l1, l2 = st.columns(2)
                    
                    # Logik für Bezeichnungen und Schrittweiten
                    if "Time" in p_type:
                        inc_label, inc_step = "Time increment (sec)", 5.0
                    elif "Reps" in p_type:
                        inc_label, inc_step = "Reps increment", 1.0
                    else:
                        inc_label, inc_step = "Weight increment", 0.25
                    
                    o_prog["inc_weight"] = l1.number_input(inc_label, 0.0, 300.0, float(o_prog.get("inc_weight", 1.25)), inc_step, format="%.2f", key=f"iw_{d_key}_{n}")
                    o_prog["freq_inc"] = l2.number_input("Success weeks for increase", 1, 10, int(o_prog.get("freq_inc", 1)), key=f"fi_{d_key}_{n}")
                    o_prog["freq_del"] = l2.number_input("Failed weeks for deload", 1, 10, int(o_prog.get("freq_del", 2)), key=f"fd_{d_key}_{n}")
