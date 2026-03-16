from pathlib import Path

import streamlit as st
import json

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
col_page_title, col_icon1, col_icon2 = st.columns([8, 1, 1], vertical_alignment="center")

with col_page_title:
    if st.session_state.current_page == "chat":
        st.markdown("<h2>💬 AI Advisor</h2>", unsafe_allow_html=True)
    else:
        st.markdown("<h2> Path Checker</h2>", unsafe_allow_html=True)

with col_icon1:
    if st.button("💬", help="Chat with AI", use_container_width=True):
        st.session_state.current_page = "chat"
        st.rerun()

with col_icon2:
    if st.button("📋", help="Check Path Rules", use_container_width=True):
        st.session_state.current_page = "checker"
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# PAGE 1: THE PATH CHECKER
# ==========================================
if st.session_state.current_page == "checker":
    from knowledge_base import CEID_COURSES, get_course_info, get_total_ects


    def format_course_with_sem(course_name):
        info = get_course_info(course_name)
        if info:
            sem_mark = "Χ" if info["semester"] == "Χειμερινό" else "Ε"
            return f"{course_name} ({sem_mark})"
        return course_name


    st.markdown("### 🎓 Σχεδιασμός & Έλεγχος Διπλώματος")
    st.info("Ακολουθήστε τα 3 βήματα για να χτίσετε το ιδανικό (και έγκυρο) πρόγραμμα σπουδών.")

    # ==========================================
    # ΒΗΜΑ 1: ΔΥΝΑΜΙΚΗ ΕΠΙΛΟΓΗ ΒΑΣΕΙ ΚΑΝΟΝΩΝ
    # ==========================================
    st.markdown("### **Βήμα 1**: Επιλογή Μαθημάτων (Κανόνες Σεναρίου)")

    scenario = st.selectbox("Επιλέξτε Σενάριο:", [
        "Σενάριο 1: Μία κύρια κατεύθυνση",
        "Σενάριο 2: Δύο κύριες κατευθύνσεις",
        "Σενάριο 3: Γενική κατεύθυνση"
    ])

    # Κρύβουμε τα μαθήματα Γενικής Παιδείας από τις επιλογές Κύριας Κατεύθυνσης
    valid_directions = [d for d in CEID_COURSES.keys() if d.startswith("Κ")]
    my_electives = []

    match scenario:
        case "Σενάριο 1: Μία κύρια κατεύθυνση":
            main_dir = st.selectbox("Επίλεξε Κύρια Κατεύθυνση", valid_directions)

            if main_dir:
                main_group_a = list(CEID_COURSES[main_dir].get("Group_A", {}).keys())
                main_group_b = list(CEID_COURSES[main_dir].get("Group_B", {}).keys())

                other_group_a = set()
                for d, d_data in CEID_COURSES.items():
                    if d != main_dir:
                        for c in d_data.get("Group_A", {}).keys():
                            other_group_a.add(c)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Από {main_dir.split(':')[0]} (Σύνολο: 10)**")
                    sel_main_a = st.multiselect("Ομάδα Α - Απαιτούνται 5:", sorted(main_group_a), max_selections=5,
                                                format_func=format_course_with_sem)
                    sel_main_b = st.multiselect("Ομάδα Β - Απαιτούνται 5:", sorted(main_group_b), max_selections=5,
                                                format_func=format_course_with_sem)

                with col2:
                    st.markdown("**Από Άλλες Κατευθύνσεις (Σύνολο: 7+)**")
                    already_selected_main = sel_main_a + sel_main_b

                    avail_other_a = [c for c in sorted(list(other_group_a)) if c not in already_selected_main]
                    sel_other_a = st.multiselect("Ομάδα Α (από 3 άλλες) - Απαιτούνται 5:", avail_other_a,
                                                 max_selections=5, format_func=format_course_with_sem)

                    avail_free = set()
                    for d, d_data in CEID_COURSES.items():
                        for group_dict in d_data.values():
                            for c in group_dict.keys():
                                avail_free.add(c)

                    already_selected_all = sel_main_a + sel_main_b + sel_other_a
                    available_free = [c for c in sorted(list(avail_free)) if c not in already_selected_all]

                    sel_free = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):",
                                              available_free, format_func=format_course_with_sem)

                my_electives = sel_main_a + sel_main_b + sel_other_a + sel_free

        case "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            col1, col2 = st.columns(2)
            with col1:
                main_dir_1 = st.selectbox("Επίλεξε 1η Κύρια Κατεύθυνση", valid_directions)
            with col2:
                valid_dirs_for_second = [d for d in valid_directions if d != main_dir_1]
                main_dir_2 = st.selectbox("Επίλεξε 2η Κύρια Κατεύθυνση", valid_dirs_for_second)

            if main_dir_1 == main_dir_2:
                st.warning("⚠️ Πρέπει να επιλέξετε διαφορετικές κατευθύνσεις!")
            else:
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    sel_m1_a = st.multiselect(f"Ομάδα Α ({main_dir_1.split(':')[0]}) - Απαιτούνται 5:",
                                              sorted(list(CEID_COURSES[main_dir_1].get("Group_A", {}).keys())),
                                              max_selections=5, format_func=format_course_with_sem)
                    sel_m1_b = st.multiselect(f"Ομάδα Β ({main_dir_1.split(':')[0]}) - Απαιτούνται 2:",
                                              sorted(list(CEID_COURSES[main_dir_1].get("Group_B", {}).keys())),
                                              max_selections=2, format_func=format_course_with_sem)
                with col_m2:
                    already_selected_m1 = sel_m1_a + sel_m1_b
                    avail_m2_a = [c for c in sorted(list(CEID_COURSES[main_dir_2].get("Group_A", {}).keys())) if
                                  c not in already_selected_m1]
                    sel_m2_a = st.multiselect(f"Ομάδα Α ({main_dir_2.split(':')[0]}) - Απαιτούνται 5:", avail_m2_a,
                                              max_selections=5, format_func=format_course_with_sem)

                    already_selected_m1_m2_a = already_selected_m1 + sel_m2_a
                    avail_m2_b = [c for c in sorted(list(CEID_COURSES[main_dir_2].get("Group_B", {}).keys())) if
                                  c not in already_selected_m1_m2_a]
                    sel_m2_b = st.multiselect(f"Ομάδα Β ({main_dir_2.split(':')[0]}) - Απαιτούνται 2:", avail_m2_b,
                                              max_selections=2, format_func=format_course_with_sem)

                st.markdown("**Ελεύθερη Επιλογή (Σύνολο: 3+)**")
                all_others = set()
                for d, d_data in CEID_COURSES.items():
                    if d not in [main_dir_1, main_dir_2]:
                        for group_dict in d_data.values():
                            for c in group_dict.keys():
                                all_others.add(c)

                already_selected_m1_m2 = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b
                avail_free_2 = [c for c in sorted(list(all_others)) if c not in already_selected_m1_m2]

                sel_free_2 = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):", avail_free_2,
                                            format_func=format_course_with_sem)

                my_electives = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b + sel_free_2

        case "Σενάριο 3: Γενική κατεύθυνση":
            all_group_a = set()
            all_courses_set = set()
            for d, d_data in CEID_COURSES.items():
                for c in d_data.get("Group_A", {}).keys():
                    all_group_a.add(c)
                for group_dict in d_data.values():
                    for c in group_dict.keys():
                        all_courses_set.add(c)

            sel_gen_a = st.multiselect("Ομάδα Α από όλες - Απαιτούνται 10:", sorted(list(all_group_a)),
                                       max_selections=10, format_func=format_course_with_sem)
            available_free_gen = [c for c in sorted(list(all_courses_set)) if c not in sel_gen_a]

            sel_gen_free = st.multiselect("Ελεύθερη Επιλογή (Επιλέξτε όσα χρειάζονται για 85 ECTS):",
                                          available_free_gen, format_func=format_course_with_sem)

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
        st.info(
            f"Έχεις επιλέξει συνολικά {len(my_electives)} μαθήματα. Από αυτά, τα {len(my_winter)} είναι Χειμερινά και τα {len(my_spring)} είναι Εαρινά.")

        st.markdown("**🌸 8ο Εξάμηνο (Εαρινό)**")
        st.multiselect("Τα Εαρινά μαθήματα τοποθετούνται αυτόματα εδώ:", my_spring, default=my_spring, disabled=True,
                       format_func=format_course_with_sem)

        st.markdown("**🍂 7ο και 9ο Εξάμηνο (Χειμερινά)**")
        col7, col9 = st.columns(2)

        with col7:
            sem7 = st.multiselect("7ο Εξάμηνο (Επιλέξτε 5):", my_winter, max_selections=5,
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
    if st.button("Οριστικός Έλεγχος & Υποβολή", type="primary", use_container_width=True):
        st.markdown("### **Τελική Αναφορά**")
        errors = 0

        # --- 1. ΕΛΕΓΧΟΣ ΠΟΣΟΤΗΤΑΣ & ECTS ---
        total_elective_ects = get_total_ects(my_electives)

        if len(my_electives) >= 17 and total_elective_ects >= 85:
            st.success(
                f"✅ **Μαθήματα & ECTS:** Έχεις {len(my_electives)} μαθήματα και συγκεντρώνεις {total_elective_ects} ECTS από επιλογές.")
        else:
            if len(my_electives) < 17:
                st.error(
                    f"❌ **Μαθήματα:** Έχεις {len(my_electives)}/17. Πρέπει να διαλέξεις τουλάχιστον 17 στο Βήμα 1.")
                errors += 1
            if total_elective_ects < 85:
                st.error(f"❌ **ECTS:** Έχεις {total_elective_ects}/85 ECTS. Χρειάζεσαι επιπλέον μαθήματα!")
                errors += 1

        # --- 2. ΕΛΕΓΧΟΣ ΕΞΑΜΗΝΩΝ (Χαλαρός έλεγχος με >=) ---
        if len(my_winter) >= 11 and len(my_spring) >= 6:
            st.success(f"✅ **Εξάμηνα:** Αποδεκτή κατανομή ({len(my_winter)} Χειμερινά, {len(my_spring)} Εαρινά).")
        else:
            st.error(
                f"❌ **Εξάμηνα:** Έχεις {len(my_winter)} Χειμερινά (πρέπει τουλάχιστον 11) και {len(my_spring)} Εαρινά (πρέπει τουλάχιστον 6).")
            errors += 1

        if len(sem7) != 5:
            st.error(f"❌ **7ο Εξάμηνο:** Έχεις βάλει {len(sem7)} μαθήματα. Πρέπει να επιλέξεις ακριβώς 5.")
            errors += 1

        # --- 3. ΕΛΕΓΧΟΣ ΔΙΑΣΠΟΡΑΣ ΑΝΑ ΣΕΝΑΡΙΟ ---
        if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
            unique_dirs = set()
            for c in sel_other_a:
                for d, d_data in CEID_COURSES.items():
                    if d != main_dir and c in d_data.get("Group_A", {}):
                        unique_dirs.add(d)
            if len(unique_dirs) < 3 and len(sel_other_a) > 0:
                st.error(
                    f"❌ **Διασπορά:** Τα 5 μαθήματα Ομάδας Α πρέπει να προέρχονται από τουλάχιστον 3 άλλες κατευθύνσεις (έχεις από {len(unique_dirs)}).")
                errors += 1

        elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            unique_dirs = set()
            for c in sel_free_2:
                for d, d_data in CEID_COURSES.items():
                    if d not in [main_dir_1, main_dir_2] and (
                            c in d_data.get("Group_A", {}) or c in d_data.get("Group_B", {})):
                        unique_dirs.add(d)
            if len(unique_dirs) < 2 and len(sel_free_2) > 0:
                st.error(
                    f"❌ **Διασπορά:** Τα μαθήματα ελεύθερης επιλογής πρέπει να προέρχονται από τουλάχιστον 2 άλλες κατευθύνσεις (έχεις από {len(unique_dirs)}).")
                errors += 1

        elif scenario == "Σενάριο 3: Γενική κατεύθυνση":
            unique_dirs = set()
            for c in sel_gen_free:
                for d, d_data in CEID_COURSES.items():
                    if c in d_data.get("Group_A", {}) or c in d_data.get("Group_B", {}):
                        unique_dirs.add(d)
            if len(unique_dirs) < 4 and len(sel_gen_free) > 0:
                st.error(
                    f"❌ **Διασπορά:** Τα 7 μαθήματα ελεύθερης επιλογής πρέπει να προέρχονται από τουλάχιστον 4 κατευθύνσεις (έχεις από {len(unique_dirs)}).")
                errors += 1

        # --- 4. ΒΑΣΙΚΟΣ ΚΑΝΟΝΑΣ (Πυλώνες) ---
        has_k1 = any(c in CEID_COURSES["Κ1: Αλγοριθμικές Θεμελιώσεις"].get("Group_A", {}) or c in CEID_COURSES[
            "Κ1: Αλγοριθμικές Θεμελιώσεις"].get("Group_B", {}) for c in my_electives)
        has_hw = any(any(
            c in CEID_COURSES[k].get("Group_A", {}) or c in CEID_COURSES[k].get("Group_B", {}) for c in my_electives)
                     for k in
                     ["Κ2: Δίκτυα και Επικοινωνίες", "Κ3: Τεχνολογία της Πληροφορίας", "Κ4: Τεχνολογία Υλικού"])
        has_sw = any(any(
            c in CEID_COURSES[k].get("Group_A", {}) or c in CEID_COURSES[k].get("Group_B", {}) for c in my_electives)
                     for k in ["Κ5: Τεχνολογία & Συστήματα Λογισμικού", "Κ6: Ευφυή Συστήματα"])

        if has_k1 and has_hw and has_sw:
            st.success("✅ **Βασικός Κανόνας:** Έχεις μαθήματα Θεωρίας, Υλικού και Λογισμικού.")
        else:
            st.error(
                "❌ **Βασικός Κανόνας:** Λείπει μάθημα από βασικό πυλώνα (Πρέπει 1 από Κ1, 1 από Υλικό Κ2-Κ4, 1 από Λογισμικό Κ5-Κ6).")
            errors += 1

        # --- 5. ΕΛΕΓΧΟΣ ΔΙΠΛΩΜΑΤΙΚΗΣ ---
        if thesis_checked:
            st.success("✅ **Διπλωματική:** Υπολογίστηκαν 30 ECTS.")
        else:
            st.warning("⚠️ **Διπλωματική:** Δεν την έχεις τσεκάρει. Απαιτείται για τη λήψη του διπλώματος.")

        # --- 6. ΤΕΛΙΚΟ ΑΠΟΤΕΛΕΣΜΑ ---
        if errors == 0:
            st.success("### 🎉 Το Πρόγραμμά σου είναι τέλειο και πλήρως εναρμονισμένο με τους κανόνες του CEID!")

# ==========================================
# PAGE 2: THE AI ADVISOR
# ==========================================
elif st.session_state.current_page == "chat":

    st.sidebar.markdown("### 🎓 My Progress")
    # --- 1. ΚΟΥΜΠΙ ΛΗΨΗΣ ΤΟΥ SCRAPER (.exe) ---
    #st.markdown("**Βήμα 1: Εξαγωγή Βαθμών**")
    #st.info(
    #    "Κατέβασε και τρέξε το εργαλείο στον υπολογιστή σου για να πάρεις τους βαθμούς σου με 100% ασφάλεια.")

    # Ψάχνουμε το .exe στον φάκελο assets
    #scraper_path = Path(__file__).parent / "assets" / "ceid_progress_scraper.exe"

    #if scraper_path.exists():
    #    with open(scraper_path, "rb") as file:
    #        st.download_button(
    #            label="🔽 Λήψη Scraper (.exe)",
    #            data=file,
    #            file_name="ceid_progress_scraper.exe",
    #            mime="application/octet-stream",
    #            use_container_width=True
    #        )
    #else:
    #    st.warning("⚠️ Το αρχείο scraper δεν βρέθηκε. Βεβαιώσου ότι είναι στον φάκελο assets.")
    #
    #st.divider()

    # --- 2. ΚΟΥΜΠΙ ΑΝΕΒΑΣΜΑΤΟΣ ΤΟΥ JSON ---
    st.markdown("**Ανέβασμα Δεδομένων**")
    uploaded_file = st.file_uploader("Upload my_grades.json", type=["json"])

    if "user_grades" not in st.session_state:
        st.session_state.user_grades = []

    if uploaded_file is not None:
        try:
            grades_data = json.load(uploaded_file)
            st.session_state.user_grades = grades_data
            st.success(f"✅ Φορτώθηκαν {len(grades_data)} περασμένα μαθήματα!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    from knowledge_base import CEID_COURSES

    # 1. Κατασκευή του Knowledge Base String (RAG)
    available_courses_str = "AVAILABLE COURSES PER DIRECTION:\n"
    for direction, groups in CEID_COURSES.items():
        available_courses_str += f"\nDirection: {direction}\n"
        for group, courses in groups.items():
            available_courses_str += f" - {group}: {', '.join(courses.keys())}\n"

    # 2. Οι Αγαπημένοι σου Base Rules
    base_rules = f"""
    You are the official Academic Advisor for the Computer Engineering & Informatics Department (CEID) at the University of Patras.

    CRITICAL INSTRUCTION 1: Process all your reasoning and rules in English to avoid mistakes, but YOUR FINAL REPLY TO THE STUDENT MUST BE IN NATURAL GREEK.
    CRITICAL INSTRUCTION 2: NEVER invent, translate, or hallucinate course names. ONLY recommend exact course names from the "AVAILABLE COURSES" list provided below.

    Degree Rules:
    - 17 elective courses total (11 in Winter semesters, 6 in Spring).
    - Basic Rule (MANDATORY): At least 1 course from K1 (Theory), at least 1 from K2, K3, or K4 (Hardware/Networks), and at least 1 from K5 or K6 (Software).
    - 3 Scenarios: 
      1) One Main Direction: 5 Group A, 5 Group B, 5 Group A of other directions, 2 free.
      2) Two Main: 5A+2B (first dir), 5A+2B (second dir), 3 free.
      3) General: 10 Group A (across all), 7 free.

    {available_courses_str}
    """

    # 3. Δυναμική Ενσωμάτωση Βαθμών
    if st.session_state.user_grades and len(st.session_state.user_grades) > 0:
        passed_names = []
        for item in st.session_state.user_grades:
            name = item.get("name", "")
            grade_val = str(item.get("grade", "0")).replace(",", ".")
            try:
                if float(grade_val) >= 5.0:
                    passed_names.append(name)
            except:
                continue

        passed_courses_str = ", ".join(passed_names)
        system_context = base_rules + f"\n\nSTUDENT'S PROGRESS: The student has already passed: [{passed_courses_str}]. DO NOT suggest these. Use them only to understand their profile."
    else:
        system_context = base_rules + "\n\nATTENTION: The student HAS NOT uploaded grades yet. Ask them to upload their JSON for personalized help."

    # 4. Διαχείριση Ιστορικού (Το κλειδί για να μην "ξεχνάει")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": system_context},
            {"role": "assistant",
             "content": "Γεια σου! Είμαι ο AI Advisor του CEID. Πώς μπορώ να σε βοηθήσω με την επιλογή των μαθημάτων σου;"}
        ]
    else:
        # Ενημερώνουμε ΠΑΝΤΑ το πρώτο μήνυμα (system) με το τρέχον context (ανέβηκαν βαθμοί ή όχι)
        st.session_state.chat_history[0]["content"] = system_context

    # 5. Εμφάνιση μηνυμάτων
    for message in st.session_state.chat_history:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # 6. Chat Input
    if user_input := st.chat_input("Ρώτησε κάτι τον Advisor..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        with st.chat_message("assistant"):
            with st.spinner("Ο Advisor αναλύει το πρόγραμμα σπουδών..."):
                from connector import get_ai_response

                bot_reply = get_ai_response(st.session_state.chat_history)
                st.markdown(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})