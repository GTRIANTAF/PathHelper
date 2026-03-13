import streamlit as st

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
    st.session_state.current_page = "chat"

# --- 2. HEADER: LOGO KAI TITLE ΕΥΘΥΓΡΑΜΜΙΣΜΕΝΑ ---
# Το vertical_alignment="center" βάζει το λογότυπο ακριβώς στη μέση του ύψους του κειμένου
col_logo, col_title = st.columns([1, 9], vertical_alignment="center")

with col_logo:
    st.image("assets/logo_ceid.jpg", width=110)

with col_title:
    # Χρησιμοποιούμε HTML για να κόψουμε τα μεγάλα κενά κάτω από τον τίτλο
    st.markdown("<h1 style='padding-bottom: 0px; margin-bottom: 0px;'>CEID Path Advisor</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='color: #555555; font-size: 15px; margin-top: 0px;'>Department of Computer Engineering & Informatics</p>",
        unsafe_allow_html=True)

st.divider()  # Η διαχωριστική γραμμή ακριβώς κάτω από τον τίτλο, όπως στη ζωγραφιά σου

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
# PAGE 1: THE AI ADVISOR
# ==========================================
if st.session_state.current_page == "chat":

    # Initialize Chat Memory
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful Academic Advisor for CEID."},
            {"role": "assistant", "content": "Hello! Are you leaning towards Software, Hardware, or Math?"}
        ]

    # Draw Chat History
    for message in st.session_state.chat_history:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Handle New Chat Input
    if user_input := st.chat_input("Type your message here..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # --- GROQ API LOGIC (We will re-add your actual API key here later) ---
        with st.chat_message("assistant"):
            st.markdown("*(Groq AI is connected, but standing by!)*")
            st.session_state.chat_history.append(
                {"role": "assistant", "content": "*(Groq AI is connected, but standing by!)*"})

# ==========================================
# PAGE 2: THE PATH CHECKER
# ==========================================
elif st.session_state.current_page == "checker":
    from knowledge_base import CEID_COURSES, get_all_unique_courses, get_course_info, get_total_ects


    # Η μαγική συνάρτηση που προσθέτει το (Χ) ή (Ε) δίπλα στα ονόματα ΜΟΝΟ οπτικά!
    def format_course_with_sem(course_name):
        info = get_course_info(course_name)
        if info:
            sem_mark = "Χ" if info["semester"] == "Χειμερινό" else "Ε"
            return f"{course_name} ({sem_mark})"
        return course_name


    st.markdown("### 🎓 Σχεδιασμός & Έλεγχος Διπλώματος")
    st.info("Ακολουθήστε τα 2 βήματα για να χτίσετε το ιδανικό (και έγκυρο) πρόγραμμα σπουδών.")

    directions_list = list(CEID_COURSES.keys())

    # ==========================================
    # ΒΗΜΑ 1: ΔΥΝΑΜΙΚΗ ΕΠΙΛΟΓΗ ΒΑΣΕΙ ΚΑΝΟΝΩΝ
    # ==========================================
    st.markdown("### 🛠️ Βήμα 1: Επιλογή Μαθημάτων (Κανόνες Σεναρίου)")

    scenario = st.selectbox("Επιλέξτε Σενάριο:", [
        "Σενάριο 1: Μία κύρια κατεύθυνση",
        "Σενάριο 2: Δύο κύριες κατευθύνσεις",
        "Σενάριο 3: Γενική κατεύθυνση"
    ])

    my_electives = []

    match scenario:
        case "Σενάριο 1: Μία κύρια κατεύθυνση":
            main_dir = st.selectbox("Επιλέξτε την Κύρια Κατεύθυνση σας:", directions_list)

            if main_dir:
                main_group_a = list(CEID_COURSES[main_dir].get("Group_A", {}).keys())
                main_group_b = list(CEID_COURSES[main_dir].get("Group_B", {}).keys())

                other_group_a = set()
                all_other_courses = set()
                for d, d_data in CEID_COURSES.items():
                    if d != main_dir:
                        for c in d_data.get("Group_A", {}).keys():
                            other_group_a.add(c)
                            all_other_courses.add(c)
                        for c in d_data.get("Group_B", {}).keys():
                            all_other_courses.add(c)

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"**Από {main_dir.split(':')[0]} (Σύνολο: 10)**")
                    # ΒΑΖΟΥΜΕ ΤΟ format_func ΣΕ ΟΛΑ ΤΑ ΚΟΥΤΙΑ!
                    sel_main_a = st.multiselect(f"Ομάδα Α - Απαιτούνται 5:", sorted(main_group_a), max_selections=5,
                                                format_func=format_course_with_sem)
                    sel_main_b = st.multiselect(f"Ομάδα Β - Απαιτούνται 5:", sorted(main_group_b), max_selections=5,
                                                format_func=format_course_with_sem)

                with col2:
                    st.markdown("**Από Άλλες Κατευθύνσεις (Σύνολο: 7)**")
                    already_selected_main = sel_main_a + sel_main_b

                    avail_other_a = [c for c in sorted(list(other_group_a)) if c not in already_selected_main]
                    sel_other_a = st.multiselect("Ομάδα Α (από 3 άλλες) - Απαιτούνται 5:", avail_other_a,
                                                 max_selections=5, format_func=format_course_with_sem)

                    already_selected_all = sel_main_a + sel_main_b + sel_other_a
                    available_free = [c for c in sorted(list(all_other_courses)) if c not in already_selected_all]
                    sel_free = st.multiselect("Ελεύθερη Επιλογή - Απαιτούνται 2:", available_free, max_selections=2,
                                              format_func=format_course_with_sem)

                my_electives = sel_main_a + sel_main_b + sel_other_a + sel_free

        case "Σενάριο 2: Δύο κύριες κατευθύνσεις":
            col1, col2 = st.columns(2)
            with col1:
                main_dir_1 = st.selectbox("Επιλέξτε 1η Κύρια Κατεύθυνση:", directions_list)
            with col2:
                main_dir_2 = st.selectbox("Επιλέξτε 2η Κύρια Κατεύθυνση:", directions_list, index=1)

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

                st.markdown("**3️⃣ Ελεύθερη Επιλογή (Σύνολο: 3)**")
                all_others = set()
                for d, d_data in CEID_COURSES.items():
                    if d not in [main_dir_1, main_dir_2]:
                        for g in ["Group_A", "Group_B"]:
                            for c in d_data.get(g, {}).keys():
                                all_others.add(c)

                already_selected_m1_m2 = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b
                avail_free_2 = [c for c in sorted(list(all_others)) if c not in already_selected_m1_m2]
                sel_free_2 = st.multiselect("Ελεύθερη Επιλογή (από 2 άλλες κατ.) - Απαιτούνται 3:", avail_free_2,
                                            max_selections=3, format_func=format_course_with_sem)

                my_electives = sel_m1_a + sel_m1_b + sel_m2_a + sel_m2_b + sel_free_2

        case "Σενάριο 3: Γενική κατεύθυνση":
            all_group_a = set()
            all_courses_set = set()
            for d, d_data in CEID_COURSES.items():
                for c in d_data.get("Group_A", {}).keys():
                    all_group_a.add(c)
                    all_courses_set.add(c)
                for c in d_data.get("Group_B", {}).keys():
                    all_courses_set.add(c)

            sel_gen_a = st.multiselect("Ομάδα Α από όλες - Απαιτούνται 10:", sorted(list(all_group_a)),
                                       max_selections=10, format_func=format_course_with_sem)
            available_free_gen = [c for c in sorted(list(all_courses_set)) if c not in sel_gen_a]
            sel_gen_free = st.multiselect("Ελεύθερη Επιλογή (από 4 κατ.) - Απαιτούνται 7:", available_free_gen,
                                          max_selections=7, format_func=format_course_with_sem)

            my_electives = sel_gen_a + sel_gen_free

    st.divider()

    # ==========================================
    # ΒΗΜΑ 2: ΧΡΟΝΟΛΟΓΙΚΟΣ ΠΡΟΓΡΑΜΜΑΤΙΣΜΟΣ (ΕΞΑΜΗΝΑ)
    # ==========================================
    st.markdown("### 📅 Βήμα 2: Κατανομή στα Εξάμηνα")

    my_winter = sorted([c for c in my_electives if get_course_info(c)["semester"] == "Χειμερινό"])
    my_spring = sorted([c for c in my_electives if get_course_info(c)["semester"] == "Εαρινό"])

    sem7 = []
    sem9 = []

    if len(my_electives) > 0:
        st.info(
            f"Έχεις επιλέξει συνολικά {len(my_electives)}/17 μαθήματα. Από αυτά, τα {len(my_winter)} είναι Χειμερινά (επιτρέπονται 11) και τα {len(my_spring)} είναι Εαρινά (επιτρέπονται 6).")

        st.markdown("**🌸 8ο Εξάμηνο (Εαρινό)**")
        st.multiselect("Τα Εαρινά μαθήματα τοποθετούνται αυτόματα εδώ (Απαιτούνται 6):", my_spring, default=my_spring,
                       disabled=True, format_func=format_course_with_sem)

        st.markdown("**🍂 7ο και 9ο Εξάμηνο (Χειμερινά)**")
        col7, col9 = st.columns(2)

        with col7:
            sem7 = st.multiselect("7ο Εξάμηνο (Επιλέξτε 5):", my_winter, max_selections=5,
                                  format_func=format_course_with_sem)

        with col9:
            leftovers_for_9 = [c for c in my_winter if c not in sem7]
            sem9 = st.multiselect("9ο Εξάμηνο (Απομένουν 6):", leftovers_for_9, default=leftovers_for_9, disabled=True,
                                  format_func=format_course_with_sem)
    else:
        st.warning("Επιλέξτε μαθήματα στο Βήμα 1 για να ξεκλειδώσετε τον προγραμματισμό των εξαμήνων.")

    st.divider()

    # ==========================================
    # UI: ΤΟ ΚΟΥΜΠΙ ΕΛΕΓΧΟΥ & Ο ΑΛΓΟΡΙΘΜΟΣ
    # ==========================================
    if st.button("Οριστικός Έλεγχος & Υποβολή", type="primary", use_container_width=True):
        st.markdown("### 📊 Τελική Αναφορά")

        errors = 0

        if len(my_electives) == 17:
            st.success("✅ **Ποσότητα:** Ακριβώς 17 μαθήματα (85 ECTS).")
        else:
            st.error(f"❌ **Ποσότητα:** Έχεις {len(my_electives)}/17. Πρέπει να διαλέξεις ακριβώς 17 στο Βήμα 1.")
            errors += 1

        if len(my_winter) == 11 and len(my_spring) == 6:
            st.success("✅ **Εξάμηνα:** Ιδανική κατανομή (11 Χειμερινά, 6 Εαρινά).")
        else:
            st.error(
                f"❌ **Εξάμηνα:** Έχεις {len(my_winter)} Χειμερινά (πρέπει 11) και {len(my_spring)} Εαρινά (πρέπει 6). Άλλαξε κάποιες επιλογές στο Βήμα 1.")
            errors += 1

        if len(sem7) != 5:
            st.error(f"❌ **7ο Εξάμηνο:** Έχεις βάλει {len(sem7)} μαθήματα. Πρέπει να επιλέξεις ακριβώς 5 στο Βήμα 2.")
            errors += 1

        # Βασικός Κανόνας (Κ1, Κ2/3/4, Κ5/6)
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

        if errors == 0:
            st.balloons()
            st.success("### 🎉 Το Πρόγραμμά σου είναι τέλειο και έτοιμο για υποβολή στη Γραμματεία!")