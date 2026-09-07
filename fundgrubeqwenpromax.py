
"""
Fundgrube – Virtuelles Fundbüro (Streamlit)
KI-Implementierung: CLIP Zero-Shot (openai/clip-vit-base-patch32) aus fundgrube_app.py
   -> getrennte Klassifikation für Kategorie, Farbe & Stil/Muster
   -> Fallbacks: ViT (ImageNet-Mapping) und reine Farbanalyse
UI-Basis: fundgrubeqwen.py (Home / Suchen / Hochladen / Detail, JSON-Persistenz)
Design: Material-3-Lavendel-Look analog zu den App-Mockups (PDF)

Installation:
    pip install streamlit pillow transformers torch torchvision
Start:
    streamlit run fundgrube.py
"""

import base64
import html as html_mod
import io
import json
import uuid
from datetime import date, datetime
from pathlib import Path

import streamlit as st
from PIL import Image, ImageDraw, ImageOps

===========================================================================
SEITEN-KONFIGURATION
===========================================================================
st.setpageconfig(
    page_title="Fundgrube – Virtuelles Fundbüro",
    page_icon="🔍",
    layout="centered",
    initialsidebarstate="collapsed",
)

FONTS = """

"""

DESIGN = """

:root{
  --bg:#F8F5FE; --surface:#FFFFFF; --surface-soft:#EEE9F7;
  --lavender:#D4C4F7; --lavender-2:#C8B5F0;
  --purple:#6B52A3; --purple-dark:#55408A;
  --text:#17151D; --muted:#716B7D; --border:#E5DFF0;
  --shadow:0 10px 30px rgba(74,54,120,.10);
}
*{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Roboto','Segoe UI',system-ui,-apple-system,sans-serif;}
.stApp{
  background:
    radial-gradient(circle at 8% 6%,  rgba(212,196,247,.50) 0 26px, transparent 27px),
    radial-gradient(circle at 88% 4%, rgba(212,196,247,.38) 0 40px, transparent 41px),
    radial-gradient(circle at 4% 38%, rgba(212,196,247,.30) 0 30px, transparent 31px),
    radial-gradient(circle at 94% 46%,rgba(212,196,247,.30) 0 26px, transparent 27px),
    radial-gradient(circle at 12% 78%,rgba(212,196,247,.34) 0 44px, transparent 45px),
    radial-gradient(circle at 90% 86%,rgba(212,196,247,.28) 0 34px, transparent 35px),
    var(--bg);
}
#MainMenu,header,footer{visibility:hidden;height:0;}
.block-container{max-width:480px;padding:1.1rem 1rem 3rem;}

/ ---------- M3 Buttons ---------- /
div.stButton>button{
  width:100%;min-height:50px;border-radius:999px;border:0;
  background:var(--lavender);color:var(--purple-dark);
  font-weight:700;font-size:.93rem;letter-spacing:.1px;
  transition:transform .15s ease, box-shadow .15s ease, background .15s ease;
}
div.stButton>button:hover{transform:translateY(-1px);box-shadow:0 8px 18px rgba(107,82,163,.18);}
div.stButton>button:active{transform:translateY(0);box-shadow:none;}
div.stButton>button:focus:not(:active){box-shadow:0 0 0 3px rgba(107,82,163,.25);}
div.stButton>button[kind="primary"]{background:var(--purple);color:#fff;box-shadow:0 4px 14px rgba(85,64,138,.28);}
div.stButton>button[kind="primary"]:hover{background:var(--purple-dark);}

/ ---------- M3 Eingabefelder ---------- /
.stTextInput input,.stTextArea textarea,.stNumberInput input{
  border-radius:22px!important;border:1.5px solid var(--border)!important;
  background:#fff!important;padding:.75rem 1rem!important;
  font-size:.92rem!important;color:var(--text)!important;min-height:48px;
}
.stTextInput input:focus,.stTextArea textarea:focus{
  border-color:var(--purple)!important;box-shadow:0 0 0 3px rgba(107,82,163,.14)!important;outline:none;
}
.stTextArea textarea{min-height:96px;}
div[data-baseweb="select"]>div{
  border-radius:999px!important;border:1.5px solid var(--border)!important;
  background:#fff!important;min-height:48px;padding-left:.9rem;
}
div[data-baseweb="datepicker"] input{
  border-radius:999px!important;border:1.5px solid var(--border)!important;
  background:#fff!important;min-height:48px;padding:.6rem 1rem!important;
}
div[role="radiogroup"]{gap:.4rem!important;}
div[role="radiogroup"]>label{
  border-radius:999px!important;padding:.35rem .95rem;background:#fff;
  border:1.5px solid var(--border);font-weight:600;color:var(--text);
}
div[role="radiogroup"]>label:has(input:checked){
  background:var(--lavender);border-color:var(--lavender-2);
  color:var(--purple-dark);font-weight:700;
}
.stTextInput label,.stTextArea label,.stSelectbox label,.stMultiSelect label,
.stRadio label,.stDateInput label,.stFileUploader label{
  color:var(--muted)!important;font-size:.76rem!important;font-weight:700!important;letter-spacing:.35px;
}

/ ---------- File-Uploader ---------- /
section[data-testid="stFileUploader"]{background:var(--lavender);border-radius:28px;padding:.7rem;margin-bottom:.8rem;}
section[data-testid="stFileUploader"] section[data-testid="stFileUploadDropzone"]{
  border:2px dashed rgba(85,64,138,.35)!important;background:rgba(255,255,255,.55)!important;border-radius:22px!important;
}
section[data-testid="stFileUploader"] span,section[data-testid="stFileUploader"] small{color:var(--purple-dark)!important;}

/ ---------- Alerts / Expander / Progress ---------- /
div[data-testid="stAlert"]{border-radius:22px!important;font-size:.88rem;}
details[data-testid="stExpander"]{background:#fff;border:1px solid var(--border);border-radius:22px;box-shadow:var(--shadow);}
details[data-testid="stExpander"] summary{font-weight:700;color:var(--purple-dark);}
div[data-testid="stProgress"]>div{background:var(--surface-soft)!important;border-radius:999px!important;border:0!important;}
div[data-testid="stProgress"]>div>div{background:var(--purple)!important;border-radius:999px!important;}
img{border-radius:20px;}

/ ---------- Brand / App-Bar ---------- /
.brand{display:flex;align-items:center;justify-content:center;gap:.55rem;
  font-size:1.9rem;line-height:1;font-weight:900;letter-spacing:-1.2px;
  color:var(--text);margin:.35rem 0 1.25rem;}
.brand .logo{width:46px;height:46px;border-radius:15px;background:var(--purple);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-size:1.35rem;
  box-shadow:0 6px 16px rgba(107,82,163,.35);flex:0 0 46px;}
.brand.small{font-size:1.35rem;margin:.1rem 0 .9rem;}
.brand.small .logo{width:38px;height:38px;border-radius:13px;font-size:1.05rem;flex:0 0 38px;}

/ ---------- Section-Label (M3-Assist-Chip) ---------- /
.section-label{display:inline-block;padding:.36rem .9rem;border-radius:999px;
  background:var(--lavender);color:var(--purple-dark);
  font-size:.72rem;font-weight:800;letter-spacing:.4px;margin:0 0 .55rem .25rem;}

/ ---------- Stat-Cards ---------- /
.stat-card{background:rgba(255,255,255,.82);border:1px solid var(--border);
  border-radius:20px;padding:.7rem .35rem;text-align:center;box-shadow:var(--shadow);}
.stat-number{font-size:1.2rem;font-weight:900;color:var(--purple);}
.stat-label{color:var(--muted);font-size:.64rem;font-weight:700;text-transform:uppercase;letter-spacing:.5px;}

/ ---------- Karten ---------- /
.fg-card{background:var(--surface);border-radius:28px;overflow:hidden;
  box-shadow:var(--shadow);border:1px solid rgba(107,82,163,.08);margin-bottom:.55rem;}
.fg-media{background:var(--surface-soft);}
.fg-media img{width:100%;aspect-ratio:1.25/1;object-fit:cover;display:block;border-radius:0;}
.fg-card.hero .fg-media img{aspect-ratio:1.45/1;}
.fg-body{padding:.85rem 1rem 1rem;}
.fg-title-row{display:flex;align-items:center;justify-content:space-between;gap:.5rem;}
.fg-title{font-size:1rem;font-weight:800;color:var(--text);}
.fg-title.big{font-size:1.25rem;font-weight:850;letter-spacing:-.4px;}
.fg-meta{color:var(--muted);font-size:.78rem;margin:.3rem 0 .5rem;}
.fg-tags{line-height:1.9;}
.pill{display:inline-block;background:var(--surface-soft);color:var(--purple);
  border-radius:999px;padding:.28rem .68rem;margin:.15rem .2rem .15rem 0;
  font-size:.72rem;font-weight:750;}
.chip{display:inline-block;padding:.26rem .7rem;border-radius:999px;font-size:.68rem;font-weight:800;white-space:nowrap;}
.chip-gefunden{background:#DFF5E1;color:#2E7D32;}
.chip-vermisst{background:#FDE3E3;color:#C62828;}
.chip-zurueck{background:#E6E2EE;color:#5A5566;}

/ ---------- Carousel-Dots ---------- /
.dots{display:flex;justify-content:center;gap:6px;margin:.55rem 0 .35rem;}
.dot{width:8px;height:8px;border-radius:50%;background:var(--lavender-2);}
.dot.active{width:22px;border-radius:999px;background:var(--purple);}

/ ---------- Upload-Box / Empty-State ---------- /
.upload-box{background:var(--lavender);border-radius:28px;min-height:230px;
  display:flex;align-items:center;justify-content:center;text-align:center;
  color:var(--purple-dark);box-shadow:var(--shadow);}
.upload-icon{font-size:2.7rem;display:block;margin-bottom:.4rem;}
.empty-state{text-align:center;padding:2.2rem 1rem;color:var(--muted);
  background:rgba(255,255,255,.72);border:1.5px dashed var(--lavender-2);border-radius:28px;}

/ ---------- Detail-Infozeilen ---------- /
.info-row{display:flex;gap:.65rem;align-items:center;background:#fff;
  border:1px solid var(--border);border-radius:18px;padding:.55rem .75rem;
  margin-bottom:.5rem;font-size:.85rem;color:var(--text);font-weight:500;}
.info-row .ico{width:36px;height:36px;border-radius:12px;background:var(--surface-soft);
  display:flex;align-items:center;justify-content:center;font-size:1.05rem;flex:0 0 36px;}
.info-row .lbl{color:var(--muted);font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.4px;display:block;}

/ ---------- KI-Panel ---------- /
.ki-panel{background:linear-gradient(135deg,#6B52A3 0%,#8B6FC9 100%);
  border-radius:24px;padding:1rem 1.05rem;color:#fff;box-shadow:var(--shadow);margin:.4rem 0 .8rem;}
.ki-title{font-weight:800;font-size:.95rem;margin-bottom:.15rem;}
.ki-sub{font-size:.74rem;opacity:.85;}
.ki-bar{height:7px;background:rgba(255,255,255,.28);border-radius:999px;overflow:hidden;margin:.6rem 0 .3rem;}
.ki-bar>span{display:block;height:100%;background:#fff;border-radius:999px;}
.ki-panel .pill{background:rgba(255,255,255,.18);color:#fff;}

.footer-note{text-align:center;color:var(--muted);font-size:.68rem;margin-top:1.6rem;letter-spacing:.3px;}
@media (max-width:520px){.block-container{padding-left:.75rem;padding-right:.75rem;}}

"""

st.markdown(FONTS + DESIGN, unsafeallowhtml=True)

===========================================================================
PFADE & DATENBANK
===========================================================================
BASE = Path(file).resolve().parent
BILDORDNER = BASE / "fundgrubebilder"
BILDORDNER.mkdir(parents=True, exist_ok=True)
DB_DATEI = BASE / "fundgrubedb.json"

def platzhalterbild():
    img = Image.new("RGB", (900, 720), "#EDE7F6")
    d = ImageDraw.Draw(img)
    d.ellipse((350, 210, 550, 410), outline="#6B52A3", width=16)
    d.line((505, 385, 600, 480), fill="#6B52A3", width=20)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

PLATZHALTER = platzhalterbild()

SEED = [
    {
        "id": "seed-1", "name": "Beiger Strickpullover", "art": "gefunden",
        "kategorie": "Pullover", "tags": ["Pullover", "beige", "Strick", "unifarben"],
        "ort": "Stadtbibliothek, 2. OG", "datum": "2026-09-05",
        "kontakt": "fundbuero@stadt.example", "status": "gefunden", "reserviert": False,
        "beschreibung": "Weicher Strickpullover, gefunden im Lesesaal.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/1f8a41506-ed38-4a38-8410-6954316a33d2.png",
        "ki": {"kategorie": "Pullover", "konfidenz": 0.93, "farben": ["beige"],
               "muster": ["Strick", "unifarben"],
               "tags": ["Pullover", "beige", "Strick", "unifarben"], "modell": "clip"},
    },
    {
        "id": "seed-2", "name": "Roter Rentier-Pulli", "art": "vermisst",
        "kategorie": "Pullover", "tags": ["Pullover", "rot", "mit Motiv", "Winter"],
        "ort": "Uni-Mensa, Campus Nord", "datum": "2026-09-03",
        "kontakt": "anna@beispiel.de", "status": "vermisst", "reserviert": False,
        "beschreibung": "Weihnachtspullover mit weißem Rentier, sehr sentimental.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/131bba6c7-0775-4b10-aa69-7516d0f402d5.png",
        "ki": {"kategorie": "Pullover", "konfidenz": 0.91, "farben": ["rot", "weiß"],
               "muster": ["mit Motiv", "Winter"],
               "tags": ["Pullover", "rot", "mit Motiv", "Winter"], "modell": "clip"},
    },
    {
        "id": "seed-3", "name": "Schwarze Lederhandschuhe", "art": "gefunden",
        "kategorie": "Handschuhe", "tags": ["Handschuhe", "schwarz", "Leder"],
        "ort": "Bushaltestelle Bahnhofstraße", "datum": "2026-09-04",
        "kontakt": "fundbuero@stadt.example", "status": "gefunden", "reserviert": False,
        "beschreibung": "Paar schwarze Lederhandschuhe auf einer Bank gefunden.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/184c9e954-ccc7-4597-b2a8-2ea19173820a.png",
        "ki": {"kategorie": "Handschuhe", "konfidenz": 0.89, "farben": ["schwarz"],
               "muster": ["unifarben"],
               "tags": ["Handschuhe", "schwarz", "Leder"], "modell": "clip"},
    },
    {
        "id": "seed-4", "name": "Blauer Rucksack", "art": "vermisst",
        "kategorie": "Rucksack", "tags": ["Rucksack", "blau", "unifarben"],
        "ort": "Uni-Mensa, Campus Nord", "datum": "2026-09-02",
        "kontakt": "max@beispiel.de", "status": "vermisst", "reserviert": False,
        "beschreibung": "Blauer Rucksack mit silbernen Reißverschlüssen, Laptopfach.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/15bafe2a0-eb5e-40f0-a65d-30763d89b22a.png",
        "ki": {"kategorie": "Rucksack", "konfidenz": 0.95, "farben": ["blau"],
               "muster": ["unifarben"],
               "tags": ["Rucksack", "blau", "unifarben"], "modell": "clip"},
    },
    {
        "id": "seed-5", "name": "Mintfarbener Hoodie", "art": "gefunden",
        "kategorie": "Hoodie", "tags": ["Hoodie", "mint", "mit Kapuze", "casual"],
        "ort": "Sporthalle, Umkleide 2", "datum": "2026-09-06",
        "kontakt": "fundbuero@stadt.example", "status": "gefunden", "reserviert": False,
        "beschreibung": "Kaum getragener Hoodie, nach dem Training liegen geblieben.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/17d658acf-227e-4d42-8c1c-b2dbf252b8a2.png",
        "ki": {"kategorie": "Hoodie", "konfidenz": 0.94, "farben": ["mint"],
               "muster": ["mit Kapuze", "casual"],
               "tags": ["Hoodie", "mint", "mit Kapuze", "casual"], "modell": "clip"},
    },
    {
        "id": "seed-6", "name": "Graue Wollmütze", "art": "gefunden",
        "kategorie": "Mütze", "tags": ["Mütze", "grau", "Strick"],
        "ort": "Café Ecke, Tisch 4", "datum": "2026-09-01",
        "kontakt": "fundbuero@stadt.example", "status": "gefunden", "reserviert": False,
        "beschreibung": "Feine Strickmütze in Graugrün, am Fensterplatz vergessen.",
        "img": "https://image.qwenlm.ai/public_source/b51d7f66-1142-49dd-b37e-78842203b9bf/17f9cac92-df43-4fee-a445-189a4c326481.png",
        "ki": {"kategorie": "Mütze", "konfidenz": 0.88, "farben": ["grau"],
               "muster": ["Strick"],
               "tags": ["Mütze", "grau", "Strick"], "modell": "clip"},
    },
]

def speichere_db(items):
    DBDATEI.writetext(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

def lade_db():
    if DB_DATEI.exists():
        try:
            return json.loads(DBDATEI.readtext(encoding="utf-8"))
        except Exception:
            pass
    speichere_db(SEED)
    return [dict(i) for i in SEED]

===========================================================================
KI-MODELL  (CLIP Zero-Shot aus fundgrube_app.py + Fallbacks)
===========================================================================
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
        "boots": "Stiefel",
        "backpack": "Rucksack",
        "cap": "Mütze / Cap",
        "beanie hat": "Mütze",
        "scarf": "Schal",
        "gloves": "Handschuhe",
        "socks": "Socken",
        "handbag": "Tasche",
        "umbrella": "Regenschirm",
        "wristwatch": "Uhr",
        "wallet": "Portemonnaie",
        "bunch of keys": "Schlüssel",
        "eyeglasses": "Brille",
        "plush toy": "Kuscheltier",
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
        "leather clothing": "Leder",
    },
}

FARBEN_RGB = {
    "schwarz": (20, 20, 20), "weiß": (245, 245, 245), "grau": (130, 130, 130),
    "rot": (200, 45, 45), "rosa": (240, 170, 190), "orange": (240, 140, 40),
    "gelb": (240, 210, 60), "grün": (70, 150, 80), "blau": (50, 100, 200),
    "braun": (120, 80, 50), "beige": (220, 200, 170), "lila": (130, 90, 180),
    "türkis": (60, 180, 180), "mint": (170, 220, 200), "dunkelblau": (30, 50, 110),
}

VIT_MAP = [
    ("sweater", "Pullover"), ("jersey", "Pullover"), ("jacket", "Jacke"), ("coat", "Jacke"),
    ("jean", "Hose"), ("trouser", "Hose"), ("dress", "Kleid"), ("skirt", "Rock"),
    ("shirt", "Shirt"), ("shoe", "Schuhe"), ("boot", "Stiefel"), ("glove", "Handschuhe"),
    ("hat", "Mütze"), ("cap", "Mütze"), ("scarf", "Schal"), ("sock", "Socken"),
    ("backpack", "Rucksack"), ("bag", "Tasche"), ("umbrella", "Regenschirm"),
    ("watch", "Uhr"), ("wallet", "Portemonnaie"), ("toy", "Kuscheltier"),
]

KATEGORIE_WORTE = {
    "hoodie": "Hoodie", "sweatshirt": "Sweatshirt", "pullover": "Pullover",
    "strickpullover": "Pullover", "strickjacke": "Jacke", "jacke": "Jacke", "mantel": "Jacke",
    "t-shirt": "T-Shirt", "hemd": "Hemd", "hose": "Hose", "jeans": "Jeans", "shorts": "Shorts",
    "kleid": "Kleid", "rock": "Rock", "schuhe": "Schuhe", "sneaker": "Schuhe", "stiefel": "Stiefel",
    "rucksack": "Rucksack", "mütze": "Mütze", "cap": "Mütze", "schal": "Schal",
    "handschuhe": "Handschuhe", "socken": "Socken", "tasche": "Tasche",
    "regenschirm": "Regenschirm", "uhr": "Uhr", "portemonnaie": "Portemonnaie",
    "schlüssel": "Schlüssel", "brille": "Brille", "kuscheltier": "Kuscheltier",
}

@st.cacheresource(showspinner=False)
def ladekimodell():
    """Lädt CLIP Zero-Shot (bevorzugt) oder ViT als Fallback."""
    try:
        from transformers import pipeline
        return ("clip", pipeline("zero-shot-image-classification",
                                 model="openai/clip-vit-base-patch32"))
    except Exception:
        try:
            from transformers import pipeline
            return ("vit", pipeline("image-classification",
                                    model="google/vit-base-patch16-224"))
        except Exception:
            return (None, None)

def klassifiziere(pipe, image, labelmap, minscore=0.0, topk=1):
    """CLIP Zero-Shot: liefert [(deutsches_label, score), ...] absteigend."""
    ergebnisse = pipe(image, candidatelabels=list(labelmap.keys()))
    ausgabe = []
    for r in ergebnisse:
        score = float(r["score"])
        if score >= min_score:
            ausgabe.append((label_map[r["label"]], score))
        if len(ausgabe) >= top_k:
            break
    return ausgabe

def dominante_farben(image, n=2):
    """Fallback-Farbanalyse ohne KI-Modell."""
    try:
        klein = image.convert("RGB").resize((48, 48))
        q = klein.quantize(colors=3)
        palette = q.getpalette()
        namen = []
        for _, idx in sorted(q.getcolors(), reverse=True):
            r, g, b = palette[idx  3: idx  3 + 3]
            farbname = min(
                FARBEN_RGB.items(),
                key=lambda kv: (kv[1][0] - r)  2 + (kv[1][1] - g)  2 + (kv[1][2] - b)  2,
            )[0]
            if farbname not in namen:
                namen.append(farbname)
            if len(namen) >= n:
                break
        return namen
    except Exception:
        return []

def ki_scan(image):
    """
    KI-Scan wie in fundgrube_app.py: getrennte CLIP-Klassifikationen für
    Kategorie, Farbe und Stil/Muster -> gleichzeitig z.B. "Hoodie + mint + Kapuze".
    Fallbacks: ViT (ImageNet-Mapping) bzw. reine Farbanalyse.
    """
    image = image.convert("RGB")
    modellart, pipe = ladeki_modell()
    kategorie, konfidenz = "Sonstiges", 0.0
    zusatz, farben, stil = [], [], []

    try:
        if modell_art == "clip":
            kat = klassifiziere(pipe, image, AILABELS["category"], top_k=3)
            if kat:
                kategorie, konfidenz = kat[0]
                zusatz = [k for k, s in kat[1:] if s >= 0.12]
            farben = [f for f,  in klassifiziere(pipe, image, AI_LABELS["color"],
                                                   minscore=0.18, topk=2)]
            stil = [s for s,  in klassifiziere(pipe, image, AI_LABELS["style"],
                                                 minscore=0.22, topk=2)]
        elif modell_art == "vit":
            preds = pipe(image, top_k=8)
            kat_tags = []
            for p in preds:
                lab = p["label"].lower()
                for kw, de in VIT_MAP:
                    if kw in lab and de not in kat_tags:
                        kat_tags.append(de)
                        break
            if kat_tags:
                kategorie, konfidenz = kat_tags[0], float(preds[0]["score"])
                zusatz = kat_tags[1:3]
    except Exception:
        modell_art = None

    if not farben:
        farben = dominante_farben(image)

    tags, gesehen = [], set()
    for t in [kategorie] + zusatz + farben + stil:
        t = t.strip()
        if t and t not in gesehen:
            gesehen.add(t)
            tags.append(t)

    return {
        "kategorie": kategorie,
        "konfidenz": round(float(konfidenz), 2),
        "farben": farben,
        "muster": stil,
        "tags": tags[:6],
        "modell": modell_art or "Farbanalyse",
    }

def kategorieaustags(tags):
    for tag in tags:
        for kw, wert in KATEGORIE_WORTE.items():
            if kw in tag.lower():
                return wert
    return "Sonstiges"

===========================================================================
SESSION-STATE & NAVIGATION
===========================================================================
if "db" not in st.session_state:
    st.sessionstate.db = ladedb()
st.session_state.setdefault("page", "home")
st.session_state.setdefault("carousel", 0)
st.session_state.setdefault("selected", None)
st.session_state.setdefault("scan", None)
st.session_state.setdefault("scanfile", None)
st.session_state.setdefault("zeigekontakt", False)
st.sessionstate.setdefault("sucheq", "")
st.sessionstate.setdefault("suchestatus", "Alle")
st.sessionstate.setdefault("suchekat", "Alle")

def navigate(page):
    st.session_state.page = page
    st.session_state.zeigekontakt = False
    st.rerun()

def esc(text):
    return html_mod.escape(str(text))

===========================================================================
UI-BAUSTEINE
===========================================================================
def bild_src(item):
    src = item.get("img")
    if not src:
        return PLATZHALTER
    if isinstance(src, str):
        if src.startswith("http") or src.startswith("data:"):
            return src
        p = Path(src)
        if p.exists():
            return "data:image/png;base64," + base64.b64encode(p.read_bytes()).decode()
    return PLATZHALTER

STATUS_KLASSE = {
    "gefunden": "chip-gefunden",
    "vermisst": "chip-vermisst",
    "zurückgegeben": "chip-zurueck",
}

def status_chip(status):
    cls = STATUS_KLASSE.get(status, "chip-gefunden")
    return f'{esc(status)}'

def pill(tag):
    return f'{esc(tag)}'

def karten_html(item):
    src = bild_src(item)
    tags = "".join(pill(t) for t in item.get("tags", [])[:4])
    res = ' 🔖 reserviert' if item.get("reserviert") else ""
    return f"""
    
      
      
        {esc(item['name'])}{status_chip(item['status'])}
        📍 {esc(item['ort'])} · 🗓 {esc(item['datum'])}{res}
        {tags}
      
    """

def hero_html(item):
    src = bild_src(item)
    tags = "".join(pill(t) for t in item.get("tags", [])[:4])
    return f"""
    
      
      
        {esc(item['name'])}{status_chip(item['status'])}
        📍 {esc(item['ort'])} · 🗓 {esc(item['datum'])}
        {tags}
      
    """

def kipanelhtml(res):
    prozent = int(float(res.get("konfidenz", 0.0)) * 100)
    tags = "".join(pill(t) for t in res.get("tags", []))
    return f"""
    
      🤖 KI-Erkenntnis
      Kategorie: {esc(res.get('kategorie', '–'))} · Modell: {esc(res.get('modell', '–'))}
      
      Konfidenz: {prozent} %
      {tags}
    """

def kopf(zurueck=None):
    if zurueck:
        c1, c2, c3 = st.columns([1, 5, 1])
        with c1:
            if st.button("←", key=f"back{st.sessionstate.page}"):
                navigate(zurueck)
        with c2:
            st.markdown('🔍Fundgrube',
                        unsafeallowhtml=True)
    else:
        st.markdown('🔍Fundgrube',
                    unsafeallowhtml=True)

def stat_karten():
    db = st.session_state.db
    fund = sum(1 for i in db if i.get("art") == "gefunden")
    vermisst = sum(1 for i in db if i.get("art") == "vermisst")
    reserv = sum(1 for i in db if i.get("reserviert"))
    c1, c2, c3 = st.columns(3)
    for col, zahl, label in ((c1, fund, "Funde"), (c2, vermisst, "Vermisst"), (c3, reserv, "Reserviert")):
        with col:
            st.markdown(
                f"{zahl}"
                f"{label}",
                unsafeallowhtml=True,
            )

===========================================================================
SEITE: HOME
===========================================================================
def render_home():
    kopf()
    stat_karten()
    st.write("")
    st.markdown("ZULETZT HINZUGEFÜGT", unsafeallowhtml=True)

    db = st.session_state.db
    liste = sorted(db, key=lambda i: i.get("datum", ""), reverse=True)
    if not liste:
        st.markdown("Noch keine Einträge."
                    "Melde deinen ersten Fund!", unsafeallowhtml=True)
    else:
        idx = st.session_state.carousel % len(liste)
        akt = liste[idx]
        st.markdown(herohtml(akt), unsafeallow_html=True)
        st.markdown(
            ""
            + "".join(
                f""
                for n in range(len(liste))
            )
            + "",
            unsafeallowhtml=True,
        )
        l, m, r = st.columns([1, 6, 1])
        with l:
            if st.button("‹", key="prev_item"):
                st.session_state.carousel = (idx - 1) % len(liste)
                st.rerun()
        with m:
            if st.button("Artikel ansehen", key="home_detail"):
                st.session_state.selected = akt["id"]
                navigate("detail")
        with r:
            if st.button("›", key="next_item"):
                st.session_state.carousel = (idx + 1) % len(liste)
                st.rerun()

    st.write("")
    if st.button("⌕  Artikel suchen", key="home_search"):
        navigate("suchen")
    if st.button("↥  Artikel hochladen", key="home_upload", type="primary"):
        navigate("hochladen")
    st.markdown("Designsprache: Material 3 · Lavendel",
                unsafeallowhtml=True)

===========================================================================
SEITE: SUCHEN
===========================================================================
def render_suchen():
    kopf(zurueck="home")
    st.markdown("ARTIKEL SUCHEN", unsafeallowhtml=True)

    query = st.text_input("suche", placeholder="Pullover, beige, Strick, Mensa …",
                          value=st.sessionstate.sucheq, label_visibility="collapsed")
    st.sessionstate.sucheq = query

    f1, f2 = st.columns(2)
    with f1:
        status = st.selectbox("STATUS", ["Alle", "gefunden", "vermisst", "zurückgegeben"],
                              index=["Alle", "gefunden", "vermisst", "zurückgegeben"]
                              .index(st.sessionstate.suchestatus)
                              if st.sessionstate.suchestatus in
                              ["Alle", "gefunden", "vermisst", "zurückgegeben"] else 0)
    with f2:
        kats = ["Alle"] + sorted({i.get("kategorie", "Sonstiges") for i in st.session_state.db})
        kat = st.selectbox("KATEGORIE", kats,
                           index=kats.index(st.sessionstate.suchekat)
                           if st.sessionstate.suchekat in kats else 0)
    st.sessionstate.suchestatus = status
    st.sessionstate.suchekat = kat

    q = query.lower().strip()
    erg = []
    for item in st.session_state.db:
        hay = " ".join([item.get("name", ""), item.get("kategorie", ""), item.get("ort", ""),
                        item.get("beschreibung", "")] + item.get("tags", [])).lower()
        if q and q not in hay:
            continue
        if status != "Alle" and item.get("status") != status:
            continue
        if kat != "Alle" and item.get("kategorie") != kat:
            continue
        erg.append(item)

    st.caption(f"{len(erg)} Treffer")
    if not erg:
        st.markdown("Kein Treffer"
                    "Versuche einen anderen Suchbegriff oder eine andere Kategorie.",
                    unsafeallowhtml=True)
        return

    cols = st.columns(2)
    for n, item in enumerate(erg):
        with cols[n % 2]:
            st.markdown(kartenhtml(item), unsafeallow_html=True)
            if item.get("reserviert"):
                if st.button("✓ Reserviert", key=f"res_{item['id']}"):
                    item["reserviert"] = False
                    speicheredb(st.sessionstate.db)
                    st.rerun()
            else:
                if st.button("🔖 Reservieren", key=f"res_{item['id']}"):
                    item["reserviert"] = True
                    speicheredb(st.sessionstate.db)
                    st.rerun()
            if st.button("Ansehen", key=f"view_{item['id']}", type="primary"):
                st.session_state.selected = item["id"]
                navigate("detail")

===========================================================================
SEITE: HOCHLADEN
===========================================================================
def render_hochladen():
    kopf(zurueck="home")
    st.markdown("ARTIKEL HOCHLADEN", unsafeallowhtml=True)
    st.caption("Foto hochladen – die KI (CLIP Zero-Shot) erkennt Kategorie, Farbe & Stil "
               "und schlägt Tags vor.")

    uploaded = st.file_uploader("Bild auswählen", type=["jpg", "jpeg", "png", "webp"],
                                label_visibility="collapsed")
    if not uploaded:
        st.markdown(
            "▧"
            "Bild auswählen"
            "JPG, PNG oder WEBP",
            unsafeallowhtml=True,
        )
        return

    if uploaded.name != st.session_state.scanfile:
        st.session_state.scan = None
        st.session_state.scanfile = uploaded.name
        for k in ("tagsinput", "nameinput"):
            st.session_state.pop(k, None)

    try:
        bildobj = ImageOps.exiftranspose(Image.open(uploaded)).convert("RGB")
    except Exception:
        st.error("Das Bild konnte nicht geöffnet werden.")
        return

    st.image(bildobj, usecontainer_width=True)

    if st.button("🤖  Hochladen & KI-Scan", type="primary", usecontainerwidth=True):
        with st.spinner("KI-Modell analysiert das Bild … (erstes Laden dauert kurz)"):
            st.sessionstate.scan = kiscan(bild_obj)
        if st.sessionstate.scan and "tagsinput" not in st.session_state:
            st.sessionstate["tagsinput"] = ", ".join(st.session_state.scan["tags"])
        st.rerun()

    res = st.session_state.scan
    if res:
        st.markdown(kipanelhtml(res), unsafeallowhtml=True)
        st.markdown("ANGABEN ZUM EINTRAG",
                    unsafeallowhtml=True)
    else:
        st.info("KI-Scan starten, um automatische Tags zu erhalten – oder Felder direkt ausfüllen.")

    name = st.textinput("BEZEICHNUNG", key="nameinput",
                         value=res["kategorie"] if res else "")
    c1, c2 = st.columns(2)
    with c1:
        art = st.radio("ART", ["gefunden", "vermisst"], horizontal=True)
    with c2:
        kat_auto = st.selectbox(
            "KATEGORIE",
            ["Automatisch (KI)"] + sorted(set(list(KATEGORIE_WORTE.values()) + ["Sonstiges"])),
        )
    ort = st.text_input("FUNDORT / VERLUSTORT", placeholder="z. B. Sporthalle, Umkleide 2")
    c3, c4 = st.columns(2)
    with c3:
        datum = st.date_input("DATUM", value=date.today())
    with c4:
        kontakt = st.text_input("KONTAKT", placeholder="E-Mail / Telefon")
    beschreibung = st.text_area("BESCHREIBUNG", placeholder="Besondere Merkmale …")
    tagstxt = st.textinput("TAGS (KI-Vorschlag, anpassbar)", key="tags_input", value="")

    if st.button("💾  In Fundgrube aufnehmen", type="primary", usecontainerwidth=True):
        if not name.strip() or not ort.strip():
            st.warning("Bitte mindestens Bezeichnung und Ort angeben.")
        else:
            if res:
                scan_res = res
            else:
                scan_res = {"kategorie": "Sonstiges", "konfidenz": 0.0, "farben": [],
                            "muster": [], "tags": [], "modell": "manuell"}
            tagliste = [t.strip() for t in tagstxt.split(",") if t.strip()]
            if not tag_liste:
                tagliste = scanres.get("tags", []) or [name.strip().lower()]
            if kat_auto == "Automatisch (KI)":
                kategorie = scanres["kategorie"] if res else kategorieaustags(tagliste)
            else:
                kategorie = kat_auto
            bid = uuid.uuid4().hex
            pfad = BILDORDNER / f"{bid}.png"
            bild_obj.save(pfad, format="PNG")
            eintrag = {
                "id": bid,
                "name": name.strip(),
                "art": art,
                "kategorie": kategorie,
                "tags": tag_liste[:6],
                "ort": ort.strip(),
                "datum": datum.isoformat(),
                "kontakt": kontakt.strip(),
                "beschreibung": beschreibung.strip(),
                "status": art,
                "reserviert": False,
                "img": str(pfad),
                "ki": scan_res,
            }
            st.session_state.db.insert(0, eintrag)
            speicheredb(st.sessionstate.db)
            st.session_state.scan = None
            st.session_state.scanfile = None
            for k in ("tagsinput", "nameinput"):
                st.session_state.pop(k, None)
            st.session_state.selected = bid
            st.session_state.carousel = 0
            st.balloons()
            navigate("detail")

===========================================================================
SEITE: DETAIL
===========================================================================
def render_detail():
    kopf(zurueck="suchen")
    item = next((i for i in st.sessionstate.db if i["id"] == st.sessionstate.selected), None)
    if not item:
        st.markdown("Dieser Artikel ist nicht mehr verfügbar.",
                    unsafeallowhtml=True)
        if st.button("Zur Startseite", type="primary"):
            navigate("home")
        return

    st.markdown(herohtml(item), unsafeallow_html=True)

    st.markdown(
        f"📍"
        f"Fundort{esc(item['ort'])}"
        f"🗓"
        f"Datum{esc(item['datum'])}"
        f"🏷"
        f"Kategorie{esc(item.get('kategorie', '–'))}",
        unsafeallowhtml=True,
    )

    if item.get("beschreibung"):
        st.markdown(f"📝"
                    f"Beschreibung{esc(item['beschreibung'])}",
                    unsafeallowhtml=True)

    with st.expander("🤖 KI-Analyse anzeigen"):
        ki = item.get("ki", {})
        if ki:
            st.markdown(kipanelhtml(ki), unsafeallowhtml=True)
            st.caption(
                f"Farben: {', '.join(ki.get('farben', [])) or '–'}  ·  "
                f"Stil/Muster: {', '.join(ki.get('muster', [])) or '–'}"
            )
        else:
            st.caption("Keine KI-Analyse vorhanden.")

    st.write("")
    c1, c2 = st.columns(2)
    with c1:
        if item.get("reserviert"):
            if st.button("✓ Reserviert", key="res_detail"):
                item["reserviert"] = False
                speicheredb(st.sessionstate.db)
                st.rerun()
        else:
            if st.button("🔖 Reservieren", key="res_detail"):
                item["reserviert"] = True
                speicheredb(st.sessionstate.db)
                st.success("Artikel wurde reserviert.")
    with c2:
        if st.button("✉ Kontaktieren", type="primary", key="kontakt_btn"):
            st.sessionstate.zeigekontakt = not st.sessionstate.zeigekontakt

    if st.session_state.zeigekontakt:
        with st.container(border=True):
            st.markdown("Kontaktanfrage")
            st.caption(f"Kontakt: {item.get('kontakt') or 'Kein Kontakt hinterlegt'}")
            st.text_area("NACHRICHT", placeholder="z. B. Wann kann ich den Artikel abholen?",
                         key="contact_message")
            if st.button("Nachricht senden", type="primary", key="send_msg"):
                st.session_state.zeigekontakt = False
                st.success("Kontaktanfrage wurde vorbereitet.")
                st.rerun()

    st.write("")
    c3, c4 = st.columns(2)
    with c3:
        if item.get("status") != "zurückgegeben":
            if st.button("✅ Zurückgegeben", key="mark_return"):
                item["status"] = "zurückgegeben"
                item["reserviert"] = False
                speicheredb(st.sessionstate.db)
                st.rerun()
    with c4:
        if st.button("🗑 Entfernen", key="delete_item"):
            st.sessionstate.db = [i for i in st.sessionstate.db if i["id"] != item["id"]]
            speicheredb(st.sessionstate.db)
            navigate("home")

===========================================================================
ROUTER
===========================================================================
seite = st.session_state.page
if seite == "home":
    render_home()
elif seite == "suchen":
    render_suchen()
elif seite == "hochladen":
    render_hochladen()
elif seite == "detail":
    render_detail()
else:
    navigate("home")
