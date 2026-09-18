import streamlit as st
from knowledge_base import (
    CEID_COURSES, get_course_info, get_total_ects,
    get_all_available_courses, get_group_a_courses_except, get_all_group_a_courses
)
from validation_engine import validate_scenario
from profile_manager import export_scenario_to_pdf, save_scenario


# ─────────────────────────────────────────────
#  CARD PICKER HELPER
# ─────────────────────────────────────────────

def render_card_picker(slot_key: str, courses: list, max_picks: int, preselected: list = None) -> list:
    """
    Two-panel card picker.
    Left : available course cards (click to add).
    Right: selected courses (click × to remove).
    Returns the current list of selected course names.
    """
    state_key = f"sel_{slot_key}"

    # Initialise state on first render or after a scenario load
    if state_key not in st.session_state:
        if preselected:
            valid = [c for c in preselected if c in courses][:max_picks]
            st.session_state[state_key] = valid
        else:
            st.session_state[state_key] = []

    selected: list = st.session_state[state_key]

    # ── Progress bar + count ──────────────────
    filled = len(selected)
    pct    = filled / max_picks if max_picks else 0
    col_bar, col_cnt = st.columns([6, 1])
    with col_bar:
        st.progress(min(pct, 1.0))
    with col_cnt:
        color = "#27ae60" if filled == max_picks else "#e67e22"
        st.markdown(
            f"<div style='text-align:right;font-weight:700;color:{color};font-size:14px;'>"
            f"{filled}/{max_picks}</div>",
            unsafe_allow_html=True,
        )

    # ── Search & Filter ────────────────────────────
    col_s, col_f = st.columns([5, 5], vertical_alignment="bottom")
    
    with col_s:
        search = st.text_input(
            "search",
            placeholder="Αναζήτηση μαθήματος...",
            key=f"search_{slot_key}",
            label_visibility="collapsed",
        )
    with col_f:
        sem_filter = st.radio(
            "Φίλτρο Εξαμήνου",
            options=["Όλα", "Χειμερινό", "Εαρινό"],
            horizontal=True,
            key=f"filter_{slot_key}",
            label_visibility="collapsed"
        )

    filtered = courses
    if search:
        filtered = [c for c in filtered if search.lower() in c.lower()]
    if sem_filter != "Όλα":
        filtered = [c for c in filtered if get_course_info(c) and get_course_info(c)["semester"] == sem_filter]

    # ── Two-panel layout ──────────────────────
    col_left, col_sep, col_right = st.columns([5, 0.1, 3])

    with col_left:
        st.markdown("<div class='card-panel-header'>Διαθέσιμα Μαθήματα</div>", unsafe_allow_html=True)

        if not filtered:
            st.markdown("<div class='empty-panel'>Δεν βρέθηκαν μαθήματα</div>", unsafe_allow_html=True)

        # Render in a 2-column card grid
        grid = [filtered[i:i+2] for i in range(0, len(filtered), 2)]
        for row in grid:
            cols = st.columns(2)
            for ci, course in enumerate(row):
                info       = get_course_info(course)
                sem        = info["semester"] if info else ""
                ects       = info["ects"]     if info else 5
                sem_mark   = "Χ" if sem == "Χειμερινό" else "Ε"
                is_selected = course in selected
                is_full     = filled >= max_picks and not is_selected

                # CSS wrapper class
                if is_selected:
                    css_class = "card-btn card-btn-selected"
                elif sem == "Χειμερινό":
                    css_class = "card-btn card-btn-winter"
                else:
                    css_class = "card-btn card-btn-spring"

                label = f"{'✓  ' if is_selected else ''}{course} {ects} ECTS · {sem_mark}"

                with cols[ci]:
                    st.markdown(f"<div class='{css_class}'>", unsafe_allow_html=True)
                    clicked = st.button(
                        label,
                        key=f"card_{slot_key}_{course}",
                        use_container_width=True,
                        disabled=is_full,
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                if clicked:
                    if is_selected:
                        st.session_state[state_key].remove(course)
                    else:
                        st.session_state[state_key].append(course)
                    st.rerun()

    # Thin separator
    with col_sep:
        st.markdown(
            "<div style='border-left:1px solid #eee;height:100%;min-height:300px;'></div>",
            unsafe_allow_html=True,
        )

    with col_right:
        st.markdown("<div class='card-panel-header'>Επιλεγμένα</div>", unsafe_allow_html=True)

        if not selected:
            st.markdown("<div class='empty-panel'>Κλίκ σε μάθημα<br>για να το προσθέσεις</div>", unsafe_allow_html=True)
        else:
            for course in list(selected):
                info     = get_course_info(course)
                sem      = info["semester"] if info else ""
                ects     = info["ects"]     if info else 5
                sem_mark = "Χ" if sem == "Χειμερινό" else "Ε"
                sem_cls  = "winter" if sem == "Χειμερινό" else "spring"

                c_name, c_btn = st.columns([5, 1])
                with c_name:
                    st.markdown(
                        f"""<div class='selected-card {sem_cls}'>
                            <div>
                                <div class='course-name'>{course}</div>
                                <div class='course-meta'>{ects} ECTS · {sem_mark}</div>
                            </div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with c_btn:
                    st.markdown("<div class='remove-btn'>", unsafe_allow_html=True)
                    if st.button("×", key=f"rm_{slot_key}_{course}"):
                        st.session_state[state_key].remove(course)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

    return st.session_state[state_key]


# ─────────────────────────────────────────────
#  SLOT STATE INITIALISER  (called on scenario load)
# ─────────────────────────────────────────────

def _init_slots_from_scenario(loaded: dict, scenario: str):
    """Pre-populate slot session-state keys from a loaded scenario."""
    electives = loaded.get("my_electives", [])
    if not electives:
        return

    if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
        main_dir = loaded.get("main_dir")
        if main_dir and main_dir in CEID_COURSES:
            group_a = list(CEID_COURSES[main_dir].get("Group_A", {}).keys())
            group_b = list(CEID_COURSES[main_dir].get("Group_B", {}).keys())
            st.session_state["sel_s1_a"]    = [c for c in electives if c in group_a][:5]
            st.session_state["sel_s1_b"]    = [c for c in electives if c in group_b][:5]
            already = st.session_state["sel_s1_a"] + st.session_state["sel_s1_b"]
            other_a = get_group_a_courses_except(main_dir)
            st.session_state["sel_s1_oa"]   = [c for c in electives if c in other_a and c not in already][:5]
            already2 = already + st.session_state["sel_s1_oa"]
            st.session_state["sel_s1_free"] = [c for c in electives if c not in already2]

    elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
        m1 = loaded.get("main_dir_1")
        m2 = loaded.get("main_dir_2")
        if m1 and m2 and m1 in CEID_COURSES and m2 in CEID_COURSES:
            m1a = list(CEID_COURSES[m1].get("Group_A", {}).keys())
            m1b = list(CEID_COURSES[m1].get("Group_B", {}).keys())
            m2a = list(CEID_COURSES[m2].get("Group_A", {}).keys())
            m2b = list(CEID_COURSES[m2].get("Group_B", {}).keys())
            st.session_state["sel_s2_m1a"]  = [c for c in electives if c in m1a][:5]
            st.session_state["sel_s2_m1b"]  = [c for c in electives if c in m1b][:2]
            st.session_state["sel_s2_m2a"]  = [c for c in electives if c in m2a][:5]
            st.session_state["sel_s2_m2b"]  = [c for c in electives if c in m2b][:2]
            already = (st.session_state["sel_s2_m1a"] + st.session_state["sel_s2_m1b"] +
                       st.session_state["sel_s2_m2a"] + st.session_state["sel_s2_m2b"])
            st.session_state["sel_s2_free"] = [c for c in electives if c not in already]

    elif scenario == "Σενάριο 3: Γενική κατεύθυνση":
        gen_a = get_all_group_a_courses()
        st.session_state["sel_s3_a"]    = [c for c in electives if c in gen_a][:10]
        already = st.session_state["sel_s3_a"]
        st.session_state["sel_s3_free"] = [c for c in electives if c not in already]


# ─────────────────────────────────────────────
#  MAIN RENDER
# ─────────────────────────────────────────────

def render():

    st.markdown("### Σχεδιασμός & Έλεγχος Διπλώματος")
    loaded_scenario = st.session_state.get("loaded_scenario", {})

    st.info("Ακολουθήστε τα 3 βήματα για να χτίσετε το ιδανικό (και έγκυρο) πρόγραμμα σπουδών.")

    # ==========================================
    # ΒΗΜΑ 1
    # ==========================================
    st.markdown("### **Βήμα 1**: Επιλογή Μαθημάτων (Κανόνες Σεναρίου)")

    scenarios_options = [
        "Σενάριο 1: Μία κύρια κατεύθυνση",
        "Σενάριο 2: Δύο κύριες κατευθύνσεις",
        "Σενάριο 3: Γενική κατεύθυνση",
    ]
    scen_idx = (
        scenarios_options.index(loaded_scenario["scenario_type"])
        if loaded_scenario and loaded_scenario.get("scenario_type") in scenarios_options
        else 0
    )

    prev_scenario = st.session_state.get("_prev_scenario")
    scenario = st.selectbox("Επιλέξτε Σενάριο:", scenarios_options, index=scen_idx)

    # If scenario or loaded scenario changed, clear slot states so cards re-init
    load_sig = str(loaded_scenario.get("my_electives", [])) + scenario
    if st.session_state.get("_load_sig") != load_sig:
        for k in list(st.session_state.keys()):
            if k.startswith("sel_s"):
                del st.session_state[k]
        if loaded_scenario:
            _init_slots_from_scenario(loaded_scenario, scenario)
        st.session_state["_load_sig"] = load_sig

    valid_directions = [d for d in CEID_COURSES.keys() if d.startswith("Κ")]
    my_electives = []

    # ── Scenario 1 ────────────────────────────
    if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
        main_dir_val = loaded_scenario.get("main_dir", valid_directions[0]) if loaded_scenario else valid_directions[0]
        m_idx  = valid_directions.index(main_dir_val) if main_dir_val in valid_directions else 0
        main_dir = st.selectbox("Κύρια Κατεύθυνση:", valid_directions, index=m_idx)

        if main_dir:
            group_a = sorted(CEID_COURSES[main_dir].get("Group_A", {}).keys())
            group_b = sorted(CEID_COURSES[main_dir].get("Group_B", {}).keys())
            other_a = get_group_a_courses_except(main_dir)

            tab1, tab2, tab3, tab4 = st.tabs([
                f"Ομάδα Α — {main_dir.split(':')[0]}  (5)",
                f"Ομάδα Β — {main_dir.split(':')[0]}  (5)",
                "Ομάδα Α Άλλων  (5)",
                "Ελεύθερη Επιλογή",
            ])
            with tab1:
                sel_main_a = render_card_picker("s1_a", group_a, 5)
            with tab2:
                sel_main_b = render_card_picker("s1_b", group_b, 5)
            with tab3:
                avail_oa = [c for c in other_a if c not in sel_main_a + sel_main_b]
                sel_other_a = render_card_picker("s1_oa", avail_oa, 5)
            with tab4:
                already = sel_main_a + sel_main_b + sel_other_a
                avail_free = [c for c in get_all_available_courses() if c not in already]
                sel_free = render_card_picker("s1_free", avail_free, 999)

            my_electives = sel_main_a + sel_main_b + sel_other_a + sel_free

    # ── Scenario 2 ────────────────────────────
    elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
        col1, col2 = st.columns(2)
        with col1:
            m1_val = loaded_scenario.get("main_dir_1", valid_directions[0]) if loaded_scenario else valid_directions[0]
            m1_idx = valid_directions.index(m1_val) if m1_val in valid_directions else 0
            main_dir_1 = st.selectbox("1η Κύρια Κατεύθυνση:", valid_directions, index=m1_idx)
        with col2:
            dirs2 = [d for d in valid_directions if d != main_dir_1]
            m2_val = loaded_scenario.get("main_dir_2", dirs2[0]) if loaded_scenario else dirs2[0]
            m2_idx = dirs2.index(m2_val) if m2_val in dirs2 else 0
            main_dir_2 = st.selectbox("2η Κύρια Κατεύθυνση:", dirs2, index=m2_idx)

        if main_dir_1 == main_dir_2:
            st.warning("Πρέπει να επιλέξετε διαφορετικές κατευθύνσεις!")
        else:
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                f"Α — {main_dir_1.split(':')[0]}  (5)",
                f"Β — {main_dir_1.split(':')[0]}  (2)",
                f"Α — {main_dir_2.split(':')[0]}  (5)",
                f"Β — {main_dir_2.split(':')[0]}  (2)",
                "Ελεύθερη Επιλογή",
            ])
            with tab1:
                sel_m1_a = render_card_picker("s2_m1a", sorted(CEID_COURSES[main_dir_1].get("Group_A", {}).keys()), 5)
            with tab2:
                sel_m1_b = render_card_picker("s2_m1b", sorted(CEID_COURSES[main_dir_1].get("Group_B", {}).keys()), 2)
            with tab3:
                avail_m2a = [c for c in sorted(CEID_COURSES[main_dir_2].get("Group_A", {}).keys())
                             if c not in sel_m1_a + sel_m1_b]
                sel_m2_a = render_card_picker("s2_m2a", avail_m2a, 5)
            with tab4:
                avail_m2b = [c for c in sorted(CEID_COURSES[main_dir_2].get("Group_B", {}).keys())
                             if c not in sel_m1_a + sel_m1_b + sel_m2_a]
                sel_m2_b = render_card_picker("s2_m2b", avail_m2b, 2)
            with tab5:
                already_sel = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b
                avail_free2 = [c for c in sorted(get_all_available_courses()) if c not in already_sel]
                sel_free_2  = render_card_picker("s2_free", avail_free2, 999)

            my_electives = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b + sel_free_2

    # ── Scenario 3 ────────────────────────────
    elif scenario == "Σενάριο 3: Γενική κατεύθυνση":
        tab1, tab2 = st.tabs(["Ομάδα Α — Όλες οι κατευθύνσεις  (10)", "Ελεύθερη Επιλογή"])
        with tab1:
            sel_gen_a = render_card_picker("s3_a", sorted(get_all_group_a_courses()), 10)
        with tab2:
            avail_gen_free = [c for c in sorted(get_all_available_courses()) if c not in sel_gen_a]
            sel_gen_free   = render_card_picker("s3_free", avail_gen_free, 999)
        my_electives = sel_gen_a + sel_gen_free

    st.divider()

    # ==========================================
    # ΒΗΜΑ 2: ΚΑΤΑΝΟΜΗ ΣΤΑ ΕΞΑΜΗΝΑ
    # ==========================================
    st.markdown("### **Βήμα 2**: Κατανομή στα Εξάμηνα")

    my_winter = sorted([c for c in my_electives if get_course_info(c) and get_course_info(c)["semester"] == "Χειμερινό"])
    my_spring = sorted([c for c in my_electives if get_course_info(c) and get_course_info(c)["semester"] == "Εαρινό"])
    sem7, sem9 = [], []

    if my_electives:
        col_w, col_s = st.columns(2)
        with col_w:
            st.markdown(f"**Χειμερινά: {len(my_winter)}/11**")
            st.progress(min(len(my_winter) / 11, 1.0))
            if len(my_winter) < 11:
                st.warning(f"Χρειάζεσαι {11 - len(my_winter)} ακόμα Χειμερινά.")
            else:
                st.success("Ολοκληρώθηκαν τα Χειμερινά!")
        with col_s:
            st.markdown(f"**Εαρινά: {len(my_spring)}/6**")
            st.progress(min(len(my_spring) / 6, 1.0))
            if len(my_spring) < 6:
                st.warning(f"Χρειάζεσαι {6 - len(my_spring)} ακόμα Εαρινά.")
            else:
                st.success("Ολοκληρώθηκαν τα Εαρινά!")

        st.markdown("<br>", unsafe_allow_html=True)

        # 8th semester (spring — auto)
        st.markdown("**8ο Εξάμηνο (Εαρινό)**")
        if my_spring:
            spring_html = "".join([
                f"""<div class='selected-card spring'>
                    <div>
                        <div class='course-name'>{c}</div>
                        <div class='course-meta'>{get_course_info(c)['ects']} ECTS · Ε</div>
                    </div>
                </div>"""
                for c in my_spring
            ])
            st.markdown(spring_html, unsafe_allow_html=True)
        else:
            st.markdown("<div class='empty-panel'>Δεν υπάρχουν Εαρινά μαθήματα ακόμα.</div>", unsafe_allow_html=True)

        # 7th / 9th semester (winter — user picks)
        st.markdown("**7ο και 9ο Εξάμηνο (Χειμερινά)**")
        st.caption("Επέλεξε 5 μαθήματα για το 7ο εξάμηνο — τα υπόλοιπα πηγαίνουν στο 9ο.")

        loaded_sem7 = loaded_scenario.get("sem7", []) if loaded_scenario else None
        
        # Build sem7 list dynamically from session state first
        sem7 = []
        for course in my_winter:
            key = f"sem7_{course}"
            # initialize state if not present based on loaded_sem7
            if key not in st.session_state:
                st.session_state[key] = (course in loaded_sem7) if loaded_sem7 is not None else False
            if st.session_state[key]:
                sem7.append(course)

        col7, col9 = st.columns(2)
        with col7:
            st.markdown("**7ο Εξάμηνο** *(επίλεξε 5)*")
            for course in my_winter:
                info    = get_course_info(course)
                ects    = info["ects"] if info else 5
                in_sem7 = course in sem7
                is_full = len(sem7) >= 5 and not in_sem7

                c_name, c_chk = st.columns([5, 1])
                border = "#3498db"
                with c_name:
                    bg = "#eaf4fb" if in_sem7 else "#fff"
                    st.markdown(
                        f"""<div style='border-left:3px solid {border};background:{bg};
                            padding:8px 12px;border-radius:6px;margin-bottom:4px;'>
                            <div style='font-size:13px;font-weight:500;'>{course}</div>
                            <div style='font-size:11px;color:#888;'>{ects} ECTS · Χ</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
                with c_chk:
                    checked = st.checkbox("Επιλογή", key=f"sem7_{course}", disabled=is_full, label_visibility="collapsed")
                    # Automatically triggers a rerun because it modifies session_state

        with col9:
            sem9 = [c for c in my_winter if c not in sem7]
            st.markdown("**9ο Εξάμηνο** *(αυτόματο)*")
            if sem9:
                for course in sem9:
                    info = get_course_info(course)
                    ects = info["ects"] if info else 5
                    st.markdown(
                        f"""<div style='border-left:3px solid #aaa;background:#f9f9f9;
                            padding:8px 12px;border-radius:6px;margin-bottom:4px;opacity:0.75;'>
                            <div style='font-size:13px;'>{course}</div>
                            <div style='font-size:11px;color:#888;'>{ects} ECTS · Χ</div>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.markdown("<div class='empty-panel'>Τα υπόλοιπα Χειμερινά θα εμφανιστούν εδώ.</div>", unsafe_allow_html=True)
    else:
        st.warning("Επιλέξτε μαθήματα στο Βήμα 1 για να ξεκλειδώσετε τον προγραμματισμό των εξαμήνων.")

    st.divider()

    # ==========================================
    # ΒΗΜΑ 3: ΔΙΠΛΩΜΑΤΙΚΗ
    # ==========================================
    st.markdown("### **Βήμα 3**: Διπλωματική Εργασία")
    thesis_checked = st.checkbox("Έχω αναλάβει / Ολοκληρώσει Διπλωματική Εργασία (30 ECTS)", value=False)

    st.divider()

    # ==========================================
    # SUBMIT + CLEAR
    # ==========================================
    col_check, col_clear = st.columns([4, 1])
    with col_check:
        if st.button("Οριστικός Έλεγχος & Υποβολή", type="primary", use_container_width=True):
            st.session_state.check_performed = True
    with col_clear:
        if st.button("Καθαρισμός", type="secondary", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("sel_s") or k.startswith("sem7_") or k == "_load_sig":
                    del st.session_state[k]
            st.session_state.loaded_scenario = {}
            st.session_state.check_performed = False
            st.rerun()

    # ==========================================
    # FINAL REPORT
    # ==========================================
    if st.session_state.get("check_performed", False):
        st.markdown("### **Τελική Αναφορά**")

        if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
            categorized_electives = {
                f"Ομάδα Α ({main_dir.split(':')[0]})": sel_main_a,
                f"Ομάδα Β ({main_dir.split(':')[0]})": sel_main_b,
                "Ομάδα Α (Άλλων Κατευθύνσεων)": sel_other_a,
                "Ελεύθερη Επιλογή": sel_free,
            }
        elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            categorized_electives = {
                f"Ομάδα Α ({main_dir_1.split(':')[0]})": sel_m1_a,
                f"Ομάδα Β ({main_dir_1.split(':')[0]})": sel_m1_b,
                f"Ομάδα Α ({main_dir_2.split(':')[0]})": sel_m2_a,
                f"Ομάδα Β ({main_dir_2.split(':')[0]})": sel_m2_b,
                "Ελεύθερη Επιλογή": sel_free_2,
            }
        else:
            categorized_electives = {
                "Ομάδα Α (Από όλες τις κατευθύνσεις)": sel_gen_a,
                "Ελεύθερη Επιλογή": sel_gen_free,
            }

        results, is_valid = validate_scenario(
            scenario=scenario,
            categorized_electives=categorized_electives,
            my_electives=my_electives,
            my_winter=my_winter,
            my_spring=my_spring,
            sem7=sem7,
            sem9=sem9,
            thesis_checked=thesis_checked,
        )
        errors = 0 if is_valid else 1

        for res in results:
            if   res["type"] == "success": st.success(res["message"])
            elif res["type"] == "error":   st.error(res["message"])
            elif res["type"] == "warning": st.warning(res["message"])

        if is_valid:
            st.success("### Το Πρόγραμμά σου είναι τέλειο και πλήρως εναρμονισμένο με τους κανόνες του CEID!")

        pdf_path = export_scenario_to_pdf(
            scenario_name="Current_Scenario",
            scenario_type=scenario,
            categorized_electives=categorized_electives,
            my_winter=my_winter,
            my_spring=my_spring,
            sem7=sem7,
            sem9=sem9,
            valid=(errors == 0),
        )
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Εξαγωγή σε PDF",
                data=pdf_file,
                file_name="ceid_scenario.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with st.form("save_scenario_form"):
            st.markdown("#### Αποθήκευση στο Προφίλ")
            am = st.session_state.get("logged_in_am")
            if not am:
                st.warning("Συνδέσου από την καρτέλα **Profile** για να αποθηκεύσεις σενάρια στον λογαριασμό σου.")
            scen_name = st.text_input("Όνομα Σεναρίου (π.χ. 'Το τέλειο πλάνο')")
            if st.form_submit_button("Αποθήκευση Σεναρίου") and scen_name:
                save_scenario(scen_name, {
                    "scenario_type": scenario,
                    "main_dir":   locals().get("main_dir"),
                    "main_dir_1": locals().get("main_dir_1"),
                    "main_dir_2": locals().get("main_dir_2"),
                    "my_electives": my_electives,
                    "my_winter": my_winter,
                    "my_spring": my_spring,
                    "sem7": sem7,
                    "sem9": sem9,
                    "valid": (errors == 0),
                }, am=am)
                if am:
                    st.success(f"Το σενάριο '{scen_name}' αποθηκεύτηκε στον λογαριασμό ΑΜ {am}!")
                else:
                    st.success(f"Το σενάριο '{scen_name}' αποθηκεύτηκε (ανώνυμα).")

