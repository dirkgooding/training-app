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
        # Wir laden die Daten ohne Cache, um sofort Ergebnisse zu sehen
        df_l = conn.read(worksheet="Log", ttl=0)
        df_s = conn.read(worksheet="Settings", ttl=0)
        return df_l, df_s
    except Exception as e:
        st.error("Verbindung zum privaten Google Sheet fehlgeschlagen.")
        st.info("Bitte prüfe die URL in den Secrets und die Freigabe (Editor).")
        st.stop()

df_log, df_settings = load_data()

# --- LOGIK: PROGRESSION ---
def get_next_values(ex_name):
    if df_settings is None or ex_name not in df_settings['Exercise'].values:
        return 10.0, 10, "Weight", 1.25
        
    set_row = df_settings[df_settings['Exercise'] == ex_name].iloc[0]
    mode, inc = set_row['Mode'], float(set_row['Increment'])
    
    # Historie filtern
    if df_log is not None and not df_log.empty:
        hist = df_log[df_log['Exercise'] == ex_name].copy()
    else:
        hist = pd.DataFrame()

    if hist.empty:
        return 10.0, 10, mode, inc
    
    hist['Date'] = pd.to_datetime(hist['Date'])
    last = hist.sort_values(by='Date').iloc[-1]
    
    curr_w, curr_r, pain = float(last['Weight']), int(last['Reps']), int(last['Pain'])
    factor = 1 if pain == 0 else (-1 if pain == 1 else -2)
    
    if mode == "Weight":
        return curr_w + (factor * inc), curr_r, mode, inc
    else:
        return curr_w, curr_r + (factor * int(inc)), mode, inc

# --- UI: MAIN ---
st.title("🏋️ Strong-Pain-Coach")

if df_settings is not None and not df_settings.empty:
    exercise = st.selectbox("Übung wählen", df_settings['Exercise'].tolist())
    target_w, target_r, m, i = get_next_values(exercise)

    with st.form("log_form"):
        st.subheader(f"Ziel: {target_w} kg x {target_r}")
        c1, c2 = st.columns(2)
        w = c1.number_input("Gewicht", value=float(target_w), step=0.25)
        r = c2.number_input("Reps", value=int(target_r), step=1)
        p = st.select_slider("Schmerz (0=OK, 1=Leicht, 2=Stopp)", options=[0, 1, 2])
        
        if st.form_submit_button("Satz speichern"):
            new_entry = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Exercise": exercise, "Weight": w, "Reps": r, "Pain": p
            }])
            updated = pd.concat([df_log, new_entry], ignore_index=True)
            conn.update(worksheet="Log", data=updated)
            st.success("Gespeichert! 🎉")
            st.balloons()
else:
    st.warning("Keine Übungen im Reiter 'Settings' gefunden.")
