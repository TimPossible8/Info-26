"""
Grafischer Taschenrechner mit Streamlit
-----------------------------------------
Benötigt nur das Paket "streamlit" - keine weiteren externen
Bibliotheken (Berechnung erfolgt mit einem selbstgeschriebenen
Auswertungs-Algorithmus, kein eval(), kein numpy o.ä.).

Installation (falls streamlit noch fehlt):
    pip install streamlit

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
# Optisches Feintuning (nur CSS, keine externe Bibliothek)
# ----------------------------------------------------------------------
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        height: 60px;
        font-size: 20px;
        border-radius: 10px;
        border: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧮 Taschenrechner")

# Anzeige
st.markdown(
    f"""
    <div style="
        background-color:#1e1e1e;
        color:white;
        font-size:36px;
        text-align:right;
        padding:20px;
        border-radius:10px;
        margin-bottom:15px;
        min-height:60px;
        word-wrap:break-word;">
        {st.session_state.anzeige}
    </div>
    """,
    unsafe_allow_html=True,
)

# Tastenlayout
tastenreihen = [
    ["C", "←", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "-"],
    ["1", "2", "3", "+"],
    ["±", "0", ",", "="],
]

for reihe in tastenreihen:
    spalten = st.columns(4)
    for spalte, taste in zip(spalten, reihe):
        with spalte:
            st.button(taste, key=f"btn_{taste}_{reihe.index(taste)}",
                      on_click=taste_gedrueckt, args=(taste,))