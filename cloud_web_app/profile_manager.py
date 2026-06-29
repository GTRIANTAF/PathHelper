import json
import os
from fpdf import FPDF
from knowledge_base import get_course_info

SCENARIOS_FILE = "saved_scenarios.json"

def load_scenarios():
    if os.path.exists(SCENARIOS_FILE):
        try:
            with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_scenario(name, data):
    scenarios = load_scenarios()
    scenarios[name] = data
    with open(SCENARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(scenarios, f, ensure_ascii=False, indent=4)

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", '', 15)
        self.cell(0, 10, 'CEID Path Advisor - Final Scenario', ln=True, align='C')
        self.ln(10)

def export_scenario_to_pdf(scenario_name, scenario_type, categorized_electives, my_winter, my_spring, sem7, sem9, valid):
    pdf = PDF()
    pdf.add_page()
    
    font_path = os.path.join(os.path.dirname(__file__), "assets", "arial.ttf")
    font_path_bd = os.path.join(os.path.dirname(__file__), "assets", "arialbd.ttf")
    if os.path.exists(font_path):
        pdf.add_font("Arial", "", font_path)
        if os.path.exists(font_path_bd):
            pdf.add_font("Arial", "B", font_path_bd)
        pdf.set_font("Arial", "", 12)
    else:
        pdf.set_font("Helvetica", size=12)

    pdf.cell(0, 10, txt=f"Scenario Name: {scenario_name}", ln=True)
    pdf.cell(0, 10, txt=f"Type: {scenario_type}", ln=True)
    pdf.cell(0, 10, txt=f"Valid Program: {'Yes' if valid else 'No'}", ln=True)
    pdf.ln(5)
    
    def render_course_table(courses_list, title):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, txt=title, ln=True)
        pdf.set_font("Arial", "", 9)
        
        if not courses_list:
            pdf.cell(0, 10, txt="Δεν έχουν επιλεγεί μαθήματα.", ln=True)
            pdf.ln(5)
            return

        with pdf.table(col_widths=(85, 10, 10, 10, 15, 25, 25), text_align="LEFT") as table:
            row = table.row()
            row.cell("Τίτλος Μαθήματος")
            row.cell("Δ")
            row.cell("Φ")
            row.cell("Ε")
            row.cell("ECTS")
            row.cell("Τομέας")
            row.cell("Εξάμηνο")
            
            for c in courses_list:
                info = get_course_info(c)
                if info:
                    ects = str(info["ects"])
                    sem_mark = "Χ" if info["semester"] == "Χειμερινό" else "Ε"
                    sector = info.get("direction", "-")
                else:
                    ects = "-"
                    sem_mark = "-"
                    sector = "-"
                
                row = table.row()
                row.cell(c)
                row.cell("-") # Δ
                row.cell("-") # Φ
                row.cell("-") # Ε
                row.cell(ects)
                row.cell(sector)
                row.cell(sem_mark)
        pdf.ln(5)

    for cat_name, courses in categorized_electives.items():
        if courses:
            render_course_table(courses, cat_name)
    render_course_table(my_winter, "Χειμερινά Μαθήματα")
    render_course_table(my_spring, "Εαρινά Μαθήματα")
        
    pdf_output_path = os.path.join(os.path.dirname(__file__), "assets", "scenario_export.pdf")
    pdf.output(pdf_output_path)
    return pdf_output_path
