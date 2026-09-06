import streamlit as st
from PIL import Image
from transformers import pipeline

# --- ECHTES KI-MODELL LADEN ---
@st.cache_resource
def load_ai_model():
    # Lädt das Vision-Transformer-Modell (beim ersten Start dauert es kurz)
    return pipeline("image-classification", model="google/vit-base-patch16-224")

# --- SEITEN-KONFIGURATION & CSS ---
st.set_page_config(page_title="Fundgrube", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #F8F5FE; }
    #MainMenu, header, footer { visibility: hidden; }
    img { border-radius: 20px; }
    
    button[kind="primary"] {
        background-color: #6B52A3 !important;
        color: white !important;
        border-radius: 25px !important;
        height: 55px !important;
        font-weight: 700 !important;
    }
    button[kind="secondary"] {
        background-color: #D4C4F7 !important;
        color: #4A4A4A !important;
        border-radius: 25px !important;
        height: 55px !important;
        font-weight: 700 !important;
    }
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

# --- DATENBANK & STATE INITIALISIEREN ---
if "db" not in st.session_state:
    st.session_state.db = [
        {"id": 1, "name": "Beiger Strickpullover", "tags": ["pullover", "beige", "strick", "winter"], "img": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?auto=format&fit=crop&w=400&q=80"},
        {"id": 2, "name": "Roter Rentier-Pulli", "tags": ["pullover", "rot", "weihnachten", "rentier"], "img": "https://images.unsplash.com/photo-1543322748-33df6d3db806?auto=format&fit=crop&w=400&q=80"},
    ]

if "page" not in st.session_state: st.session_state.page = "home"
if "carousel_idx" not in st.session_state: st.session_state.carousel_idx = 0
if "selected_item" not in st.session_state: st.session_state.selected_item = None

def navigate(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- SCREEN 1: HOME ---
if st.session_state.page == "home":
    st.markdown("<div class='app-title'>Fundgrube</div>", unsafe_allow_html=True)
    st.markdown("<div class='badge-label'>Zuletzt Hinzugefügt</div>", unsafe_allow_html=True)
    
    current_item = st.session_state.db[st.session_state.carousel_idx]
    
    # Bilder werden direkt in Streamlit angezeigt, wenn es hochgeladene PIL-Bilder sind oder URLs
    if isinstance(current_item["img"], str):
        st.image(current_item["img"], use_container_width=True)
    else:
        st.image(current_item["img"], use_container_width=True)
        
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        if st.button("🔍 Artikel Suchen", use_container_width=True):
            navigate("search")
        st.write("")
        if st.button("↑ Artikel Hochladen", type="primary", use_container_width=True):
            navigate("upload")

# --- SCREEN 2: SUCHE ---
elif st.session_state.page == "search":
    if st.button("↩ Zurück"): navigate("home")
        
    query = st.text_input("🔍 Suchen", value="")
    
    if query:
        q = query.lower().strip()
        filtered_db = [
            item for item in st.session_state.db 
            if q in item["name"].lower() or any(q in tag.lower() for tag in item["tags"])
        ]
    else:
        filtered_db = st.session_state.db
        
    st.write("")
    
    cols = st.columns(2)
    for i, item in enumerate(filtered_db):
        with cols[i % 2]:
            st.image(item["img"], use_container_width=True)
            if st.button("Ansehen", key=f"btn_{item['id']}", use_container_width=True):
                st.session_state.selected_item = item
                navigate("detail")

# --- SCREEN 3: DETAILANSICHT ---
elif st.session_state.page == "detail":
    if st.button("↩ Zurück"): navigate("search")
        
    item = st.session_state.selected_item
    if item:
        st.image(item["img"], use_container_width=True)
        st.caption(f"**KI-Tags:** {', '.join(item['tags'])}")
        
        st.write("---")
        col1, col2, col3 = st.columns([1, 4, 1])
        with col2:
            if st.button("🔖 Reservieren", use_container_width=True):
                st.success("Artikel reserviert!")
            if st.button("✉ Kontaktieren", type="primary", use_container_width=True):
                st.success("Kontaktformular geöffnet!")

# --- SCREEN 4: ECHTER KI-UPLOAD ---
elif st.session_state.page == "upload":
    if st.button("↩ Zurück"): navigate("home")
        
    st.markdown("### Neuer Artikel")
    uploaded_file = st.file_uploader("Bild auswählen", type=["jpg", "png", "jpeg"])
    
    if uploaded_file and st.button("Hochladen & KI-Scan", type="primary", use_container_width=True):
        with st.spinner("KI analysiert das Bild... (beim ersten Mal dauert das kurz)"):
            try:
                # Bild öffnen
                image = Image.open(uploaded_file)
                
                # Echtes Modell laden und Bild scannen
                classifier = load_ai_model()
                predictions = classifier(image)
                
                # Die Top 3 erkannten Begriffe als Tags extrahieren
                new_tags = [pred['label'].split(',')[0].lower() for pred in predictions[:3]]
                
                # In Datenbank speichern
                st.session_state.db.insert(0, {
                    "id": len(st.session_state.db) + 1,
                    "name": "Neues Kleidungsstück",
                    "tags": new_tags,
                    "img": image
                })
                
                st.success(f"Bild erkannt! Tags: {', '.join(new_tags)}")
                st.balloons()
            except Exception as e:
                st.error(f"Fehler bei der KI-Analyse: {e}")
