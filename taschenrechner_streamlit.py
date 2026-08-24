"""
Grafischer Taschenrechner mit Streamlit - Material-You-Design
----------------------------------------------------------------
Benötigt nur das Paket "streamlit" - keine weiteren externen
Bibliotheken (Berechnung erfolgt mit einem selbstgeschriebenen
Auswertungs-Algorithmus, kein eval(), kein numpy o.ä.).

Design: Material 3 / Material You (Farbtöne, runde Formen,
abgestufte Container) - umgesetzt rein mit CSS.

Responsiv: Das Layout passt sich per CSS (clamp(), vw-Einheiten,
Flex-Grid) automatisch an jede Bildschirmgröße an - vom Smartphone
bis zum Desktop-Fenster.

Voraussetzung: Streamlit >= 1.32 (wegen st.container(key=...),
das für die Material-Farbtöne der einzelnen Tasten benötigt wird).

Installation (falls streamlit noch fehlt oder veraltet ist):
    pip install --upgrade streamlit

Start:
    streamlit run taschenrechner_streamlit.py
"""

import streamlit as st

st.set_page_config(page_title="Taschenrechner", page_icon="🧮", layout="centered")


# ----------------------------------------------------------------------
# Eigener Auswertungs-Algorithmus (Shunting-Yard), ohne eval()
# ----------------------------------------------------------------------
def sichere_auswertung(ausdruck: str):
    erlaubte_zeichen = set("0123456789.+-*/% ")
    if not set(ausdruck) <= erlaubte_zeichen:
        raise ValueError("Ungültiges Zeichen")

    zahlen, operatoren = [], []
    rangfolge = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2}

    def anwenden():
        op = operatoren.pop()
        b = zahlen.pop()
        a = zahlen.pop()
        if op == "+":
            zahlen.append(a + b)
        elif op == "-":
            zahlen.append(a - b)
        elif op == "*":
            zahlen.append(a * b)
        elif op == "/":
            zahlen.append(a / b)
        elif op == "%":
            zahlen.append(a % b)

    i, n = 0, len(ausdruck)
    erwartet_zahl = True
    while i < n:
        ch = ausdruck[i]
        if ch == " ":
            i += 1
            continue
        if ch.isdigit() or ch == "." or (ch == "-" and erwartet_zahl):
            j = i + 1
            while j < n and (ausdruck[j].isdigit() or ausdruck[j] == "."):
                j += 1
            zahlen.append(float(ausdruck[i:j]))
            i = j
            erwartet_zahl = False
        elif ch in rangfolge:
            while operatoren and rangfolge[operatoren[-1]] >= rangfolge[ch]:
                anwenden()
            operatoren.append(ch)
            i += 1
            erwartet_zahl = True
        else:
            raise ValueError("Unerwartetes Zeichen")

    while operatoren:
        anwenden()

    if len(zahlen) != 1:
        raise ValueError("Ungültiger Ausdruck")
    return zahlen[0]


# ----------------------------------------------------------------------
# Zustand initialisieren
# ----------------------------------------------------------------------
if "eingabe" not in st.session_state:
    st.session_state.eingabe = ""
if "ausdruck" not in st.session_state:
    st.session_state.ausdruck = ""
if "anzeige" not in st.session_state:
    st.session_state.anzeige = "0"


def taste_gedrueckt(taste: str):
    if taste == "C":
        st.session_state.eingabe = ""
        st.session_state.ausdruck = ""
        st.session_state.anzeige = "0"

    elif taste == "←":
        st.session_state.eingabe = st.session_state.eingabe[:-1]
        st.session_state.anzeige = st.session_state.eingabe or "0"

    elif taste == "±":
        if st.session_state.eingabe.startswith("-"):
            st.session_state.eingabe = st.session_state.eingabe[1:]
        elif st.session_state.eingabe:
            st.session_state.eingabe = "-" + st.session_state.eingabe
        st.session_state.anzeige = st.session_state.eingabe or "0"

    elif taste == "=":
        voller_ausdruck = st.session_state.ausdruck + st.session_state.eingabe
        if voller_ausdruck:
            try:
                ergebnis = sichere_auswertung(voller_ausdruck)
                if float(ergebnis).is_integer():
                    ergebnis = int(ergebnis)
                st.session_state.anzeige = str(ergebnis)
                st.session_state.eingabe = str(ergebnis)
                st.session_state.ausdruck = ""
            except (ZeroDivisionError, ValueError, SyntaxError):
                st.session_state.anzeige = "Fehler"
                st.session_state.eingabe = ""
                st.session_state.ausdruck = ""

    elif taste in ("÷", "×", "+", "-", "%"):
        if st.session_state.eingabe:
            op = {"÷": "/", "×": "*"}.get(taste, taste)
            st.session_state.ausdruck += st.session_state.eingabe + op
            st.session_state.eingabe = ""
            st.session_state.anzeige = st.session_state.ausdruck

    else:  # Ziffern und Komma
        zeichen = "." if taste == "," else taste
        st.session_state.eingabe += zeichen
        st.session_state.anzeige = st.session_state.eingabe


# ----------------------------------------------------------------------
# Material-You (Material 3) Design + responsives Layout
# (reines CSS/HTML - keine externe Bibliothek)
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500&family=Roboto:wght@400;500;700&display=swap');

    :root{
        --md-primary:            #6750A4;
        --md-on-primary:         #FFFFFF;
        --md-primary-container:  #EADDFF;
        --md-on-primary-container:#21005D;
        --md-secondary-container:#E8DEF8;
        --md-on-secondary-container:#1D192B;
        --md-tertiary-container: #FFD8E4;
        --md-on-tertiary-container:#31111D;
        --md-error-container:    #F9DEDC;
        --md-on-error-container: #410E0B;
        --md-surface:            #FEF7FF;
        --md-surface-container:  #F3EDF7;
        --md-surface-variant:    #E7E0EC;
        --md-on-surface:         #1C1B1F;
        --md-on-surface-variant: #49454F;
        --md-outline:            #79747E;
    }

    @media (prefers-color-scheme: dark){
        :root{
            --md-primary:            #D0BCFF;
            --md-on-primary:         #381E72;
            --md-primary-container:  #4F378B;
            --md-on-primary-container:#EADDFF;
            --md-secondary-container:#4A4458;
            --md-on-secondary-container:#E8DEF8;
            --md-tertiary-container:  #633B48;
            --md-on-tertiary-container:#FFD8E4;
            --md-error-container:     #8C1D18;
            --md-on-error-container:  #F9DEDC;
            --md-surface:             #141218;
            --md-surface-container:   #211F26;
            --md-surface-variant:     #49454F;
            --md-on-surface:          #E6E1E5;
            --md-on-surface-variant:  #CAC4D0;
            --md-outline:             #938F99;
        }
    }

    html, body, [class*="css"]{
        font-family: 'Google Sans', 'Roboto', sans-serif;
    }

    .stApp{
        background: var(--md-surface);
    }

    /* App-Fenster wie eine Handy-Karte zentrieren -> passt sich jeder
       Bildschirmgroesse an (Desktop, Tablet, Handy) */
    .main .block-container{
        max-width: 420px;
        margin: 0 auto;
        padding: clamp(0.75rem, 4vw, 1.5rem);
    }

    .md-titel{
        font-size: clamp(1.25rem, 5vw, 1.6rem);
        font-weight: 500;
        color: var(--md-on-surface);
        margin: 0.25rem 0 1rem 0;
        text-align: center;
        letter-spacing: 0.02em;
    }

    /* Anzeige = Material 3 "Surface Container" mit grosser Rundung */
    .md-display{
        background: var(--md-surface-container);
        border: 1px solid var(--md-outline);
        color: var(--md-on-surface);
        border-radius: clamp(20px, 5vw, 28px);
        padding: clamp(1rem, 5vw, 1.5rem) clamp(1.25rem, 5vw, 1.75rem);
        margin-bottom: clamp(0.75rem, 3vw, 1.25rem);
        min-height: 48px;
        text-align: right;
        word-wrap: break-word;
        overflow-wrap: anywhere;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.08);
    }
    .md-display .ausdruck-zeile{
        font-size: clamp(0.85rem, 3vw, 1rem);
        color: var(--md-on-surface-variant);
        min-height: 1.2em;
    }
    .md-display .ergebnis-zeile{
        font-size: clamp(2rem, 10vw, 3rem);
        font-weight: 500;
        line-height: 1.15;
    }

    /* Grundform aller Tasten: kreisrunde Material-3-Buttons,
       die sich per aspect-ratio jeder Bildschirmbreite anpassen */
    div.stButton > button{
        width: 100%;
        aspect-ratio: 1 / 1;
        height: auto;
        border-radius: 50%;
        border: none;
        font-family: 'Google Sans', 'Roboto', sans-serif;
        font-size: clamp(1rem, 4.5vw, 1.4rem);
        font-weight: 500;
        color: var(--md-on-surface);
        background: var(--md-surface-variant);
        transition: transform 0.08s ease, filter 0.15s ease;
        box-shadow: none;
    }
    div.stButton > button:hover{
        filter: brightness(0.95);
        border: none;
    }
    div.stButton > button:active{
        transform: scale(0.94);
    }
    div.stButton > button:focus:not(:active){
        border: none;
        box-shadow: 0 0 0 3px var(--md-primary-container);
    }

    /* Zahlen-Tasten: "Secondary Container" Ton */
    div[class*="st-key-num-key"] div.stButton > button{
        background: var(--md-secondary-container);
        color: var(--md-on-secondary-container);
    }

    /* Operator-Tasten (+ - x /) : "Primary Container" Ton */
    div[class*="st-key-op-key"] div.stButton > button{
        background: var(--md-primary-container);
        color: var(--md-on-primary-container);
        font-weight: 700;
    }

    /* "=" hebt sich zusaetzlich als gefuellter Primary-Button ab */
    div[class*="st-key-equals-key"] div.stButton > button{
        background: var(--md-primary);
        color: var(--md-on-primary);
        font-weight: 700;
    }

    /* Funktions-Tasten (Loeschen, %, +/-): "Tertiary" Ton */
    div[class*="st-key-func-key"] div.stButton > button{
        background: var(--md-tertiary-container);
        color: var(--md-on-tertiary-container);
    }

    /* "C" (alles loeschen): "Error" Ton */
    div[class*="st-key-clear-key"] div.stButton > button{
        background: var(--md-error-container);
        color: var(--md-on-error-container);
    }

    /* Reihen der Tastatur bleiben IMMER als Grid nebeneinander,
       auch auf sehr schmalen Handy-Bildschirmen (kein Umbrechen) */
    div[data-testid="stHorizontalBlock"]{
        flex-direction: row !important;
        gap: clamp(6px, 2.5vw, 12px) !important;
        margin-bottom: clamp(6px, 2.5vw, 12px);
    }
    div[data-testid="column"]{
        width: 100% !important;
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
    }

    /* Sehr kleine Handy-Breiten: Abstaende weiter verringern */
    @media (max-width: 360px){
        div[data-testid="stHorizontalBlock"]{ gap: 5px !important; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="md-titel">🧮 Taschenrechner</div>', unsafe_allow_html=True)

# Anzeige (obere Zeile = laufender Ausdruck, untere Zeile = aktueller Wert)
st.markdown(
    f"""
    <div class="md-display">
        <div class="ausdruck-zeile">{st.session_state.ausdruck or "&nbsp;"}</div>
        <div class="ergebnis-zeile">{st.session_state.anzeige}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tastenlayout: (Beschriftung, CSS-Klasse fuer den Material-Farbton)
tastenreihen = [
    [("C", "clear-key"), ("←", "func-key"), ("%", "func-key"), ("÷", "op-key")],
    [("7", "num-key"), ("8", "num-key"), ("9", "num-key"), ("×", "op-key")],
    [("4", "num-key"), ("5", "num-key"), ("6", "num-key"), ("-", "op-key")],
    [("1", "num-key"), ("2", "num-key"), ("3", "num-key"), ("+", "op-key")],
    [("±", "func-key"), ("0", "num-key"), (",", "num-key"), ("=", "equals-key")],
]

for r_idx, reihe in enumerate(tastenreihen):
    spalten = st.columns(4)
    for c_idx, (spalte, (taste, css_klasse)) in enumerate(zip(spalten, reihe)):
        with spalte:
            # st.container(key=...) erzeugt eine div mit der Klasse
            # "st-key-<key>" - darueber laesst sich jede Taste gezielt
            # per CSS einfaerben (benoetigt Streamlit >= 1.32).
            with st.container(key=f"{css_klasse}-{r_idx}-{c_idx}"):
                st.button(taste, key=f"btn_{r_idx}_{c_idx}",
                          on_click=taste_gedrueckt, args=(taste,))
