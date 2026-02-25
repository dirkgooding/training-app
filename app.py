import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'cycle_weeks' not in st.session_state: st.session_state.cycle_weeks = 4
if 'my_plan' not in st.session_state: st.session_state.my_plan = {"Tag A": [{"name": "Kniebeugen", "sets": [3] * st.session_state.cycle_weeks}, {"name": "Bankdrücken", "sets": [3] * st.session_state.cycle_weeks}]}
if 'training_logs' not in st.session_state: st.session_state.training_logs = {}
if 'device_settings' not in st.session_state: st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan = st.tabs(["Training", "Planer & Excel-Export"])

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
            sets_list = ex_data["sets"]
            
            if not isinstance(sets_list, list): sets_list = [sets_list] * st.session_state.cycle_weeks
            
            c_sets = sets_list[w_idx] if w_idx < len(sets_list) else sets_list[-1]
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sätze)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"Notiz", key=f"note_{name}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
                
                r_kg = s_cols[1].number_input("kg", value=float(cur_l.get("kg", 20.0)), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("r", value=int(cur_l.get("r", 10)), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("rir", value=int(cur_l.get("rir", 2)), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(cur_l.get("p", 0)), key=f"p_in_{l_key}", label_visibility="collapsed")
                
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p}
            st.divider()

# --- TAB 2: PLANER ---
with tab_plan:
    st.header("Daten-Verwaltung")
    
    uploaded_csv = st.file_uploader("Excel-Import (CSV) hochladen", type=["csv"])
    if uploaded_csv is not None:
        try:
            df_import = pd.read_csv(uploaded_csv, sep=";")
            for _, row in df_import.iterrows():
                l_key = f"{row['Woche']}_{row['Tag']}_{row['Übung']}_{row['Satz']}"
                st.session_state.training_logs[l_key] = {"kg": float(row["KG"]), "r": int(row["Reps"]), "rir": int(row["RIR"]), "p": int(row["Pain"])}
            st.success("Daten erfolgreich importiert!")
        except Exception as e:
            st.error(f"Fehler beim Import: {e}. Bitte stelle sicher, dass es die von hier exportierte CSV-Datei ist.")

    if st.session_state.training_logs:
        exp_list = []
        for k, v in st.session_state.training_logs.items():
            p = k.split("_")
            if len(p) >= 4:
                exp_list.append({"Woche": p[0], "Tag": p[1], "Übung": p[2], "Satz": p[3], "KG": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        df = pd.DataFrame(exp_list)
        csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button("Excel-Export (CSV)", data=csv, file_name="training_export.csv", mime="text/csv")
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.header("Konfiguration")
    
    new_w = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_w != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_w
        st.rerun()

    for d_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {d_key}", expanded=True):
            new_name = st.text_input("Name des Tages:", value=d_key, key=f"ren_{d_key}")
            cur_exs = st.session_state.my_plan[d_key]
            ex_txt = "\n".join([e["name"] for e in cur_exs])
            new_ex_txt = st.text_area("Übungen (eine pro Zeile):", value=ex_txt, key=f"edit_{d_key}")
            
            names = [n.strip() for n in new_ex_txt.split("\n") if n.strip()]
            upd_data = []
            
            for n in names:
                st.write(f"**Sätze pro Woche für: {n}**")
                o_sets = [3] * st.session_state.cycle_weeks
                for e in cur_exs:
                    if e["name"] == n:
                        if isinstance(e["sets"], list): o_sets = e["sets"]
                        else: o_sets = [e["sets"]] * st.session_state.cycle_weeks
                
                w_cols = st.columns(st.session_state.cycle_weeks)
                n_sets = []
                for w in range(st.session_state.cycle_weeks):
                    v = o_sets[w] if w < len(o_sets) else o_sets[-1]
                    s_v = w_cols[w].number_input(f"W{w+1}", 1, 15, int(v), key=f"s_{d_key}_{n}_{w}")
                    n_sets.append(s_v)
                upd_data.append({"name": n, "sets": n_sets})
                st.divider()
            
            st.session_state.my_plan[d_key] = upd_data
            
            c_s, c_d = st.columns(2)
            if c_s.button("Tag umbenennen", key=f"save_{d_key}"):
                if new_name != d_key:
                    st.session_state.my_plan.pop(d_key)
                    st.session_state.my_plan[new_name] = upd_data
                    st.rerun()
            if c_d.button("Tag löschen", key=f"del_{d_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(d_key)
                    st.rerun()

    st.divider()
    if st.button("Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Neue Übung", "sets": [3] * st.session_state.cycle_weeks}]
        st.rerun()
