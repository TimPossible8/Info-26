import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import json
import os
from datetime import datetime

# --- KONFIGURATION & SETUP ---
MODEL_PATH = "model.h5"
DB_PATH = "items.json"
IMAGE_DIR = "images"

# Erstelle den Bilder-Ordner, falls er nicht existiert
os.makedirs(IMAGE_DIR, exist_ok=True)

# Kategorien-Mapping: Passe die Namen und Container an dein trainiertes Modell an.
# Das Modell hat laut Spezifikation 2 Output-Klassen.
CATEGORIES = {
    0: {"name": "Jacke / Oberteil", "container": "Container 1 (Kleidung)"},
    1: {"name": "Mütze / Schal", "container": "Container 2 (Accessoires)"}
}

# --- HILFSFUNKTIONEN ---

@st.cache_resource
def load_ai_model():
    """Lädt das Keras-Modell in den Cache, um Ladezeiten zu minimieren."""
    if not os.path.exists(MODEL_PATH):
        return None
    return tf.keras.models.load_model(MODEL_PATH)

def process_image(img_file):
    """Skaliert das Bild auf 224x224 RGB und konvertiert es in ein float32-Array."""
    img = Image.open(img_file).convert('RGB')
    img = img.resize((224, 224))
    
    # Konvertierung in Float32 Array und Hinzufügen der Batch-Dimension
    img_array = np.array(img, dtype=np.float32)
    img_array = np.expand_dims(img_array, axis=0)
    
    # Optional: Normalisierung (abhängig vom Training, z.B. img_array / 255.0)
    # img_array = img_array / 255.0 
    
    return img, img_array

def load_database():
    """Lädt die JSON-Datenbank."""
    if not os.path.exists(DB_PATH):
        return []
    try:
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []

def save_to_database(item_data):
    """Speichert einen neuen Eintrag in der JSON-Datenbank."""
    db = load_database()
    db.append(item_data)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=4, ensure_ascii=False)

# --- APP-LAYOUT & LOGIK ---

st.set_page_config(page_title="Schul-Fundbüro AI", page_icon="🧥", layout="wide")

# Modell laden
model = load_ai_model()

# Sidebar Navigation
st.sidebar.title("Navigation")
app_mode = st.sidebar.radio("Wähle eine Aktion:", ["Neues Kleidungsstück scannen", "Fundbüro durchsuchen"])

if app_mode == "Neues Kleidungsstück scannen":
    st.title("📸 Neues Kleidungsstück scannen")
    
    if model is None:
        st.error(f"Kritischer Fehler: Das Modell '{MODEL_PATH}' wurde nicht gefunden. Bitte lade die Datei in das Verzeichnis hoch.")
    else:
        # Auswahl der Eingabemethode
        input_method = st.radio("Wie möchtest du das Bild erfassen?", ["Bild hochladen", "Kamera nutzen"])
        
        img_file_buffer = None
        if input_method == "Bild hochladen":
            img_file_buffer = st.file_uploader("Lade ein Bild hoch (JPG, PNG)", type=["jpg", "jpeg", "png"])
        else:
            img_file_buffer = st.camera_input("Mache ein Foto mit der Kamera")
            
        if img_file_buffer is not None:
            # Bild verarbeiten
            display_img, img_array = process_image(img_file_buffer)
            
            # KI Vorhersage
            with st.spinner("KI analysiert das Bild..."):
                predictions = model.predict(img_array)
                class_index = np.argmax(predictions[0])
                confidence = np.max(predictions[0]) * 100
                
                # Zuweisung anhand des Dictionaries
                detected_cat = CATEGORIES.get(class_index, {"name": "Unbekannt", "container": "Sammelbox"})
            
            # Anzeige der Ergebnisse in Spalten
            col1, col2 = st.columns(2)
            with col1:
                st.image(display_img, caption="Erfasstes Bild", use_container_width=True)
            with col2:
                st.success("Analyse erfolgreich!")
                st.metric(label="Erkanntes Kleidungsstück", value=detected_cat["name"])
                st.metric(label="Zuweisung", value=detected_cat["container"])
                st.info(f"Sicherheit der KI: {confidence:.1f}%")
            
            st.divider()
            
            # Metadaten Formular
            st.subheader("Artikel im System speichern")
            with st.form("save_item_form"):
                title = st.text_input("Kurzer Titel (z.B. 'Schwarze Regenjacke')")
                description = st.text_area("Besondere Merkmale (z.B. Marke, Flecken, Größe)")
                submit_btn = st.form_submit_button("Im Fundbüro speichern")
                
                if submit_btn:
                    if not title:
                        st.warning("Bitte gib mindestens einen Titel ein.")
                    else:
                        # Bild lokal speichern
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        img_path = os.path.join(IMAGE_DIR, f"item_{timestamp}.jpg")
                        display_img.save(img_path)
                        
                        # Datensatz erstellen
                        new_item = {
                            "id": timestamp,
                            "title": title,
                            "description": description,
                            "category": detected_cat["name"],
                            "container": detected_cat["container"],
                            "image_path": img_path,
                            "date_added": datetime.now().strftime("%d.%m.%Y %H:%M")
                        }
                        save_to_database(new_item)
                        st.success("Der Artikel wurde erfolgreich in die Datenbank aufgenommen!")

elif app_mode == "Fundbüro durchsuchen":
    st.title("🔍 Fundbüro durchsuchen")
    
    items = load_database()
    
    if not items:
        st.info("Das Fundbüro ist aktuell leer. Es wurden noch keine `items.json` Daten angelegt.")
    else:
        # Suchleiste
        search_query = st.text_input("Suche nach Titel, Beschreibung oder Kleidungsart...", "").lower()
        
        # Filtern der Ergebnisse
        filtered_items = [
            item for item in items 
            if search_query in item["title"].lower() 
            or search_query in item["description"].lower() 
            or search_query in item["category"].lower()
        ]
        
        if not filtered_items:
            st.warning("Keine Artikel gefunden, die deiner Suche entsprechen.")
        else:
            st.write(f"**{len(filtered_items)} Artikel gefunden:**")
            
            # Rasteransicht erstellen (3 Spalten)
            cols = st.columns(3)
            for index, item in enumerate(filtered_items):
                with cols[index % 3]:
                    st.container(border=True)
                    # Bild laden (falls vorhanden)
                    if os.path.exists(item["image_path"]):
                        st.image(item["image_path"], use_container_width=True)
                    else:
                        st.warning("Bilddatei fehlt.")
                        
                    st.subheader(item["title"])
                    st.write(f"**Kategorie:** {item['category']}")
                    st.write(f"**Lagerort:** {item['container']}")
                    st.write(f"**Datum:** {item['date_added']}")
                    if item["description"]:
                        st.write(f"**Info:** {item['description']}")
                    st.write("---")