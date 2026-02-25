import streamlit as st
import pandas as pd

# 'wide' nutzt die volle Bildschirmbreite deines Handys
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DEIN TRAININGSPLAN (Hier kannst du Übungen festlegen)
if 'my_plan' not in st.session_state:
    st.session_state.my_plan = {
        "Tag A (Push)": ["Bankdrücken", "Schulterdrücken", "Trizeps Dips"],
        "Tag B (Pull)": ["Klimmzüge", "Rudern", "Bizeps Curls"],
        "Tag C (Beine)": ["Kniebeugen", "Beinstrecker", "Wadenheben"]
    }

st.title("🏋️ Trainings-Einheit")

# 2. TAG WÄHLEN
selected_day = st.selectbox("Welcher Tag steht an?", list(st.session_state.my_plan.keys()))
current_exercises = st.session_state.my_plan[selected_day]

st.markdown("---")

# 3. DAS DASHBOARD (Alles permanent offen)
# Wir nutzen KEINE Expander. Alles ist untereinander sichtbar.
for i, ex in enumerate(current_exercises):
    
    # Header Zeile: Übungsname und Sortier-Buttons
    col_header, col_move = st.columns([7, 3])
    
    with col_header:
        st.subheader(f"{i+1}. {ex}")
    
    with col_move:
        # Hier ist die Logik für das Verschieben (Syntax-Fix für image_217025.png)
        up_col, down_col = st.columns(2)
        if up_col.button("▲", key=f"btn_up_{i}"):
            if i > 0:
                current_exercises[i], current_exercises[i-1] = current_exercises[i-1], current_exercises[i]
                st.rerun()
        if down_col.button("▼", key=f"btn_down_{i}"):
            if i < len(current_exercises)-1:
                current_exercises[i], current_exercises[i+1] = current_exercises[i+1], current_exercises[i]
                st.rerun()

    # Die Satz-Matrix (3 Sätze immer präsent)
    # Layout: Set | KG | Reps | RIR | Pain
    cols = st.columns([1, 2, 2, 2, 3])
    cols[0].write("**Set**")
    cols[1].write("**KG**")
    cols[2].write("**Reps**")
    cols[3].write("**RIR**")
    cols[4].write("**Pain**")

    for s in range(1, 4):
        s_cols = st.columns([1, 2, 2, 2, 3])
        s_cols[0].write(f"#{s}")
        # Keys sind jetzt sauber geschlossen (Fix für image_21c25c.png)
        s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}", label_visibility="collapsed")
        s_cols[2].number_input("r", value=10, step=1, key=f"r_{ex}_{s}", label_visibility="collapsed")
        s_cols[3].number_input("rir", value=2, step=1, key=f"rir_{ex}_{s}", label_visibility="collapsed")
        s_cols[4].select_slider("p", options=[0, 1, 2], key=f"p_{ex}_{s}", label_visibility="collapsed")
    
    st.markdown(" ") # Abstandshalter
    st.divider() # Trennung zur nächsten Übung

# 4. ABSCHLUSS
if st.button("✅ Training beenden & Speichern", use_container_width=True):
    st.balloons()
    st.success("Hervorragend! Alles im Kasten.")
