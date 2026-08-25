import os
import sqlite3
from datetime import datetime
import numpy as np
from PIL import Image
import streamlit as st
import tensorflow as tf

# -----------------------------------------------------------------------------
# CONSTANTS & CONFIGURATION
# -----------------------------------------------------------------------------
DB_FILE = "fundbuero.db"
UPLOAD_DIR = "uploads"
MODEL_PATH = "model.h5"

CONTAINER_MAPPING = {
    0: "Container A: Bekleidung & Sport",
    1: "Container B: Wertsachen & Elektronik"
}

st.set_page_config(page_title="Schul-Fundbüro", page_icon="🎒", layout="wide")

# -----------------------------------------------------------------------------
# INITIALIZATION & CACHING
# -----------------------------------------------------------------------------
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db_connection():
    """Erstellt eine SQLite-Verbindung und gibt sie zurück."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialisiert die Datenbank-Tabelle, falls diese nicht existiert."""
    try:
        with get_db_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    image_path TEXT NOT NULL,
                    container TEXT NOT NULL,
                    description TEXT NOT NULL,
                    date_found TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Fehler bei der Datenbank-Initialisierung: {e}")

@st.cache_resource
def load_ai_model():
    """Lädt das Keras-Modell mit Fehlerbehandlung und Caching."""
    if not os.path.exists(MODEL_PATH):
        st.warning(f"Hinweis: Modelldatei '{MODEL_PATH}' nicht gefunden. KI-Klassifizierung ist deaktiviert.")
        return None
    try:
        model = tf.keras.models.load_model(MODEL_PATH)
        return model
    except Exception as e:
        st.error(f"Fehler beim Laden des KI-Modells ({MODEL_PATH}): {e}")
        return None

# Initialisierungen ausführen
init_db()
model = load_ai_model()

# -----------------------------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------------------------
def predict_container(image: Image.Image):
    """Bereitet das Bild auf und führt die Modell-Inferenz aus."""
    if model is None:
        return None, 0.0
    
    try:
        # Resize auf 224x224 und Pixel-Normalisierung [0, 1]
        img = image.convert("RGB").resize((224, 224))
        img_array = np.array(img, dtype=np.float32) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        class_idx = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))

        predicted_container = CONTAINER_MAPPING.get(class_idx, f"Container {class_idx}")
        return predicted_container, confidence
    except Exception as e:
        st.error(f"Fehler während der KI-Bildanalyse: {e}")
        return None, 0.0

# -----------------------------------------------------------------------------
# USER INTERFACE
# -----------------------------------------------------------------------------
st.title("🎒 Schul-Fundbüro Management")

tab1, tab2 = st.tabs(["📸 Fundgegenstand scannen", "🔍 Suchen & Verwalten"])

# =============================================================================
# TAB 1: NEUEN FUNDGEGENSTAND EINTRAGEN
# =============================================================================
with tab1:
    st.header("Neuen Artikel erfassen")
    
    input_method = st.radio("Bildquelle wählen:", ["Datei-Upload", "Kamera nutzen"], horizontal=True)
    uploaded_image = None

    if input_method == "Datei-Upload":
        uploaded_file = st.file_uploader("Bild des Gegenstands hochladen", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            uploaded_image = Image.open(uploaded_file)
    else:
        camera_file = st.camera_input("Foto aufnehmen")
        if camera_file:
            uploaded_image = Image.open(camera_file)

    if uploaded_image is not None:
        col_img, col_info = st.columns([1, 1])
        
        with col_img:
            st.image(uploaded_image, caption="Vorschau", use_container_width=True)

        with col_info:
            predicted_container = "Container A: Bekleidung & Sport"
            confidence = 0.0

            if model is not None:
                with st.spinner("KI analysiert das Bild..."):
                    predicted_container, confidence = predict_container(uploaded_image)
                st.success(f"**Vorgeschlagener Container:** {predicted_container}")
                st.info(f"**Konfidenz:** {confidence * 100:.1f}%")
            else:
                st.info("Manuelle Container-Zuordnung (kein KI-Modell aktiv).")
                predicted_container = st.selectbox("Container wählen", list(CONTAINER_MAPPING.values()))

            description = st.text_input("Beschreibung / Fundort", placeholder="z. B. Roter Nike-Rucksack, Turnhalle 2")

            if st.button("In Datenbank speichern", type="primary"):
                if not description.strip():
                    st.warning("Bitte gib eine kurze Beschreibung an.")
                else:
                    try:
                        # Bild im Uploads-Ordner speichern
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"item_{timestamp}.jpg"
                        save_path = os.path.join(UPLOAD_DIR, filename)
                        uploaded_image.convert("RGB").save(save_path)

                        # Datenbank-Eintrag erstellen
                        with get_db_connection() as conn:
                            conn.execute(
                                """
                                INSERT INTO items (image_path, container, description, date_found, status)
                                VALUES (?, ?, ?, ?, ?)
                                """,
                                (save_path, predicted_container, description.strip(), datetime.now().strftime("%Y-%m-%d %H:%M"), "Offen")
                            )
                            conn.commit()

                        st.balloons()
                        st.success("Fundgegenstand erfolgreich registriert!")
                    except Exception as e:
                        st.error(f"Fehler beim Speichern des Gegenstands: {e}")

# =============================================================================
# TAB 2: GEGENSTÄNDE SUCHEN & VERWALTEN
# =============================================================================
with tab2:
    st.header("Erfasste Fundgegenstände")

    # Filter-Optionen
    col_search, col_filter_c, col_filter_s = st.columns([2, 1, 1])
    
    with col_search:
        search_term = st.text_input("Freitext-Suche", placeholder="Beschreibung oder Ort durchsuchen...")
    
    with col_filter_c:
        container_filter = st.selectbox("Container-Filter", ["Alle"] + list(CONTAINER_MAPPING.values()))
    
    with col_filter_s:
        status_filter = st.selectbox("Status-Filter", ["Alle", "Offen", "Abgeholt"])

    # Datenbankabfrage aufbauen
    query = "SELECT * FROM items WHERE 1=1"
    params = []

    if search_term:
        query += " AND description LIKE ?"
        params.append(f"%{search_term}%")
    
    if container_filter != "Alle":
        query += " AND container = ?"
        params.append(container_filter)
        
    if status_filter != "Alle":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"

    # Ergebnisse abrufen & anzeigen
    try:
        with get_db_connection() as conn:
            items = conn.execute(query, params).fetchall()

        if not items:
            st.info("Keine passenden Gegenstände gefunden.")
        else:
            # Raster mit 3 Spalten erzeugen
            cols_per_row = 3
            for i in range(0, len(items), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, item in enumerate(items[i:i + cols_per_row]):
                    with cols[j]:
                        with st.container(border=True):
                            if os.path.exists(item["image_path"]):
                                st.image(item["image_path"], use_container_width=True)
                            else:
                                st.caption("🖼️ Bild nicht gefunden")

                            st.markdown(f"**ID:** #{item['id']} | **Status:** `{item['status']}`")
                            st.markdown(f"**Ort/Beschreibung:** {item['description']}")
                            st.markdown(f"**Ort:** {item['container']}")
                            st.caption(f"Datum: {item['date_found']}")

                            if item["status"] == "Offen":
                                if st.button("Als abgeholt markieren", key=f"btn_{item['id']}"):
                                    conn_update = get_db_connection()
                                    conn_update.execute("UPDATE items SET status = 'Abgeholt' WHERE id = ?", (item["id"],))
                                    conn_update.commit()
                                    conn_update.close()
                                    st.rerun()
    except sqlite3.Error as e:
        st.error(f"Fehler beim Abrufen der Daten: {e}")