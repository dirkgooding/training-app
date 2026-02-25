import streamlit as st

# 'wide' Layout nutzen, damit die Tabellen Platz haben
st.set_page_config(page_title="Strong-Pain-Coach", layout="wide")

# 1. DEIN GESAMTER TRAININGSPLAN (Alle Tage untereinander)
# Du kannst hier einfach weitere Übungen in die Listen schreiben
TRAINING_PLAN = {
    "Tag A (Unterkörper)": ["Kniebeugen", "Beinstrecker", "Wadenheben"],
    "Tag B (Oberkörper)": ["Bankdrücken", "Rudern", "Schulterdrücken"],
    "Tag C (Zusatz/Reha)": ["Tibialis Curl", "Facepulls"]
}

# Permanenter Speicher für Geräte-Einstellungen (z.B. Sitzhöhe)
if 'device_settings' not in st.session_state:
    st.session_state.device_settings = {}

st.title("🏋️ Mein Trainingszyklus")

# --- DIE WOCHE ALS HAUPTSCHALTER ---
# Dieser Schalter ändert die Daten für die GESAMTE Seite
woche = st.select_slider(
    "📅 Aktuelle Trainingswoche auswählen:", 
    options=[f"Woche {i}" for i in range(1, 13)]
)

st.markdown(f"# {woche}")
st.info("Alle Tage deines Plans sind unten aufgelistet. Scrolle einfach zum jeweiligen Tag.")

# --- DAS DASHBOARD (Alle Tage untereinander) ---
for tag_name, exercises in TRAINING_PLAN.items():
    st.markdown(f"## 🔴 {tag_name}")
    st.divider()

    for i, ex in enumerate(exercises):
        # Übungs-Header
        st.subheader(f"{ex}")

        # NOTIZFELDER
        col_note1, col_note2 = st.columns(2)
        with col_note1:
            # IMMER DA: Geräte-Einstellung (Persistent)
            old_val = st.session_state.device_settings.get(ex, "")
            new_val = st.text_input(f"⚙️ Gerät (fest)", value=old_val, key=f"device_{ex}")
            st.session_state.device_settings[ex] = new_val
        with col_note2:
            # NUR FÜR DIESE WOCHE: Notiz
            st.text_input(f"📝 Notiz für {woche}", key=f"note_{ex}_{woche}")

        # DIE SATZ-MATRIX (3 Sätze)
        cols = st.columns([1, 2, 2, 2, 3])
        cols[0].caption("Set")
        cols[1].caption("KG")
        cols[2].caption("Reps")
        cols[3].caption("RIR")
        cols[4].caption("Pain")

        for s in range(1, 4):
            s_cols = st.columns([1, 2, 2, 2, 3])
            s_cols[0].write(f"**{s}**")
            # Daten sind an die Woche gekoppelt
            s_cols[1].number_input("kg", value=20.0, step=1.25, key=f"w_{ex}_{s}_{woche}", label_visibility="
