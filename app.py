import streamlit as st
import pandas as pd
from datetime import datetime

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'my_plan' not in st.session_state: st.session_state.my_plan = {"Tag 1": [{"name": "Test 1", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}, {"name": "Test 2", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}], "Tag 2": [{"name": "Test 3", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}, {"name": "Test 4", "sets": [1, 2, 3, 4], "reps": [10, 10, 10, 10]}]}
if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan, tab_data, tab_calendar = st.tabs(["Training", "Planer", "Daten-Verwaltung", "Historie"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("Woche wählen:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Woche {x+1}")
        w_label = f"Woche {w_idx + 1}"
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("Tag wählen:", options=tag_namen)

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
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sätze | Ziel: {c_reps} Reps)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"Notiz", key=f"note_{name}_{w_label}_{selected_day}")

            # Neue Spalte für das Done-Häkchen hinzugefügt
            cols = st.columns([1, 2, 2, 2, 3, 1])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain"); cols[5].caption("Done")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3, 1])
                s_cols[0].write(f"**{s}**")
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": c_reps, "rir": 2, "p": 0, "done": False, "ts": ""})
                
                r_kg = s_cols[1].number_input("kg", value=float(cur_l.get("kg", 20.0)), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("r", value=int(cur_l.get("r", c_reps)), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("rir", value=int(cur_l.get("rir", 2)), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(cur_l.get("p", 0)), key=f"p_in_{l_key}", label_visibility="collapsed")
                r_done = s_cols[5].checkbox("Done", value=cur_l.get("done", False), key=f"done_in_{l_key}", label_visibility="collapsed")
                
                # Zeitstempel-Logik
                ts = cur_l.get("ts", "")
                if r_done and not cur_l.get("done", False):
                    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
                elif not r_done:
                    ts = ""
                
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p, "done": r_done, "ts": ts}
            st.divider()

# --- TAB 2: PLANER (GELOCKT) ---
with tab_plan:
    st.header("Konfiguration")
    
    new_w = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {d_key}", expanded=True):
            new_name = st.text_input("Name des Tages:", value=d_key, key=f"ren_{d_key}")
            
            if new_name != d_key and new_name.strip() != "":
                if new_name not in st.session_state.my_plan:
                    st.session_state.my_plan[new_name] = st.session_state.my_plan.pop(d_key)
                    st.rerun()
                else:
                    st.warning("Dieser Name existiert bereits. Bitte wähle einen anderen.")
                
            cur_exs = st.session_state.my_plan[d_key]
            ex_txt = "\n".join([e["name"] for e in cur_exs])
            new_ex_txt = st.text_area("Übungen (eine pro Zeile):", value=ex_txt, key=f"edit_{d_key}")
            
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            upd_data = []
            
            for n in names:
                st.write(f"**Sätze & Reps für: {n}**")
                o_sets = [3] * st.session_state.cycle_weeks
                o_reps = [10] * st.session_state.cycle_weeks
                for e in cur_exs:
                    if e["name"] == n:
                        if "sets" in e and isinstance(e["sets"], list): o_sets = e["sets"]
                        elif "sets" in e: o_sets = [e["sets"]] * st.session_state.cycle_weeks
                        if "reps" in e and isinstance(e["reps"], list): o_reps = e["reps"]
                        elif "reps" in e: o_reps = [e["reps"]] * st.session_state.cycle_weeks
                
                w_cols = st.columns(st.session_state.cycle_weeks)
                n_sets = []
                n_reps = []
                for w in range(st.session_state.cycle_weeks):
                    v_s = o_sets[w] if w < len(o_sets) else o_sets[-1]
                    v_r = o_reps[w] if w < len(o_reps) else o_reps[-1]
                    s_v = w_cols[w].number_input(f"W{w+1} Sätze", 1, 15, int(v_s), key=f"s_{d_key}_{n}_{w}")
                    r_v = w_cols[w].number_input(f"W{w+1} Reps", 1, 100, int(v_r), key=f"r_{d_key}_{n}_{w}")
                    n_sets.append(s_v)
                    n_reps.append(r_v)
                upd_data.append({"name": n, "sets": n_sets, "reps": n_reps})
                st.divider()
            
            st.session_state.my_plan[d_key] = upd_data
            
            if st.button("Tag löschen", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

    st.divider()
    if st.button("Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Neue Übung", "sets": [3] * st.session_state.cycle_weeks, "reps": [10] * st.session_state.cycle_weeks}]
        st.rerun()

# --- TAB 3: DATEN-VERWALTUNG ---
with tab_data:
    st.header("Daten Import & Export")
    
    uploaded_csv = st.file_uploader("Excel-Import (CSV) hochladen", type=["csv"])
    if uploaded_csv is not None:
        if st.button("Import bestätigen"):
            try:
                df_import = pd.read_csv(uploaded_csv, sep=";")
                if not df_import.empty:
                    for _, row in df_import.iterrows():
                        l_key = f"{row['Woche']}_{row['Tag']}_{row['Übung']}_{row['Satz']}"
                        st.session_state.training_logs[l_key] = {
                            "kg": float(row["KG"]), 
                            "r": int(row["Reps"]), 
                            "rir": int(row["RIR"]), 
                            "p": int(row["Pain"]),
                            "done": True,
                            "ts": str(row["Datum"]) if "Datum" in row else ""
                        }
                st.success("Daten erfolgreich importiert!")
                st.rerun()
            except Exception as e:
                st.error(f"Fehler beim Import: {e}. Bitte stelle sicher, dass es die von hier exportierte CSV-Datei ist.")

    st.divider()
    
    if st.session_state.training_logs:
        exp_list = []
        for k, v in st.session_state.training_logs.items():
            # Exportiert NUR Sätze, die als "done" markiert sind
            if v.get("done", False):
                p = k.split("_")
                if len(p) >= 4:
                    exp_list.append({"Datum": v.get("ts", ""), "Woche": p[0], "Tag": p[1], "Übung": p[2], "Satz": p[3], "KG": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        
        if exp_list:
            df = pd.DataFrame(exp_list)
            csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
            st.download_button("Excel-Export (CSV) herunterladen", data=csv, file_name="training_export.csv", mime="text/csv")
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Noch keine Sätze als erledigt markiert. Nichts zu exportieren.")

# --- TAB 4: HISTORIE ---
with tab_calendar:
    st.header("Trainingshistorie")
    
    if not st.session_state.training_logs:
        st.info("Noch keine Trainingsdaten vorhanden.")
    else:
        hist_list = []
        for k, v in st.session_state.training_logs.items():
            # Zeigt NUR Sätze, die als "done" markiert sind
            if v.get("done", False):
                p = k.split("_")
                if len(p) >= 4:
                    hist_list.append({"Datum": v.get("ts", ""), "Woche": p[0], "Tag": p[1], "Übung": p[2], "Satz": p[3], "KG": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        
        if hist_list:
            df_hist = pd.DataFrame(hist_list)
            wochen = df_hist["Woche"].unique()
            for woche in sorted(wochen):
                with st.expander(f"Ansicht: {woche}", expanded=False):
                    df_woche = df_hist[df_hist["Woche"] == woche]
                    tage = df_woche["Tag"].unique()
                    for tag in sorted(tage):
                        st.markdown(f"**{tag}**")
                        df_tag = df_woche[df_woche["Tag"] == tag]
                        st.dataframe(df_tag[["Datum", "Übung", "Satz", "KG", "Reps", "RIR", "Pain"]], use_container_width=True, hide_index=True)
        else:
            st.info("Noch keine Sätze als erledigt markiert.")
