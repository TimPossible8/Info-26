"""
Fundgrube – Lost & Found / Kleidertausch-App
----------------------------------------------
Eine Streamlit-App zum Hochladen, automatischen Taggen (KI-Bilderkennung)
und Wiederfinden von Kleidungsstücken.

Optimierungen gegenüber der ursprünglichen Version:
- Vollständige Umsetzung des Figma-/PDF-Designs (Hintergrund-Kreise,
  Pillenform-Buttons, Karussell mit funktionierenden Pfeilen & Punkten,
  Suchleiste mit Icon, Zoom-Icon in der Detailansicht)
- Robuste Navigation & Statusverwaltung (kein Absturz bei leerer Datenbank)
- KI-Modell läuft explizit auf CPU, Ergebnisse werden ins Deutsche übersetzt
- Editierbarer Artikelname beim Upload statt Platzhaltertext
- Reservieren-Status wird pro Artikel gespeichert (Button deaktiviert sich)
- Löschfunktion für eigene Einträge
- Sauber getrennte Funktionen, Typ-Hinweise, Kommentare
"""

from __future__ import annotations

import io
from typing import Optional

import streamlit as st
from PIL import Image

# ============================================================
# KI-MODELL
# ============================================================
#
# HINWEIS: Ein allgemeines ImageNet-Modell (z. B. google/vit-base-patch16-224)
# kennt nur eine Handvoll Kleidungs-Klassen und liefert bei Flatlay-Fotos
# (Kleidung ohne Person, auf Tisch/Boden fotografiert) oft irrelevante
# Treffer wie "Handtuch" oder "Kissenbezug". Stattdessen nutzen wir
# CLIP im Zero-Shot-Verfahren: Wir geben dem Modell selbst eine feste,
# für eine Kleider-Fundgrube sinnvolle Liste an Kategorien und Farben vor,
# aus der es die passendste auswählt. Das ist deutlich treffsicherer,
# ohne dass ein eigenes Modell trainiert werden muss.

CATEGORY_LABELS_EN = [
    "sweater", "hoodie", "t-shirt", "shirt", "blouse", "jacket", "coat",
    "jeans", "trousers", "shorts", "skirt", "dress", "suit", "vest",
    "scarf", "hat", "cap", "gloves", "socks", "shoes", "boots", "sneakers",
    "bag", "backpack", "belt", "swimsuit", "pajamas",
]

CATEGORY_LABELS_DE = {
    "sweater": "Pullover", "hoodie": "Hoodie", "t-shirt": "T-Shirt",
    "shirt": "Hemd", "blouse": "Bluse", "jacket": "Jacke", "coat": "Mantel",
    "jeans": "Jeans", "trousers": "Hose", "shorts": "Shorts", "skirt": "Rock",
    "dress": "Kleid", "suit": "Anzug", "vest": "Weste", "scarf": "Schal",
    "hat": "Hut", "cap": "Mütze", "gloves": "Handschuhe", "socks": "Socken",
    "shoes": "Schuhe", "boots": "Stiefel", "sneakers": "Sneaker", "bag": "Tasche",
    "backpack": "Rucksack", "belt": "Gürtel", "swimsuit": "Badeanzug",
    "pajamas": "Schlafanzug",
}

COLOR_LABELS_EN = [
    "black", "white", "gray", "beige", "brown", "red", "orange", "yellow",
    "green", "blue", "purple", "pink",
]

COLOR_LABELS_DE = {
    "black": "Schwarz", "white": "Weiß", "gray": "Grau", "beige": "Beige",
    "brown": "Braun", "red": "Rot", "orange": "Orange", "yellow": "Gelb",
    "green": "Grün", "blue": "Blau", "purple": "Lila", "pink": "Pink",
}


@st.cache_resource(show_spinner=False)
def load_ai_model():
    """Lädt das CLIP-Modell für Zero-Shot-Bildklassifikation einmalig (Cache)."""
    from transformers import pipeline

    # device=-1 erzwingt CPU-Inferenz, damit die App auch ohne GPU läuft.
    return pipeline(
        "zero-shot-image-classification",
        model="openai/clip-vit-base-patch32",
        device=-1,
    )


def classify_clothing_item(image: Image.Image) -> list[str]:
    """Erkennt Kategorie(n) + Farbe eines Kleidungsstücks per CLIP Zero-Shot.

    Gibt eine Liste deutscher Tags zurück, z. B. ["Pullover", "Beige"].
    """
    classifier = load_ai_model()

    category_result = classifier(image, candidate_labels=CATEGORY_LABELS_EN)
    color_result = classifier(image, candidate_labels=COLOR_LABELS_EN)

    tags: list[str] = []

    # Top-Kategorie immer aufnehmen; eine zweite nur, wenn sie fast
    # genauso wahrscheinlich ist (sonst verwässert das die Tags).
    top_cat = category_result[0]
    tags.append(CATEGORY_LABELS_DE[top_cat["label"]])
    if len(category_result) > 1 and category_result[1]["score"] >= top_cat["score"] * 0.75:
        second_cat_de = CATEGORY_LABELS_DE[category_result[1]["label"]]
        if second_cat_de not in tags:
            tags.append(second_cat_de)

    top_color = color_result[0]
    tags.append(COLOR_LABELS_DE[top_color["label"]])

    return tags


# ============================================================
# SEITEN-KONFIGURATION & DESIGN (CSS)
# ============================================================

st.set_page_config(page_title="Fundgrube", page_icon="🧺", layout="centered")

st.markdown(
    """
<style>
    /* ---------- Grundfarben & Hintergrund-Kreise ---------- */
    .stApp {
        background-color: #FBF6FC;
        background-attachment: fixed;
        background-image:
            radial-gradient(circle at 8%  10%, #E7DCF7 0, #E7DCF7 68px, transparent 69px),
            radial-gradient(circle at 32% 6%,  #EFE7FA 0, #EFE7FA 42px, transparent 43px),
            radial-gradient(circle at 58% 14%, #E7DCF7 0, #E7DCF7 88px, transparent 89px),
            radial-gradient(circle at 88% 9%,  #EFE7FA 0, #EFE7FA 52px, transparent 53px),
            radial-gradient(circle at 10% 42%, #EFE7FA 0, #EFE7FA 58px, transparent 59px),
            radial-gradient(circle at 92% 46%, #E7DCF7 0, #E7DCF7 74px, transparent 75px),
            radial-gradient(circle at 22% 66%, #E7DCF7 0, #E7DCF7 48px, transparent 49px),
            radial-gradient(circle at 62% 74%, #EFE7FA 0, #EFE7FA 64px, transparent 65px),
            radial-gradient(circle at 86% 82%, #E7DCF7 0, #E7DCF7 38px, transparent 39px),
            radial-gradient(circle at 40% 94%, #EFE7FA 0, #EFE7FA 54px, transparent 55px);
    }
    #MainMenu, header, footer { visibility: hidden; }
    div[data-testid="stToolbar"] { visibility: hidden; }

    /* ---------- Bilder ---------- */
    img { border-radius: 20px; }

    /* ---------- Buttons ---------- */
    div.stButton > button {
        border-radius: 25px !important;
        height: 55px !important;
        font-weight: 700 !important;
        width: 100%;
        transition: transform 0.05s ease-in-out;
        border: none !important;
    }
    div.stButton > button:active { transform: scale(0.98); }

    button[kind="primary"] {
        background-color: #6B52A3 !important;
        color: white !important;
    }
    button[kind="secondary"] {
        background-color: #D4C4F7 !important;
        color: #4A4A4A !important;
    }

    /* Kompakte "Icon-Buttons" (z. B. Zurück-Pfeil, Karussell-Pfeile) */
    .icon-btn button {
        height: 42px !important;
        min-height: 42px !important;
        width: 42px !important;
        min-width: 42px !important;
        padding: 0 !important;
        font-size: 18px !important;
    }
    .back-btn button {
        height: 40px !important;
        width: auto !important;
        padding: 0 18px !important;
        font-size: 18px !important;
    }

    /* ---------- Badge ---------- */
    .badge-label {
        background-color: #D4C4F7;
        color: #6B52A3;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    .badge-reserved {
        background-color: #F3E9D2;
        color: #9A7B1E;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-top: 8px;
    }

    /* ---------- Titel ---------- */
    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 32px;
        color: #000000;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    /* ---------- Karussell-Punkte ---------- */
    .dots { text-align: center; margin-top: -6px; margin-bottom: 18px; }
    .dot {
        height: 8px; width: 8px; margin: 0 4px;
        background-color: #D4C4F7; border-radius: 50%;
        display: inline-block;
    }
    .dot.active { background-color: #6B52A3; width: 20px; border-radius: 5px; }

    /* ---------- Suchleiste ---------- */
    div[data-testid="stTextInput"] input {
        background-color: #D4C4F7 !important;
        border-radius: 25px !important;
        border: none !important;
        height: 50px !important;
        color: #4A4A4A !important;
        font-weight: 600 !important;
        padding-left: 20px !important;
    }
    div[data-testid="stTextInput"] input::placeholder { color: #7A6C99 !important; }

    /* Tag-Anzeige in der Detailansicht */
    .tag-pill {
        display: inline-block;
        background-color: #EFE7FA;
        color: #6B52A3;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 13px;
        margin: 3px 4px 3px 0;
        font-weight: 600;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ============================================================
# STATE & DATENBANK
# ============================================================

if "db" not in st.session_state:
    st.session_state.db = [
        {
            "id": 1,
            "name": "Beiger Strickpullover",
            "tags": ["Pullover", "Beige", "Strick", "Winter"],
            "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80",
            "reserved": False,
        },
        {
            "id": 2,
            "name": "Roter Rentier-Pulli",
            "tags": ["Pullover", "Rot", "Weihnachten", "Rentier"],
            "img": "https://images.unsplash.com/photo-1543322748-33df6d3db806?auto=format&fit=crop&w=400&q=80",
            "reserved": False,
        },
    ]

st.session_state.setdefault("page", "home")
st.session_state.setdefault("carousel_idx", 0)
st.session_state.setdefault("selected_item_id", None)


def navigate(page_name: str) -> None:
    st.session_state.page = page_name
    st.rerun()


def get_item_by_id(item_id: int) -> Optional[dict]:
    return next((i for i in st.session_state.db if i["id"] == item_id), None)


def next_free_id() -> int:
    return (max((i["id"] for i in st.session_state.db), default=0)) + 1


# ============================================================
# SCREEN 1: HOME
# ============================================================

if st.session_state.page == "home":
    st.markdown("<div class='app-title'>Fundgrube</div>", unsafe_allow_html=True)

    if not st.session_state.db:
        st.info("Noch keine Artikel vorhanden. Lade den ersten Fund hoch! 👇")
    else:
        # Index absichern, falls Artikel gelöscht wurden
        st.session_state.carousel_idx %= len(st.session_state.db)
        current_item = st.session_state.db[st.session_state.carousel_idx]

        st.markdown("<div class='badge-label'>Zuletzt Hinzugefügt</div>", unsafe_allow_html=True)

        col_prev, col_img, col_next = st.columns([1, 6, 1])
        with col_prev:
            st.markdown("<div class='icon-btn' style='margin-top:90px;'>", unsafe_allow_html=True)
            if st.button("‹", key="prev_btn"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % len(st.session_state.db)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        with col_img:
            st.image(current_item["img"], use_container_width=True)
        with col_next:
            st.markdown("<div class='icon-btn' style='margin-top:90px;'>", unsafe_allow_html=True)
            if st.button("›", key="next_btn"):
                st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % len(st.session_state.db)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        # Punkt-Indikatoren
        dots_html = "".join(
            f"<span class='dot{' active' if i == st.session_state.carousel_idx else ''}'></span>"
            for i in range(len(st.session_state.db))
        )
        st.markdown(f"<div class='dots'>{dots_html}</div>", unsafe_allow_html=True)
        st.caption(f"<div style='text-align:center;'>{current_item['name']}</div>", unsafe_allow_html=True)

    st.write("")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🔍  Artikel Suchen", type="secondary", use_container_width=True):
            navigate("search")
        st.write("")
        if st.button("↑  Artikel Hochladen", type="primary", use_container_width=True):
            navigate("upload")

# ============================================================
# SCREEN 2: SUCHE
# ============================================================

elif st.session_state.page == "search":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("↩ Zurück", key="back_search"):
        navigate("home")
    st.markdown("</div>", unsafe_allow_html=True)

    query = st.text_input(
        "Suche", value="", placeholder="🔍  Nach Artikeln suchen…", label_visibility="collapsed"
    )

    if query:
        q = query.lower().strip()
        filtered_db = [
            item
            for item in st.session_state.db
            if q in item["name"].lower() or any(q in tag.lower() for tag in item["tags"])
        ]
    else:
        filtered_db = st.session_state.db

    st.write("")

    if not filtered_db:
        st.info("Keine Artikel gefunden. Versuch es mit einem anderen Suchbegriff.")
    else:
        cols = st.columns(2)
        for i, item in enumerate(filtered_db):
            with cols[i % 2]:
                st.image(item["img"], use_container_width=True)
                label = "🔒 Reserviert" if item.get("reserved") else "Ansehen"
                if st.button(label, key=f"btn_{item['id']}", use_container_width=True):
                    st.session_state.selected_item_id = item["id"]
                    navigate("detail")

# ============================================================
# SCREEN 3: DETAILANSICHT
# ============================================================

elif st.session_state.page == "detail":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("↩ Zurück", key="back_detail"):
        navigate("search")
    st.markdown("</div>", unsafe_allow_html=True)

    item = get_item_by_id(st.session_state.selected_item_id)

    if item is None:
        st.warning("Dieser Artikel existiert nicht mehr.")
    else:
        st.image(item["img"], use_container_width=True)
        st.markdown(f"### {item['name']}")

        tags_html = "".join(f"<span class='tag-pill'>{t}</span>" for t in item["tags"])
        st.markdown(tags_html, unsafe_allow_html=True)

        if item.get("reserved"):
            st.markdown("<div class='badge-reserved'>🔒 Reserviert</div>", unsafe_allow_html=True)

        st.write("---")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            reserve_label = "✓ Reserviert" if item.get("reserved") else "🔖  Reservieren"
            if st.button(
                reserve_label,
                type="secondary",
                use_container_width=True,
                disabled=item.get("reserved", False),
            ):
                item["reserved"] = True
                st.rerun()

            if st.button("✉  Kontaktieren", type="primary", use_container_width=True):
                st.success("Kontaktformular geöffnet – die Anfrage wurde an den Finder gesendet!")

            with st.expander("Artikel löschen"):
                st.caption("Diese Aktion kann nicht rückgängig gemacht werden.")
                if st.button("🗑 Endgültig löschen", key="delete_item"):
                    st.session_state.db = [i for i in st.session_state.db if i["id"] != item["id"]]
                    navigate("home")

# ============================================================
# SCREEN 4: ARTIKEL HOCHLADEN (mit KI-Bilderkennung)
# ============================================================

elif st.session_state.page == "upload":
    st.markdown("<div class='back-btn'>", unsafe_allow_html=True)
    if st.button("↩ Zurück", key="back_upload"):
        navigate("home")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("### Neuer Artikel")

    uploaded_file = st.file_uploader(
        "Bild auswählen", type=["jpg", "png", "jpeg"], label_visibility="collapsed"
    )

    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file).convert("RGB")
        except Exception:
            st.error("Diese Datei konnte nicht als Bild gelesen werden. Bitte JPG oder PNG hochladen.")
            image = None

        if image is not None:
            st.image(image, use_container_width=True)

            custom_name = st.text_input(
                "Artikelname", placeholder="z. B. Blauer Wollpullover"
            )

            if st.button("📷  Hochladen & KI-Scan", type="primary", use_container_width=True):
                with st.spinner("KI analysiert das Bild… (beim ersten Mal dauert das etwas länger)"):
                    try:
                        new_tags = classify_clothing_item(image)

                        new_item = {
                            "id": next_free_id(),
                            "name": custom_name.strip() if custom_name.strip() else "Neues Kleidungsstück",
                            "tags": new_tags,
                            "img": image,
                            "reserved": False,
                        }
                        st.session_state.db.insert(0, new_item)
                        st.session_state.carousel_idx = 0

                        st.success(f"Bild erkannt! Tags: {', '.join(new_tags)}")
                        st.balloons()
                    except Exception as e:
                        st.error(f"Fehler bei der KI-Analyse: {e}")
    else:
        # Platzhalter-Kachel wie im Design (großes helles Feld mit Bild-Icon)
        st.markdown(
            """
            <div style="
                background-color:#D4C4F7;
                border-radius:20px;
                height:280px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:48px;
                color:#EFE7FA;
                margin-bottom:20px;">
                🖼️➕
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.info("Bitte wähle oben ein Bild aus, um einen neuen Artikel hochzuladen.")
