# -*- coding: utf-8 -*-
"""
Fundgrube – Virtuelles Fundbüro
================================
Streamlit-App mit echtem CLIP Zero-Shot KI-Modell (aus fundgrube_app.py)
und UI-Design orientiert an den mobilen SVG-Mockups.

Installation:
    pip install streamlit pillow transformers torch

Start:
    streamlit run fundgrubeqwen.py
"""

import json
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
from PIL import Image, ImageOps

# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Fundgrube – Virtuelles Fundbüro",
    page_icon="🔍",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# DESIGN SYSTEM – SVG-Mockups (Lavendel)
# =========================================================
st.markdown(
    """
    <style>
        :root {
            --bg: #F8F5FE;
            --surface: #FFFFFF;
            --surface-soft: #EEE9F7;
            --lavender: #D4C4F7;
            --lavender-2: #C8B5F0;
            --purple: #6B52A3;
            --purple-dark: #55408A;
            --text: #17151D;
            --muted: #716B7D;
            --border: #E5DFF0;
            --shadow: 0 10px 30px rgba(74, 54, 120, .10);
        }

        * { box-sizing: border-box; }

        .stApp {
            background:
                radial-gradient(circle at 10% 12%, rgba(212,196,247,.48) 0 22px, transparent 23px),
                radial-gradient(circle at 82% 10%, rgba(212,196,247,.38) 0 34px, transparent 35px),
                radial-gradient(circle at 18% 44%, rgba(212,196,247,.30) 0 28px, transparent 29px),
                radial-gradient(circle at 88% 48%, rgba(212,196,247,.30) 0 25px, transparent 26px),
                radial-gradient(circle at 35% 82%, rgba(212,196,247,.34) 0 38px, transparent 39px),
                var(--bg);
        }

        #MainMenu, header, footer { visibility: hidden; height: 0; }

        .block-container {
            max-width: 470px;
            padding: 1.1rem 1rem 2.5rem;
        }

        .brand {
            text-align: center;
            font-size: 2rem;
            line-height: 1;
            font-weight: 900;
            letter-spacing: -1.2px;
            color: var(--text);
            margin: .35rem 0 .15rem;
        }

        .brand-sub {
            text-align: center;
            color: var(--purple);
            font-size: .8rem;
            font-weight: 700;
            margin: 0 0 1.25rem;
        }

        .section-label {
            display: inline-block;
            padding: .34rem .85rem;
            border-radius: 999px;
            background: var(--lavender);
            color: var(--purple);
            font-size: .72rem;
            font-weight: 800;
            margin: 0 0 -.1rem .75rem;
            position: relative;
            z-index: 3;
        }

        .hero-card {
            background: var(--surface);
            border-radius: 25px;
            padding: .45rem .45rem .8rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(107,82,163,.08);
        }

        .hero-card img {
            width: 100%;
            aspect-ratio: 1.45 / 1;
            object-fit: cover;
            border-radius: 20px;
        }

        .item-title {
            font-size: 1.25rem;
            font-weight: 850;
            color: var(--text);
            margin: .85rem .2rem .15rem;
        }

        .muted {
            color: var(--muted);
            font-size: .88rem;
        }

        .pill {
            display: inline-block;
            background: #EEE9F7;
            color: var(--purple);
            border-radius: 999px;
            padding: .3rem .65rem;
            margin: .2rem .15rem .2rem 0;
            font-size: .72rem;
            font-weight: 750;
        }

        .status {
            display: inline-block;
            border-radius: 999px;
            padding: .25rem .7rem;
            margin-left: .4rem;
            font-size: .68rem;
            font-weight: 800;
            vertical-align: 2px;
        }
        .status-gefunden       { background: #DFF5E1; color: #2E7D32; }
        .status-vermisst       { background: #FDE3E3; color: #C62828; }
        .status-zurueckgegeben { background: #E3E3E3; color: #555; }

        .search-shell {
            background: var(--lavender);
            border-radius: 999px;
            padding: .05rem .3rem;
            margin-bottom: .9rem;
            box-shadow: var(--shadow);
        }
        .search-shell [data-testid="stTextInput"] input,
        .search-shell .stTextInput input {
            background: transparent !important;
            box-shadow: none !important;
        }

        .empty-state {
            text-align: center;
            padding: 2.4rem 1rem;
            color: var(--muted);
            background: rgba(255,255,255,.65);
            border: 1px dashed var(--border);
            border-radius: 24px;
        }

        .upload-box {
            background: var(--lavender);
            border-radius: 25px;
            min-height: 250px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            color: var(--purple);
            box-shadow: var(--shadow);
        }

        .upload-icon {
            font-size: 3rem;
            display: block;
            margin-bottom: .35rem;
        }

        .grid-card {
            background: var(--surface);
            border-radius: 18px;
            padding: .4rem .4rem .75rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(107,82,163,.08);
            margin-bottom: .85rem;
        }

        .grid-card img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 14px;
        }

        .grid-caption {
            font-size: .84rem;
            font-weight: 800;
            color: var(--text);
            margin: .45rem .3rem .2rem;
        }

        .stat-card {
            background: rgba(255,255,255,.78);
            border: 1px solid var(--border);
            border-radius: 18px;
            padding: .75rem;
            text-align: center;
        }

        .stat-number {
            font-size: 1.15rem;
            font-weight: 900;
            color: var(--purple);
        }

        .stat-label {
            color: var(--muted);
            font-size: .68rem;
        }

        .ai-card {
            background: var(--surface-soft);
            border-radius: 20px;
            padding: 1rem 1.1rem;
            border: 1px solid var(--border);
        }

        .ai-headline {
            font-weight: 900;
            color: var(--text);
            margin-bottom: .4rem;
            font-size: .95rem;
        }

        .confidence-bar {
            background: var(--lavender);
            border-radius: 999px;
            height: 10px;
            overflow: hidden;
            margin: .5rem 0 .3rem;
        }

        .confidence-fill {
            background: linear-gradient(90deg, var(--purple), var(--lavender-2));
            height: 100%;
            border-radius: 999px;
        }

        .divider {
            height: 1px;
            background: var(--border);
            margin: 1rem 0;
        }

        /* --- Buttons (Pill-Style wie Mockups) --- */
        div.stButton > button {
            width: 100%;
            min-height: 48px;
            border-radius: 999px !important;
            border: 0 !important;
            font-weight: 800 !important;
            letter-spacing: -.1px;
            transition: transform .15s ease, box-shadow .15s ease;
        }
        div.stButton > button:hover {
            transform: translateY(-1px);
            box-shadow: 0 8px 18px rgba(107,82,163,.18);
        }
        div.stButton > button[kind="primary"] {
            background: var(--purple) !important;
            color: white !important;
        }
        div.stButton > button[kind="secondary"],
        div.stButton > button.secondary {
            background: var(--lavender) !important;
            color: var(--purple) !important;
        }

        /* --- Widgets --- */
        [data-testid="stTextInput"] input, .stTextInput input {
            border-radius: 999px !important;
            border: 0 !important;
            background: var(--surface) !important;
            padding: .75rem 1rem !important;
            box-shadow: var(--shadow);
        }
        [data-testid="stTextArea"] textarea, .stTextArea textarea {
            border-radius: 18px !important;
            border: 0 !important;
            background: var(--surface) !important;
            padding: .75rem 1rem !important;
            box-shadow: var(--shadow);
        }
        [data-testid="stDateInput"] input, .stDateInput input {
            border-radius: 999px !important;
            border: 0 !important;
            background: var(--surface) !important;
            padding: .55rem 1rem !important;
            box-shadow: var(--shadow);
        }
        div[data-baseweb="select"] > div {
            border-radius: 999px !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            box-shadow: var(--shadow);
            min-height: 46px;
        }
        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stDateInput"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stRadio"] > label {
            font-size: .78rem !important;
            font-weight: 800 !important;
            color: var(--purple) !important;
        }
        div[role="radiogroup"] {
            background: var(--surface-soft);
            border-radius: 999px;
            padding: .25rem .3rem;
        }
        div[role="radiogroup"] label {
            padding: .35rem .9rem;
            border-radius: 999px;
            font-size: .82rem;
            font-weight: 700;
        }

        .stFileUploader, [data-testid="stFileUploader"] {
            background: var(--lavender);
            border-radius: 25px;
            padding: .65rem;
            margin-bottom: .75rem;
        }
        .stFileUploader section, [data-testid="stFileUploader"] section {
            border: 0 !important;
            background: transparent !important;
        }
        .stFileUploader label, [data-testid="stFileUploader"] label {
            display: none !important;
        }

        .stImage img, [data-testid="stImage"] img {
            border-radius: 20px;
        }

        @media (max-width: 520px) {
            .block-container { padding-left: .75rem; padding-right: .75rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# PFADE & DATENBANK
# =========================================================
BASE = Path(__file__).resolve().parent
BILDORDNER = BASE / "fundgrubebilder"
BILDORDNER.mkdir(parents=True, exist_ok=True)
DB_DATEI = BASE / "fundgrubedb.json"

# =========================================================
# KI-MODELL – CLIP Zero-Shot (Implementierung aus fundgrube_app.py)
# =========================================================
@st.cache_resource(show_spinner=False)
def load_ai_model():
    """
    Lädt CLIP statt eines normalen ImageNet-Klassifikators.

    Warum CLIP?
    Das alte ViT-Modell kennt nur die festen ImageNet-Klassen. Für eine
    Fundgrube-App führt das zu schlechten Ergebnissen wie "jersey", "web site"
    oder komplett unpassenden Objekten. CLIP kann ein Bild direkt mit unseren
    eigenen Begriffen vergleichen.
    """
    from transformers import pipeline

    return pipeline(
        "zero-shot-image-classification",
        model="openai/clip-vit-base-patch32",
    )


AI_LABELS = {
    "category": {
        # Kleidung
        "hoodie": "Hoodie",
        "sweatshirt": "Sweatshirt",
        "sweater": "Pullover",
        "knitted sweater": "Strickpullover",
        "jacket": "Jacke",
        "coat": "Mantel",
        "t-shirt": "T-Shirt",
        "shirt": "Hemd",
        "trousers": "Hose",
        "jeans": "Jeans",
        "shorts": "Shorts",
        "dress": "Kleid",
        "skirt": "Rock",
        "shoes": "Schuhe",
        "sneakers": "Sneaker",
        "boots": "Stiefel",
        "backpack": "Rucksack",
        "cap": "Mütze",
        "beanie": "Mütze",
        "hat": "Hut",
        "scarf": "Schal",
        "gloves": "Handschuhe",
        "bag": "Tasche",
        "handbag": "Handtasche",
        # Typische Fundbüro-Funde (Erweiterung gegenüber fundgrube_app.py)
        "umbrella": "Regenschirm",
        "wristwatch": "Uhr",
        "wallet": "Portemonnaie",
        "keys": "Schlüsselbund",
        "glasses": "Brille",
        "sunglasses": "Sonnenbrille",
        "plush toy": "Kuscheltier",
        "stuffed animal": "Kuscheltier",
        "book": "Buch",
        "headphones": "Kopfhörer",
        "phone": "Smartphone",
    },
    "color": {
        "black": "schwarz",
        "white": "weiß",
        "grey": "grau",
        "beige": "beige",
        "brown": "braun",
        "red": "rot",
        "orange": "orange",
        "yellow": "gelb",
        "green": "grün",
        "mint green": "mint",
        "blue": "blau",
        "navy blue": "dunkelblau",
        "purple": "lila",
        "pink": "rosa",
    },
    "style": {
        "sporty clothing": "sportlich",
        "winter clothing": "Winter",
        "casual clothing": "casual",
        "formal clothing": "elegant",
        "striped clothing": "gestreift",
        "plain clothing": "unifarben",
        "patterned clothing": "gemustert",
        "hooded clothing": "mit Kapuze",
        "denim clothing": "Denim",
        "knitted clothing": "Strick",
        "leather item": "Leder",
    },
}


def _best_clip_label(classifier, image, labels):
    """Gibt das wahrscheinlichste Label und seine Konfidenz zurück."""
    candidates = list(labels.keys())
    results = classifier(image, candidate_labels=candidates)
    if not results:
        return None, 0.0

    best = results[0]
    return best["label"], float(best["score"])


def run_ai_scan(image: Image.Image):
    """
    Erkennt Kategorie, Farbe und Stil/Eigenschaften mit CLIP.

    Es werden bewusst getrennte Klassifikationen durchgeführt. Dadurch kann
    die KI gleichzeitig z. B. "Pullover + beige + Strick" erkennen, statt
    fünf nahezu identische ImageNet-Klassen zurückzugeben.
    """
    try:
        classifier = load_ai_model()
    except Exception as exc:
        return None, (
            "KI-Modell konnte nicht geladen werden. Prüfe die Internetverbindung "
            "und installiere die Abhängigkeiten (pip install transformers torch). "
            f"Details: {exc}"
        )

    ergebnis = {
        "kategorie": "Sonstiges",
        "konfidenz": 0.0,
        "farbe": None,
        "farbe_konfidenz": 0.0,
        "stil": [],
        "tags": [],
        "modell": "clip",
    }

    try:
        # 1) Hauptkategorie
        label, score = _best_clip_label(classifier, image, AI_LABELS["category"])
        if label:
            ergebnis["kategorie"] = AI_LABELS["category"][label]
            ergebnis["konfidenz"] = round(score, 2)

        # 2) Farbe – nur bei ausreichender Sicherheit übernehmen
        label, score = _best_clip_label(classifier, image, AI_LABELS["color"])
        if label and score >= 0.18:
            ergebnis["farbe"] = AI_LABELS["color"][label]
            ergebnis["farbe_konfidenz"] = round(score, 2)

        # 3) Stil / Muster / Material – die zwei besten Treffer
        style_results = classifier(
            image, candidate_labels=list(AI_LABELS["style"].keys())
        )
        for r in (style_results or [])[:2]:
            if float(r["score"]) >= 0.22:
                stil = AI_LABELS["style"][r["label"]]
                if stil not in ergebnis["stil"]:
                    ergebnis["stil"].append(stil)
    except Exception as exc:
        return None, f"Fehler während des KI-Scans: {exc}"

    # Tags ohne Duplikate, Reihenfolge behalten
    kandidaten = [ergebnis["kategorie"].lower()]
    if ergebnis["farbe"]:
        kandidaten.append(ergebnis["farbe"])
    kandidaten += [s.lower() for s in ergebnis["stil"]]

    tags, gesehen = [], set()
    for t in kandidaten:
        if t and t not in gesehen:
            gesehen.add(t)
            tags.append(t)
    ergebnis["tags"] = tags[:5]

    return ergebnis, None


def basis_scan():
    """Fallback, falls die KI nicht verfügbar ist – Eintrag bleibt möglich."""
    return {
        "kategorie": "Sonstiges",
        "konfidenz": 0.0,
        "farbe": None,
        "farbe_konfidenz": 0.0,
        "stil": [],
        "tags": ["sonstiges"],
        "modell": "manuell",
    }

# =========================================================
# SEED-DATEN (im neuen KI-Format)
# =========================================================
SEED = [
    {
        "id": "seed-1",
        "name": "Beiger Strickpullover",
        "art": "gefunden",
        "kategorie": "Pullover",
        "tags": ["pullover", "beige", "strick", "unifarben"],
        "ort": "Stadtbibliothek, 2. OG",
        "datum": "2024-05-14",
        "kontakt": "fundbuero@stadt.example",
        "status": "gefunden",
        "beschreibung": "Weicher Strickpullover, gefunden im Lesesaal.",
        "img": "https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/1d93f06d3-e699-478f-b5ab-1c80c9f270f7.png",
        "ki": {
            "kategorie": "Pullover",
            "konfidenz": 0.93,
            "farbe": "beige",
            "farbe_konfidenz": 0.55,
            "stil": ["Strick", "unifarben"],
            "tags": ["pullover", "beige", "strick", "unifarben"],
            "modell": "clip",
        },
    },
    {
        "id": "seed-2",
        "name": "Roter Rentier-Pulli",
        "art": "vermisst",
        "kategorie": "Pullover",
        "tags": ["pullover", "rot", "gemustert", "winter"],
        "ort": "Weihnachtsmarkt, Innenstadt",
        "datum": "2024-05-10",
        "kontakt": "anna@beispiel.de",
        "status": "vermisst",
        "beschreibung": "Weihnachtspullover mit weißem Rentier, sehr sentimental.",
        "img": "https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/168fbd83f-e612-4312-b852-b759a837bec2.png",
        "ki": {
            "kategorie": "Pullover",
            "konfidenz": 0.91,
            "farbe": "rot",
            "farbe_konfidenz": 0.61,
            "stil": ["gemustert", "Winter"],
            "tags": ["pullover", "rot", "gemustert", "winter"],
            "modell": "clip",
        },
    },
    {
        "id": "seed-3",
        "name": "Schwarze Lederhandschuhe",
        "art": "gefunden",
        "kategorie": "Handschuhe",
        "tags": ["handschuhe", "schwarz", "leder", "unifarben"],
        "ort": "Bushaltestelle Bahnhofstraße",
        "datum": "2024-05-12",
        "kontakt": "fundbuero@stadt.example",
        "status": "gefunden",
        "beschreibung": "Paar schwarze Lederhandschuhe auf einer Bank gefunden.",
        "img": "https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/15a9f5af0-4f00-436c-846d-2b28f45c8668.png",
        "ki": {
            "kategorie": "Handschuhe",
            "konfidenz": 0.89,
            "farbe": "schwarz",
            "farbe_konfidenz": 0.72,
            "stil": ["Leder", "unifarben"],
            "tags": ["handschuhe", "schwarz", "leder", "unifarben"],
            "modell": "clip",
        },
    },
    {
        "id": "seed-4",
        "name": "Blauer Rucksack",
        "art": "vermisst",
        "kategorie": "Rucksack",
        "tags": ["rucksack", "blau", "unifarben", "sportlich"],
        "ort": "Uni-Mensa, Campus Nord",
        "datum": "2024-05-08",
        "kontakt": "max@beispiel.de",
        "status": "vermisst",
        "beschreibung": "Blauer Rucksack mit silbernen Reißverschlüssen, Laptopfach.",
        "img": "https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/10568a9d7-a103-4755-a7fb-04a7ea6c3348.png",
        "ki": {
            "kategorie": "Rucksack",
            "konfidenz": 0.95,
            "farbe": "blau",
            "farbe_konfidenz": 0.64,
            "stil": ["unifarben", "sportlich"],
            "tags": ["rucksack", "blau", "unifarben", "sportlich"],
            "modell": "clip",
        },
    },
]

# =========================================================
# DATENBANK-FUNKTIONEN
# =========================================================
def speichere_db(items):
    """Speichert die Datenbank in eine JSON-Datei."""
    DB_DATEI.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def lade_db():
    """Lädt die Datenbank aus der JSON-Datei oder erstellt SEED-Daten."""
    if DB_DATEI.exists():
        try:
            return json.loads(DB_DATEI.read_text(encoding="utf-8"))
        except Exception:
            pass
    speichere_db(SEED)
    return [dict(i) for i in SEED]

# =========================================================
# SESSION-STATE
# =========================================================
if "db" not in st.session_state:
    st.session_state.db = lade_db()
if "page" not in st.session_state:
    st.session_state.page = "home"
if "carousel" not in st.session_state:
    st.session_state.carousel = 0
if "selected" not in st.session_state:
    st.session_state.selected = None
if "scan" not in st.session_state:
    st.session_state.scan = None
if "scan_error" not in st.session_state:
    st.session_state.scan_error = None
if "scanfile" not in st.session_state:
    st.session_state.scanfile = None
if "zeigekontakt" not in st.session_state:
    st.session_state.zeigekontakt = False

# =========================================================
# HILFSFUNKTIONEN
# =========================================================
def go(page):
    st.session_state.page = page
    st.session_state.zeigekontakt = False
    st.rerun()


def header():
    if st.session_state.page != "home":
        if st.button("←  Zurück", key="global_back"):
            go("home")
    st.markdown("<div class='brand'>Fundgrube</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='brand-sub'>Virtuelles Fundbüro – Verlorenes wiederfinden</div>",
        unsafe_allow_html=True,
    )


def status_badge(status):
    cls = {
        "gefunden": "status-gefunden",
        "vermisst": "status-vermisst",
        "zurückgegeben": "status-zurueckgegeben",
    }.get(status, "status-gefunden")
    return f"<span class='status {cls}'>{status}</span>"


def pills_html(tags, limit=6):
    return "".join(f"<span class='pill'>{t}</span>" for t in (tags or [])[:limit])


def ai_karte_scan_html(res):
    """KI-Ergebnis als HTML-Karte (Upload-Seite)."""
    prozent = int(max(0.0, min(1.0, float(res.get("konfidenz") or 0))) * 100)
    farbe = res.get("farbe")
    stil = res.get("stil") or []
    modell = (res.get("modell") or "KI").upper()
    return (
        "<div class='ai-card'>"
        "<div class='ai-headline'>🤖 KI-Erkenntnis</div>"
        f"<div>Erkannte Kategorie: <strong>{res['kategorie']}</strong>"
        f" <span class='muted'>· Modell: {modell}</span></div>"
        f"<div class='confidence-bar'><div class='confidence-fill' style='width:{prozent}%'></div></div>"
        f"<div class='muted'>Konfidenz: {prozent} %</div>"
        "<div class='divider'></div>"
        f"<div class='muted'>Farbe: <strong>{farbe or '–'}</strong></div>"
        f"<div class='muted'>Merkmale: <strong>{', '.join(stil) or '–'}</strong></div>"
        f"<div style='margin-top:.6rem'>{pills_html(res.get('tags'))}</div>"
        "</div>"
    )


def ki_karte_detail_html(item):
    """KI-Analyse in der Detailansicht – abwärtskompatibel zum alten DB-Format."""
    ki = item.get("ki") or {}
    kategorie = ki.get("kategorie") or item.get("kategorie") or "–"
    prozent = int(max(0.0, min(1.0, float(ki.get("konfidenz") or 0))) * 100)

    farbe = ki.get("farbe")
    farben = [farbe] if farbe else list(ki.get("farben") or [])
    stil = list(ki.get("stil") or ki.get("muster") or [])
    modell = (ki.get("modell") or "KI").upper()

    return (
        "<div class='ai-card'>"
        "<div class='ai-headline'>🤖 KI-Analyse</div>"
        f"<div>Erkannte Kategorie: <strong>{kategorie}</strong>"
        f" <span class='muted'>· Modell: {modell}</span></div>"
        f"<div class='confidence-bar'><div class='confidence-fill' style='width:{prozent}%'></div></div>"
        f"<div class='muted'>Konfidenz: {prozent} %</div>"
        f"<div class='muted' style='margin-top:.35rem'>Farbe: <strong>{', '.join(farben) or '–'}</strong></div>"
        f"<div class='muted'>Merkmale: <strong>{', '.join(stil) or '–'}</strong></div>"
        "</div>"
    )

# =========================================================
# SEITE: START
# =========================================================
def render_home():
    header()

    db = st.session_state.db
    gefunden = sum(1 for i in db if i["art"] == "gefunden")
    vermisst = sum(1 for i in db if i["art"] == "vermisst")
    offen = sum(1 for i in db if i["status"] != "zurückgegeben")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{gefunden}</div>"
            "<div class='stat-label'>Funde</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{vermisst}</div>"
            "<div class='stat-label'>Vermisst</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{offen}</div>"
            "<div class='stat-label'>Offen</div></div>", unsafe_allow_html=True)

    st.write("")
    st.markdown("<span class='section-label'>Zuletzt hinzugefügt</span>", unsafe_allow_html=True)

    liste = sorted(db, key=lambda i: i["datum"], reverse=True)
    if not liste:
        st.markdown(
            "<div class='empty-state'>Noch keine Einträge vorhanden.<br>"
            "Melde deinen ersten Fund!</div>", unsafe_allow_html=True)
        if st.button("↥  Fund melden", type="primary", key="home_upload_empty"):
            go("hochladen")
        return

    idx = st.session_state.carousel % len(liste)
    akt = liste[idx]

    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.image(akt["img"], use_container_width=True)
    st.markdown(
        f"<div class='item-title'>{akt['name']} {status_badge(akt['status'])}</div>"
        f"<div class='muted' style='margin:.1rem .25rem .35rem'>📍 {akt['ort']} · 🗓 {akt['datum']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div style='padding:0 .25rem'>{pills_html(akt['tags'], 4)}</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("")
    a, b, c = st.columns([1, 3, 1])
    with a:
        if st.button("‹", key="prev_item"):
            st.session_state.carousel = (idx - 1) % len(liste)
            st.rerun()
    with b:
        if st.button("Ansehen", key="home_detail", type="secondary"):
            st.session_state.selected = akt["id"]
            go("detail")
    with c:
        if st.button("›", key="next_item"):
            st.session_state.carousel = (idx + 1) % len(liste)
            st.rerun()

    st.write("")
    if st.button("⌕  Fundstück suchen", key="home_search", type="secondary"):
        go("suchen")
    st.write("")
    if st.button("↥  Fund melden", key="home_upload", type="primary"):
        go("hochladen")

# =========================================================
# SEITE: SUCHE
# =========================================================
def render_suchen():
    header()
    st.markdown("<span class='section-label'>Fundstück suchen</span>", unsafe_allow_html=True)
    st.write("")

    st.markdown("<div class='search-shell'>", unsafe_allow_html=True)
    query = st.text_input(
        "Suchbegriff", placeholder="Pullover, beige, Bibliothek …",
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    f1, f2 = st.columns(2)
    with f1:
        status_filter = st.selectbox("Status", ["Alle", "gefunden", "vermisst", "zurückgegeben"])
    with f2:
        kats = ["Alle"] + sorted({i.get("kategorie", "Sonstiges") for i in st.session_state.db})
        kat_filter = st.selectbox("Kategorie", kats)

    erg = st.session_state.db
    q = query.lower().strip()
    if q:
        erg = [
            i for i in erg
            if q in i["name"].lower()
            or q in i["ort"].lower()
            or q in i.get("kategorie", "").lower()
            or any(q in t.lower() for t in i.get("tags", []))
        ]
    if status_filter != "Alle":
        erg = [i for i in erg if i["status"] == status_filter]
    if kat_filter != "Alle":
        erg = [i for i in erg if i.get("kategorie") == kat_filter]

    st.caption(f"{len(erg)} Treffer")

    if not erg:
        st.markdown(
            "<div class='empty-state'><strong>Kein Treffer</strong><br>"
            "Versuche einen anderen Suchbegriff – oder melde den Fund selbst.</div>",
            unsafe_allow_html=True,
        )
        if st.button("↥  Fund melden", type="primary", key="search_empty_upload"):
            go("hochladen")
        return

    cols = st.columns(2)
    for n, item in enumerate(erg):
        with cols[n % 2]:
            st.markdown("<div class='grid-card'>", unsafe_allow_html=True)
            st.image(item["img"], use_container_width=True)
            st.markdown(
                f"<div class='grid-caption'>{item['name']} {status_badge(item['status'])}</div>"
                f"<div class='muted' style='margin:.1rem .3rem .3rem'>📍 {item['ort']}</div>"
                f"<div style='padding:0 .3rem'>{pills_html(item['tags'], 3)}</div>",
                unsafe_allow_html=True,
            )
            if st.button("Ansehen", key=f"view_{item['id']}", type="secondary"):
                st.session_state.selected = item["id"]
                go("detail")
            st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# SEITE: HOCHLADEN / KI-SCAN
# =========================================================
def render_hochladen():
    header()
    st.markdown("<span class='section-label'>Fund melden / Vermisstenanzeige</span>", unsafe_allow_html=True)
    st.write("")

    uploaded = st.file_uploader(
        "Foto hochladen", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if not uploaded:
        st.markdown(
            "<div class='upload-box'><div><span class='upload-icon'>↥</span>"
            "<strong>Foto hochladen</strong><br>"
            "<span class='muted'>JPG, PNG oder WEBP – die KI erkennt Kategorie, Farbe &amp; Merkmale</span>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        return

    # Scan zurücksetzen, wenn eine neue Datei hochgeladen wurde
    if uploaded.name != st.session_state.scanfile:
        st.session_state.scan = None
        st.session_state.scan_error = None
        st.session_state.scanfile = uploaded.name

    try:
        bild_obj = Image.open(uploaded)
        bild_obj = ImageOps.exif_transpose(bild_obj).convert("RGB")
    except Exception:
        st.error("Das Bild konnte nicht geöffnet werden.")
        return

    st.image(bild_obj, use_container_width=True)
    st.write("")

    if st.button("🤖 Hochladen & KI-Scan", type="primary", key="start_scan"):
        with st.spinner("KI analysiert das Bild … (erstes Laden dauert kurz)"):
            res, error = run_ai_scan(bild_obj)
        if res:
            st.session_state.scan = res
            st.session_state.scan_error = None
        else:
            # KI nicht verfügbar → trotzdem fortfahren (Basis-Eintrag)
            st.session_state.scan = basis_scan()
            st.session_state.scan_error = error

    if st.session_state.scan_error:
        st.warning(st.session_state.scan_error)

    if not st.session_state.scan:
        st.info("Starte den KI-Scan – Kategorie, Farbe & Merkmale werden automatisch erkannt.")
        return

    res = st.session_state.scan
    st.markdown(ai_karte_scan_html(res), unsafe_allow_html=True)
    st.write("")

    st.markdown("<span class='section-label'>Angaben zum Eintrag</span>", unsafe_allow_html=True)
    st.write("")

    name = st.text_input("Bezeichnung", value=res["kategorie"])
    art = st.radio("Art", ["gefunden", "vermisst"], horizontal=True)
    ort = st.text_input("Fundort / Verlustort")
    datum = st.date_input("Datum", value=date.today())
    kontakt = st.text_input("Kontakt (E-Mail / Telefon)")
    beschreibung = st.text_area("Beschreibung")
    tags_txt = st.text_input("Tags (KI-Vorschlag, anpassbar)", value=", ".join(res["tags"]))

    if st.button("💾 In Fundgrube aufnehmen", type="primary", key="save_item"):
        if not name.strip() or not ort.strip():
            st.warning("Bitte mindestens Bezeichnung und Ort angeben.")
        else:
            bid = uuid.uuid4().hex
            pfad = BILDORDNER / f"{bid}.png"
            bild_obj.save(pfad, format="PNG")
            eintrag = {
                "id": bid,
                "name": name.strip(),
                "art": art,
                "kategorie": res["kategorie"],
                "tags": [t.strip() for t in tags_txt.split(",") if t.strip()],
                "ort": ort.strip(),
                "datum": datum.isoformat(),
                "kontakt": kontakt.strip(),
                "beschreibung": beschreibung.strip(),
                "status": art,
                "img": str(pfad),
                "ki": res,
            }
            st.session_state.db.insert(0, eintrag)
            speichere_db(st.session_state.db)
            st.session_state.scan = None
            st.session_state.scan_error = None
            st.session_state.scanfile = None
            st.session_state.selected = bid
            st.balloons()
            go("detail")

# =========================================================
# SEITE: DETAIL
# =========================================================
def render_detail():
    header()
    item = next((i for i in st.session_state.db if i["id"] == st.session_state.selected), None)

    if not item:
        st.markdown(
            "<div class='empty-state'>Dieser Eintrag ist nicht mehr verfügbar.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Zur Startseite", type="primary", key="detail_notfound"):
            go("home")
        return

    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.image(item["img"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"<div class='item-title'>{item['name']} {status_badge(item['status'])}</div>"
        f"<div class='muted' style='margin:.15rem .2rem .4rem'>📍 {item['ort']} · 🗓 {item['datum']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(pills_html(item["tags"]), unsafe_allow_html=True)

    if item.get("beschreibung"):
        st.markdown(
            f"<div class='muted' style='margin:.7rem .2rem'>{item['beschreibung']}</div>",
            unsafe_allow_html=True,
        )

    st.write("")
    ki = item.get("ki") or {}
    konfidenz = int(max(0.0, min(1.0, float(ki.get("konfidenz") or 0))) * 100)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{item.get('kategorie', '–')}</div>"
            "<div class='stat-label'>Kategorie</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{konfidenz} %</div>"
            "<div class='stat-label'>KI-Konfidenz</div></div>", unsafe_allow_html=True)

    st.write("")
    st.markdown(ki_karte_detail_html(item), unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("✉  Kontakt anzeigen", type="primary", key="show_contact"):
            st.session_state.zeigekontakt = not st.session_state.zeigekontakt
    with c2:
        if item["status"] != "zurückgegeben":
            if st.button("✅  Zurückgegeben", type="secondary", key="mark_returned"):
                item["status"] = "zurückgegeben"
                speichere_db(st.session_state.db)
                st.rerun()

    if st.session_state.zeigekontakt:
        st.markdown(
            "<div class='ai-card'><strong>📞 Kontakt</strong><br>"
            f"<span class='muted'>{item.get('kontakt') or 'Kein Kontakt hinterlegt'}</span></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    if st.button("🗑  Eintrag entfernen", key="delete_item"):
        st.session_state.db = [i for i in st.session_state.db if i["id"] != item["id"]]
        speichere_db(st.session_state.db)
        go("home")

# =========================================================
# ROUTER
# =========================================================
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "suchen":
    render_suchen()
elif st.session_state.page == "hochladen":
    render_hochladen()
elif st.session_state.page == "detail":
    render_detail()
else:
    go("home")
