import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- KONFIGURATION ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# --- GOOGLE SHEETS VERBINDUNG ---
# Wir nutzen die TTL=0, damit er nicht alte Daten aus dem Cache lädt
conn = st.connection("gsheets", type=GSheetsConnection)

def save_to_sheets():
    try:
        flat_data = []
        for day, exercises in st.session_state.my_plan.items():
            for ex in exercises:
                flat_data.append({
                    "Tag": day,
                    "Übung": ex["name"],
                    "Sätze": int(ex["sets"])
                })
        df = pd.DataFrame(flat_data)
        # Hier nutzen wir das Update mit expliziter Übergabe
        conn.update(data=df)
        st.success("Plan erfolgreich in Google Sheets gespeichert!")
    except Exception as e:
        st.error(f"Schreibfehler: Stelle sicher, dass das Sheet für 'Jeden mit dem Link' auf 'Bearbeiter' steht! Fehler: {e}")

def load_from_sheets():
    try:
        # Erhöht die Chance, dass er das Sheet findet
        df = conn.read(ttl=0)
        if df is None or df.empty:
            return False
        
        new_plan = {}
        # Wir korrigieren hier den Zugriff auf die Spaltennamen
        for _, row in df.iterrows():
            tag = str(row.iloc[0]) # Spalte 1: Tag
            name = str(row.iloc[1]) # Spalte 2: Übung
            sets = int(row.iloc[2]) # Spalte 3: Sätze
            
            if tag not in new_plan:
                new_plan[tag] = []
            new_plan[tag].append({"name": name, "sets": sets})
        
        if new_plan:
            st.session_state.my_plan = new_plan
            return True
        return False
    except Exception:
        return False

# --- INITIALISIERUNG ---
if 'my_plan' not in st.session_state:
    if not load_from_sheets():
        st.session_state.my_plan = {
            "Tag A": [{"name": "Kniebeugen", "sets": 3}, {"name": "Bankdrücken", "sets": 3}],
            "Tag B": [{"name": "Kreuzheben", "sets": 3}, {"name": "Klimmzüge", "sets": 3}]
        }
    st.session_state.device_settings = {}
    st.session_state.cycle_weeks = 12

# --- TABS ---
tab_train, tab_plan = st.tabs(["🏋️ Training", "⚙️ Planer & Einstellungen"])

# --- TAB 1: TRAINING ---
with tab_train:
    col_nav1, col_nav2 = st.columns(2)
    with col_nav1:
        wochen_liste = [f"Woche {i}" for i in range(1, st.session_state.cycle_weeks + 1)]
        woche = st.selectbox("📅 Woche:", options=wochen_liste, key="select_woche")
    with col_nav2:
        tag_namen = list(st.session_state.my_plan.keys())
        selected_day = st.selectbox("📋 Tag wählen:", options=tag_namen, key="select_tag")

    if selected_day in st.session_state.my_plan:
        current_exercises = st.session_state.my_plan[selected_day]
        st.markdown(f"## {selected_day}")
        st.divider()

        for i, ex_data in enumerate(current_exercises):
            ex_name = ex_data["name"]
            ex_sets = int(ex_data["sets"])
            st.subheader(f"{i+1}. {ex_name}")
            
            c_n1, c_n2 = st.columns(2)
            with c_n1:
                old_val = st.session_state.device_settings.get(ex_name, "")
                st.session_state.device_settings[ex_name] = st.text_input(f"⚙️ Einstellung", value=old_val, key=f"dev_{ex_name}_{selected_day}")
            with c_n2:
                st.text_input(f"📝 Notiz {woche}", key=f"note_{ex_name}_{woche}_{selected_day}")

            cols = st.columns([1, 2, 2, 2, 3])
            cols[0].caption("Set"); cols[1].caption("KG"); cols[2].caption("Reps"); cols[3].caption("RIR"); cols[4].caption("Pain")

            for s in range(1, ex_sets + 1):
                s_cols = st.columns([1, 2, 2, 2, 3])
                s_cols[0].write(f"**{s}**")
                # Syntax-Fix für Bild 1 (Klammern korrekt)
                s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex_name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex_name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex_name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
                s_cols[4].selectbox("p", options=[0, 1, 2], key=f"p_{ex_name}_{s}_{woche}_{selected_day}", label_visibility="collapsed")
            st.divider()

# --- TAB 2: PLANER ---
with tab_plan:
    st.header("Konfiguration")
    if st.button("☁️ PLAN IN GOOGLE SHEETS SICHERN", use_container_width=True, type="primary"):
        save_to_sheets()
    
    st.divider()
    new_cycle = st.number_input("Zyklus-Dauer (Wochen):", min_value=1, max_value=52, value=st.session_state.cycle_weeks, key="cycle_input")
    if new_cycle != st.session_state.cycle_weeks:
        st.session_state.cycle_weeks = new_cycle
        st.rerun()
    
    for day_key in list(st.session_state.my_plan.keys()):
        with st.expander(f"Bearbeite: {day_key}"):
            new_day_name = st.text_input("Name:", value=day_key, key=f"rename_{day_key}")
            current_ex_list = st.session_state.my_plan[day_key]
            ex_names_only = "\n".join([ex["name"] for ex in current_ex_list])
            new_ex_names = st.text_area("Übungen:", value=ex_names_only, key=f"ex_edit_{day_key}")
            
            temp_names = [n.strip() for n in new_ex_names.split("\n") if n.strip()]
            updated_data = []
            for n in temp_names:
                default_s = 3
                for old_ex in current_ex_list:
                    if old_ex["name"] == n: default_s = old_ex["sets"]
                s_val = st.number_input(f"Sätze für {n}:", min_value=1, max_value=15, value=int(default_s), key=f"s_edit_{day_key}_{n}")
                updated_data.append({"name": n, "sets": s_val})
            
            c_save, c_del = st.columns(2)
            # Syntax-Fix für Bild 2 (Doppelpunkt korrekt)
            if c_save.button(f"Übernehmen", key=f"save_btn_{day_key}"):
                if new_day_name != day_key:
                    st.session_state.my_plan.pop(day_key)
                st.session_state.my_plan[new_day_name] = updated_data
                st.rerun()
            if c_del.button(f"🗑️ Löschen", key=f"del_btn_{day_key}"):
                if len(st.session_state.my_plan) > 1:
                    st.session_state.my_plan.pop(day_key)
                    st.rerun()

    if st.button("➕ Neuer Tag"):
        st.session_state.my_plan["Neuer Tag"] = [{"name": "Übung 1", "sets": 3}]
        st.rerun()
