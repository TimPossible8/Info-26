
import streamlit as st

# Seitenkonfiguration
st.set_page_config(
    page_title="Material Taschenrechner",
    page_icon="🧮",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS für Material Design Look
st.markdown("""
<style>
/* Hauptcontainer */
.calculator-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    max-width: 400px;
    margin: 0 auto;
}

/* Display Bereich */
.display-container {
    background: #ffffff;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.display-value {
    font-size: 48px;
    font-weight: 300;
    text-align: right;
    color: #333;
    min-height: 60px;
    word-wrap: break-word;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
}

.display-expression {
    font-size: 14px;
    color: #666;
    text-align: right;
    min-height: 20px;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Button Grid */
.button-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
}

/* Button Styling */
.stButton > button {
    border: none !important;
    border-radius: 16px !important;
    padding: 20px 0 !important;
    font-size: 24px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15) !important;
    height: 70px !important;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.15) !important;
}

/* Zahl Buttons - Light */
.btn-number {
    background: #ffffff !important;
    color: #333333 !important;
}

.btn-number:hover {
    background: #f5f5f5 !important;
}

/* Operator Buttons - Primary Color */
.btn-operator {
    background: #3f51b5 !important;
    color: #ffffff !important;
}

.btn-operator:hover {
    background: #303f9f !important;
}

/* Funktion Buttons - Secondary */
.btn-function {
    background: #e0e0e0 !important;
    color: #333333 !important;
}

.btn-function:hover {
    background: #d0d0d0 !important;
}

/* Equals Button - Accent */
.btn-equals {
    background: #ff4081 !important;
    color: #ffffff !important;
}

.btn-equals:hover {
    background: #f50057 !important;
}

/* Zero Button - Spans 2 columns */
.btn-zero {
    grid-column: span 2 !important;
}

/* Responsive Anpassungen */
@media (max-width: 480px) {
    .calculator-container {
        padding: 16px;
        border-radius: 16px;
    }

    .display-value {
        font-size: 36px !important;
    }

    .stButton > button {
        padding: 16px 0 !important;
        height: 60px !important;
        font-size: 20px !important;
    }

    .button-grid {
        gap: 8px;
    }
}

@media (min-width: 768px) {
    .calculator-container {
        max-width: 450px;
        padding: 32px;
    }

    .display-value {
        font-size: 56px !important;
    }

    .stButton > button {
        height: 80px !important;
        font-size: 28px !important;
    }
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Session State Initialisierung
if 'current_value' not in st.session_state:
    st.session_state.current_value = '0'
if 'expression' not in st.session_state:
    st.session_state.expression = ''
if 'last_was_result' not in st.session_state:
    st.session_state.last_was_result = False

def calculate_expression(expr):
    """Berechnet einen mathematischen Ausdruck sicher."""
    try:
        # Ersetze visuelle Operatoren durch Python-Operatoren
        expr = expr.replace('×', '*').replace('÷', '/')
        # Evaluiere den Ausdruck (nur Zahlen und Operatoren erlaubt)
        result = eval(expr)
        # Runde auf maximale 10 Dezimalstellen
        if isinstance(result, float):
            result = round(result, 10)
            # Entferne unnötige Nullen nach dem Komma
            if result == int(result):
                result = int(result)
        return str(result)
    except:
        return 'Error'

def add_digit(digit):
    """Fügt eine Ziffer zum aktuellen Wert hinzu."""
    if st.session_state.last_was_result:
        st.session_state.current_value = digit
        st.session_state.expression = ''
        st.session_state.last_was_result = False
    else:
        if st.session_state.current_value == '0' and digit != '.':
            st.session_state.current_value = digit
        elif digit == '.' and '.' in st.session_state.current_value:
            pass  # Verhindere mehrere Dezimalpunkte
        else:
            st.session_state.current_value += digit

def add_operator(op):
    """Fügt einen Operator zur Expression hinzu."""
    current = st.session_state.current_value

    if st.session_state.last_was_result:
        st.session_state.expression = current + ' ' + op + ' '
        st.session_state.last_was_result = False
    else:
        if st.session_state.expression:
            st.session_state.expression = st.session_state.expression.rstrip() + ' ' + op + ' '
        else:
            st.session_state.expression = current + ' ' + op + ' '

    st.session_state.current_value = '0'

def calculate():
    """Berechnet das Ergebnis der aktuellen Expression."""
    if st.session_state.expression:
        full_expr = st.session_state.expression + st.session_state.current_value
        result = calculate_expression(full_expr)
        st.session_state.expression = ''
        st.session_state.current_value = result
        st.session_state.last_was_result = True

def clear():
    """Setzt den Rechner zurück."""
    st.session_state.current_value = '0'
    st.session_state.expression = ''
    st.session_state.last_was_result = False

def delete_last():
    """Löscht das letzte Zeichen."""
    if st.session_state.last_was_result:
        clear()
    else:
        if len(st.session_state.current_value) > 1:
            st.session_state.current_value = st.session_state.current_value[:-1]
        else:
            st.session_state.current_value = '0'

def toggle_sign():
    """Wechselt das Vorzeichen."""
    if st.session_state.current_value != '0':
        if st.session_state.current_value.startswith('-'):
            st.session_state.current_value = st.session_state.current_value[1:]
        else:
            st.session_state.current_value = '-' + st.session_state.current_value

def percentage():
    """Berechnet Prozent."""
    try:
        value = float(st.session_state.current_value)
        result = value / 100
        if result == int(result):
            st.session_state.current_value = str(int(result))
        else:
            st.session_state.current_value = str(round(result, 10))
    except:
        pass

# UI Layout
st.markdown('<div class="calculator-container">', unsafe_allow_html=True)

# Display
st.markdown(f"""
<div class="display-container">
    <div class="display-expression">{st.session_state.expression}</div>
    <div class="display-value">{st.session_state.current_value}</div>
</div>
""", unsafe_allow_html=True)

# Button Grid mit unique Keys
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    if st.button("C", key="btn_c", use_container_width=True):
        clear()
    if st.button("%", key="btn_percent", use_container_width=True):
        percentage()
    if st.button("±", key="btn_sign", use_container_width=True):
        toggle_sign()
    if st.button("÷", key="btn_div", use_container_width=True):
        add_operator('÷')

with col2:
    if st.button("7", key="btn_7", use_container_width=True):
        add_digit('7')
    if st.button("8", key="btn_8", use_container_width=True):
        add_digit('8')
    if st.button("9", key="btn_9", use_container_width=True):
        add_digit('9')
    if st.button("×", key="btn_mul", use_container_width=True):
        add_operator('×')

with col3:
    if st.button("4", key="btn_4", use_container_width=True):
        add_digit('4')
    if st.button("5", key="btn_5", use_container_width=True):
        add_digit('5')
    if st.button("6", key="btn_6", use_container_width=True):
        add_digit('6')
    if st.button("−", key="btn_sub", use_container_width=True):
        add_operator('-')

with col4:
    if st.button("1", key="btn_1", use_container_width=True):
        add_digit('1')
    if st.button("2", key="btn_2", use_container_width=True):
        add_digit('2')
    if st.button("3", key="btn_3", use_container_width=True):
        add_digit('3')
    if st.button("+", key="btn_add", use_container_width=True):
        add_operator('+')

# Zweite Reihe von Buttons
col1, col2, col3, col4 = st.columns(4, gap="small")

with col1:
    if st.button("⌫", key="btn_delete", use_container_width=True):
        delete_last()
with col2:
    if st.button("0", key="btn_0", use_container_width=True):
        add_digit('0')
with col3:
    if st.button(".", key="btn_dot", use_container_width=True):
        add_digit('.')
with col4:
    if st.button("=", key="btn_equals", use_container_width=True):
        calculate()

st.markdown('</div>', unsafe_allow_html=True)

# Footer mit kleiner Info
st.markdown("""
<style>
.footer-info {
    text-align: center;
    color: rgba(255, 255, 255, 0.7);
    font-size: 12px;
    margin-top: 20px;
    font-family: 'Roboto', -apple-system, BlinkMacSystemFont, sans-serif;
}
</style>
<div class="footer-info">Material Design Taschenrechner • Streamlit</div>
""", unsafe_allow_html=True)
