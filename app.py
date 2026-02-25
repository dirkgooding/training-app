import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# --- UI SETUP ---
st.set_page_config(page_title="Strong-Pain-Coach", layout="centered")

# --- DATABASE CONNECTION ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data():
    try:
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        return df_l, df_s
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_log, df_settings = load_data()

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

if not df_settings.empty and "Exercise" in df_settings.columns:
    exercise = st.selectbox("Wähle Übung", df_settings['Exercise'].tolist())
    
    with st.form("log_form"):
        st.subheader(f"Training loggen")
        
        col1, col2, col3 = st.columns(3)
        w = col1.number_input("KG", value=10.0, step=0.25)
        r = col2.number_input("Reps", value=10, step=1)
        rir = col3.number_input("RIR", value=2, step=1, help="Reps in Reserve (Wie viele hättest du noch geschafft?)")
        
        p = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": exercise, 
                "Weight": w, 
                "Reps": r, 
                "RIR": rir, 
                "Pain": p
            }])
            updated = pd.concat([df_log, new_row], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert inkl. RIR! 🎉")
            st.balloons()
else:
    st.warning("⚠️ Bitte trage im Reiter 'Settings' eine Übung ein.")
