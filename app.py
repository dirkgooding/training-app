import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 4

if 'my_plan' not in st.session_state:
    # Initialisierung mit Listen für die Sätze
    st.session_state.my_plan = {
        "Tag A": [
            {"name": "Kniebeugen", "sets": [3] * st.session_state.cycle_weeks},
            {"name": "Bankdrücken", "sets": [3] * st.session_state.cycle_weeks}
        ]
    }

if 'training_logs' not in st.session_state:
    st.session_state.training_logs = {}

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Excel-Export"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        w_idx = st.selectbox("📅 Woche wählen:", range(st.session_state.cycle_weeks), 
                             format_func=lambda x: f"Woche {x+1}")
        w_label = f"Woche {w_idx + 1}"
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen)

    if selected_day in st.session_state.my_plan:
        current_exercises = st.session_state.my_plan[selected_day]
        st.markdown(f"## {selected_day} - {w_label}")
        st.divider()

        for i, ex_data in enumerate(current_exercises):
            name = ex_data["name"]
            sets_list = ex_data["sets"]
            
            # Sicherstellen, dass wir eine Liste haben
            if not isinstance(sets_list, list):
                sets_list = [sets_list] * st.session_state.cycle_weeks
            
            # Aktuelle Satzanzahl für diese Woche
            c_sets = sets_list[w_idx] if w_idx < len(sets_list) else sets_list[-1]
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sätze)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2:
                st.text_input(f"📝 Notiz", key=f"note_{name}_{w_label}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

            for s in range(1, c_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                l_key = f"{w_label}_{selected_day}_{name}_{s}"
                cur_l = st.session_state.training_logs.get(l_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
                
                # Werte sauber auslesen und speichern
                r_kg = s_cols[1].number_input("kg", value=float(cur_l.get("kg", 20.0)), step=1.25, key=f"w_in_{l_key}", label_visibility="collapsed")
                r_r = s_cols[2].number_input("r", value=int(cur_l.get("r", 10)), step=1, key=f"r_in_{l_key}", label_visibility="collapsed")
                r_rir = s_cols[3].number_input("rir", value=int(cur_l.get("rir", 2)), step=1, key=f"rir_in_{l_key}", label_visibility="collapsed")
                r_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(cur_l.get("p", 0)), key=f"p_in_{l_key}", label_visibility="collapsed")
                
                st.session_state.training_logs[l_key] = {"kg": r_kg, "r": r_r, "rir": r_rir, "p": r_p}
            st.divider()

# --- TAB 2: PLANER ---
with tab_plan:
    st.header("📊 Daten-Verwaltung")
    if st.session_state.training_logs:
        exp_list = []
        for k, v in st.session_state.training_logs.items():
            p = k.split("_")
            if len(p) >= 4:
                exp_list.append({"Woche": p[0], "Tag": p[1], "Übung": p[2], "Satz": p[3], "KG": v["kg"], "Reps": v["r"], "RIR": v["rir"], "Pain": v["p"]})
        df = pd.DataFrame(exp_list)
        csv = df.to_csv(index=False, sep=";", encoding="utf-8-sig")
        st.download_button("📥 Excel-Export (CSV)", data=csv, file_name="training_export.csv", mime="text/csv")
        st.dataframe(df, use_container_width=True)

    st.divider()
    st.header("⚙️ Konfiguration")
    
    new_w = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=12, value=st.session_state.cycle_weeks)
    if new_w != st.session_state
