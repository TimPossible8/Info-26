# -*- coding: utf-8 -*-
"""
Fundgrube – Virtuelles Fundbüro
================================
Streamlit-App mit echtem CLIP Zero-Shot KI-Modell und
mobil optimiertem Layout (Handy-Format, automatisch responsiv).

Installation:
    pip install streamlit pillow transformers torch

Start:
    streamlit run fundgrubeqwen.py
"""

import base64
import io
import json
import uuid
from datetime import date
from html import escape as _esc
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
# DESIGN SYSTEM – mobil optimiert (Lavendel)
#  * fluide Maße via clamp() → passt sich der Fensterbreite an
#  * Flex-Layouts statt fester Spalten
#  * Media Queries für sehr schmale / flache Screens
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

        * { box-sizing: border-box; -webkit-tap-highlight-color: transparent; }
        html { -webkit-text-size-adjust: 100%; }

        /* Nie horizontal scrollen, egal wie schmal das Fenster ist */
        html, body, .stApp { max-width: 100vw; overflow-x: hidden; }

        .stApp {
            background:
                radial-gradient(circle at 10% 12%, rgba(212,196,247,.48) 0 22px, transparent 23px),
                radial-gradient(circle at 82% 10%, rgba(212,196,247,.38) 0 34px, transparent 35px),
                radial-gradient(circle at 18% 44%, rgba(212,196,247,.30) 0 28px, transparent 29px),
                radial-gradient(circle at 88% 48%, rgba(212,196,247,.30) 0 25px, transparent 26px),
                radial-gradient(circle at 35% 82%, rgba(212,196,247,.34) 0 38px, transparent 39px),
                var(--bg);
        }

        /* --- Streamlit-Chrome ausblenden --- */
        #MainMenu, header, footer,
        [data-testid="stToolbar"], [data-testid="stDecoration"], [data-testid="stStatusWidget"] {
            display: none !important;
            height: 0 !important;
            min-height: 0 !important;
        }

        /* --- Inhaltsbühne --- */
        .block-container,
        .main .block-container,
        [data-testid="stAppViewBlockContainer"],
        [data-testid="stMainBlockContainer"] {
            max-width: 470px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            padding:
                .55rem
                clamp(.55rem, 3.2vw, 1rem)
                calc(1.5rem + env(safe-area-inset-bottom))
                !important;
        }

        /* --- FIX: EINheitlicher vertikaler Rhythmus.
               Streamlit-Elemente bringen je nach Version eigene Außenabstände
               mit – zusammen mit dem Gap des VerticalBlock führte das zu
               aneinanderklebenden bzw. verschobenen Elementen.
               Jetzt: alle Element-Margins auf 0, der Gap regelt ALLE Abstände. --- */
        [data-testid="stVerticalBlock"] { gap: .55rem !important; }
        [data-testid="stElementContainer"],
        [data-testid="stMarkdownContainer"],
        [data-testid="stImage"],
        [data-testid="stAlert"],
        [data-testid="stFileUploader"],
        [data-testid="stTextInput"],
        [data-testid="stTextArea"],
        [data-testid="stDateInput"],
        [data-testid="stSelectbox"],
        [data-testid="stRadio"],
        div.stButton { margin: 0 !important; }
        [data-testid="stMarkdownContainer"] > p { margin: 0 !important; }
        [data-testid="stWidgetLabel"] { padding-bottom: .15rem !important; }

        /* --- FIX: Spalten müssen schrumpfen dürfen. Ohne min-width: 0
               drücken breite Inhalte (Bilder, Karten) Nachbar-Spalten
               beiseite. Der alte Selektor kannte nur den veralteten
               Testid "column" – aktuelle Versionen nutzen "stColumn". --- */
        [data-testid="stHorizontalBlock"] { gap: .5rem !important; }
        [data-testid="column"], [data-testid="stColumn"] { min-width: 0 !important; }

        /* --- Marke --- */
        .brand {
            text-align: center;
            font-size: clamp(1.5rem, 8.5vw, 2rem);
            line-height: 1.05;
            font-weight: 900;
            letter-spacing: -1.1px;
            color: var(--text);
            margin: .2rem 0 .05rem;
        }
        .brand-sub {
            text-align: center;
            color: var(--purple);
            font-size: clamp(.7rem, 3.2vw, .8rem);
            font-weight: 700;
            margin: 0 0 .25rem;
        }

        /* --- FIX: Kompakte App-Kopfzeile. Statt des fragilen Tricks mit
               fester line-height wird flexibel zentriert. Der Titel ist
               exakt so hoch wie der Zurück-Button (46 px) und kann dank
               overflow: hidden nie in den Button hineinragen. --- */
        .brand-kompakt {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 46px;
            font-size: clamp(.95rem, 4vw, 1.05rem);
            font-weight: 900;
            letter-spacing: -.4px;
            color: var(--text);
            white-space: nowrap;
            overflow: hidden;
        }

        .section-label {
            display: inline-block;
            padding: .3rem .8rem;
            border-radius: 999px;
            background: var(--lavender);
            color: var(--purple);
            font-size: .7rem;
            font-weight: 800;
            margin: .3rem 0 .05rem .05rem;
        }

        /* --- Statistikleiste --- */
        .stats-row { display: flex; gap: .45rem; margin-top: .1rem; }
        .stats-row .stat-card { flex: 1 1 0; min-width: 0; }
        .stat-card {
            background: rgba(255,255,255,.78);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: .55rem .3rem;
            text-align: center;
        }
        .stat-number {
            font-size: clamp(.95rem, 4vw, 1.15rem);
            font-weight: 900;
            color: var(--purple);
            line-height: 1.25;
            overflow-wrap: anywhere;
        }
        .stat-label { color: var(--muted); font-size: .66rem; }

        /* --- Echte HTML-Karten --- */
        .hero-card {
            background: var(--surface);
            border-radius: 25px;
            padding: .4rem .4rem .6rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(107,82,163,.08);
        }
        .hero-card img {
            width: 100%;
            aspect-ratio: 1.45 / 1;
            object-fit: cover;
            border-radius: 20px;
            display: block;
        }
        .grid-card {
            background: var(--surface);
            border-radius: 18px;
            padding: .3rem .3rem .55rem;
            box-shadow: var(--shadow);
            border: 1px solid rgba(107,82,163,.08);
        }
        .grid-card img {
            width: 100%;
            aspect-ratio: 1 / 1;
            object-fit: cover;
            border-radius: 14px;
            display: block;
        }

        /* --- FIX: Titelzeilen als Flex-Row mit Umbruch. Vorher war das
               Status-Badge inline mit vertical-align hinter dem Titel und
               lief bei langen Namen in den Text / die Nachbarzeile. --- */
        .item-title {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: .2rem .3rem;
            font-size: clamp(1.05rem, 4.6vw, 1.25rem);
            font-weight: 850;
            color: var(--text);
            margin: .5rem .35rem .05rem;
            overflow-wrap: anywhere;
        }
        .grid-caption {
            display: flex;
            align-items: center;
            flex-wrap: wrap;
            gap: .15rem .25rem;
            font-size: clamp(.74rem, 3.2vw, .84rem);
            font-weight: 800;
            color: var(--text);
            margin: .3rem .35rem .05rem;
            overflow-wrap: anywhere;
        }
        .meta-zeile { margin: .05rem .35rem .2rem; font-size: .8rem; }
        .grid-meta { margin: .05rem .35rem .15rem; font-size: .72rem; }
        .muted { color: var(--muted); font-size: .85rem; }
        .beschreibung { margin: .15rem .35rem .2rem; }

        .pill-row { padding: 0 .35rem; }
        .pill {
            display: inline-block;
            background: var(--surface-soft);
            color: var(--purple);
            border-radius: 999px;
            padding: .26rem .6rem;
            margin: .15rem .2rem 0 0;
            font-size: clamp(.62rem, 2.8vw, .72rem);
            font-weight: 750;
        }

        /* --- FIX: Badge ohne eigenen Außenabstand (Abstand macht die
               gap der Titel-Flex-Row), bleibt bei langen Titeln ganz. --- */
        .status {
            display: inline-block;
            border-radius: 999px;
            padding: .22rem .65rem;
            font-size: .66rem;
            font-weight: 800;
            white-space: nowrap;
            flex: 0 0 auto;
        }
        .status-gefunden       { background: #DFF5E1; color: #2E7D32; }
        .status-vermisst       { background: #FDE3E3; color: #C62828; }
        .status-zurueckgegeben { background: #E3E3E3; color: #555; }

        /* --- Suchfeld-Schale: deckt jetzt ALLE Wrapping-Varianten ab
               (Marker direkt, in einem <p> oder im ElementContainer). --- */
        .search-marker { display: none; }
        div:has(.search-marker) + [data-testid="stTextInput"],
        div:has(.search-marker) + [data-testid="stElementContainer"]:has([data-testid="stTextInput"]),
        [data-testid="stElementContainer"]:has(.search-marker) + [data-testid="stTextInput"],
        [data-testid="stElementContainer"]:has(.search-marker)
            + [data-testid="stElementContainer"]:has([data-testid="stTextInput"]) {
            background: var(--lavender);
            border-radius: 999px;
            padding: .3rem .5rem;
            box-shadow: var(--shadow);
        }
        div:has(.search-marker) + [data-testid="stTextInput"] input,
        div:has(.search-marker) + [data-testid="stElementContainer"] [data-testid="stTextInput"] input,
        [data-testid="stElementContainer"]:has(.search-marker) + [data-testid="stTextInput"] input,
        [data-testid="stElementContainer"]:has(.search-marker)
            + [data-testid="stElementContainer"] [data-testid="stTextInput"] input {
            box-shadow: none !important;
            background: var(--surface) !important;
        }

        .empty-state {
            text-align: center;
            padding: 1.5rem .9rem;
            color: var(--muted);
            background: rgba(255,255,255,.65);
            border: 1px dashed var(--border);
            border-radius: 20px;
            font-size: .88rem;
        }

        /* --- KI-Karten --- */
        .ai-card {
            background: var(--surface-soft);
            border-radius: 20px;
            padding: .8rem .95rem;
            border: 1px solid var(--border);
            font-size: .84rem;
        }
        .ai-headline { font-weight: 900; color: var(--text); margin-bottom: .35rem; font-size: .92rem; }
        .confidence-bar { background: var(--lavender); border-radius: 999px; height: 9px; overflow: hidden; margin: .4rem 0 .25rem; }
        .confidence-fill { background: linear-gradient(90deg, var(--purple), var(--lavender-2)); height: 100%; border-radius: 999px; }
        .divider { height: 1px; background: var(--border); margin: .65rem 0; }

        /* --- Buttons --- */
        div.stButton > button {
            width: 100%;
            min-height: 46px;
            border-radius: 999px !important;
            border: 0 !important;
            font-weight: 800 !important;
            font-size: .9rem !important;
            letter-spacing: -.1px;
            padding: .45rem .8rem !important;
            transition: transform .12s ease, box-shadow .12s ease;
        }
        div.stButton > button:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(107,82,163,.18); }
        div.stButton > button:active { transform: scale(.97); }
        div.stButton > button[kind="primary"],
        div.stButton > button.primary { background: var(--purple) !important; color: #fff !important; }
        div.stButton > button[kind="secondary"],
        div.stButton > button.secondary { background: var(--lavender) !important; color: var(--purple) !important; }

        /* --- Widgets ---
           FIX gegen "Feld im Feld": Streamlit/BaseWeb setzt den Rahmen je
           nach Version auf den Wrapper (data-baseweb="input") ODER auf das
           echte <input>. Der Wrapper wird deshalb immer transparent
           geschaltet – die Pill-Optik liegt auf genau einer Ebene. */
        [data-testid="stTextInput"] div[data-baseweb="input"],
        [data-testid="stDateInput"] div[data-baseweb="input"] {
            border: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: 0 !important;
        }

        /* 16 px Schrift in Feldern → iOS-Safari zoomt beim Antippen nicht rein. */
        [data-testid="stTextInput"] input, .stTextInput input,
        [data-testid="stDateInput"] input, .stDateInput input {
            border-radius: 999px !important;
            border: 0 !important;
            background: var(--surface) !important;
            padding: .7rem 1rem !important;
            box-shadow: var(--shadow);
            font-size: 16px !important;
            width: 100% !important;
        }
        /* FIX Datumsfeld: rechts Platz für das Kalender-Icon,
           damit Icon und Eingabetext sich nicht überlagern */
        [data-testid="stDateInput"] input, .stDateInput input {
            padding: .7rem 2.7rem .7rem 1rem !important;
        }

        [data-testid="stTextArea"] textarea, .stTextArea textarea {
            border-radius: 18px !important;
            border: 0 !important;
            background: var(--surface) !important;
            padding: .7rem 1rem !important;
            box-shadow: var(--shadow);
            font-size: 16px !important;
            min-height: 88px !important;
        }
        input::placeholder, textarea::placeholder { color: var(--muted) !important; }

        /* FIX Selectbox: Pill-Optik liegt auf dem Control, das interne
           Eingabefeld ist transparent – kein doppelter Rahmen mehr. */
        div[data-baseweb="select"] > div {
            border-radius: 999px !important;
            border: 1px solid var(--border) !important;
            background: var(--surface) !important;
            box-shadow: var(--shadow);
            min-height: 46px;
            padding: 0 .9rem !important;
        }
        div[data-baseweb="select"] input {
            border: 0 !important;
            border-radius: 0 !important;
            background: transparent !important;
            box-shadow: none !important;
            padding: .5rem .2rem .5rem 0 !important;
            font-size: 16px !important;
        }

        [data-testid="stTextInput"] label,
        [data-testid="stTextArea"] label,
        [data-testid="stDateInput"] label,
        [data-testid="stSelectbox"] label,
        [data-testid="stRadio"] > label {
            font-size: .76rem !important;
            font-weight: 800 !important;
            color: var(--purple) !important;
            margin-bottom: .15rem !important;
        }

        /* FIX Radio-Gruppe: saubere Umbruch-Abstände statt
           aneinanderklebender Optionen */
        div[role="radiogroup"] {
            background: var(--surface-soft);
            border-radius: 999px;
            padding: .22rem .3rem;
            flex-wrap: wrap;
            row-gap: .25rem;
            column-gap: .3rem;
        }
        div[role="radiogroup"] label {
            padding: .35rem .9rem;
            border-radius: 999px;
            font-size: .82rem;
            font-weight: 700;
            white-space: nowrap;
        }
        [data-testid="stAlert"] { border-radius: 16px; font-size: .85rem; }

        /* --- Foto-Uploader --- */
        .stFileUploader, [data-testid="stFileUploader"] {
            background: var(--lavender);
            border-radius: 22px;
            padding: .45rem .45rem .3rem;
        }
        .stFileUploader section, [data-testid="stFileUploader"] section {
            border: 0 !important;
            background: transparent !important;
            width: 100% !important;
        }
        .stFileUploader label, [data-testid="stFileUploader"] label { display: none !important; }
        [data-testid="stFileUploaderDropzone"] {
            background: rgba(255,255,255,.6) !important;
            border: 0 !important;
            border-radius: 15px !important;
            min-height: 112px !important;
            width: 100% !important;
        }
        /* ältere Streamlit-Versionen: "Browse files"-Button in der Dropzone */
        [data-testid="stFileUploaderDropzone"] button {
            border-radius: 999px !important;
            border: 0 !important;
            background: var(--purple) !important;
            color: #fff !important;
            font-weight: 800 !important;
            min-height: 44px !important;
            padding: .4rem 1.3rem !important;
        }
        /* neuere Streamlit-Versionen: Dropzone ist selbst ein <button> */
        button[data-testid="stFileUploaderDropzone"] { color: var(--purple) !important; }
        button[data-testid="stFileUploaderDropzone"] p,
        button[data-testid="stFileUploaderDropzone"] b,
        button[data-testid="stFileUploaderDropzone"] strong {
            color: var(--purple) !important;
            font-weight: 700 !important;
        }
        [data-testid="stFileUploaderDropzoneInstructions"] {
            color: var(--purple) !important;
            font-weight: 700 !important;
            font-size: .85rem !important;
        }
        [data-testid="stFileUploader"] small, .stFileUploader small {
            color: var(--purple) !important;
            font-size: .68rem !important;
        }

        /* Bildvorschau beim Upload */
        .stImage img, [data-testid="stImage"] img {
            width: 100%;
            aspect-ratio: 4 / 3;
            object-fit: cover;
            border-radius: 20px;
            max-height: 48vh;
        }

        /* --- Feinanpassung für sehr schmale / flache Fenster --- */
        @media (max-width: 380px) {
            .stat-card { padding: .45rem .2rem; }
            .grid-card { padding: .25rem .25rem .5rem; }
            .ai-card { padding: .65rem .7rem; }
        }
        @media (max-height: 700px) and (max-width: 560px) {
            .hero-card img { aspect-ratio: 1.7 / 1; }
            .stImage img, [data-testid="stImage"] img { aspect-ratio: 1.7 / 1; }
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
    """Kopfzeile: großes Branding auf der Startseite,
    kompakte App-Kopfzeile mit Zurück-Pfeil auf Unterseiten."""
    if st.session_state.page == "home":
        st.markdown("<div class='brand'>Fundgrube</div>", unsafe_allow_html=True)
        st.markdown(
            "<div class='brand-sub'>Virtuelles Fundbüro – Verlorenes wiederfinden</div>",
            unsafe_allow_html=True,
        )
    else:
        # Spalten vertikal zentrieren, falls die Streamlit-Version
        # vertical_alignment unterstützt (sonst fängt die feste
        # 46-px-Höhe im CSS die Ausrichtung ab).
        try:
            links, mitte, rechts = st.columns(
                [1, 3, 1], gap="small", vertical_alignment="center"
            )
        except TypeError:
            links, mitte, rechts = st.columns([1, 3, 1], gap="small")
        with links:
            if st.button("←", key="global_back"):
                go("home")
        with mitte:
            st.markdown(
                "<div class='brand-kompakt'>Fundgrube</div>", unsafe_allow_html=True
            )
        with rechts:
            pass


def status_badge(status):
    cls = {
        "gefunden": "status-gefunden",
        "vermisst": "status-vermisst",
        "zurückgegeben": "status-zurueckgegeben",
    }.get(status, "status-gefunden")
    return f"<span class='status {cls}'>{_esc(status)}</span>"


def pills_html(tags, limit=6):
    return "".join(
        f"<span class='pill'>{_esc(str(t))}</span>" for t in (tags or [])[:limit]
    )


@st.cache_data(show_spinner=False)
def bild_quelle(img_str, max_seite=800):
    """Liefert eine <img>-taugliche Bildquelle:
    Remote-URLs direkt, lokale Dateien als kompakte, gecachte Data-URI
    (automatisch auf max. 800 px verkleinert → schnell & platzsparend)."""
    if not img_str:
        return ""
    if str(img_str).startswith(("http://", "https://", "data:")):
        return img_str
    try:
        pfad = Path(img_str)
        if not pfad.exists():
            return ""
        bild = Image.open(pfad)
        bild = ImageOps.exif_transpose(bild).convert("RGB")
        bild.thumbnail((max_seite, max_seite))
        puffer = io.BytesIO()
        bild.save(puffer, format="JPEG", quality=82)
        return "data:image/jpeg;base64," + base64.b64encode(puffer.getvalue()).decode()
    except Exception:
        return ""


def hero_card_html(item, tag_limit=4, mit_beschreibung=False):
    """Start-/Detailkarte als echte HTML-Karte (Bild + Infos in einer Fläche)."""
    beschreibung = ""
    if mit_beschreibung and item.get("beschreibung"):
        beschreibung = (
            f"<div class='muted beschreibung'>{_esc(item['beschreibung'])}</div>"
        )
    return f"""
        <div class='hero-card'>
            <img src='{bild_quelle(item.get("img"))}' alt='{_esc(item["name"])}'/>
            <div class='item-title'>{_esc(item['name'])} {status_badge(item['status'])}</div>
            <div class='muted meta-zeile'>📍 {_esc(item['ort'])} · 🗓 {item['datum']}</div>
            <div class='pill-row'>{pills_html(item.get('tags'), tag_limit)}</div>
            {beschreibung}
        </div>
        """


def grid_card_html(item):
    """Kompakte Karte für das Suchraster."""
    return f"""
        <div class='grid-card'>
            <img src='{bild_quelle(item.get("img"))}' alt='{_esc(item["name"])}'/>
            <div class='grid-caption'>{_esc(item['name'])} {status_badge(item['status'])}</div>
            <div class='muted grid-meta'>📍 {_esc(item['ort'])}</div>
            <div class='pill-row'>{pills_html(item.get('tags'), 3)}</div>
        </div>
        """


def ai_karte_scan_html(res):
    """KI-Ergebnis als HTML-Karte (Upload-Seite)."""
    prozent = int(max(0.0, min(1.0, float(res.get("konfidenz") or 0))) * 100)
    farbe = res.get("farbe")
    stil = res.get("stil") or []
    modell = (res.get("modell") or "KI").upper()
    return (
        "<div class='ai-card'>"
        "<div class='ai-headline'>🤖 KI-Erkenntnis</div>"
        f"<div>Erkannte Kategorie: <strong>{_esc(res['kategorie'])}</strong>"
        f" <span class='muted'>· Modell: {modell}</span></div>"
        f"<div class='confidence-bar'><div class='confidence-fill' style='width:{prozent}%'></div></div>"
        f"<div class='muted'>Konfidenz: {prozent} %</div>"
        "<div class='divider'></div>"
        f"<div class='muted'>Farbe: <strong>{_esc(farbe) or '–'}</strong></div>"
        f"<div class='muted'>Merkmale: <strong>{', '.join(_esc(s) for s in stil) or '–'}</strong></div>"
        f"<div class='pill-row' style='margin-top:.4rem'>{pills_html(res.get('tags'))}</div>"
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
        f"<div>Erkannte Kategorie: <strong>{_esc(str(kategorie))}</strong>"
        f" <span class='muted'>· Modell: {modell}</span></div>"
        f"<div class='confidence-bar'><div class='confidence-fill' style='width:{prozent}%'></div></div>"
        f"<div class='muted'>Konfidenz: {prozent} %</div>"
        f"<div class='muted' style='margin-top:.35rem'>Farbe: <strong>{', '.join(_esc(str(f)) for f in farben) or '–'}</strong></div>"
        f"<div class='muted'>Merkmale: <strong>{', '.join(_esc(str(s)) for s in stil) or '–'}</strong></div>"
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

    st.markdown(
        "<div class='stats-row'>"
        f"<div class='stat-card'><div class='stat-number'>{gefunden}</div>"
        "<div class='stat-label'>Funde</div></div>"
        f"<div class='stat-card'><div class='stat-number'>{vermisst}</div>"
        "<div class='stat-label'>Vermisst</div></div>"
        f"<div class='stat-card'><div class='stat-number'>{offen}</div>"
        "<div class='stat-label'>Offen</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

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

    st.markdown(hero_card_html(akt, tag_limit=4), unsafe_allow_html=True)

    # Karussell-Steuerung
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

    # Hauptaktionen nebeneinander → platzsparend, direkt erreichbar
    links, rechts = st.columns(2)
    with links:
        if st.button("⌕  Suchen", key="home_search", type="secondary"):
            go("suchen")
    with rechts:
        if st.button("↥  Fund melden", key="home_upload", type="primary"):
            go("hochladen")

# =========================================================
# SEITE: SUCHE
# =========================================================
def render_suchen():
    header()
    st.markdown("<span class='section-label'>Fundstück suchen</span>", unsafe_allow_html=True)

    st.markdown("<div class='search-marker'></div>", unsafe_allow_html=True)
    query = st.text_input(
        "Suchbegriff", placeholder="Pullover, beige, Bibliothek …",
        label_visibility="collapsed",
    )

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
            st.markdown(grid_card_html(item), unsafe_allow_html=True)
            if st.button("Ansehen", key=f"view_{item['id']}", type="secondary"):
                st.session_state.selected = item["id"]
                go("detail")

# =========================================================
# SEITE: HOCHLADEN / KI-SCAN
# =========================================================
def render_hochladen():
    header()
    st.markdown(
        "<span class='section-label'>Fund melden / Vermisstenanzeige</span>",
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Foto hochladen", type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if not uploaded:
        st.caption("JPG, PNG oder WEBP – die KI erkennt Kategorie, Farbe & Merkmale")
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

    # Kompakte Vorschau: verkleinerte Kopie → schnellere Reruns,
    # Proportion + Maximalhöhe regelt das CSS (max. ~halber Bildschirm)
    vorschau = bild_obj.copy()
    vorschau.thumbnail((800, 800))
    st.image(vorschau, use_container_width=True)

    if st.button("🤖  KI-Scan starten", type="primary", key="start_scan"):
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

    st.markdown("<span class='section-label'>Angaben zum Eintrag</span>", unsafe_allow_html=True)

    name = st.text_input("Bezeichnung", value=res["kategorie"])
    art = st.radio("Art", ["gefunden", "vermisst"], horizontal=True)
    ort = st.text_input("Fundort / Verlustort")
    datum = st.date_input("Datum", value=date.today())
    kontakt = st.text_input("Kontakt (E-Mail / Telefon)")
    beschreibung = st.text_area("Beschreibung")
    tags_txt = st.text_input("Tags (KI-Vorschlag, anpassbar)", value=", ".join(res["tags"]))

    if st.button("💾  In Fundgrube aufnehmen", type="primary", key="save_item"):
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

    st.markdown(
        hero_card_html(item, tag_limit=6, mit_beschreibung=True),
        unsafe_allow_html=True,
    )

    ki = item.get("ki") or {}
    konfidenz = int(max(0.0, min(1.0, float(ki.get("konfidenz") or 0))) * 100)
    st.markdown(
        "<div class='stats-row'>"
        f"<div class='stat-card'><div class='stat-number'>{_esc(str(item.get('kategorie') or '–'))}</div>"
        "<div class='stat-label'>Kategorie</div></div>"
        f"<div class='stat-card'><div class='stat-number'>{konfidenz} %</div>"
        "<div class='stat-label'>KI-Konfidenz</div></div>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(ki_karte_detail_html(item), unsafe_allow_html=True)

    if item["status"] != "zurückgegeben":
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✉  Kontakt", type="primary", key="show_contact"):
                st.session_state.zeigekontakt = not st.session_state.zeigekontakt
        with c2:
            if st.button("✅  Zurückgegeben", type="secondary", key="mark_returned"):
                item["status"] = "zurückgegeben"
                speichere_db(st.session_state.db)
                st.rerun()
    else:
        if st.button("✉  Kontakt anzeigen", type="primary", key="show_contact"):
            st.session_state.zeigekontakt = not st.session_state.zeigekontakt

    if st.session_state.zeigekontakt:
        st.markdown(
            "<div class='ai-card'><strong>📞 Kontakt</strong><br>"
            f"<span class='muted'>{_esc(item.get('kontakt') or 'Kein Kontakt hinterlegt')}</span></div>",
            unsafe_allow_html=True,
        )

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
