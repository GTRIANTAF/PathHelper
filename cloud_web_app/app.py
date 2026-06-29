import streamlit as st
from pathlib import Path
import sys

# Ensure the app directory is in the Python path for Streamlit Cloud
sys.path.append(str(Path(__file__).parent))

st.set_page_config(page_title="CEID Path Advisor", layout="wide", initial_sidebar_state="collapsed")

# ==========================================
# CSS: ΤΟ "BOX-LIKE" DESIGN, ΡΙΓΕΣ & ΜΠΛΕ ΚΟΥΤΙΑ
# ==========================================
st.markdown("""
    <style>
        /* Κρύβουμε τα default μενού του Streamlit */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}

        /* 1. Το εξωτερικό φόντο (Αχνό γκρι-γαλάζιο για να ξεχωρίζει το λευκό κουτί) */
        .stApp {
            background-color: #F0F4F8;
        }

        /* 2. Το κεντρικό "Κουτί" (Λευκό κέντρο, Γαλάζιες ρίγες πάνω και δεξιά) */
        .block-container {
            background-color: #FFFFFF;
            border-top: 8px solid #3498db;    /* Γαλάζια ρίγα πάνω */
            border-right: 8px solid #3498db;  /* Γαλάζια ρίγα δεξιά */
            border-radius: 4px 15px 15px 4px; /* Ελαφριά καμπύλη πάνω δεξιά και κάτω δεξιά */
            padding-top: 2.5rem !important; 
            padding-bottom: 3rem !important;
            padding-left: 4rem !important;
            padding-right: 4rem !important;
            margin-top: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0px 8px 24px rgba(0, 0, 0, 0.08); /* Σκιά για αίσθηση βάθους */
            max-width: 1200px; /* Δεν το αφήνουμε να απλώσει σε όλη την οθόνη, κρατάει το σχήμα κουτιού */
        }

        /* 3. Μπλε απόχρωση στα κουτιά επιλογής (Selectbox & Multiselect) */
        div[data-baseweb="select"] > div {
            background-color: #F8FBFF; /* Πολύ απαλό γαλάζιο φόντο μέσα στα κουτιά */
            border: 1px solid #3498db; /* Γαλάζιο περίγραμμα */
            border-radius: 6px;
        }

        /* 4. Δυναμικά Premium Buttons (Hover effects & Micro-animations) */
        div.stButton > button {
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            border-radius: 8px;
            font-weight: 600;
            border: 1px solid #e0e6ed;
            box-shadow: 0 2px 4px rgba(0,0,0,0.04);
            background-color: #ffffff;
            color: #2c3e50;
        }

        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(52, 152, 219, 0.15);
            border-color: #3498db;
            color: #3498db;
        }

        /* Primary Buttons (Gradient & Solid) */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
            border: none;
            color: white;
            box-shadow: 0 4px 10px rgba(41, 128, 185, 0.3);
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #2980b9 0%, #1f6391 100%);
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(41, 128, 185, 0.4);
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# --- 1. INITIALIZE NAVIGATION STATE ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "checker"

# --- 2. HEADER: LOGO KAI TITLE ΕΥΘΥΓΡΑΜΜΙΣΜΕΝΑ ---
col_logo, col_title = st.columns([1, 9], vertical_alignment="center")

with col_logo:
    current_dir = Path(__file__).parent
    logo_path = current_dir / "assets" / "logo_ceid.jpg"

    if logo_path.exists():
        st.image(str(logo_path), width=110)
    else:
        st.info("CEID Logo")

with col_title:
    st.markdown("<h1 style='padding-bottom: 0px; margin-bottom: 0px;'>CEID Path Advisor</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #555555; font-size: 15px; margin-top: 0px;'>Department of Computer Engineering & Informatics</p>",
        unsafe_allow_html=True)

st.divider()

# --- 3. PAGE TITLE & ICONS ---
col_page_title, col_icon1, col_icon2, col_icon3 = st.columns([5.5, 1.5, 1.5, 1.5], vertical_alignment="center")

with col_page_title:
    if st.session_state.current_page == "chat":
        st.markdown("<h2>AI Advisor</h2>", unsafe_allow_html=True)
    elif st.session_state.current_page == "profile":
        st.markdown("<h2>Το Προφίλ Μου</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2> Path Checker</h2>", unsafe_allow_html=True)

with col_icon1:
    btn_type = "primary" if st.session_state.current_page == "chat" else "secondary"
    if st.button("Chat", help="Chat with AI", use_container_width=True, type=btn_type):
        st.session_state.current_page = "chat"
        st.rerun()

with col_icon2:
    btn_type = "primary" if st.session_state.current_page == "checker" else "secondary"
    if st.button("Checker", help="Check Path Rules", use_container_width=True, type=btn_type):
        st.session_state.current_page = "checker"
        st.rerun()

with col_icon3:
    btn_type = "primary" if st.session_state.current_page == "profile" else "secondary"
    if st.button("Profile", help="My Profile & Scenarios", use_container_width=True, type=btn_type):
        st.session_state.current_page = "profile"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PAGE ROUTER
# ==========================================
if st.session_state.current_page == "checker":
    import views.checker as checker_view
    checker_view.render()

elif st.session_state.current_page == "chat":
    import views.chat as chat_view
    chat_view.render()

elif st.session_state.current_page == "profile":
    import views.profile as profile_view
    profile_view.render()
