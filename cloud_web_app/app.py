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

        /* 3. Μπλε απόχρωση στα κουτιά επιλογής */
        div[data-baseweb="select"] > div {
            background-color: #F8FBFF;
            border: 1px solid #3498db;
            border-radius: 6px;
        }

        /* 4. Premium Buttons */
        div.stButton > button {
            transition: all 0.2s ease;
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

        /* 5. Course Card Picker Styles */
        .card-panel-header {
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #888;
            margin-bottom: 8px;
            padding-bottom: 6px;
            border-bottom: 2px solid #f0f0f0;
        }
        .selected-card {
            border-radius: 8px;
            padding: 10px 14px;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            background: #f8fbff;
        }
        .selected-card.winter { border-left: 4px solid #3498db; }
        .selected-card.spring { border-left: 4px solid #e67e22; }
        .selected-card .course-name {
            font-size: 13px;
            font-weight: 600;
            color: #2c3e50;
        }
        .selected-card .course-meta {
            font-size: 11px;
            color: #888;
            margin-top: 2px;
        }
        .empty-panel {
            text-align: center;
            padding: 32px 16px;
            color: #bbb;
            font-style: italic;
            font-size: 13px;
            border: 2px dashed #e8e8e8;
            border-radius: 10px;
        }

        /* Card button styles — available courses grid */
        .card-btn > div.stButton > button {
            text-align: left !important;
            height: auto !important;
            white-space: normal !important;
            padding: 10px 12px !important;
            line-height: 1.4 !important;
            font-weight: 500 !important;
            font-size: 13px !important;
        }
        .card-btn-winter > div.stButton > button {
            border-left: 3px solid #3498db !important;
        }
        .card-btn-spring > div.stButton > button {
            border-left: 3px solid #e67e22 !important;
        }
        .card-btn-selected > div.stButton > button {
            background-color: #eaf4fb !important;
            border-left: 3px solid #3498db !important;
            color: #2980b9 !important;
        }
        .remove-btn > div.stButton > button {
            border: none !important;
            color: #ccc !important;
            font-size: 16px !important;
            padding: 4px 8px !important;
            box-shadow: none !important;
            background: transparent !important;
            font-weight: 400 !important;
        }
        .remove-btn > div.stButton > button:hover {
            color: #e74c3c !important;
            background: transparent !important;
            transform: none !important;
            box-shadow: none !important;
        }
        .slot-tabs button[data-baseweb="tab"] {
            font-size: 13px;
        }
        .picker-search input {
            border-radius: 20px !important;
            font-size: 13px !important;
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
    am = st.session_state.get("logged_in_am")
    title_suffix = (
        f"<span style='font-size:13px;font-weight:500;color:#27ae60;"
        f"background:#eafaf1;padding:3px 10px;border-radius:12px;"
        f"margin-left:12px;vertical-align:middle;'>ΑΜ {am}</span>"
        if am else ""
    )
    st.markdown(
        f"<h1 style='padding-bottom:0;margin-bottom:0;'>CEID Path Advisor {title_suffix}</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#555555;font-size:15px;margin-top:0;'>"
        "Department of Computer Engineering &amp; Informatics</p>",
        unsafe_allow_html=True,
    )

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
