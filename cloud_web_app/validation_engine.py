from knowledge_base import CEID_COURSES, get_total_ects

def validate_scenario(scenario, categorized_electives, my_electives, my_winter, my_spring, sem7, sem9, thesis_checked):
    """
    Returns a list of dicts with {"type": "success"|"error"|"warning", "message": "..."}
    and a boolean indicating if the program is completely valid (errors == 0).
    """
    results = []
    errors = 0

    # --- 1. ΕΛΕΓΧΟΣ ΠΟΣΟΤΗΤΑΣ & ECTS ---
    total_elective_ects = get_total_ects(my_electives)
    if len(my_electives) >= 17 and total_elective_ects >= 85:
        results.append({
            "type": "success", 
            "message": f"**Μαθήματα & ECTS:** Έχεις {len(my_electives)} μαθήματα και συγκεντρώνεις {total_elective_ects} ECTS από επιλογές."
        })
    else:
        if len(my_electives) < 17:
            results.append({"type": "error", "message": f"**Μαθήματα:** Έχεις {len(my_electives)}/17. Πρέπει να διαλέξεις τουλάχιστον 17 στο Βήμα 1."})
            errors += 1
        if total_elective_ects < 85:
            results.append({"type": "error", "message": f"**ECTS:** Έχεις {total_elective_ects}/85 ECTS. Χρειάζεσαι επιπλέον μαθήματα!"})
            errors += 1

    # --- 2. ΕΛΕΓΧΟΣ ΕΞΑΜΗΝΩΝ ---
    if len(my_winter) >= 11 and len(my_spring) >= 6:
        results.append({"type": "success", "message": f"**Εξάμηνα:** Αποδεκτή κατανομή ({len(my_winter)} Χειμερινά, {len(my_spring)} Εαρινά)."})
    else:
        results.append({"type": "error", "message": f"**Εξάμηνα:** Έχεις {len(my_winter)} Χειμερινά (πρέπει τουλάχιστον 11) και {len(my_spring)} Εαρινά (πρέπει τουλάχιστον 6)."})
        errors += 1

    if len(sem7) != 5:
        results.append({"type": "error", "message": f"**7ο Εξάμηνο:** Έχεις βάλει {len(sem7)} μαθήματα. Πρέπει να επιλέξεις ακριβώς 5."})
        errors += 1

    # --- 3. ΕΛΕΓΧΟΣ ΔΙΑΣΠΟΡΑΣ ΑΝΑ ΣΕΝΑΡΙΟ ---
    if scenario == "Σενάριο 1: Μία κύρια κατεύθυνση":
        sel_other_a = categorized_electives.get("Ομάδα Α (Άλλων Κατευθύνσεων)", [])
        # Find the main direction from the first category key (which should be "Ομάδα Α (KX)")
        main_dir_prefix = list(categorized_electives.keys())[0].split("(")[1].replace(")", "")
        main_dir = next((d for d in CEID_COURSES.keys() if d.startswith(main_dir_prefix)), None)

        unique_dirs = set()
        for c in sel_other_a:
            for d, d_data in CEID_COURSES.items():
                if d != main_dir and c in d_data.get("Group_A", {}):
                    unique_dirs.add(d)
        if len(unique_dirs) < 3 and len(sel_other_a) > 0:
            results.append({"type": "error", "message": f"**Διασπορά:** Τα 5 μαθήματα Ομάδας Α πρέπει να προέρχονται από τουλάχιστον 3 άλλες κατευθύνσεις (έχεις από {len(unique_dirs)})."})
            errors += 1

    elif scenario == "Σενάριο 2: Δύο κύριες κατευθύνσεις":
        sel_free_2 = categorized_electives.get("Ελεύθερη Επιλογή", [])
        m1_prefix = list(categorized_electives.keys())[0].split("(")[1].replace(")", "")
        m2_prefix = list(categorized_electives.keys())[2].split("(")[1].replace(")", "")
        
        main_dir_1 = next((d for d in CEID_COURSES.keys() if d.startswith(m1_prefix)), None)
        main_dir_2 = next((d for d in CEID_COURSES.keys() if d.startswith(m2_prefix)), None)

        unique_dirs = set()
        for c in sel_free_2:
            for d, d_data in CEID_COURSES.items():
                if d not in [main_dir_1, main_dir_2] and (c in d_data.get("Group_A", {}) or c in d_data.get("Group_B", {})):
                    unique_dirs.add(d)
        if len(unique_dirs) < 2 and len(sel_free_2) > 0:
            results.append({"type": "error", "message": f"**Διασπορά:** Τα μαθήματα ελεύθερης επιλογής πρέπει να προέρχονται από τουλάχιστον 2 άλλες κατευθύνσεις (έχεις από {len(unique_dirs)})."})
            errors += 1

    elif scenario == "Σενάριο 3: Γενική κατεύθυνση":
        sel_gen_free = categorized_electives.get("Ελεύθερη Επιλογή", [])
        unique_dirs = set()
        for c in sel_gen_free:
            for d, d_data in CEID_COURSES.items():
                if c in d_data.get("Group_A", {}) or c in d_data.get("Group_B", {}):
                    unique_dirs.add(d)
        if len(unique_dirs) < 4 and len(sel_gen_free) > 0:
            results.append({"type": "error", "message": f"**Διασπορά:** Τα 7 μαθήματα ελεύθερης επιλογής πρέπει να προέρχονται από τουλάχιστον 4 κατευθύνσεις (έχεις από {len(unique_dirs)})."})
            errors += 1

    # --- 4. ΒΑΣΙΚΟΣ ΚΑΝΟΝΑΣ (Πυλώνες) ---
    has_k1 = any(c in CEID_COURSES["Κ1: Αλγοριθμικές Θεμελιώσεις"].get("Group_A", {}) or c in CEID_COURSES["Κ1: Αλγοριθμικές Θεμελιώσεις"].get("Group_B", {}) for c in my_electives)
    has_hw = any(any(c in CEID_COURSES[k].get("Group_A", {}) or c in CEID_COURSES[k].get("Group_B", {}) for c in my_electives) for k in ["Κ2: Δίκτυα και Επικοινωνίες", "Κ3: Τεχνολογία της Πληροφορίας", "Κ4: Τεχνολογία Υλικού"])
    has_sw = any(any(c in CEID_COURSES[k].get("Group_A", {}) or c in CEID_COURSES[k].get("Group_B", {}) for c in my_electives) for k in ["Κ5: Τεχνολογία & Συστήματα Λογισμικού", "Κ6: Ευφυή Συστήματα"])

    if has_k1 and has_hw and has_sw:
        results.append({"type": "success", "message": "**Βασικός Κανόνας:** Έχεις μαθήματα Θεωρίας, Υλικού και Λογισμικού."})
    else:
        results.append({"type": "error", "message": "**Βασικός Κανόνας:** Λείπει μάθημα από βασικό πυλώνα (Πρέπει 1 από Κ1, 1 από Υλικό Κ2-Κ4, 1 από Λογισμικό Κ5-Κ6)."})
        errors += 1

    # --- 5. ΕΛΕΓΧΟΣ ΔΙΠΛΩΜΑΤΙΚΗΣ ---
    if thesis_checked:
        results.append({"type": "success", "message": "**Διπλωματική:** Υπολογίστηκαν 30 ECTS."})
    else:
        results.append({"type": "warning", "message": "**Διπλωματική:** Δεν την έχεις τσεκάρει. Απαιτείται για τη λήψη του διπλώματος."})

    return results, (errors == 0)
