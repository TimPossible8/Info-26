import streamlit as st
import numpy as np
import sympy as sp
import plotly.graph_objects as go
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Material 3 Graphing Calculator",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# Enhanced Material 3 CSS & Keyframe Animations
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Keyframe Animations */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes pulseValue {
        0% { transform: scale(0.98); opacity: 0.8; }
        50% { transform: scale(1.02); }
        100% { transform: scale(1); opacity: 1; }
    }

    @keyframes glowPrimary {
        0% { box-shadow: 0 0 0 0 rgba(103, 80, 164, 0.4); }
        70% { box-shadow: 0 0 0 8px rgba(103, 80, 164, 0); }
        100% { box-shadow: 0 0 0 0 rgba(103, 80, 164, 0); }
    }

    /* Global Base */
    html, body, [data-testid="stAppViewContainer"] {
        background-color: #FEF7FF !important;
        color: #1D1B20;
        font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        scroll-behavior: smooth;
    }

    .block-container {
        padding: 1.2rem 1.5rem !important;
        max-width: 100% !important;
        animation: fadeInUp 0.4s cubic-bezier(0.2, 0.0, 0, 1.0);
    }

    #MainMenu, header, footer, [data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Animated Surface Cards */
    .m3-card {
        background-color: #F4EFF4;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0px 1px 3px rgba(0,0,0,0.08), 0px 1px 2px rgba(0,0,0,0.04);
        border: 1px solid #E7E0EC;
        margin-bottom: 16px;
        transition: box-shadow 0.3s ease, transform 0.2s ease;
    }

    .m3-card:hover {
        box-shadow: 0px 4px 12px rgba(0,0,0,0.12);
    }

    /* M3 Calculator Display with Smooth State Transitions */
    .m3-display-container {
        background: linear-gradient(135deg, #EADDFF 0%, #E8DEF8 100%);
        border-radius: 24px;
        padding: 20px 24px;
        text-align: right;
        min-height: 110px;
        box-shadow: inset 0px 2px 4px rgba(0,0,0,0.06), 0px 2px 6px rgba(0,0,0,0.04);
        margin-bottom: 16px;
        border: 1px solid #D0BCFF;
        display: flex;
        flex-direction: column;
        justify-content: center;
        transition: all 0.3s cubic-bezier(0.2, 0, 0, 1);
    }

    .m3-display-expr {
        font-size: 0.95rem;
        color: #49454F;
        font-weight: 500;
        min-height: 22px;
        word-break: break-all;
        font-family: 'Roboto Mono', monospace;
        opacity: 0.9;
    }

    .m3-display-val {
        font-size: 2.2rem;
        font-weight: 700;
        color: #21005D;
        word-break: break-all;
        line-height: 1.2;
        animation: pulseValue 0.25s cubic-bezier(0.2, 0, 0, 1);
    }

    /* Fluid Dynamic Buttons */
    div.stButton > button {
        width: 100% !important;
        border-radius: 28px !important;
        height: 52px !important;
        font-size: 1.15rem !important;
        font-weight: 600 !important;
        border: 1px solid #CAC4D0 !important;
        background-color: #F3EDF7 !important;
        color: #1D192B !important;
        transition: all 0.2s cubic-bezier(0.2, 0, 0, 1) !important;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.05) !important;
        will-change: transform, background-color, box-shadow;
    }

    div.stButton > button:hover {
        background-color: #E8DEF8 !important;
        border-color: #79747E !important;
        color: #1D192B !important;
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0px 4px 8px rgba(0,0,0,0.12) !important;
    }

    div.stButton > button:active {
        transform: translateY(1px) scale(0.96) !important;
        box-shadow: 0px 1px 2px rgba(0,0,0,0.06) !important;
    }

    /* Primary Accent Buttons */
    div.stButton > button[kind="primary"] {
        background-color: #6750A4 !important;
        color: #FFFFFF !important;
        border: none !important;
        animation: glowPrimary 2s infinite;
    }

    div.stButton > button[kind="primary"]:hover {
        background-color: #523B8B !important;
        color: #FFFFFF !important;
        box-shadow: 0px 4px 12px rgba(103, 80, 164, 0.4) !important;
    }

    /* Input Fields & Control Styling */
    div[data-baseweb="input"] {
        border-radius: 14px !important;
        background-color: #ECE6F0 !important;
        border: 1px solid transparent !important;
        transition: all 0.2s ease !important;
    }

    div[data-baseweb="input"]:focus-within {
        border-color: #6750A4 !important;
        box-shadow: 0 0 0 2px rgba(103, 80, 164, 0.2) !important;
    }

    /* Modern Expander */
    .stExpander {
        background-color: #F4EFF4 !important;
        border-radius: 18px !important;
        border: 1px solid #E7E0EC !important;
        transition: border-color 0.2s ease !important;
    }

    .stExpander:hover {
        border-color: #D0BCFF !important;
    }

    /* Responsive Queries for Mobile Devices */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.8rem 0.6rem !important;
        }
        .m3-display-val {
            font-size: 1.8rem !important;
        }
        div.stButton > button {
            height: 46px !important;
            font-size: 1rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Session State Setup
# ---------------------------------------------------------
for key, val in {
    "calc_input": "",
    "calc_result": "0",
    "history": [],
    "plot_expr": "sin(x) + 0.5*x",
    "xmin": -10.0,
    "xmax": 10.0,
    "ymin": -5.0,
    "ymax": 5.0
}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ---------------------------------------------------------
# Safe Parsing Logic
# ---------------------------------------------------------
def safe_evaluate(expr_str):
    if not expr_str.strip():
        return "0"
    try:
        clean_expr = expr_str.replace("×", "*").replace("÷", "/").replace("^", "**")
        transformations = standard_transformations + (implicit_multiplication_application,)
        x = sp.Symbol('x')
        parsed = parse_expr(clean_expr, transformations=transformations, local_dict={'x': x, 'e': sp.E, 'pi': sp.pi})
        
        if parsed.has(x):
            return str(sp.simplify(parsed))
        
        val = float(parsed.evalf())
        return str(int(val)) if val.is_integer() else f"{val:.8g}"
    except Exception:
        return "Error"

def append_to_input(token):
    st.session_state.calc_input += token

def clear_input():
    st.session_state.calc_input = ""
    st.session_state.calc_result = "0"

def delete_last():
    st.session_state.calc_input = st.session_state.calc_input[:-1]

def evaluate_current():
    res = safe_evaluate(st.session_state.calc_input)
    st.session_state.calc_result = res
    if res != "Error" and st.session_state.calc_input:
        st.session_state.history.insert(0, f"{st.session_state.calc_input} = {res}")
        st.session_state.history = st.session_state.history[:15]

# ---------------------------------------------------------
# Responsive Layout
# ---------------------------------------------------------
col_left, col_right = st.columns([5, 7], gap="large")

# =========================================================
# CALCULATOR PANEL
# =========================================================
with col_left:
    st.markdown("### 🧮 Material 3 Calculator")
    
    expr_display = st.session_state.calc_input if st.session_state.calc_input else "0"
    res_display = st.session_state.calc_result
    
    st.markdown(f"""
    <div class="m3-display-container">
        <div class="m3-display-expr">{expr_display}</div>
        <div class="m3-display-val">{res_display}</div>
    </div>
    """, unsafe_allow_html=True)
    
    keypad = [
        [("C", clear_input), ("DEL", delete_last), ("(", lambda: append_to_input("(")), (")", lambda: append_to_input(")")), ("^", lambda: append_to_input("^"))],
        [("sin", lambda: append_to_input("sin(")), ("cos", lambda: append_to_input("cos(")), ("tan", lambda: append_to_input("tan(")), ("sqrt", lambda: append_to_input("sqrt(")), ("÷", lambda: append_to_input("÷"))],
        [("7", lambda: append_to_input("7")), ("8", lambda: append_to_input("8")), ("9", lambda: append_to_input("9")), ("×", lambda: append_to_input("×")), ("log", lambda: append_to_input("log("))],
        [("4", lambda: append_to_input("4")), ("5", lambda: append_to_input("5")), ("6", lambda: append_to_input("6")), ("-", lambda: append_to_input("-")), ("exp", lambda: append_to_input("exp("))],
        [("1", lambda: append_to_input("1")), ("2", lambda: append_to_input("2")), ("3", lambda: append_to_input("3")), ("+", lambda: append_to_input("+")), ("x", lambda: append_to_input("x"))],
        [("0", lambda: append_to_input("0")), (".", lambda: append_to_input(".")), ("π", lambda: append_to_input("pi")), ("e", lambda: append_to_input("e")), ("=", evaluate_current)]
    ]
    
    for row in keypad:
        cols = st.columns(5)
        for i, (label, action) in enumerate(row):
            btn_type = "primary" if label == "=" else "secondary"
            if cols[i].button(label, key=f"btn_{label}_{i}", type=btn_type):
                action()
                st.rerun()

    if st.button("📈 Send Expression to Plotter", type="secondary", use_container_width=True):
        if st.session_state.calc_input:
            st.session_state.plot_expr = st.session_state.calc_input
            st.rerun()

    with st.expander("🕒 Calculation History", expanded=False):
        if st.session_state.history:
            for item in st.session_state.history:
                st.markdown(f"`{item}`")
            if st.button("Clear History", key="clear_hist"):
                st.session_state.history = []
                st.rerun()
        else:
            st.caption("No calculations recorded yet.")

# =========================================================
# GRAPHICAL PLOTTER PANEL
# =========================================================
with col_right:
    st.markdown("### 📊 Interactive Function Plotter")
    
    c_f1, c_f2 = st.columns([3, 1])
    with c_f1:
        func_input = st.text_input("Function f(x)", value=st.session_state.plot_expr, key="plot_expr_input")
    with c_f2:
        st.write("")
        st.write("")
        plot_trigger = st.button("Plot Function", type="primary")

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        xmin = st.number_input("X Min", value=st.session_state.xmin, step=1.0)
    with r2:
        xmax = st.number_input("X Max", value=st.session_state.xmax, step=1.0)
    with r3:
        ymin = st.number_input("Y Min", value=st.session_state.ymin, step=1.0)
    with r4:
        ymax = st.number_input("Y Max", value=st.session_state.ymax, step=1.0)

    fig = go.Figure()

    if func_input:
        try:
            x_sym = sp.Symbol('x')
            clean_f = func_input.replace("×", "*").replace("÷", "/").replace("^", "**")
            transformations = standard_transformations + (implicit_multiplication_application,)
            parsed_expr = parse_expr(clean_f, transformations=transformations, local_dict={'x': x_sym, 'e': sp.E, 'pi': sp.pi})
            
            f_np = sp.lambdify(x_sym, parsed_expr, modules=['numpy', 'math'])
            x_vals = np.linspace(xmin, xmax, 1000)
            y_vals = f_np(x_vals)

            if isinstance(y_vals, (int, float)):
                y_vals = np.full_like(x_vals, y_vals)

            fig.add_trace(go.Scatter(
                x=x_vals,
                y=y_vals,
                mode='lines',
                name=f'f(x) = {func_input}',
                line=dict(color='#6750A4', width=3.5, shape='spline'),
                hovertemplate='<b>x</b>: %{x:.3f}<br><b>f(x)</b>: %{y:.3f}<extra></extra>'
            ))

            try:
                derivative = sp.diff(parsed_expr, x_sym)
                f_prime = sp.lambdify(x_sym, derivative, modules=['numpy', 'math'])
                y_prime = f_prime(x_vals)
                if not isinstance(y_prime, (int, float)):
                    sign_changes = np.where(np.diff(np.sign(y_prime)))[0]
                    if 0 < len(sign_changes) < 20:
                        fig.add_trace(go.Scatter(
                            x=x_vals[sign_changes],
                            y=y_vals[sign_changes],
                            mode='markers',
                            name='Local Extrema',
                            marker=dict(color='#B3261E', size=10, symbol='diamond-open-dot', line=dict(width=2)),
                            hovertemplate='<b>Extremum</b><br>x: %{x:.3f}<br>y: %{y:.3f}<extra></extra>'
                        ))
            except Exception:
                pass

        except Exception as err:
            st.error(f"Error plotting function: {err}")

    fig.add_hline(y=0, line_width=1.5, line_color="#79747E", line_dash="dash")
    fig.add_vline(x=0, line_width=1.5, line_color="#79747E", line_dash="dash")

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='#F4EFF4',
        margin=dict(l=20, r=20, t=30, b=20),
        height=480,
        autosize=True,
        transition=dict(duration=300, easing="cubic-in-out"),
        xaxis=dict(
            range=[xmin, xmax],
            gridcolor='#E7E0EC',
            zeroline=False,
            title=dict(text="x", font=dict(color="#49454F", size=14)),
            tickfont=dict(color="#49454F")
        ),
        yaxis=dict(
            range=[ymin, ymax],
            gridcolor='#E7E0EC',
            zeroline=False,
            title=dict(text="f(x)", font=dict(color="#49454F", size=14)),
            tickfont=dict(color="#49454F")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#1D192B")
        ),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': True, 'responsive': True})