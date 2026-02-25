import streamlit as st
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- INITIALISIERUNG ---
if 'cycle_weeks' not in st.session_state:
    st.session_state.cycle_weeks = 4

if 'my_plan' not in st.session_state:
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
        w_idx = st.selectbox("📅 Woche wählen:", range(st.session_state.cycle_weeks), format_func=lambda x: f"Woche {x+1}")
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
            
            if not isinstance(sets_list, list):
                sets_list = [sets_list] * st.session_state.cycle_weeks
            
            c_sets = sets_list[w_idx] if w_idx < len(sets_list) else sets_list[-1]
            
            st.subheader(f"{i+1}. {name} ({c_sets} Sätze)")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_dev = st.session_state.device_settings.get(name, "")
                st.session_state.device_settings[name] = st.text_input(f"⚙️ Einstellung", value=old_dev, key=f"dev_{name}_{selected_day}")
            with c_n2
