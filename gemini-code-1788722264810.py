import streamlit as st
import random

# --- SEITENKONFIGURATION ---
st.set_page_config(page_title="Fundgrube App", layout="centered", initial_sidebar_state="collapsed")

# Ein wenig CSS, um die Buttons abzurunden (ähnlich deinem Design)
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 15px;
        height: 50px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- DATENBANK & NAVIGATION INITIALISIEREN ---
if "mock_db" not in st.session_state:
    st.session_state.mock_db = [
        {"id": 1, "name": "Beiger Pullover", "tags": ["pullover", "beige", "winter", "strick"], "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80"},
        {"id": 2, "name": "Roter Weihnachtspullover", "tags": ["pullover", "rot", "weihnachten", "rentier"], "image": "https://images.unsplash.com/photo-1543322748-33df6d3db806?auto=format&fit=crop&w=400&q=80"},
        {"id": 3, "name": "Lila Strickjacke", "tags": ["pullover", "lila", "strickjacke", "herbst"], "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=400&q=80"},
        {"id": 4, "name": "Weißer Hoodie", "tags": ["pullover", "hoodie", "weiß", "basic"], "image": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80"},
    ]

if "page" not in st.session_state:
    st.session_state.page = "home"

if "selected_item" not in st.session_state:
    st.session_state.selected_item = None

# Hilfsfunktionen für die Navigation
def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

def view_item(item):
    st.session_state.selected_item = item
    navigate_to("detail")

# --- SCREEN 1: HOME ---
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align: center;'>Fundgrube</h1>", unsafe_allow_html=True)
    st.write("")
    
    st.markdown("### Zuletzt Hinzugefügt")
    # Zeigt das erste Bild aus der simulierten Datenbank an
    latest_item = st.session_state.mock_db[0]
    st.image(item["image"], use_container_width=True)
    
    st.write("")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🔍 Artikel Suchen"):
            navigate_to("search")
        if st.button("⬆️ Artikel Hochladen", type="primary"):
            navigate_to("upload")

# --- SCREEN 2: UPLOAD & KI TAGGING ---
elif st.session_state.page == "upload":
    if st.button("⬅️ Zurück"):
        navigate_to("home")
        
    st.header("Artikel Hochladen")
    
    # Datei-Upload-Feld
    uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "png", "jpeg"])
    
    st.write("")
    if st.button("Artikel Hochladen (KI-Scan starten)", type="primary"):
        # Simuliere das KI Tagging
        new_tags = ["pullover", "grau", "vintage", "neu"]
        new_item = {
            "id": random.randint(10, 1000),
            "name": "Neuer KI-erkannter Pullover",
            "tags": new_tags,
            "image": "https://images.unsplash.com/photo-1620799140408-edc6dcb6d633?auto=format&fit=crop&w=400&q=80" # Platzhalterbild
        }
        st.session_state.mock_db.insert(0, new_item)
        
        st.success(f"Erfolgreich hochgeladen! Die KI hat folgende Tags erkannt: {', '.join(new_tags)}")
        st.balloons() # Kleine Streamlit-Animation als Feedback

# --- SCREEN 3: SUCHE ---
elif st.session_state.page == "search":
    if st.button("⬅️ Zurück zum Start"):
        navigate_to("home")
        
    search_query = st.text_input("🔍 Suchen (z.B. Pullover, rot...)", placeholder="Suchen...")
    st.write("")
    
    # Filter-Logik: Sucht in Namen und KI-Tags
    query = search_query.lower()
    results = [
        item for item in st.session_state.mock_db 
        if query in item["name"].lower() or any(query in tag for tag in item["tags"])
    ]
    
    # Rasterdarstellung (2 Spalten)
    cols = st.columns(2)
    for i, item in enumerate(results):
        with cols[i % 2]:
            st.image(item["image"], use_container_width=True)
            if st.button(f"Ansehen", key=f"view_{item['id']}"):
                view_item(item)
            st.write("") # Abstand

# --- SCREEN 4: DETAILANSICHT ---
elif st.session_state.page == "detail":
    if st.button("⬅️ Zurück zur Suche"):
        navigate_to("search")
        
    item = st.session_state.selected_item
    if not item:
        navigate_to("home")
    
    st.image(item["image"], use_container_width=True)
    st.subheader(item["name"])
    st.caption(f"Erkannte KI-Tags: {', '.join(item['tags'])}")
    
    st.write("")
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🔖 Reservieren"):
            st.toast("Artikel wurde für dich reserviert!", icon="🎉")
        if st.button("💬 Kontaktieren", type="primary"):
            st.toast("Nachrichten-Funktion öffnet sich...", icon="✉️")
