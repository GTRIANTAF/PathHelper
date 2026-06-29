import streamlit as st
import json
from knowledge_base import CEID_COURSES
from connector import get_ai_response

def render():
    st.sidebar.markdown("### My Progress")
    st.markdown("**Ανέβασμα Δεδομένων**")
    uploaded_file = st.file_uploader("Upload my_grades.json", type=["json"])

    if "user_grades" not in st.session_state:
        st.session_state.user_grades = []

    if uploaded_file is not None:
        try:
            grades_data = json.load(uploaded_file)
            st.session_state.user_grades = grades_data
            st.success(f"Φορτώθηκαν {len(grades_data)} περασμένα μαθήματα!")
        except Exception as e:
            st.error(f"Error reading file: {e}")

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

    # 4. Διαχείριση Ιστορικού
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": system_context},
            {"role": "assistant",
             "content": "Γεια σου! Είμαι ο AI Advisor του CEID. Πώς μπορώ να σε βοηθήσω με την επιλογή των μαθημάτων σου;"}
        ]
    else:
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
                bot_reply = get_ai_response(st.session_state.chat_history)
                st.markdown(bot_reply)
                st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
