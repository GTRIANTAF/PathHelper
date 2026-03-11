# -*- coding: utf-8 -*-

import ollama
import json
import os
import sys
from upnet_api import UpnetScraper

# --- CONFIGURATION ---
MODEL = "llama3.2"

# --- SYSTEM INSTRUCTION (The Rules) ---
SYSTEM_INSTRUCTION = """
You are an expert Academic Advisor for CEID (University of Patras).
Your goal is to help students choose their "Direction of Deepening" (Katefthinsi) based on the official 2025-2026 rules.

--- THE 6 DIRECTIONS (K1-K6) ---
K1: Algorithmic Foundations (Theory, Math)
K2: Networks & Communications
K3: Information Engineering
K4: Hardware & Architecture
K5: Software Engineering
K6: Intelligent Systems & Big Data (AI)

--- THE 3 OFFICIAL SCENARIOS ---
You must recommend one of these three paths:
1. "SCENARIO 1: The Specialist" (Requires: 10 from Main + 5 from others + 2 Free)
2. "SCENARIO 2: The Hybrid" (Requires: 7 from Dir A + 7 from Dir B + 3 Free)
3. "SCENARIO 3: The Generalist" (Requires: 10 Core courses spread across ALL + 7 Free)

--- CRITICAL RULE: BREADTH REQUIREMENT ---
Every student MUST take at least one course from each pillar:
1. THEORY: A course from K1.
2. HARDWARE: A course from K2, K3, or K4.
3. SOFTWARE: A course from K5 or K6.

--- YOUR TASK ---
1. Analyze the "Progress Report" I give you (it tells you exactly how many A/B courses they passed in each Direction).
2. Ask 3 short questions to find their interest.
3. Recommend the best Direction (K1-K6) AND the best Scenario.
"""

# --- THE KNOWLEDGE BASE (Moved out of the string so Python can read it!) ---
COURSE_KNOWLEDGE = {
    "K1": {
        "title": "Algorithmic Foundations",
        "A": ["Αλγόριθμοι & Βελτιστοποίηση", "Κατανεμημένα Συστήματα",
              "Όρια Υπολογισμού & Αλγοριθμικές Μέθοδοι Επίλυσης", "Πιθανοτικές Τεχνικές & Τυχαιοκρατικοί Αλγόριθμοι",
              "Κρυπτογραφία", "Αλγοριθμικές Τεχνικές Επιστήμης Δεδομένων", "Υπολογιστική Νοημοσύνη"],
        "B": ["Παράλληλοι Αλγόριθμοι", "Αλγόριθμοι Επικοινωνιών",
              "Αλγόριθμοι και Εφαρμογές Τεχνητής Νοημοσύνης για το Διαδίκτυο των Αντικειμένων (IoT)",
              "Αλγοριθμική Θεωρία Παιγνίων", "Στατιστικές μέθοδοι μηχανικής μάθησης",
              "Τεχνολογίες Υλοποίησης Αλγορίθμων", "Ειδικά Θέματα Υπολογιστικής Λογικής",
              "Μαθηματική Λογική και Εφαρμογές της", "Σημασιολογία στην Επιστήμη των Υπολογιστών",
              "Πολυδιάστατες Δομές Δεδομένων", "Ανάπτυξη βιντεοπαιγνιδιών", "Εισαγωγή στη Βιοπληροφορική",
              "Κυβερνοασφάλεια", "Τοπολογική Ανάλυση Δεδομένων", "Ρομποτική",
              "Μέθοδοι μητρών και υπολογιστικά εργαλεία στην επιστήμη δεδομένων"]
    },
    "K2": {
        "title": "Networks & Communications",
        "A": ["Βασικές Αρχές Δικτύων Κινητών Επικοινωνιών", "Ευφυείς Τεχνολογίες Ασύρματων και Κινητών Επικοινωνιών",
              "Αρχιτεκτονικές δικτύων επόμενης γενιάς τεχνολογίες και εφαρμογές", "Ασφάλεια Υπολογιστών και Δικτύων",
              "Υλοποιήσεις και Εφαρμογές Ασφάλειας Δικτύων",
              "Αλγόριθμοι και Εφαρμογές Τεχνητής Νοημοσύνης για το Διαδίκτυο των Αντικειμένων (IoT)",
              "Ευρυζωνικές Τεχνολογίες"],
        "B": ["Οπτικά Δίκτυα Επικοινωνιών", "Προχωρημένα Θέματα Ψηφιακών Τηλεπικοινωνιών", "Αλγόριθμοι Επικοινωνιών",
              "Δίκτυα Δημόσιας Χρήσης και Διασύνδεση Δικτύων", "Τηλεματική και Νέες Υπηρεσίες",
              "Κατανεμημένα Συστήματα", "Όρια Υπολογισμού και Αλγοριθμικές Μέθοδοι Επίλυσης", "Παράλληλοι Αλγόριθμοι",
              "Κρυπτογραφία", "Κυβερνοασφάλεια", "Ανάπτυξη Βιντεοπαιγνιδιών",
              "Τεχνικές Εκτίμησης Υπολογιστικών Συστημάτων και Δικτύων", "Διάχυτος Υπολογισμός"]
    },
    "K3": {
        "title": "Information Engineering",
        "A": ["Επεξεργασία και Ανάλυση Εικόνας", "Ανάκτηση Πληροφορίας", "Στατιστικές μέθοδοι μηχανικής μάθησης",
              "Κυβερνοασφάλεια", "Στατιστική Επεξεργασία Σήματος & Θέματα Μηχανικής Μάθησης",
              "Όραση Υπολογιστών & Γραφικά", "Ρομποτική"],
        "B": ["Επεξεργασία και Ανάλυση Video", "Αρθρωτά Κβαντικά Συστήματα", "Αρχές Ψηφιακού Ελέγχου",
              "Εισαγωγή στην Βιοπληροφορική", "Επεξεργασία και Κατανόηση της Φυσικής Γλώσσας",
              "Εικονική & Επαυξημένη Πραγματικότητα", "Εξόρυξη Δεδομένων & Μηχανική Μάθηση", "Ενσωματωμένα Συστήματα",
              "Επεξεργασία Σημάτων Θεωρία Γραφημάτων και Μάθηση", "Προγραμματισμός Συστημάτων Μηχανικής Μάθησης",
              "Συστήματα Διαχείρισης Μεγάλων Δεδομένων", "Τεχνολογίες Ευφυών Συστημάτων και Ρομποτική",
              "Αλγόριθμοι και Εφαρμογές Τεχνητής Νοημοσύνης για το Διαδίκτυο των Αντικειμένων (IoT)",
              "Μέθοδοι μητρών και υπολογιστικά εργαλεία στην επιστήμη δεδομένων"]
    },
    "K4": {
        "title": "Hardware Engineering",
        "A": ["Σχεδιασμός Συστημάτων Ειδικού Σκοπού", "Εισαγωγή σε VLSI",
              "Προχωρημένα Θέματα Αρχιτεκτονικής Υπολογιστών", "Σχεδιασμός Συστημάτων με Χρήση Υπολογιστών (CAD)",
              "Ενσωματωμένα Συστήματα", "Ασφάλεια σε Υλικό", "Σχεδιασμός Συστημάτων VLSI"],
        "B": ["Κυβερνοασφάλεια", "Επεξεργασία και Ανάλυση Εικόνας", "Εφαρμογές της Ψηφιακής Επεξεργασίας Σημάτων",
              "Όραση Υπολογιστών και Γραφικά", "Αρθρωτά Κβαντικά Συστήματα",
              "Προγραμματισμός Συστημάτων Μηχανικής Μάθησης", "Υπολογιστική Νοημοσύνη",
              "Τεχνολογίες Υλοποίησης Αλγορίθμων",
              "Αλγόριθμοι και Εφαρμογές Τεχνητής Νοημοσύνης για το Διαδίκτυο των Αντικειμένων (IoT)",
              "Τεχνολογίες Ευφυών Συστημάτων και Ρομποτική", "Ρομποτική", "Κρυπτογραφία", "Κατανεμημένα Συστήματα"]
    },
    "K5": {
        "title": "Software Engineering",
        "A": ["Λογισμικό και Προγραμματισμός Συστημάτων Υψηλής Επίδοσης",
              "Διαχείριση έργων λογισμικού και ανάπτυξη με ευέλικτες μεθόδους", "Ποιότητα λογισμικού",
              "Προηγμένα πληροφοριακά συστήματα", "Διάχυτος υπολογισμός", "Παράλληλη επεξεργασία",
              "Αλληλεπίδραση ανθρώπου-υπολογιστή"],
        "B": ["Συστήματα διαχείρισης μεγάλων δεδομένων", "Ανάκτηση πληροφορίας",
              "Αναπαράσταση γνώσης στον παγκόσμιο ιστό", "e-επιχειρείν",
              "Κοινωνικές και νομικές πλευρές της τεχνολογίας", "Πολυδιάστατες δομές δεδομένων",
              "Εξόρυξη δεδομένων και μηχανική μάθηση", "Εισαγωγή στη βιοπληροφορική",
              "Τεχνικές εκτίμησης υπολογιστικών συστημάτων και δικτύων",
              "Αλγόριθμοι και εφαρμογές τεχνητής νοημοσύνης για το διαδίκτυο των αντικειμένων (IoT)",
              "Τεχνολογίες και αλγόριθμοι αποκεντρωμένων δεδομένων", "Ανάπτυξη βιντεοπαιγνιδιών"]
    },
    "K6": {
        "title": "Intelligent Systems & Big Data",
        "A": ["Πολυδιάστατες δομές δεδομένων", "Λογισμικό και Προγραμματισμός Συστημάτων Υψηλής Επίδοσης",
              "Συστήματα διαχείρισης μεγάλων δεδομένων", "Εξόρυξη δεδομένων και μηχανική μάθηση",
              "Υπολογιστική νοημοσύνη", "Παράλληλη επεξεργασία", "Ανάκτηση πληροφορίας"],
        "B": ["Στατιστικές μέθοδοι μηχανικής μάθησης", "Παράλληλοι αλγόριθμοι", "Επιστημονικός υπολογισμός",
              "Κατανεμημένα συστήματα", "Εισαγωγή στα πληροφοριακά συστήματα", "Προηγμένα πληροφοριακά συστήματα",
              "Διάχυτος υπολογισμός", "Τεχνικές εκτίμησης υπολογιστικών συστημάτων και δικτύων",
              "Εισαγωγή στη βιοπληροφορική",
              "Αλγόριθμοι και εφαρμογές τεχνητής νοημοσύνης για το διαδίκτυο των αντικειμένων (IoT)", "Κυβερνοασφάλεια",
              "Κρυπτογραφία", "Τοπολογική ανάλυση δεδομένων",
              "Μέθοδοι μητρώων και υπολογιστικά εργαλεία στην επιστήμη δεδομένων",
              "Τεχνολογίες και αλγόριθμοι αποκεντρωμένων δεδομένων"]
    }
}


def generate_progress_report(student_grades):
    """Checks student grades against the database to calculate passed courses."""
    report = "--- ACADEMIC PROGRESS REPORT ---\n"

    # 1. Get a clean list of passed courses (lower case for easier matching)
    passed_courses = []
    for g in student_grades:
        try:
            # Handle both commas and dots for decimals
            grade_val = float(g['grade'].replace(',', '.'))
            if grade_val >= 5.0:
                passed_courses.append(g['name'].lower().strip())
        except ValueError:
            continue

    report += f"Total Courses Passed: {len(passed_courses)}\n\n"

    # 2. Iterate through the K1-K6 dictionary to see what they have completed
    for k_code, k_data in COURSE_KNOWLEDGE.items():
        report += f"[{k_code}] {k_data['title']}:\n"

        # Check Group A
        passed_a = [course for course in k_data['A'] if course.lower().strip() in passed_courses]
        report += f"   - Group A Passed ({len(passed_a)}): {', '.join(passed_a) if passed_a else 'None'}\n"

        # Check Group B
        passed_b = [course for course in k_data['B'] if course.lower().strip() in passed_courses]
        report += f"   - Group B Passed ({len(passed_b)}): {', '.join(passed_b) if passed_b else 'None'}\n"

    return report


def main():
    grades = []

    # 1. TRY LOADING FROM FILE
    if os.path.exists("my_grades.json"):
        print("Found saved grades! Skipping login...")
        with open("my_grades.json", "r", encoding="utf-8") as f:
            grades = json.load(f)
    else:
        # 2. RUN SCRAPER IF NEEDED
        print("Launching Scraper to get your grades...")
        try:
            scraper = UpnetScraper()
            grades = scraper.fetch_grades_manual()
            scraper.close()

            if grades:
                with open("my_grades.json", "w", encoding="utf-8") as f:
                    json.dump(grades, f, ensure_ascii=False, indent=4)
                    print("Grades saved to 'my_grades.json'")
        except Exception as e:
            print(f"Scraper failed: {e}")
            return

    if not grades:
        print("No grades found. I cannot advise you without data.")
        return

    # 3. GENERATE ANALYSIS
    progress_report = generate_progress_report(grades)

    # Optional: print the raw text of their grades so you know what is being sent
    grades_text = "\n".join([f"- {g['name']}: {g['grade']}" for g in grades])

    print("\n" + "=" * 50)
    print(progress_report)
    print("=" * 50 + "\n")

    # 4. START CHAT
    print(f"Bootstrapping {MODEL}... (Type 'exit' to quit)\n")

    history = [
        {'role': 'system', 'content': SYSTEM_INSTRUCTION},
        {'role': 'user', 'content': f"""
        Here is my student data:

        1. MY RAW GRADES:
        {grades_text}

        2. MY PROGRESS REPORT (Analysis of official requirements):
        {progress_report}

        Based on this, which Scenario (1, 2, or 3) is easiest for me?
        Start the interview now.
        """}
    ]

    while True:
        print("Advisor is typing...\r", end="", flush=True)
        try:
            response = ollama.chat(model=MODEL, messages=history)
            bot_msg = response['message']['content']
        except Exception as e:
            print(f"\nError calling Ollama: {e}")
            break

        print(f"\033[KADVISOR: {bot_msg}\n")
        history.append({'role': 'assistant', 'content': bot_msg})

        print("-" * 50)
        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:
            print("Good luck finding your perfect path!")
            break

        history.append({'role': 'user', 'content': user_input})


if __name__ == "__main__":
    main()