import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A": [{"name": "Kniebeugen", "sets": 3}, {"name": "Bankdrücken", "sets": 3}],
        "Tag B": [{"name": "Kreuzheben", "sets": 3}, {"name": "Klimmzüge", "sets": 3}]
    }

if 'training_logs' not in st.session_state:
    st.session_state.training_logs = {}

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 12

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Excel-Export"])

# --- TAB 1: TRAINING (DEIN KERN) ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", options=wochen_liste)
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen)

    current_exercises = st.session_state.my_plan[selected_day]
    st.markdown(f"## {selected_day} - {woche}")
    st.divider()

    for i, ex_data in enumerate(current_exercises):
        name, sets = ex_data["name"], int(ex_data["sets"])
        st.subheader(f"{i+1}. {name}")
        
        c_n1, c_n2 = st.columns(2)
        with c_n1:
            old_dev = st.session_state.device_settings.get(name, "")
            st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
        with c_n2:
            st.text_input(f"📝 Notiz", key=f"note_{name}_{woche}_{selected_day}")

        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

        for s in range(1, sets + 1):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            
            log_key = f"{woche}_{selected_day}_{name}_{s}"
            current_log = st.session_state.training_logs.get(log_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
            
            res_kg = s_cols[1].number_input("kg", value=float(current_log["kg"]), step=1.25, key=f"w_in_{log_key}", label_visibility="collapsed")
            res_r = s_cols[2].number_input("r", value=int(current_log["r"]), step=1, key=f"r_in_{log_key}", label_visibility="collapsed")
            res_rir = s_cols[3].number_input("rir", value=int(current_log["rir"]), step=1, key=f"rir_in_{log_key}", label_visibility="collapsed")
            res_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(current_log["p"]), key=f"p_in_{log_key}", label_visibility="collapsed")
            
            st.session_state.training_logs[log_key] = {"kg": res_kg, "r": res_r, "rir": res_rir, "p": res_p}
        st.divider()

# --- TAB 2: PLANER & EXPORT (WIEDER VOLLSTÄNDIG) ---
with tab_plan:
    st.header("📊 Excel-Export")
    if st.session_state.training_logs:
        export_list = []
        for key, val in st.session_state.training_logs.items():
            parts = key.split("_")
            if len(parts) >= 4:
                export_list.append({"Woche": parts[0], "Tag": parts[1], "Übung": parts[2], "Satz": parts[3], "KG": val["kg"], "Reps": val["r"], "RIR": val["rir"], "Pain": val["p"]})
        df_export = pd.DataFrame(export_list)
        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button("📥 Als CSV (Excel) herunterladen", data=csv, file_name="training_export.csv", mime="text/csv")
    
    st.divider()
    st.header("⚙️ Trainingsplan-Konfiguration")
    
    # Zyklus-Dauer
    new_cycle = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=52, value=st.session_state.cycle_weeks)
    if new_cycle != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_cycle
        st.rerun()

    # TAGE BEARBEITEN (DEIN URSPRÜNGLICHER PLANER)
    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}", expanded=True):
            new_day_name = st.text_input("Name des Tages:", value=day_key, key=f"rename_{day_key}")
            
            current_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in current_ex_list])
            new_ex_names = st.text_area("Übungen (eine pro Zeile):", value=ex_names_only, key=f"ex_edit_{day_key}")
            
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            updated_data = []
            
            for n in temp_names:
                # Alten Satz-Wert suchen oder Standard 3
                val_s = 3
                for old_ex in current_ex_list:
                    if old_ex["name"] == n:
                        val_s = old_ex["sets"]
                
                s_count = st.number_input(f"Sätze für {n}:", min_value=1, max_value=15, value=int(val_s), key=f"s_edit_{day_key}_{n}")
                updated_data.append({"name": n, "sets": s_count})
            
            c_save, c_del = st.columns(2)
            if c_save.button(f"Speichern", key=f"save_btn_{day_key}"):
                if new_day_name != day_key:
                    st.session_state.my_plan.pop(day_key)
                st.session_state.my_plan[new_day_name] = updated_data
                st.rerun()
            if c_del.button(f"🗑️ Tag löschen", key=f"del_btn_{day_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(day_key)
                    st.rerun()

    if st.button("➕ Neuen Trainingstag hinzufügen"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Übung 1", "sets": 3}]
        st.rerun()
