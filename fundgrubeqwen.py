import json
import uuid
from datetime import date
from pathlib import Path

import streamlit as st
from PIL import Image


st.setpageconfig(pagetitle="Fundgrube – Virtuelles Fundbüro", pageicon="🔍", layout="centered")

st.markdown("""

    .stApp { background-color: #F8F5FE; }
    #MainMenu, header, footer { visibility: hidden; }
    img { border-radius: 20px; }
    button[kind="primary"] {
        background-color: #6B52A3 !important; color: white !important;
        border-radius: 25px !important; height: 52px !important; font-weight: 700 !important;
    }
    button[kind="secondary"] {
        background-color: #D4C4F7 !important; color: #4A4A4A !important;
        border-radius: 25px !important; height: 52px !important; font-weight: 700 !important;
    }
    .app-title { text-align:center; font-weight:900; font-size:34px; color:#000;
                 margin-top:14px; margin-bottom:6px; }
    .app-sub { text-align:center; color:#6B52A3; font-size:14px; margin-bottom:22px; }
    .badge-label { background-color:#D4C4F7; color:#6B52A3; padding:5px 15px; border-radius:20px;
                   font-size:12px; font-weight:bold; display:inline-block; margin-bottom:10px; }
    .tag { background:#EDE7F6; color:#6B52A3; padding:3px 11px; border-radius:12px;
           font-size:12px; font-weight:600; display:inline-block; margin:2px 4px 2px 0; }
    .meta { color:#6b6b6b; font-size:13px; }
    .card { background:#ffffff; border-radius:20px; padding:14px;
            box-shadow:0 3px 12px rgba(107,82,163,.14); margin-bottom:16px; }
    .status-gefunden { background:#DFF5E1; color:#2E7D32; padding:3px 12px; border-radius:12px;
                       font-size:12px; font-weight:700; display:inline-block; }
    .status-vermisst { background:#FDE3E3; color:#C62828; padding:3px 12px; border-radius:12px;
                       font-size:12px; font-weight:700; display:inline-block; }
    .status-zurueckgegeben { background:#E3E3E3; color:#555; padding:3px 12px; border-radius:12px;
                             font-size:12px; font-weight:700; display:inline-block; }

""", unsafeallowhtml=True)

BASE = Path(file).resolve().parent if "file" in globals() else Path.cwd()
BILDORDNER = BASE / "fundgrubebilder"
BILDORDNER.mkdir(parents=True, existok=True)
DBDATEI = BASE / "fundgrubedb.json"

KATEGORIE_LABELS = {
    "a photo of a sweater or pullover": "Pullover",
    "a photo of a jacket or coat": "Jacke",
    "a photo of pants or trousers": "Hose",
    "a photo of a dress": "Kleid",
    "a photo of a skirt": "Rock",
    "a photo of a t-shirt or shirt": "Shirt",
    "a photo of shoes or sneakers": "Schuhe",
    "a photo of boots": "Stiefel",
    "a photo of gloves": "Handschuhe",
    "a photo of a hat or beanie": "Mütze",
    "a photo of a scarf": "Schal",
    "a photo of socks": "Socken",
    "a photo of a backpack": "Rucksack",
    "a photo of a handbag or bag": "Tasche",
    "a photo of an umbrella": "Regenschirm",
    "a photo of a wristwatch": "Uhr",
    "a photo of a wallet": "Portemonnaie",
    "a photo of keys": "Schlüssel",
    "a photo of glasses": "Brille",
    "a photo of a plush toy": "Kuscheltier",
}
MUSTER_LABELS = {
    "solid single color": "einfarbig",
    "striped pattern": "gestreift",
    "checkered pattern": "kariert",
    "floral pattern": "gemustert",
    "animal motif print": "mit Motiv",
    "logo or text print": "mit Aufdruck",
}
VIT_MAP = [
    ("sweater", "Pullover"), ("jersey", "Pullover"), ("jacket", "Jacke"), ("coat", "Jacke"),
    ("jean", "Hose"), ("trouser", "Hose"), ("dress", "Kleid"), ("skirt", "Rock"),
    ("shirt", "Shirt"), ("shoe", "Schuhe"), ("boot", "Stiefel"), ("glove", "Handschuhe"),
    ("hat", "Mütze"), ("cap", "Mütze"), ("scarf", "Schal"), ("sock", "Socken"),
    ("backpack", "Rucksack"), ("bag", "Tasche"), ("umbrella", "Regenschirm"),
    ("watch", "Uhr"), ("wallet", "Portemonnaie"), ("toy", "Kuscheltier"),
]
FARB_RGB = {
    "schwarz": (20, 20, 20), "weiß": (245, 245, 245), "grau": (130, 130, 130),
    "rot": (200, 45, 45), "rosa": (240, 170, 190), "orange": (240, 140, 40),
    "gelb": (240, 210, 60), "grün": (70, 150, 80), "blau": (50, 100, 200),
    "braun": (120, 80, 50), "beige": (220, 200, 170), "lila": (130, 90, 180),
    "türkis": (60, 180, 180),
}

@st.cacheresource(showspinner=False)
def ladekimodell():
    """Lädt ein echtes KI-Modell (CLIP Zero-Shot). Fallbacks: ViT, dann Farbanalyse."""
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

def dominante_farben(image, n=2):
    try:
        klein = image.convert("RGB").resize((48, 48))
        q = klein.quantize(colors=3)
        palette = q.getpalette()
        namen = []
        for _, idx in sorted(q.getcolors(), reverse=True):
            r, g, b = palette[idx  3:idx  3 + 3]
            name = min(FARB_RGB.items(),
                       key=lambda kv: (kv[1][0] - r)  2 + (kv[1][1] - g)  2 + (kv[1][2] - b)  2)[0]
            if name not in namen:
                namen.append(name)
            if len(namen) >= n:
                break
        return namen
    except Exception:
        return []

def ki_scan(image):
    """Echte KI-Erkennung: Kategorie, Muster, Farben -> Tags."""
    art, pipe = ladekimodell()
    farben = dominante_farben(image)
    kategorie, konf, zusatz, muster = "Sonstiges", 0.0, [], []
    if art == "clip":
        kat = sorted(((KATEGORIE_LABELS[r["label"]], r["score"])
                      for r in pipe(image, candidatelabels=list(KATEGORIELABELS))),
                     key=lambda t: -t[1])
        kategorie, konf = kat[0]
        zusatz = [k for k, _ in kat[1:3]]
        muster = [MUSTER_LABELS[m["label"]]
                  for m in pipe(image, candidatelabels=list(MUSTERLABELS))[:1]]
    elif art == "vit":
        preds = pipe(image, top_k=5)
        kat_tags = []
        for p in preds:
            lab = p["label"].lower()
            for kw, de in VIT_MAP:
                if kw in lab and de not in kat_tags:
                    kat_tags.append(de)
                    break
        if kat_tags:
            kategorie, konf = kat_tags[0], preds[0]["score"]
            zusatz = kat_tags[1:3]
    tags, gesehen = [], set()
    for t in [kategorie] + zusatz + farben + muster:
        if t not in gesehen:
            gesehen.add(t)
            tags.append(t)
    return {"kategorie": kategorie, "konfidenz": round(float(konf), 2),
            "farben": farben, "muster": muster, "tags": tags[:6], "modell": art or "Farbanalyse"}


SEED = [
    dict(id="seed-1", name="Beiger Strickpullover", art="gefunden", kategorie="Pullover",
         tags=["Pullover", "beige", "einfarbig"], ort="Stadtbibliothek, 2. OG",
         datum="2024-05-14", kontakt="fundbuero@stadt.example", status="gefunden",
         beschreibung="Weicher Strickpullover, gefunden im Lesesaal.",
         img="https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/1d93f06d3-e699-478f-b5ab-1c80c9f270f7.png",
         ki=dict(kategorie="Pullover", konfidenz=0.93, farben=["beige"], muster=["einfarbig"],
                 tags=["Pullover", "beige", "einfarbig"], modell="clip")),
    dict(id="seed-2", name="Roter Rentier-Pulli", art="vermisst", kategorie="Pullover",
         tags=["Pullover", "rot", "mit Motiv"], ort="Weihnachtsmarkt, Innenstadt",
         datum="2024-05-10", kontakt="anna@beispiel.de", status="vermisst",
         beschreibung="Weihnachtspullover mit weißem Rentier, sehr sentimental.",
         img="https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/168fbd83f-e612-4312-b852-b759a837bec2.png",
         ki=dict(kategorie="Pullover", konfidenz=0.91, farben=["rot", "weiß"], muster=["mit Motiv"],
                 tags=["Pullover", "rot", "mit Motiv"], modell="clip")),
    dict(id="seed-3", name="Schwarze Lederhandschuhe", art="gefunden", kategorie="Handschuhe",
         tags=["Handschuhe", "schwarz", "Leder"], ort="Bushaltestelle Bahnhofstraße",
         datum="2024-05-12", kontakt="fundbuero@stadt.example", status="gefunden",
         beschreibung="Paar schwarze Lederhandschuhe auf einer Bank gefunden.",
         img="https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/15a9f5af0-4f00-436c-846d-2b28f45c8668.png",
         ki=dict(kategorie="Handschuhe", konfidenz=0.89, farben=["schwarz"], muster=["einfarbig"],
                 tags=["Handschuhe", "schwarz", "einfarbig"], modell="clip")),
    dict(id="seed-4", name="Blauer Rucksack", art="vermisst", kategorie="Rucksack",
         tags=["Rucksack", "blau", "einfarbig"], ort="Uni-Mensa, Campus Nord",
         datum="2024-05-08", kontakt="max@beispiel.de", status="vermisst",
         beschreibung="Blauer Rucksack mit silbernen Reißverschlüssen, Laptopfach.",
         img="https://image.qwenlm.ai/public_source/eb1442b2-84be-470b-9d4e-407314fab36b/10568a9d7-a103-4755-a7fb-04a7ea6c3348.png",
         ki=dict(kategorie="Rucksack", konfidenz=0.95, farben=["blau"], muster=["einfarbig"],
                 tags=["Rucksack", "blau", "einfarbig"], modell="clip")),
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

if "db" not in st.session_state:
    st.sessionstate.db = ladedb()
if "page" not in st.session_state:
    st.session_state.page = "home"
if "carousel" not in st.session_state:
    st.session_state.carousel = 0
if "selected" not in st.session_state:
    st.session_state.selected = None
if "scan" not in st.session_state:
    st.session_state.scan = None
if "scanfile" not in st.sessionstate:
    st.sessionstate.scanfile = None
if "zeigekontakt" not in st.sessionstate:
    st.sessionstate.zeigekontakt = False

def navigate(page):
    st.session_state.page = page
    st.sessionstate.zeigekontakt = False
    st.rerun()

def badge(text):
    return f"{text}"

def status_badge(status):
    cls = {"gefunden": "status-gefunden", "vermisst": "status-vermisst",
           "zurückgegeben": "status-zurueckgegeben"}.get(status, "status-gefunden")
    return f"{status}"

def karte(item, key):
    with st.container():
        st.markdown("", unsafeallowhtml=True)
        st.image(item["img"], usecontainerwidth=True)
        st.markdown(f"{item['name']} &nbsp; {status_badge(item['status'])}",
                    unsafeallowhtml=True)
        st.markdown(f"📍 {item['ort']} · 🗓 {item['datum']}",
                    unsafeallowhtml=True)
        st.markdown("".join(badge(t) for t in item["tags"][:4]), unsafeallowhtml=True)
        if st.button("Ansehen", key=key, usecontainerwidth=True):
            st.session_state.selected = item["id"]
            navigate("detail")
        st.markdown("", unsafeallowhtml=True)
        
if st.session_state.page == "home":
    st.markdown("🔍 Fundgrube", unsafeallowhtml=True)
    st.markdown("Virtuelles Fundbüro – Verlorenes wiederfinden & Funde melden",
                unsafeallowhtml=True)

    db = st.session_state.db
    offen = [i for i in db if i["status"] != "zurückgegeben"]
    c1, c2, c3 = st.columns(3)
    c1.metric("Fundstücke", sum(1 for i in db if i["art"] == "gefunden"))
    c2.metric("Vermisst", sum(1 for i in db if i["art"] == "vermisst"))
    c3.metric("Offene Einträge", len(offen))

    st.markdown("Zuletzt hinzugefügt", unsafeallowhtml=True)
    liste = sorted(db, key=lambda i: i["datum"], reverse=True)
    if liste:
        idx = st.session_state.carousel % len(liste)
        akt = liste[idx]
        l, m, r = st.columns([1, 6, 1])
        with l:
            if st.button("‹", usecontainerwidth=True):
                st.session_state.carousel = (idx - 1) % len(liste)
                st.rerun()
        with m:
            st.image(akt["img"], usecontainerwidth=True)
            st.markdown(f"{akt['name']} &nbsp; {status_badge(akt['status'])}",
                        unsafeallowhtml=True)
            st.markdown("".join(badge(t) for t in akt["tags"][:4]), unsafeallowhtml=True)
        with r:
            if st.button("›", usecontainerwidth=True):
                st.session_state.carousel = (idx + 1) % len(liste)
                st.rerun()
        st.write("")
        c1, c2, c3 = st.columns([1, 4, 1])
        with c2:
            if st.button("🔍 Fundstück suchen", usecontainerwidth=True):
                navigate("suchen")
            st.write("")
            if st.button("↑ Fund melden", type="primary", usecontainerwidth=True):
                navigate("hochladen")
    else:
        st.info("Noch keine Einträge vorhanden. Melde deinen ersten Fund!")
        if st.button("↑ Fund melden", type="primary", usecontainerwidth=True):
            navigate("hochladen")



elif st.session_state.page == "suchen":
    if st.button("↩ Zurück"):
        navigate("home")
    st.markdown("### 🔍 Fundstück suchen")
    query = st.text_input("Suchbegriff (Name, Tag, Ort …)", value="")
    f1, f2 = st.columns(2)
    with f1:
        status_filter = st.selectbox("Status", ["Alle", "gefunden", "vermisst", "zurückgegeben"])
    with f2:
        kats = sorted({i["kategorie"] for i in st.session_state.db})
        kat_filter = st.multiselect("Kategorie", kats)

    erg = st.session_state.db
    if query:
        q = query.lower().strip()
        erg = [i for i in erg if q in i["name"].lower() or q in i["ort"].lower()
               or any(q in t.lower() for t in i["tags"])]
    if status_filter != "Alle":
        erg = [i for i in erg if i["status"] == status_filter]
    if kat_filter:
        erg = [i for i in erg if i["kategorie"] in kat_filter]

    st.write("")
    if erg:
        cols = st.columns(2)
        for n, item in enumerate(erg):
            with cols[n % 2]:
                karte(item, key=f"k_{item['id']}")
    else:
        st.info("Kein Treffer – vielleicht magst du selbst einen Fund melden?")



elif st.session_state.page == "hochladen":
    if st.button("↩ Zurück"):
        navigate("home")
    st.markdown("### ↑ Fund melden / Vermisstenanzeige")
    uploaded = st.file_uploader("Foto hochladen", type=["jpg", "jpeg", "png"])

    if uploaded:
        if uploaded.name != st.sessionstate.scanfile:
            st.session_state.scan = None
            st.sessionstate.scanfile = uploaded.name
        bild_obj = Image.open(uploaded).convert("RGB")
        st.image(bildobj, usecontainer_width=True)

        if st.button("🤖 Hochladen & KI-Scan", type="primary", usecontainerwidth=True):
            with st.spinner("KI-Modell analysiert das Bild … (erstes Laden dauert kurz)"):
                st.sessionstate.scan = kiscan(bild_obj)

        if st.session_state.scan:
            res = st.session_state.scan
            st.markdown("#### 🤖 KI-Erkenntnis")
            st.markdown(f"Kategorie: {res['kategorie']} · Modell: {res['modell']}")
            st.progress(float(res["konfidenz"]))
            st.caption(f"Konfidenz: {int(res['konfidenz'] * 100)} %")
            st.markdown("".join(badge(t) for t in res["tags"]), unsafeallowhtml=True)

            st.markdown("#### Angaben zum Eintrag")
            name = st.text_input("Bezeichnung", value=res["kategorie"])
            art = st.radio("Art", ["gefunden", "vermisst"], horizontal=True)
            ort = st.text_input("Fundort / Verlustort")
            datum = st.date_input("Datum", value=date.today())
            kontakt = st.text_input("Kontakt (E-Mail / Telefon)")
            beschreibung = st.text_area("Beschreibung")
            tagstxt = st.textinput("Tags (KI-Vorschlag, anpassbar)",
                                     value=", ".join(res["tags"]))
            if st.button("💾 In Fundgrube aufnehmen", type="primary", usecontainerwidth=True):
                if not name.strip() or not ort.strip():
                    st.warning("Bitte mindestens Bezeichnung und Ort angeben.")
                else:
                    bid = uuid.uuid4().hex
                    pfad = BILD_ORDNER / f"{bid}.png"
                    bild_obj.save(pfad, format="PNG")
                    eintrag = dict(id=bid, name=name.strip(), art=art,
                                   kategorie=res["kategorie"],
                                   tags=[t.strip() for t in tags_txt.split(",") if t.strip()],
                                   ort=ort.strip(), datum=datum.isoformat(),
                                   kontakt=kontakt.strip(), beschreibung=beschreibung.strip(),
                                   status=art, img=str(pfad), ki=res)
                    st.session_state.db.insert(0, eintrag)
                    speicheredb(st.sessionstate.db)
                    st.session_state.scan = None
                    st.sessionstate.scanfile = None
                    st.session_state.selected = bid
                    st.balloons()
                    navigate("detail")
    else:
        st.info("Bitte lade ein Foto hoch – die KI erkennt automatisch Kategorie, Farben & Muster.")



elif st.session_state.page == "detail":
    if st.button("↩ Zurück"):
        navigate("suchen")
    item = next((i for i in st.sessionstate.db if i["id"] == st.sessionstate.selected), None)
    if item:
        st.image(item["img"], usecontainerwidth=True)
        st.markdown(f"### {item['name']}")
        st.markdown(f"{status_badge(item['status'])} &nbsp; "
                    f"📍 {item['ort']} · 🗓 {item['datum']}",
                    unsafeallowhtml=True)
        st.markdown("".join(badge(t) for t in item["tags"]), unsafeallowhtml=True)
        if item.get("beschreibung"):
            st.write(item["beschreibung"])

        with st.expander("🤖 KI-Analyse anzeigen"):
            ki = item.get("ki", {})
            st.markdown(f"Erkannte Kategorie: {ki.get('kategorie', '–')} "
                        f"· Modell: {ki.get('modell', '–')}")
            st.progress(float(ki.get("konfidenz", 0.0)))
            st.markdown(f"Farben: {', '.join(ki.get('farben', [])) or '–'}  ·  "
                        f"Muster: {', '.join(ki.get('muster', [])) or '–'}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✉ Kontakt anzeigen", usecontainerwidth=True):
                st.sessionstate.zeigekontakt = not st.sessionstate.zeigekontakt
        with c2:
            if item["status"] != "zurückgegeben":
                if st.button("✅ Als zurückgegeben markieren", usecontainerwidth=True):
                    item["status"] = "zurückgegeben"
                    speicheredb(st.sessionstate.db)
                    st.rerun()
        if st.sessionstate.zeigekontakt:
            st.success(f"Kontakt: {item.get('kontakt') or 'Kein Kontakt hinterlegt'}")
        if st.button("🗑 Eintrag entfernen", usecontainerwidth=True):
            st.sessionstate.db = [i for i in st.sessionstate.db if i["id"] != item["id"]]
            speicheredb(st.sessionstate.db)
            navigate("home")
    else:
        st.warning("Eintrag nicht gefunden.")
        if st.button(" Zur Startseite", usecontainerwidth=True):
            navigate("home")
