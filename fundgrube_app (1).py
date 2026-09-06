import io
import uuid
from datetime import datetime

import streamlit as st
from PIL import Image, ImageOps
from transformers import pipeline


# =========================================================
# CONFIG
# =========================================================
st.set_page_config(
    page_title="Fundgrube",
    page_icon="🔎",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# =========================================================
# DESIGN SYSTEM – based on the supplied mobile mockups
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
            margin: .35rem 0 1.35rem;
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
            padding: .45rem;
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

        .search-shell {
            background: var(--lavender);
            border-radius: 999px;
            padding: .05rem .25rem;
            margin-bottom: .9rem;
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

        .back-row {
            margin-bottom: .6rem;
        }

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
            box-shadow: 0 8px 18px rgba(107,82,163,.15);
        }

        div.stButton > button[kind="primary"] {
            background: var(--purple) !important;
            color: white !important;
        }

        div.stButton > button[kind="secondary"] {
            background: var(--lavender) !important;
            color: var(--purple) !important;
        }

        .stTextInput input {
            border-radius: 999px !important;
            border: 0 !important;
            background: transparent !important;
            padding: .75rem 1rem !important;
        }

        .stTextInput label,
        .stFileUploader label {
            display: none !important;
        }

        .stFileUploader {
            background: var(--lavender);
            border-radius: 25px;
            padding: .65rem;
            margin-bottom: .75rem;
        }

        .stFileUploader section {
            border: 0 !important;
            background: transparent !important;
        }

        .stImage img {
            border-radius: 20px;
        }

        .grid-caption {
            font-size: .82rem;
            font-weight: 800;
            color: var(--text);
            margin: .35rem .1rem .55rem;
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

        .divider {
            height: 1px;
            background: var(--border);
            margin: 1rem 0;
        }

        @media (max-width: 520px) {
            .block-container { padding-left: .75rem; padding-right: .75rem; }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# DATA / STATE
# =========================================================
DEFAULT_DB = [
    {
        "id": "demo-1",
        "name": "Beiger Strickpullover",
        "category": "Pullover",
        "condition": "Sehr gut",
        "location": "Fundbüro",
        "created_at": "Heute",
        "tags": ["pullover", "beige", "strick", "winter"],
        "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=85",
    },
    {
        "id": "demo-2",
        "name": "Roter Rentier-Pulli",
        "category": "Pullover",
        "condition": "Gut",
        "location": "Fundbüro",
        "created_at": "Gestern",
        "tags": ["pullover", "rot", "weihnachten", "rentier"],
        "img": "https://images.unsplash.com/photo-1543322748-33df6d3db806?auto=format&fit=crop&w=900&q=85",
    },
    {
        "id": "demo-3",
        "name": "Mintfarbener Hoodie",
        "category": "Hoodie",
        "condition": "Sehr gut",
        "location": "Sporthalle",
        "created_at": "Vor 2 Tagen",
        "tags": ["hoodie", "mint", "sport", "oberteil"],
        "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=900&q=82",
    },
    {
        "id": "demo-4",
        "name": "Blau-weißer Strickpullover",
        "category": "Pullover",
        "condition": "Gut",
        "location": "Klassenraum",
        "created_at": "Vor 3 Tagen",
        "tags": ["pullover", "blau", "weiß", "strick"],
        "img": "https://images.unsplash.com/photo-1576566588028-4147f3842f27?auto=format&fit=crop&w=900&q=85",
    },
]


def init_state():
    if "db" not in st.session_state:
        st.session_state.db = DEFAULT_DB.copy()
    st.session_state.setdefault("page", "home")
    st.session_state.setdefault("carousel_idx", 0)
    st.session_state.setdefault("selected_id", None)
    st.session_state.setdefault("reserved", set())
    st.session_state.setdefault("search_query", "")
    st.session_state.setdefault("search_category", "Alle")
    st.session_state.setdefault("notice", None)
    st.session_state.setdefault("contact_open", False)


init_state()


# =========================================================
# HELPERS
# =========================================================
def go(page: str):
    st.session_state.page = page
    st.session_state.notice = None
    st.rerun()


def get_item(item_id):
    return next((x for x in st.session_state.db if x["id"] == item_id), None)


def image_to_bytes(image: Image.Image) -> bytes:
    buf = io.BytesIO()
    image.convert("RGB").save(buf, format="JPEG", quality=90)
    return buf.getvalue()


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
    return pipeline(
        "zero-shot-image-classification",
        model="openai/clip-vit-base-patch32",
    )


AI_LABELS = {
    "category": {
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
        "backpack": "Rucksack",
        "cap": "Mütze / Cap",
        "scarf": "Schal",
        "gloves": "Handschuhe",
        "bag": "Tasche",
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
    Erkennt Kleidungsstück, Farbe und sichtbare Eigenschaften mit CLIP.

    Es werden bewusst getrennte Klassifikationen durchgeführt. Dadurch kann
    die KI gleichzeitig z.B. "Hoodie + schwarz + sportlich" erkennen, statt
    fünf nahezu identische ImageNet-Klassen zurückzugeben.
    """
    try:
        classifier = load_ai_model()

        detected = []
        confidence = {}

        # 1. Hauptkategorie
        category_label, category_score = _best_clip_label(
            classifier, image, AI_LABELS["category"]
        )
        if category_label:
            category = AI_LABELS["category"][category_label]
            detected.append(category.lower())
            confidence["category"] = category_score

        # 2. Farbe
        color_label, color_score = _best_clip_label(
            classifier, image, AI_LABELS["color"]
        )
        if color_label and color_score >= 0.18:
            detected.append(AI_LABELS["color"][color_label])
            confidence["color"] = color_score

        # 3. Stil / Material / Muster
        style_results = classifier(
            image,
            candidate_labels=list(AI_LABELS["style"].keys()),
        )
        if style_results:
            # Nur wirklich brauchbare Zusatz-Tags übernehmen.
            for result in style_results[:2]:
                if float(result["score"]) >= 0.22:
                    detected.append(AI_LABELS["style"][result["label"]])

        # Doppelte Tags entfernen, Reihenfolge behalten
        unique_tags = []
        for tag in detected:
            tag = tag.strip().lower()
            if tag and tag not in unique_tags:
                unique_tags.append(tag)

        if not unique_tags:
            return [], "Die KI konnte auf dem Bild kein passendes Merkmal sicher erkennen."

        return [(tag, confidence.get("category", 0.0)) for tag in unique_tags[:5]], None

    except Exception as exc:
        return [], (
            "KI-Modell konnte nicht geladen werden. Prüfe die Internetverbindung "
            "und installiere die Abhängigkeiten neu. Details: " + str(exc)
        )


def make_item_name(tags):
    if not tags:
        return "Neuer Fund"
    return tags[0][0].replace("_", " ").title()


def notify(message, kind="success"):
    if kind == "success":
        st.success(message)
    elif kind == "info":
        st.info(message)
    else:
        st.error(message)


# =========================================================
# GLOBAL HEADER
# =========================================================
def header():
    if st.session_state.page != "home":
        if st.button("←  Zurück", key="global_back"):
            go("home")
    st.markdown("<div class='brand'>Fundgrube</div>", unsafe_allow_html=True)


# =========================================================
# HOME
# =========================================================
def render_home():
    header()

    total = len(st.session_state.db)
    reserved = len(st.session_state.reserved)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{total}</div>"
            "<div class='stat-label'>Artikel</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{reserved}</div>"
            "<div class='stat-label'>Reserviert</div></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            "<div class='stat-card'><div class='stat-number'>KI</div>"
            "<div class='stat-label'>Erkennung</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("<span class='section-label'>Zuletzt hinzugefügt</span>", unsafe_allow_html=True)

    if not st.session_state.db:
        st.markdown("<div class='empty-state'>Noch keine Artikel vorhanden.</div>", unsafe_allow_html=True)
    else:
        idx = min(st.session_state.carousel_idx, len(st.session_state.db) - 1)
        item = st.session_state.db[idx]

        st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
        st.image(item["img"], use_container_width=True)
        st.markdown(
            f"<div class='item-title'>{item['name']}</div>"
            f"<div class='muted'>{item['location']} · {item['created_at']}</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "".join(f"<span class='pill'>{tag}</span>" for tag in item["tags"][:4]),
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.write("")
        a, b, c = st.columns([1, 2, 1])
        with a:
            if st.button("‹", key="prev_item"):
                st.session_state.carousel_idx = (idx - 1) % len(st.session_state.db)
                st.rerun()
        with b:
            if st.button("Artikel ansehen", key="home_detail", type="secondary"):
                st.session_state.selected_id = item["id"]
                go("detail")
        with c:
            if st.button("›", key="next_item"):
                st.session_state.carousel_idx = (idx + 1) % len(st.session_state.db)
                st.rerun()

    st.write("")
    if st.button("⌕  Artikel suchen", key="home_search", type="secondary"):
        go("search")
    if st.button("↥  Artikel hochladen", key="home_upload", type="primary"):
        go("upload")


# =========================================================
# SEARCH
# =========================================================
def render_search():
    header()
    st.markdown("### Artikel finden")

    st.markdown("<div class='search-shell'>", unsafe_allow_html=True)
    query = st.text_input(
        "search",
        placeholder="Pullover, beige, Strick …",
        value=st.session_state.search_query,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)
    st.session_state.search_query = query

    categories = ["Alle"] + sorted({x["category"] for x in st.session_state.db})
    st.session_state.search_category = st.selectbox(
        "Kategorie",
        categories,
        index=categories.index(st.session_state.search_category)
        if st.session_state.search_category in categories else 0,
    )

    q = query.lower().strip()
    filtered = []
    for item in st.session_state.db:
        haystack = " ".join(
            [item["name"], item["category"], item["condition"], item["location"]] + item["tags"]
        ).lower()
        matches_query = not q or q in haystack
        matches_category = (
            st.session_state.search_category == "Alle"
            or item["category"] == st.session_state.search_category
        )
        if matches_query and matches_category:
            filtered.append(item)

    st.caption(f"{len(filtered)} Treffer")

    if not filtered:
        st.markdown(
            "<div class='empty-state'><strong>Kein Treffer</strong><br>"
            "Versuche einen anderen Suchbegriff oder eine andere Kategorie.</div>",
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(2)
    for i, item in enumerate(filtered):
        with cols[i % 2]:
            st.image(item["img"], use_container_width=True)
            st.markdown(f"<div class='grid-caption'>{item['name']}</div>", unsafe_allow_html=True)
            st.caption(f"{item['category']} · {item['condition']}")
            if st.button("Ansehen", key=f"view_{item['id']}"):
                st.session_state.selected_id = item["id"]
                go("detail")


# =========================================================
# DETAIL
# =========================================================
def render_detail():
    header()
    item = get_item(st.session_state.selected_id)

    if not item:
        st.markdown(
            "<div class='empty-state'>Dieser Artikel ist nicht mehr verfügbar.</div>",
            unsafe_allow_html=True,
        )
        if st.button("Zur Suche", type="primary"):
            go("search")
        return

    st.markdown("<div class='hero-card'>", unsafe_allow_html=True)
    st.image(item["img"], use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f"<div class='item-title'>{item['name']}</div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='muted'>{item['location']} · hinzugefügt {item['created_at']}</div>",
        unsafe_allow_html=True,
    )

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{item['condition']}</div>"
            "<div class='stat-label'>Zustand</div></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='stat-card'><div class='stat-number'>{item['category']}</div>"
            "<div class='stat-label'>Kategorie</div></div>",
            unsafe_allow_html=True,
        )

    st.write("")
    st.markdown("**KI-Tags**")
    st.markdown(
        "".join(f"<span class='pill'>#{tag}</span>" for tag in item["tags"]),
        unsafe_allow_html=True,
    )

    st.write("")
    is_reserved = item["id"] in st.session_state.reserved

    if is_reserved:
        if st.button("✓  Reservierung aufheben", type="secondary", key="unreserve"):
            st.session_state.reserved.remove(item["id"])
            st.rerun()
    else:
        if st.button("🔖  Reservieren", type="secondary", key="reserve"):
            st.session_state.reserved.add(item["id"])
            st.success("Artikel wurde reserviert.")

    if st.button("✉  Kontakt aufnehmen", type="primary", key="contact"):
        st.session_state.contact_open = True

    if st.session_state.contact_open:
        with st.container(border=True):
            st.markdown("**Kontaktanfrage**")
            message = st.text_area(
                "Nachricht",
                placeholder="z. B. Wann kann ich den Artikel abholen?",
                key="contact_message",
            )
            if st.button("Nachricht senden", type="primary"):
                st.session_state.contact_open = False
                st.success("Kontaktanfrage wurde vorbereitet.")


# =========================================================
# UPLOAD / AI
# =========================================================
def render_upload():
    header()
    st.markdown("### Neuer Artikel")
    st.caption("Foto hochladen – die KI schlägt automatisch passende Tags vor.")

    uploaded = st.file_uploader(
        "Bild auswählen",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if not uploaded:
        st.markdown(
            "<div class='upload-box'><div><span class='upload-icon'>▧</span>"
            "<strong>Bild auswählen</strong><br><span class='muted'>JPG, PNG oder WEBP</span>"
            "</div></div>",
            unsafe_allow_html=True,
        )
        st.write("")
        return

    try:
        image = Image.open(uploaded)
        image = ImageOps.exif_transpose(image).convert("RGB")
    except Exception:
        st.error("Das Bild konnte nicht geöffnet werden.")
        return

    st.image(image, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        category = st.selectbox(
            "Kategorie",
            ["Automatisch", "Pullover", "Hoodie", "Jacke", "Hose", "Schuhe", "Sonstiges"],
        )
    with c2:
        condition = st.selectbox(
            "Zustand",
            ["Sehr gut", "Gut", "Gebraucht", "Unbekannt"],
        )

    location = st.text_input("Fundort", placeholder="z. B. Sporthalle")

    if st.button("↥  Hochladen & KI-Scan", type="primary"):
        with st.spinner("KI analysiert das Bild …"):
            predictions, error = run_ai_scan(image)

        tags = [x[0] for x in predictions[:5]]

        if category == "Automatisch":
            chosen_category = "Sonstiges"
            category_words = {
                "hoodie": "Hoodie",
                "sweatshirt": "Sweatshirt",
                "pullover": "Pullover",
                "strickpullover": "Pullover",
                "jacke": "Jacke",
                "mantel": "Jacke",
                "t-shirt": "T-Shirt",
                "hemd": "Hemd",
                "hose": "Hose",
                "jeans": "Jeans",
                "shorts": "Shorts",
                "kleid": "Kleid",
                "rock": "Rock",
                "schuhe": "Schuhe",
                "sneaker": "Schuhe",
                "rucksack": "Rucksack",
                "mütze": "Mütze / Cap",
                "cap": "Mütze / Cap",
                "schal": "Schal",
                "handschuhe": "Handschuhe",
                "tasche": "Tasche",
            }
            for tag in tags:
                for key, value in category_words.items():
                    if key in tag:
                        chosen_category = value
                        break
                if chosen_category != "Sonstiges":
                    break
        else:
            chosen_category = category

        if not tags:
            tags = ["neu", chosen_category.lower()]

        item = {
            "id": str(uuid.uuid4()),
            "name": make_item_name(predictions),
            "category": chosen_category,
            "condition": condition,
            "location": location.strip() or "Fundbüro",
            "created_at": datetime.now().strftime("%d.%m.%Y"),
            "tags": tags,
            "img": Image.open(io.BytesIO(image_to_bytes(image))),
        }

        st.session_state.db.insert(0, item)
        st.session_state.carousel_idx = 0

        if error:
            st.warning(
                "Der KI-Dienst war nicht verfügbar. Der Artikel wurde trotzdem gespeichert "
                "und mit Basis-Tags versehen."
            )
        else:
            st.success(f"Artikel erkannt: {', '.join(tags[:5])}")

        st.balloons()
        st.session_state.selected_id = item["id"]

        if st.button("Artikel ansehen", type="secondary", key="new_item_detail"):
            go("detail")


# =========================================================
# ROUTER
# =========================================================
if st.session_state.page == "home":
    render_home()
elif st.session_state.page == "search":
    render_search()
elif st.session_state.page == "detail":
    render_detail()
elif st.session_state.page == "upload":
    render_upload()
else:
    go("home")
