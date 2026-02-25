import streamlit as st
import pandas as pd
import io

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

# --- TAB 1: TRAINING ---
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
            
            # Eindeutiger Key für Speicherung
            log_key = f"{woche}_{selected_day}_{name}_{s}"
            current_log = st.session_state.training_logs.get(log_key, {"kg": 20.0, "r": 10, "rir": 2, "p": 0})
            
            # Eingabe
            res_kg = s_cols[1].number_input("kg", value=float(current_log["kg"]), step=1.25, key=f"w_in_{log_key}", label_visibility="collapsed")
            res_r = s_cols[2].number_input("r", value=int(current_log["r"]), step=1, key=f"r_in_{log_key}", label_visibility="collapsed")
            res_rir = s_cols[3].number_input("rir", value=int(current_log["rir"]), step=1, key=f"rir_in_{log_key}", label_visibility="collapsed")
            res_p = s_cols[4].selectbox("p", options=[0, 1, 2], index=int(current_log["p"]), key=f"p_in_{log_key}", label_visibility="collapsed")
            
            # Sofort-Speicherung im State
            st.session_state.training_logs[log_key] = {"kg": res_kg, "r": res_r, "rir": res_rir, "p": res_p}
            
        st.divider()

# --- TAB 2: PLANER & EXCEL-EXPORT ---
with tab_plan:
    st.header("📊 Daten-Export für Excel")
    
    if st.session_state.training_logs:
        # Umwandlung der Logs in eine Liste für den CSV-Export
        export_list = []
        for key, val in st.session_state.training_logs.items():
            # Key splitten: Woche_Tag_Übung_Satz
            parts = key.split("_")
            if len(parts) >= 4:
                export_list.append({
                    "Woche": parts[0],
                    "Tag": parts[1],
                    "Übung": parts[2],
                    "Satz": parts[3],
                    "KG": val["kg"],
                    "Reps": val["r"],
                    "RIR": val["rir"],
                    "Pain": val["p"]
                })
        
        df_export = pd.DataFrame(export_list)
        
        # CSV-Erstellung
        csv = df_export.to_csv(index=False, sep=";", encoding="utf-8-sig")
        
        st.download_button(
            label="📥 Trainingsdaten als CSV (Excel) herunterladen",
            data=csv,
            file_name="mein_training_export.csv",
            mime="text/csv",
            use_container_width=True
        )
        st.dataframe(df_export, use_container_width=True) # Vorschau
    else:
        st.info("Noch keine Trainingsdaten vorhanden. Trage Werte im Training-Tab ein!")

    st.divider()
    st.header("Konfiguration")
    
    # ... (Restliche Planer-Logik wie gehabt) ...
    # Hier folgt der bekannte Code für die Zyklus-Wochen und Übungseinstellungen
