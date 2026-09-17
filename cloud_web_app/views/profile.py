import streamlit as st
from auth import send_code, verify_code, is_valid_am
from profile_manager import load_scenarios, delete_scenario


# ─────────────────────────────────────────────
#  LOGIN FORM
# ─────────────────────────────────────────────

def _render_login():
    st.markdown("### Σύνδεση με Webmail")
    st.info(
        "Εισάγετε τον Αριθμό Μητρώου σας (ΑΜ). Θα σας σταλεί ένας κωδικός "
        "επαλήθευσης στο webmail **upXXXXXX@upnet.gr** για να συνδεθείτε."
    )

    # ── Step 1 : enter AM ────────────────────
    with st.form("am_form"):
        am_input = st.text_input("Αριθμός Μητρώου (ΑΜ):", placeholder="π.χ. 1088888", max_chars=8)
        send_btn = st.form_submit_button("Αποστολή Κωδικού", type="primary", use_container_width=True)

    if send_btn:
        if not is_valid_am(am_input):
            st.error("Το ΑΜ πρέπει να είναι 6–8 ψηφία.")
        else:
            code = send_code(am_input)
            st.session_state["_pending_am"]   = am_input
            st.session_state["_pending_code"] = code   # only set in MOCK mode
            st.rerun()

    # ── Step 2 : enter code (after AM sent) ──
    if "_pending_am" in st.session_state:
        pending_am = st.session_state["_pending_am"]
        st.success(f"Κωδικός στάλθηκε για ΑΜ: **{pending_am}**")

        # MOCK: show the code in a highlighted box
        mock_code = st.session_state.get("_pending_code")
        if mock_code:
            st.warning(
                f"**[MOCK MODE]** Ο κωδικός σου είναι: `{mock_code}`\n\n"
                "_Αφού συνδεθείς με SMTP email, αυτό το μήνυμα θα αφαιρεθεί._"
            )

        with st.form("code_form"):
            code_input = st.text_input("Εισάγετε τον κωδικό επαλήθευσης:", max_chars=6, placeholder="6-ψήφιος κωδικός")
            verify_btn = st.form_submit_button("Επαλήθευση", type="primary", use_container_width=True)

        if verify_btn:
            ok, msg = verify_code(pending_am, code_input)
            if ok:
                st.session_state["logged_in_am"] = pending_am
                del st.session_state["_pending_am"]
                st.session_state.pop("_pending_code", None)
                st.rerun()
            else:
                st.error(msg)

        if st.button("Χρησιμοποίησε άλλο ΑΜ"):
            st.session_state.pop("_pending_am",   None)
            st.session_state.pop("_pending_code", None)
            st.rerun()


# ─────────────────────────────────────────────
#  SCENARIO LIST
# ─────────────────────────────────────────────

def _render_scenarios(am: str):
    st.markdown(f"### Τα Σενάριά μου  ·  ΑΜ {am}")
    saved = load_scenarios(am)

    col_logout, _ = st.columns([2, 5])
    with col_logout:
        if st.button("Αποσύνδεση", type="secondary", use_container_width=True):
            st.session_state.pop("logged_in_am", None)
            st.rerun()

    st.divider()

    if not saved:
        st.info("Δεν υπάρχουν αποθηκευμένα σενάρια ακόμα. Πήγαινε στον **Path Checker** για να δημιουργήσεις ένα!")
        return

    for name, data in saved.items():
        with st.container():
            col_info, col_actions = st.columns([4, 1])
            with col_info:
                valid_badge = (
                    "<span style='color:#27ae60;font-weight:700;'>Έγκυρο</span>"
                    if data.get("valid")
                    else "<span style='color:#e74c3c;font-weight:700;'>Μη Έγκυρο</span>"
                )
                st.markdown(
                    f"<div style='border-left:4px solid #3498db;padding:10px 16px;"
                    f"background:#f8fbff;border-radius:6px;'>"
                    f"<div style='font-size:16px;font-weight:700;'>{name}</div>"
                    f"<div style='font-size:13px;color:#555;margin-top:4px;'>"
                    f"{data.get('scenario_type', '—')} &nbsp;·&nbsp; "
                    f"{len(data.get('my_electives', []))} μαθήματα &nbsp;·&nbsp; {valid_badge}"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            with col_actions:
                if st.button("Φόρτωση", key=f"load_{am}_{name}", use_container_width=True, type="primary"):
                    st.session_state.loaded_scenario = data
                    st.session_state.check_performed = False
                    # Clear card picker slot states so they re-init from loaded scenario
                    for k in list(st.session_state.keys()):
                        if k.startswith("sel_s") or k == "_load_sig":
                            del st.session_state[k]
                    st.session_state.current_page = "checker"
                    st.rerun()
                if st.button("Διαγραφή", key=f"del_{am}_{name}", use_container_width=True):
                    delete_scenario(name, am)
                    st.rerun()
            st.divider()


# ─────────────────────────────────────────────
#  MAIN ENTRY POINT
# ─────────────────────────────────────────────

def render():
    am = st.session_state.get("logged_in_am")
    if am:
        _render_scenarios(am)
    else:
        _render_login()
