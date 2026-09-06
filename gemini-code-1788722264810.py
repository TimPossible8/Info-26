import streamlit as st

# --- 1. SEITEN-KONFIGURATION ---
st.set_page_config(page_title="Fundgrube", layout="centered")

# --- 2. EXACT DESIGN (CUSTOM CSS) ---
st.markdown("""
<style>
    /* Hintergrund leicht lila einfärben für den Bubble-Look-Vibe */
    .stApp {
        background-color: #F8F5FE;
    }
    
    /* Standard-Streamlit Menüs verstecken für App-Feeling */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Bilder abrunden wie im Design */
    img {
        border-radius: 20px;
    }

    /* Dunkellila Buttons (Primär) -> z.B. Artikel Hochladen, Kontaktieren */
    button[kind="primary"] {
        background-color: #6B52A3 !important;
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        height: 55px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }

    /* Helllila Buttons (Sekundär) -> z.B. Artikel Suchen, Reservieren */
    button[kind="secondary"] {
        background-color: #D4C4F7 !important;
        color: #4A4A4A !important;
        border-radius: 25px !important;
        border: none !important;
        height: 55px !important;
        font-weight: 700 !important;
        font-size: 18px !important;
    }

    /* Das "Zuletzt Hinzugefügt" Badge */
    .badge-label {
        background-color: #D4C4F7;
        color: #6B52A3;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        display: inline-block;
        margin-bottom: -15px;
        position: relative;
        z-index: 10;
    }

    /* Titel Styling */
    .app-title {
        text-align: center;
        font-weight: 900;
        font-size: 32px;
        color: #000000;
        margin-top: 20px;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)


# --- 3. DATENBANK & STATE INITIALISIEREN ---
if "db" not in st.session_state:
    st.session_state.db = [
        {"id": 1, "name": "Beiger Strickpullover", "tags": ["pullover", "beige", "strick", "winter"], "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80"},
        {"id": 2, "name": "Roter Rentier-Pulli", "tags": ["pullover", "rot", "weihnachten", "rentier"], "img": "https://images.unsplash.com/photo-1543322748-33df6d3db806?auto=format&fit=crop&w=400&q=80"},
        {"id": 3, "name": "Lila Strickjacke", "tags": ["strickjacke", "lila", "herbst"], "img": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=400&q=80"},
        {"id": 4, "name": "Weißer Hoodie", "tags": ["hoodie", "weiß", "basic", "pullover"], "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80"}
    ]

if "page" not in st.session_state:
    st.session_state.page = "home"
if "carousel_idx" not in st.session_state:
    st.session_state.carousel_idx = 0
if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()


# --- SCREEN 1: HOME (1_2.jpg) ---
if st.session_state.page == "home":
    st.markdown("<div class='app-title'>Fundgrube</div>", unsafe_allow_html=True)
    
    col_main, col_space = st.columns([10, 1])
    with col_main:
        st.markdown("<div class='badge-label'>Zuletzt Hinzugefügt</div>", unsafe_allow_html=True)
    
    # Bilder-Karussell Simulation
    c_left, c_img, c_right = st.columns([1, 8, 1], gap="small")
    
    with c_left:
        st.write("\n\n\n")
        if st.button("❮", key="prev"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx - 1) % len(st.session_state.db)
            st.rerun()
            
    with c_img:
        current_item = st.session_state.db[st.session_state.carousel_idx]
        st.image(current_item["img"], use_container_width=True)
        
    with c_right:
        st.write("\n\n\n")
        if st.button("❯", key="next"):
            st.session_state.carousel_idx = (st.session_state.carousel_idx + 1) % len(st.session_state.db)
            st.rerun()
            
    st.write("---")
    
    # Action Buttons
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🔍 Artikel Suchen", use_container_width=True): # Sekundär (Hell)
            navigate("search")
        st.write("")
        if st.button("↑ Artikel Hochladen", type="primary", use_container_width=True): # Primär (Dunkel)
            navigate("upload")


# --- SCREEN 2: SUCHE (3_2.jpg) ---
elif st.session_state.page == "search":
    if st.button("↩ Zurück"):
        navigate("home")
        
    # HIER IST DER GEFIXTE FILTER FÜR DIE KI-TAGS
    query = st.text_input("🔍 Suchen (z.B. Pullover)", value="")
    
    if query:
        q = query.lower().strip()
        # Sucht jetzt robust im Namen ODER in JEDEM einzelnen KI-Tag 
        filtered_db = [
            item for item in st.session_state.db 
            if q in item["name"].lower() or any(q in tag.lower() for tag in item["tags"])
        ]
    else:
        filtered_db = st.session_state.db
        
    st.write("")
    
    # Rasteransicht
    cols = st.columns(2)
    for i, item in enumerate(filtered_db):
        with cols[i % 2]:
            st.image(item["img"], use_container_width=True)
            if st.button("Ansehen", key=f"btn_{item['id']}", use_container_width=True):
                st.session_state.selected_item = item
                navigate("detail")
            st.write("")


# --- SCREEN 3: DETAILANSICHT (4_2.jpg) ---
elif st.session_state.page == "detail":
    if st.button("↩ Zurück"):
        navigate("search")
        
    item = st.session_state.selected_item
    if item:
        st.image(item["img"], use_container_width=True)
        st.caption(f"**Erkannte KI-Tags:** {', '.join(item['tags'])}")
        
        st.write("---")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            if st.button("🔖 Reservieren", use_container_width=True): # Sekundär (Hell)
                st.success("Artikel wurde reserviert!")
            st.write("")
            if st.button("✉ Kontaktieren", type="primary", use_container_width=True): # Primär (Dunkel)
                st.success("Kontaktformular geöffnet!")


# --- SCREEN 4: UPLOAD (Fallback) ---
elif st.session_state.page == "upload":
    if st.button("↩ Zurück"):
        navigate("home")
        
    st.markdown("### Neuer Artikel (KI-Tagging)")
    st.file_uploader("Bild auswählen", type=["jpg", "png"])
    
    if st.button("Hochladen & KI-Scan", type="primary", use_container_width=True):
        new_tags = ["pullover", "neu", "grau"]
        st.session_state.db.insert(0, {
            "id": len(st.session_state.db) + 1,
            "name": "Neuer Artikel",
            "tags": new_tags,
            "img": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=400&q=80"
        })
        st.success(f"Erfolgreich! KI-Tags: {', '.join(new_tags)}")
        st.balloons()
