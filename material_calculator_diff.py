import streamlit as st

st.set_page_config(page_title="Material You Taschenrechner", page_icon="🧮", layout="centered")


# ----------------------------------------------------------------------
# Sichere Auswertung ohne eval()[cite: 1]
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
# Zustand initialisieren[cite: 1]
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

    else:
        zeichen = "." if taste == "," else taste
        st.session_state.eingabe += zeichen
        st.session_state.anzeige = st.session_state.eingabe


# ----------------------------------------------------------------------
# Dynamisches Material You (M3) Design & Adaptive Fenster-Skalierung
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Google+Sans:wght@400;500;700&display=swap');

    :root {
        --md-sys-color-primary: #6750A4;
        --md-sys-color-on-primary: #FFFFFF;
        --md-sys-color-primary-container: #EADDFF;
        --md-sys-color-on-primary-container: #21005D;
        --md-sys-color-secondary-container: #E8DEF8;
        --md-sys-color-on-secondary-container: #1D192B;
        --md-sys-color-tertiary-container: #FFD8E4;
        --md-sys-color-on-tertiary-container: #31111D;
        --md-sys-color-error-container: #F9DEDC;
        --md-sys-color-on-error-container: #410E0B;
        --md-sys-color-surface: #FEF7FF;
        --md-sys-color-surface-container-high: #F3EDF7;
        --md-sys-color-surface-container-highest: #E6E0E9;
        --md-sys-color-on-surface: #1D1B20;
        --md-sys-color-on-surface-variant: #49454F;
        --md-sys-color-outline-variant: #CAC4D0;
        
        --md-sys-motion-easing: cubic-bezier(0.2, 0.0, 0.0, 1.0);
    }

    @media (prefers-color-scheme: dark) {
        :root {
            --md-sys-color-primary: #D0BCFF;
            --md-sys-color-on-primary: #381E72;
            --md-sys-color-primary-container: #4F378B;
            --md-sys-color-on-primary-container: #EADDFF;
            --md-sys-color-secondary-container: #4A4458;
            --md-sys-color-on-secondary-container: #E8DEF8;
            --md-sys-color-tertiary-container: #633B48;
            --md-sys-color-on-tertiary-container: #FFD8E4;
            --md-sys-color-error-container: #8C1D18;
            --md-sys-color-on-error-container: #F9DEDC;
            --md-sys-color-surface: #141218;
            --md-sys-color-surface-container-high: #2B2930;
            --md-sys-color-surface-container-highest: #36343B;
            --md-sys-color-on-surface: #E6E1E5;
            --md-sys-color-on-surface-variant: #CAC4D0;
            --md-sys-color-outline-variant: #49454F;
        }
    }

    /* Streamlit UI Anpassung */
    header, footer, [data-testid="stHeader"] { display: none !important; }
    
    html, body, [class*="css"] {
        font-family: 'Google Sans', sans-serif;
    }

    .stApp {
        background: var(--md-sys-color-surface);
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 100vh;
        min-height: 100dvh;
    }

    /* Dynamische Container-Anpassung basierend auf Fenster-Breite UND -Höhe */
    .main .block-container {
        width: min(92vw, calc(80vh * 0.65));
        max-width: 440px;
        margin: auto;
        padding: clamp(0.75rem, 2vh, 1.5rem);
        background: var(--md-sys-color-surface-container-high);
        border-radius: clamp(24px, 4vw, 36px);
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        border: 1px solid var(--md-sys-color-outline-variant);
    }

    .md-titel {
        font-size: clamp(1rem, 2.5vh, 1.3rem);
        font-weight: 500;
        color: var(--md-sys-color-on-surface);
        margin-bottom: clamp(0.5rem, 1.5vh, 1rem);
        text-align: center;
        letter-spacing: 0.01em;
    }

    /* M3 Surface Container Display */
    .md-display {
        background: var(--md-sys-color-surface-container-highest);
        color: var(--md-sys-color-on-surface);
        border-radius: clamp(18px, 3.5vw, 24px);
        padding: clamp(0.75rem, 2vh, 1.25rem) clamp(1rem, 3vw, 1.5rem);
        margin-bottom: clamp(0.75rem, 2vh, 1.25rem);
        text-align: right;
        word-wrap: break-word;
        overflow-wrap: anywhere;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
    }
    
    .md-display .ausdruck-zeile {
        font-size: clamp(0.8rem, 2vh, 1rem);
        color: var(--md-sys-color-on-surface-variant);
        min-height: 1.4em;
    }
    
    .md-display .ergebnis-zeile {
        font-size: clamp(1.8rem, 5vh, 2.8rem);
        font-weight: 500;
        line-height: 1.1;
    }

    /* M3 Dynamic State Layer Buttons */
    div.stButton > button {
        width: 100%;
        aspect-ratio: 1 / 1;
        height: auto;
        border-radius: clamp(16px, 3.5vw, 28px);
        border: none;
        font-family: 'Google Sans', sans-serif;
        font-size: clamp(1rem, 3vh, 1.4rem);
        font-weight: 500;
        color: var(--md-sys-color-on-surface);
        background: var(--md-sys-color-surface-container-highest);
        transition: transform 0.15s var(--md-sys-motion-easing), 
                    filter 0.2s var(--md-sys-motion-easing),
                    border-radius 0.2s var(--md-sys-motion-easing);
    }

    div.stButton > button:hover {
        filter: brightness(0.92);
        border: none;
        border-radius: clamp(12px, 2.5vw, 20px);
    }

    div.stButton > button:active {
        transform: scale(0.92);
    }

    div.stButton > button:focus:not(:active) {
        border: none;
        outline: 2px solid var(--md-sys-color-primary);
    }

    /* Tonal Color Mapping */
    div[class*="st-key-num-key"] div.stButton > button {
        background: var(--md-sys-color-secondary-container);
        color: var(--md-sys-color-on-secondary-container);
    }

    div[class*="st-key-op-key"] div.stButton > button {
        background: var(--md-sys-color-primary-container);
        color: var(--md-sys-color-on-primary-container);
        font-weight: 700;
    }

    div[class*="st-key-equals-key"] div.stButton > button {
        background: var(--md-sys-color-primary);
        color: var(--md-sys-color-on-primary);
        font-weight: 700;
        border-radius: clamp(18px, 4vw, 32px);
    }

    div[class*="st-key-func-key"] div.stButton > button {
        background: var(--md-sys-color-tertiary-container);
        color: var(--md-sys-color-on-tertiary-container);
    }

    div[class*="st-key-clear-key"] div.stButton > button {
        background: var(--md-sys-color-error-container);
        color: var(--md-sys-color-on-error-container);
    }

    /* Raster-Layout für mobile und Desktop-Fenster */
    div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        gap: clamp(4px, 1.2vh, 10px) !important;
        margin-bottom: clamp(4px, 1.2vh, 10px);
    }

    div[data-testid="column"] {
        width: 100% !important;
        flex: 1 1 0 !important;
        min-width: 0 !important;
        padding: 0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="md-titel">🧮 Taschenrechner</div>', unsafe_allow_html=True)

# Display[cite: 1]
st.markdown(
    f"""
    <div class="md-display">
        <div class="ausdruck-zeile">{st.session_state.ausdruck or "&nbsp;"}</div>
        <div class="ergebnis-zeile">{st.session_state.anzeige}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Tasten-Grid[cite: 1]
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
            with st.container(key=f"{css_klasse}-{r_idx}-{c_idx}"):
                st.button(
                    taste,
                    key=f"btn_{r_idx}_{c_idx}",
                    on_click=taste_gedrueckt,
                    args=(taste,),
                )
