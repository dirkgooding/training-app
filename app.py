import streamlit as st

# 'wide' für optimale Smartphone-Darstellung
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DATENSTRUKTUR
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

st.title("🏋️ Trainings-Steuerung")

# --- NAVIGATION: WOCHE & TAG ALS DROPDOWN ---
col_nav1, col_nav2 = st.columns(2)

with col_nav1:
    # Woche als Dropdown statt Slider
    woche = st.selectbox(
        "📅 Wähle die Woche:", 
        options=[f"Woche {i}" for i in range(1, 13)],
        index=0
    )

with col_nav2:
    # Tag als Dropdown
    selected_day = st.selectbox(
        "📋 Welchen Tag heute?", 
        options=list(st.session_state.my_plan.keys()),
        index=0
    )

st.markdown(f"## {selected_day} <small>({woche})</small>", unsafe_allow_html=True)
st.divider()

# --- DIE ÜBUNGEN DES TAGES ---
current_exercises = st.session_state.my_plan[selected_day]

for i, ex in enumerate(current_exercises):
    # Header mit Sortierung
    col_h, col_m = st.columns([8, 2])
    col_h.subheader(f"{i+1}. {ex}")
    
    with col_m:
        up, down = st.columns(2)
        if up.button("▲", key=f"up_{ex}_{i}") and i > 0:
            current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
            st.rerun()
        if down.button("▼", key=f"down_{ex}_{i}") and i < len(current_exercises)-1:
            current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
            st.rerun()

    # NOTIZFELDER
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        old_val = st.session_state.device_settings.get(ex, "")
        st.session_state.device_settings[ex] = st.text_input(
            f"⚙️ Einstellung (fest)", value=old_val, key=f"dev_{ex}"
        )
    with col_n2:
        st.text_input(f"📝 Notiz {woche}", key=f"note_{ex}_{woche}")

    # SATZ-MATRIX
    cols = st.columns([1, 2, 2, 2, 3])
    cols[0].caption("Set")
    cols[1].caption("KG")
    cols[2].caption("Reps")
    cols[3].caption("RIR")
    cols[4].caption("Pain")

    for s in range(1, 4):
        s_cols = st.columns([1, 2, 2, 2, 3])
        s_cols[0].write(f"**{s}**")
        
        # Eingabefelder
        s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}_{woche}", label_visibility="collapsed")
        s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}_{woche}", label_visibility="collapsed")
        
        # Schmerz als Dropdown statt Slider
        s_cols[4].selectbox(
            "p", 
            options=[0, 1, 2], 
            key=f"p_{ex}_{s}_{woche}", 
            label_visibility="collapsed",
            format_func=lambda x: f"Schmerz: {x}"
        )
    
    st.divider()

# SPEICHERN
if st.button("✅ Trainingstag abschließen", use_container_width=True):
    st.balloons()
    st.success(f"Daten für {selected_day} ({woche}) gesichert!")
