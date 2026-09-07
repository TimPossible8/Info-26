# -*- coding: utf-8 -*-
"""
Fundgrube – Virtuelles Fundbüro 
Inklusive verbessertem KI-Scan (CLIP) und Material/Mockup-Design
"""

import json
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
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

# --- Pfade & Datenbank (Aus fundgrubeqwen.py) ---
BASE = Path(__file__).resolve().parent
BILDORDNER = BASE / "fundgrubebilder"
BILDORDNER.mkdir(parents=True, exist_ok=True)
DB_DATEI = BASE / "fundgrubedb.json"

# --- KI-Modell & Labels (Aus fundgrube_app.py) ---
AI_LABELS = {
    "category": {
        "hoodie": "Hoodie", "sweatshirt": "Sweatshirt", "sweater": "Pullover",
        "knitted sweater": "Strickpullover", "jacket": "Jacke", "coat": "Mantel",
        "t-shirt": "T-Shirt", "shirt": "Hemd", "trousers": "Hose", "jeans": "Jeans",
        "dress": "Kleid", "skirt": "Rock", "shoes": "Schuhe", "sneakers": "Sneaker",
        "backpack": "Rucksack", "cap": "Mütze / Cap", "scarf": "Schal", "gloves": "Handschuhe",
        "bag": "Tasche",
    },
    "color": {
        "black": "schwarz", "white": "weiß", "grey": "grau", "beige": "beige",
        "brown": "braun", "red": "rot", "orange": "orange", "yellow": "gelb",
        "green": "grün", "mint green": "mint", "blue": "blau", "purple": "lila",
        "pink": "rosa",
    },
    "style": {
        "sporty clothing": "sportlich", "winter clothing": "Winter",
        "casual clothing": "casual", "striped clothing": "gestreift",
        "plain clothing": "unifarben", "patterned clothing": "gemustert",
    },
}

@st.cache_resource(show_spinner=False)
def load_ai_model():
    """Lädt CLIP für Zero-Shot Klassifikation."""
    from transformers import pipeline
    return pipeline("zero-shot-image-classification", model="openai/clip-vit-base-patch32")

def _best_clip_label(classifier, image, labels):
    """Gibt das wahrscheinlichste Label und seine Konfidenz zurück."""
    candidates = list(labels.keys())
    results = classifier(image, candidate_labels=candidates)
    if not results:
        return None, 0.0
    best = results[0]
    return best["label"], float(best["score"])

def run_ai_scan(image: Image.Image):
    """Erkennt Kleidungsstück, Farbe und sichtbare Eigenschaften mit CLIP."""
    try:
        classifier = load_ai_model()
        detected = []
        confidence = {}

        # 1. Hauptkategorie
        cat_label, cat_score = _best_clip_label(classifier, image, AI_LABELS["category"])
        if cat_label:
            category = AI_LABELS["category"][cat_label]
            detected.append(category)
            confidence["category"] = cat_score

        # 2. Farbe
        col_label, col_score = _best_clip_label(classifier, image, AI_LABELS["color"])
        if col_label and col_score >= 0.18:
            detected.append(AI_LABELS["color"][col_label])

        # 3. Stil / Muster
        style_results = classifier(image, candidate_labels=list(AI_LABELS["style"].keys()))
        if style_results:
            for result in style_results[:2]:
                if float(result["score"]) >= 0.22:
                    detected.append(AI_LABELS["style"][result["label"]])

        unique_tags = []
        for tag in detected:
            tag_clean = tag.strip()
            if tag_clean and tag_clean not in unique_tags:
                unique_tags.append(tag_clean)

        if not unique_tags:
            return [], "KI konnte keine spezifischen Merkmale erkennen."

        return [(t, confidence.get("category", 0.0)) for t in unique_tags[:5]], None
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
            with st.spinner("KI-Modell analysiert das Bild..."):
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
            st.success(f"Erkannte Tags: {', '.join(res['tags'])}")
            
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
        
        # Buttons wie im Detail-Mockup (4.jpg)
        if st.button("🔖 Reservieren", type="secondary"):
            st.success("Artikel wurde erfolgreich für dich reserviert!")
            
        if st.button("✉ Kontaktieren", type="primary"):
            st.info("Kontaktanfrage wird vorbereitet...")
            
    else:
        st.error("Artikel nicht gefunden.")