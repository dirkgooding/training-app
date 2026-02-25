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
        up, down = st.
