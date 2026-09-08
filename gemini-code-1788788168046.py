# -*- coding: utf-8 -*-
"""
Fundgrube – Virtuelles Fundbüro 
Angepasst für ein selbsttrainiertes Keras/TensorFlow (.h5) Modell
"""

import json
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
import numpy as np
from PIL import Image, ImageOps

# --- Seiten-Konfiguration ---
st.set_page_config(
    page_title="Fundgrube – Virtuelles Fundbüro",
    page_icon="🔍",
    layout="centered"
)

# --- Design System (Angepasst an die Mockups & Material UI 3) ---
st.markdown(
    """
    <style>
    :root {
        --bg: #FCFAFF;
        --purple-dark: #6B52A3;
        --purple-light: #D4C4F7;
        --purple-subtle: #EFE9FB;
        --text: #17151D;
    }
    
    /* Blasen-Hintergrund basierend auf den Mockups */
    .stApp { 
        background-color: var(--bg);
        background-image: 
            radial-gradient(circle at 10% 20%, var(--purple-subtle) 15%, transparent 15.5%),
            radial-gradient(circle at 85% 15%, var(--purple-subtle) 18%, transparent 18.5%),
            radial-gradient(circle at 50% 50%, var(--purple-subtle) 25%, transparent 25.5%),
            radial-gradient(circle at 20% 85%, var(--purple-subtle) 18%, transparent 18.5%),
            radial-gradient(circle at 85% 85%, var(--purple-subtle) 22%, transparent 22.5%);
        background-attachment: fixed;
    }
    
    #MainMenu, header, footer { visibility: hidden; }
    
    img { border-radius: 20px; }
    
    /* Buttons im Mockup-Design (Pillenform) */
    div.stButton > button {
        width: 100%;
        min-height: 54px;
        border-radius: 999px !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 16px !important;
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 18px rgba(107,82,163,.2);
    }
    div.stButton > button[kind="primary"] {
        background: var(--purple-dark) !important;
        color: white !important;
    }
    div.stButton > button[kind="secondary"] {
        background: var(--purple-light) !important;
        color: var(--purple-dark) !important;
    }

    /* Suchfeld im Mockup-Design */
    .stTextInput input {
        border-radius: 999px !important;
        border: none !important;
        background: var(--purple-light) !important;
        color: var(--purple-dark) !important;
        padding: 1rem 1.5rem !important;
        font-weight: bold;
    }
    .stTextInput input::placeholder {
        color: var(--purple-dark);
        opacity: 0.7;
    }

    /* Text und Layout-Elemente */
    .app-title { text-align:center; font-weight:900; font-size:36px; color:var(--text); margin-top:14px; margin-bottom:6px; }
    .section-label { 
        background-color: var(--purple-light); color: var(--purple-dark); 
        padding: 6px 16px; border-radius: 999px; font-size: 12px; font-weight: bold; 
        display: inline-block; margin-bottom: 12px; 
    }
    .card { 
        background: rgba(255, 255, 255, 0.6); border-radius: 20px; padding: 14px;
        box-shadow: 0 4px 15px rgba(107,82,163,.05); margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.8);
    }
    .tag { 
        background: var(--purple-subtle); color: var(--purple-dark); padding: 4px 12px; 
        border-radius: 12px; font-size: 12px; font-weight: 600; display: inline-block; margin: 2px 4px 2px 0; 
    }
    
    /* Bild-Upload-Box */
    .stFileUploader {
        background: var(--purple-light);
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
    }
    .stFileUploader section { border: none !important; background: transparent !important; }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Pfade & Datenbank ---
BASE = Path(__file__).resolve().parent
BILDORDNER = BASE / "fundgrubebilder"
BILDORDNER.mkdir(parents=True, exist_ok=True)
DB_DATEI = BASE / "fundgrubedb.json"

# =====================================================================
# --- EINSTELLUNGEN FÜR DEIN LOKALES .h5 MODELL ---
# =====================================================================
MODELL_PFAD = "model/keras_model.h5"  # <--- HIER den Namen deiner .h5 Datei eintragen
ZIEL_BILDGROESSE = (224, 224)   # <--- HIER die Größe eintragen, mit der dein Modell trainiert wurde (z.B. 224x224, 150x150)

# Trage hier deine Klassen in GENAU der Reihenfolge ein, wie sie trainiert wurden!
MEINE_KLASSEN = [
    "Pullover", 
    "Hose", 
    "Jacke", 
    "T-Shirt", 
    "Tasche", 
    "Schuhe"
] 
# =====================================================================

@st.cache_resource(show_spinner=False)
def load_ai_model():
    """Lädt dein selbsttrainiertes Keras/TensorFlow Modell (.h5)."""
    import tensorflow as tf
    try:
        model = tf.keras.models.load_model(MODELL_PFAD)
        return model
    except Exception as e:
        st.error(f"Konnte Modell nicht laden. Liegt die Datei '{MODELL_PFAD}' im selben Ordner? Fehler: {e}")
        return None

def run_ai_scan(image: Image.Image):
    """Nutzt das lokale .h5 Modell, um das Bild zu klassifizieren."""
    try:
        model = load_ai_model()
        if model is None:
            return [], "Modell konnte nicht geladen werden."

        import tensorflow as tf
        
        # 1. Bild vorbereiten (Größe anpassen und in Array umwandeln)
        img_resized = image.resize(ZIEL_BILDGROESSE)
        img_array = tf.keras.preprocessing.image.img_to_array(img_resized)
        
        # 2. Normalisierung (Ganz wichtig!)
        # Wenn dein Modell mit Werten zwischen 0 und 1 trainiert wurde, entkommentiere die nächste Zeile:
        # img_array = img_array / 255.0
        
        # 3. Batch-Dimension hinzufügen (aus (224,224,3) wird (1,224,224,3))
        img_batch = np.expand_dims(img_array, axis=0)
        
        # 4. Vorhersage machen
        predictions = model.predict(img_batch)
        
        # 5. Wahrscheinlichste Klasse finden
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        
        # Sicherstellen, dass der Index nicht außerhalb der Liste liegt
        if predicted_class_idx < len(MEINE_KLASSEN):
            best_label = MEINE_KLASSEN[predicted_class_idx]
        else:
            best_label = f"Unbekannte Klasse ({predicted_class_idx})"

        # Rückgabe im Format [(Label, Wahrscheinlichkeit)]
        return [(best_label, confidence)], None
        
    except Exception as exc:
        return [], f"Fehler beim KI-Scan: {str(exc)}"

# --- Datenbank-Initialisierung ---
SEED = [
    {
        "id": "seed-1",
        "name": "Beiger Strickpullover",
        "kategorie": "Pullover",
        "tags": ["Pullover", "beige", "unifarben"],
        "ort": "Stadtbibliothek",
        "datum": "2024-05-14",
        "kontakt": "fundbuero@stadt.example",
        "status": "gefunden",
        "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=85",
    },
]

def speichere_db(items):
    DB_DATEI.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def lade_db():
    if DB_DATEI.exists():
        try:
            return json.loads(DB_DATEI.read_text(encoding="utf-8"))
        except Exception:
            pass
    speichere_db(SEED)
    return [dict(i) for i in SEED]

# --- State ---
if "db" not in st.session_state:
    st.session_state.db = lade_db()
if "page" not in st.session_state:
    st.session_state.page = "home"
if "carousel" not in st.session_state:
    st.session_state.carousel = 0
if "selected" not in st.session_state:
    st.session_state.selected = None
if "scan_res" not in st.session_state:
    st.session_state.scan_res = None

def navigate(page):
    st.session_state.page = page
    st.rerun()

def badge(text):
    return f'<span class="tag">{text}</span>'

# --- UI Views ---
if st.session_state.page == "home":
    st.markdown('<p class="app-title">Fundgrube</p>', unsafe_allow_html=True)
    
    db = st.session_state.db
    st.markdown('<span class="section-label">Zuletzt Hinzugefügt</span>', unsafe_allow_html=True)
    
    if db:
        idx = st.session_state.carousel % len(db)
        akt = db[idx]
        
        # Carousel Anzeige
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(akt["img"], use_container_width=True)
        st.markdown(f'**{akt["name"]}**<br><small>📍 {akt["ort"]}</small>', unsafe_allow_html=True)
        st.markdown("".join(badge(t) for t in akt["tags"][:4]), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 4, 1])
        with c1:
            if st.button("‹"): st.session_state.carousel = (idx - 1) % len(db); st.rerun()
        with c2:
            if st.button("Ansehen", type="secondary"): 
                st.session_state.selected = akt["id"]
                navigate("detail")
        with c3:
            if st.button("›"): st.session_state.carousel = (idx + 1) % len(db); st.rerun()
            
    st.write("")
    if st.button("🔍 Artikel Suchen", type="secondary"):
        navigate("suchen")
    if st.button("↑ Artikel Hochladen", type="primary"):
        st.session_state.scan_res = None
        navigate("hochladen")


elif st.session_state.page == "suchen":
    if st.button("↩", type="secondary"): navigate("home")
    
    query = st.text_input("Suche", placeholder="🔍 Pullover, Jacke, beige...", label_visibility="collapsed")
    
    erg = st.session_state.db
    if query:
        q = query.lower().strip()
        erg = [i for i in erg if q in i["name"].lower() or any(q in t.lower() for t in i["tags"])]
        
    if erg:
        cols = st.columns(2)
        for n, item in enumerate(erg):
            with cols[n % 2]:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.image(item["img"], use_container_width=True)
                st.caption(item["name"])
                if st.button("Ansehen", key=f"btn_{item['id']}", type="secondary"):
                    st.session_state.selected = item["id"]
                    navigate("detail")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Keine passenden Artikel gefunden.")


elif st.session_state.page == "hochladen":
    if st.button("↩", type="secondary"): navigate("home")
    
    uploaded = st.file_uploader("Bild auswählen", type=["jpg", "png", "webp"])
    
    if uploaded:
        try:
            bild_obj = Image.open(uploaded)
            bild_obj = ImageOps.exif_transpose(bild_obj).convert("RGB")
            st.image(bild_obj, use_container_width=True)
        except Exception:
            st.error("Bild konnte nicht geladen werden.")
            
        if st.button("🤖 Hochladen & KI-Scan", type="primary"):
            with st.spinner("Dein lokales Modell analysiert das Bild..."):
                predictions, error = run_ai_scan(bild_obj)
                if not error:
                    st.session_state.scan_res = {
                        "tags": [p[0] for p in predictions],
                        "kategorie": predictions[0][0] if predictions else "Sonstiges"
                    }
                else:
                    st.error(error)
                    
        if st.session_state.scan_res:
            res = st.session_state.scan_res
            st.success(f"Erkannte Kategorie: {', '.join(res['tags'])}")
            
            name = st.text_input("Name", value=f"Neuer Fund ({res['kategorie']})")
            ort = st.text_input("Fundort")
            tags_txt = st.text_input("Tags (durch Komma getrennt)", value=", ".join(res["tags"]))
            
            if st.button("💾 Speichern", type="primary"):
                if not name or not ort:
                    st.warning("Bitte Name und Ort angeben.")
                else:
                    bid = uuid.uuid4().hex
                    pfad = BILDORDNER / f"{bid}.png"
                    bild_obj.save(pfad, format="PNG")
                    
                    eintrag = {
                        "id": bid, "name": name.strip(), "kategorie": res["kategorie"],
                        "tags": [t.strip() for t in tags_txt.split(",") if t.strip()],
                        "ort": ort.strip(), "datum": date.today().isoformat(),
                        "status": "gefunden", "img": str(pfad)
                    }
                    st.session_state.db.insert(0, eintrag)
                    speichere_db(st.session_state.db)
                    st.balloons()
                    st.session_state.selected = bid
                    navigate("detail")


elif st.session_state.page == "detail":
    if st.button("↩", type="secondary"): navigate("home")
    
    item = next((i for i in st.session_state.db if i["id"] == st.session_state.selected), None)
    if item:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.image(item["img"], use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown(f"### {item['name']}")
        st.markdown(f"📍 {item['ort']} &nbsp; · &nbsp; 🗓 {item['datum']}")
        st.markdown("".join(badge(t) for t in item["tags"]), unsafe_allow_html=True)
        st.write("")
        
        if st.button("🔖 Reservieren", type="secondary"):
            st.success("Artikel wurde erfolgreich für dich reserviert!")
            
        if st.button("✉ Kontaktieren", type="primary"):
            st.info("Kontaktanfrage wird vorbereitet...")
            
    else:
        st.error("Artikel nicht gefunden.")
