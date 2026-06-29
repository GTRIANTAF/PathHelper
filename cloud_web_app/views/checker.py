import streamlit as st
from knowledge_base import CEID_COURSES, get_course_info, get_total_ects, get_all_available_courses, get_group_a_courses_except, get_all_group_a_courses
from validation_engine import validate_scenario
from profile_manager import export_scenario_to_pdf, save_scenario

def render():

    from knowledge_base import CEID_COURSES, get_course_info, get_total_ects


    def format_course_with_sem(course_name):
        info = get_course_info(course_name)
        if info:
            return f"{course_name}  [{info['ects']} ECTS | {info['semester']}]"
        return course_name


    st.markdown("### Σχεδιασμός & Έλεγχος Διπλώματος")
    loaded_scenario = st.session_state.get("loaded_scenario", {})
    loaded_electives = loaded_scenario.get("my_electives", []) if loaded_scenario else None
    loaded_sem7 = loaded_scenario.get("sem7", []) if loaded_scenario else None
    loaded_sem9 = loaded_scenario.get("sem9", []) if loaded_scenario else None

    st.info("Ακολουθήστε τα 3 βήματα για να χτίσετε το ιδανικό (και έγκυρο) πρόγραμμα σπουδών.")

    # ==========================================
    # ΒΗΜΑ 1: ΔΥΝΑΜΙΚΗ ΕΠΙΛΟΓΗ ΒΑΣΕΙ ΚΑΝΟΝΩΝ
    # ==========================================
    st.markdown("### **Βήμα 1**: Επιλογή Μαθημάτων (Κανόνες Σεναρίου)")

    scenarios_options = [
        "Σενάριο 1: Μία κύρια κατεύθυνση",
        "Σενάριο 2: Δύο κύριες κατευθύνσεις",
        "Σενάριο 3: Γενική κατεύθυνση"
    ]
    scen_idx = scenarios_options.index(loaded_scenario["scenario_type"]) if loaded_scenario and loaded_scenario["scenario_type"] in scenarios_options else 0
    scenario = st.selectbox("Επιλέξτε Σενάριο:", scenarios_options, index=scen_idx)


    # Κρύβουμε τα μαθήματα Γενικής Παιδείας από τις επιλογές Κύριας Κατεύθυνσης
    valid_directions = [d for d in CEID_COURSES.keys() if d.startswith("Κ")]
    my_electives = []

    match scenario:
        case "Σενάριο 1: Μία κύρια κατεύθυνση":
            main_dir_val = loaded_scenario.get("main_dir", valid_directions[0]) if loaded_scenario else valid_directions[0]
            m_idx = valid_directions.index(main_dir_val) if main_dir_val in valid_directions else 0
            main_dir = st.selectbox("Επίλεξε Κύρια Κατεύθυνση", valid_directions, index=m_idx)

            if main_dir:
                main_group_a = list(CEID_COURSES[main_dir].get("Group_A", {}).keys())
                main_group_b = list(CEID_COURSES[main_dir].get("Group_B", {}).keys())

                other_group_a = get_group_a_courses_except(main_dir)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Από {main_dir.split(':')[0]} (Σύνολο: 10)**")
                    def_a = [c for c in sorted(main_group_a) if c in loaded_electives][:5] if loaded_electives is not None else None
                    sel_main_a = st.multiselect("Ομάδα Α - Απαιτούνται 5:", sorted(main_group_a), max_selections=5, default=def_a,
                                                format_func=format_course_with_sem)
                    def_b = [c for c in sorted(main_group_b) if c in loaded_electives][:5] if loaded_electives is not None else None
                    sel_main_b = st.multiselect("Ομάδα Β - Απαιτούνται 5:", sorted(main_group_b), max_selections=5, default=def_b,
                                                format_func=format_course_with_sem)

                with col2:
                    st.markdown("**Από Άλλες Κατευθύνσεις (Σύνολο: 7+)**")
                    already_selected_main = sel_main_a + sel_main_b

                    avail_other_a = [c for c in sorted(list(other_group_a)) if c not in already_selected_main]
                    def_other_a = [c for c in avail_other_a if c in loaded_electives][:5] if loaded_electives is not None else None
                    sel_other_a = st.multiselect("Ομάδα Α (από 3 άλλες) - Απαιτούνται 5:", avail_other_a,
                                                 max_selections=5, default=def_other_a, format_func=format_course_with_sem)

                    avail_free = get_all_available_courses()

                    already_selected_all = sel_main_a + sel_main_b + sel_other_a
                    available_free = [c for c in sorted(list(avail_free)) if c not in already_selected_all]

                    def_free = [c for c in available_free if c in loaded_electives] if loaded_electives is not None else None
                    sel_free = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):",
                                              available_free, default=def_free, format_func=format_course_with_sem)

                my_electives = sel_main_a + sel_main_b + sel_other_a + sel_free

        case "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            col1, col2 = st.columns(2)
            with col1:
                main_dir_1_val = loaded_scenario.get("main_dir_1", valid_directions[0]) if loaded_scenario else valid_directions[0]
                m1_idx = valid_directions.index(main_dir_1_val) if main_dir_1_val in valid_directions else 0
                main_dir_1 = st.selectbox("Επίλεξε 1η Κύρια Κατεύθυνση", valid_directions, index=m1_idx)
            with col2:
                valid_dirs_for_second = [d for d in valid_directions if d != main_dir_1]
                main_dir_2_val = loaded_scenario.get("main_dir_2", valid_dirs_for_second[0]) if loaded_scenario else valid_dirs_for_second[0]
                m2_idx = valid_dirs_for_second.index(main_dir_2_val) if main_dir_2_val in valid_dirs_for_second else 0
                main_dir_2 = st.selectbox("Επίλεξε 2η Κύρια Κατεύθυνση", valid_dirs_for_second, index=m2_idx)

            if main_dir_1 == main_dir_2:
                st.warning("Πρέπει να επιλέξετε διαφορετικές κατευθύνσεις!")
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    m1_a_opts = sorted(list(CEID_COURSES[main_dir_1].get("Group_A", {}).keys()))
                    def_m1_a = [c for c in m1_a_opts if c in loaded_electives][:5] if loaded_electives is not None else None
                    sel_m1_a = st.multiselect(f"Ομάδα Α ({main_dir_1.split(':')[0]}) - Απαιτούνται 5:",
                                              m1_a_opts,
                                              max_selections=5, default=def_m1_a, format_func=format_course_with_sem)
                    m1_b_opts = sorted(list(CEID_COURSES[main_dir_1].get("Group_B", {}).keys()))
                    def_m1_b = [c for c in m1_b_opts if c in loaded_electives][:2] if loaded_electives is not None else None
                    sel_m1_b = st.multiselect(f"Ομάδα Β ({main_dir_1.split(':')[0]}) - Απαιτούνται 2:",
                                              m1_b_opts,
                                              max_selections=2, default=def_m1_b, format_func=format_course_with_sem)
                with col_m2:
                    already_selected_m1 = sel_m1_a + sel_m1_b
                    avail_m2_a = [c for c in sorted(list(CEID_COURSES[main_dir_2].get("Group_A", {}).keys())) if
                                  c not in already_selected_m1]
                    def_m2_a = [c for c in avail_m2_a if c in loaded_electives][:5] if loaded_electives is not None else None
                    sel_m2_a = st.multiselect(f"Ομάδα Α ({main_dir_2.split(':')[0]}) - Απαιτούνται 5:", avail_m2_a,
                                              max_selections=5, default=def_m2_a, format_func=format_course_with_sem)

                    already_selected_m1_m2_a = already_selected_m1 + sel_m2_a
                    avail_m2_b = [c for c in sorted(list(CEID_COURSES[main_dir_2].get("Group_B", {}).keys())) if
                                  c not in already_selected_m1_m2_a]
                    def_m2_b = [c for c in avail_m2_b if c in loaded_electives][:2] if loaded_electives is not None else None
                    sel_m2_b = st.multiselect(f"Ομάδα Β ({main_dir_2.split(':')[0]}) - Απαιτούνται 2:", avail_m2_b,
                                              max_selections=2, default=def_m2_b, format_func=format_course_with_sem)

                st.markdown("**Ελεύθερη Επιλογή (Σύνολο: 3+)**")
                # all courses not in main_dir_1 or main_dir_2
                all_others = set(get_all_available_courses())
                for d in [main_dir_1, main_dir_2]:
                    for g_dict in CEID_COURSES[d].values():
                        for c in g_dict.keys():
                            if c in all_others:
                                all_others.remove(c)

                already_selected_m1_m2 = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b
                avail_free_2 = [c for c in sorted(list(all_others)) if c not in already_selected_m1_m2]

                def_free_2 = [c for c in avail_free_2 if c in loaded_electives] if loaded_electives is not None else None
                sel_free_2 = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):", avail_free_2,
                                            default=def_free_2, format_func=format_course_with_sem)

                my_electives = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b + sel_free_2

        case "Σενάριο 3: Γενική κατεύθυνση":
            all_group_a = get_all_group_a_courses()
            all_courses_set = get_all_available_courses()

            gen_a_opts = sorted(list(all_group_a))
            def_gen_a = [c for c in gen_a_opts if c in loaded_electives][:10] if loaded_electives is not None else None
            sel_gen_a = st.multiselect("Ομάδα Α από όλες - Απαιτούνται 10:", gen_a_opts,
                                       max_selections=10, default=def_gen_a, format_func=format_course_with_sem)
            available_free_gen = [c for c in sorted(list(all_courses_set)) if c not in sel_gen_a]

            def_gen_free = [c for c in available_free_gen if c in loaded_electives] if loaded_electives is not None else None
            sel_gen_free = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):",
                                          available_free_gen, default=def_gen_free, format_func=format_course_with_sem)

            my_electives = sel_gen_a + sel_gen_free

    st.divider()

    # ==========================================
    # ΒΗΜΑ 2: ΧΡΟΝΟΛΟΓΙΚΟΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ
    # ==========================================
    st.markdown("### **Βήμα 2**: Κατανομή στα Εξάμηνα")

    my_winter = sorted([c for c in my_electives if get_course_info(c)["semester"] == "Χειμερινό"])
    my_spring = sorted([c for c in my_electives if get_course_info(c)["semester"] == "Εαρινό"])

    sem7 = []
    sem9 = []

    if len(my_electives) > 0:
        col_w, col_s = st.columns(2)
    
        winter_needed = max(0, 11 - len(my_winter))
        winter_progress = min(1.0, len(my_winter) / 11.0)
        with col_w:
            st.markdown(f"**Χειμερινά Μαθήματα: {len(my_winter)}/11**")
            st.progress(winter_progress)
            if winter_needed > 0:
                st.warning(f"Χρειάζεσαι {winter_needed} ακόμα Χειμερινά.")
            else:
                st.success("Ολοκληρώθηκαν τα Χειμερινά!")
            
        spring_needed = max(0, 6 - len(my_spring))
        spring_progress = min(1.0, len(my_spring) / 6.0)
        with col_s:
            st.markdown(f"**Εαρινά Μαθήματα: {len(my_spring)}/6**")
            st.progress(spring_progress)
            if spring_needed > 0:
                st.warning(f"Χρειάζεσαι {spring_needed} ακόμα Εαρινά.")
            else:
                st.success("Ολοκληρώθηκαν τα Εαρινά!")
    
        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown("**8ο Εξάμηνο (Εαρινό)**")
        st.multiselect("Τα Εαρινά μαθήματα τοποθετούνται αυτόματα εδώ:", my_spring, default=my_spring, disabled=True,
                       format_func=format_course_with_sem)

        st.markdown("**7ο και 9ο Εξάμηνο (Χειμερινά)**")
        col7, col9 = st.columns(2)

        with col7:
            def_sem7 = [c for c in my_winter if c in loaded_sem7][:5] if loaded_sem7 is not None else None
            sem7 = st.multiselect("7ο Εξάμηνο (Επιλέξτε 5):", my_winter, max_selections=5, default=def_sem7,
                                  format_func=format_course_with_sem)

        with col9:
            leftovers_for_9 = [c for c in my_winter if c not in sem7]
            sem9 = st.multiselect("9ο Εξάμηνο (Τα υπόλοιπα):", leftovers_for_9, default=leftovers_for_9, disabled=True,
                                  format_func=format_course_with_sem)
    else:
        st.warning("Επιλέξτε μαθήματα στο Βήμα 1 για να ξεκλειδώσετε τον προγραμματισμό των εξαμήνων.")

    st.divider()

    # ==========================================
    # ΒΗΜΑ 3: ΔΙΠΛΩΜΑΤΙΚΗ ΕΡΓΑΣΙΑ
    # ==========================================
    st.markdown("### **Βήμα 3**: Διπλωματική Εργασία")
    thesis_checked = st.checkbox("Έχω αναλάβει / Ολοκληρώσει Διπλωματική Εργασία (30 ECTS)", value=False)

    st.divider()

    # ==========================================
    # UI: ΤΟ ΚΟΥΜΠΙ ΕΛΕΓΧΟΥ & Ο ΑΛΓΟΡΙΘΜΟΣ
    # ==========================================
    col_check, col_clear = st.columns([4, 1])
    with col_check:
        if st.button("Οριστικός Έλεγχος & Υποβολή", type="primary", use_container_width=True):
            st.session_state.check_performed = True
    with col_clear:
        if st.button("Καθαρισμός", type="secondary", use_container_width=True):
            st.session_state.loaded_scenario = {}
            st.session_state.check_performed = False
            st.rerun()

    if st.session_state.get("check_performed", False):
        st.markdown("### **Τελική Αναφορά**")

        if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
            categorized_electives = {
                f"Ομάδα Α ({main_dir.split(':')[0]})": sel_main_a,
                f"Ομάδα Β ({main_dir.split(':')[0]})": sel_main_b,
                "Ομάδα Α (Άλλων Κατευθύνσεων)": sel_other_a,
                "Ελεύθερη Επιλογή": sel_free
            }
        elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            categorized_electives = {
                f"Ομάδα Α ({main_dir_1.split(':')[0]})": sel_m1_a,
                f"Ομάδα Β ({main_dir_1.split(':')[0]})": sel_m1_b,
                f"Ομάδα Α ({main_dir_2.split(':')[0]})": sel_m2_a,
                f"Ομάδα Β ({main_dir_2.split(':')[0]})": sel_m2_b,
                "Ελεύθερη Επιλογή": sel_free_2
            }
        else:
            categorized_electives = {
                "Ομάδα Α (Από όλες τις κατευθύνσεις)": sel_gen_a,
                "Ελεύθερη Επιλογή": sel_gen_free
            }

        results, is_valid = validate_scenario(
            scenario=scenario, 
            categorized_electives=categorized_electives, 
            my_electives=my_electives, 
            my_winter=my_winter, 
            my_spring=my_spring, 
            sem7=sem7, 
            sem9=sem9, 
            thesis_checked=thesis_checked
        )
        errors = 0 if is_valid else 1

        for res in results:
            if res["type"] == "success":
                st.success(res["message"])
            elif res["type"] == "error":
                st.error(res["message"])
            elif res["type"] == "warning":
                st.warning(res["message"])

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
            valid=(errors==0)
        )
        with open(pdf_path, "rb") as pdf_file:
            st.download_button(
                label="Εξαγωγή σε PDF",
                data=pdf_file,
                file_name="ceid_scenario.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        with st.form("save_scenario_form"):
            st.markdown("#### Αποθήκευση στο Προφίλ")
            scen_name = st.text_input("Όνομα Σεναρίου (π.χ. 'Το τέλειο πλάνο')")
            submitted = st.form_submit_button("Αποθήκευση Σεναρίου")
            if submitted and scen_name:
                data_to_save = {
                    "scenario_type": scenario,
                    "main_dir": main_dir if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση" else None,
                    "main_dir_1": main_dir_1 if scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις" else None,
                    "main_dir_2": main_dir_2 if scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις" else None,
                    "my_electives": my_electives,
                    "my_winter": my_winter,
                    "my_spring": my_spring,
                    "sem7": sem7,
                    "sem9": sem9,
                    "valid": (errors==0)
                }
                save_scenario(scen_name, data_to_save)
                st.success(f"Το σενάριο '{scen_name}' αποθηκεύτηκε με επιτυχία!")

    # ==========================================
    # PAGE 2: THE AI ADVISOR
    # ==========================================
