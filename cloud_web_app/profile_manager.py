import json
import os
from fpdf import FPDF
from knowledge_base import get_course_info

SCENARIOS_FILE = os.path.join(os.path.dirname(__file__), "saved_scenarios.json")


# ─────────────────────────────────────────────
#  JSON I/O  (per-AM structure)
# ─────────────────────────────────────────────

def _load_all() -> dict:
    """Load the full JSON file.  Returns {} on missing / corrupt file."""
    if os.path.exists(SCENARIOS_FILE):
        try:
            with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_all(data: dict) -> None:
    with open(SCENARIOS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# ─────────────────────────────────────────────
#  PUBLIC API
# ─────────────────────────────────────────────

def load_scenarios(am: str | None = None) -> dict:
    """
    If am is provided → return only that student's scenarios.
    If am is None     → return all scenarios (legacy / admin view).
    """
    all_data = _load_all()
    if am is None:
        return all_data
    return all_data.get(str(am), {})


def save_scenario(name: str, data: dict, am: str | None = None) -> None:
    """
    Save a scenario.
    If am is provided → stored under that AM.
    If am is None     → stored at the top level (anonymous, backwards-compat).
    """
    all_data = _load_all()
    if am:
        if str(am) not in all_data:
            all_data[str(am)] = {}
        all_data[str(am)][name] = data
    else:
        # anonymous save — kept for backwards compatibility
        all_data[name] = data
    _save_all(all_data)


def delete_scenario(name: str, am: str) -> None:
    all_data = _load_all()
    if str(am) in all_data and name in all_data[str(am)]:
        del all_data[str(am)][name]
        _save_all(all_data)


# ─────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "", 13)
        self.cell(0, 10, "CEID Path Advisor — Final Scenario", ln=True, align="C")
        self.ln(6)


def export_scenario_to_pdf(
    scenario_name: str,
    scenario_type: str,
    categorized_electives: dict,
    my_winter: list,
    my_spring: list,
    sem7: list,
    sem9: list,
    valid: bool,
) -> str:
    pdf = PDF()
    pdf.add_page()

    base = os.path.dirname(__file__)
    font_path    = os.path.join(base, "assets", "arial.ttf")
    font_path_bd = os.path.join(base, "assets", "arialbd.ttf")

    if os.path.exists(font_path):
        pdf.add_font("Arial", "",  font_path)
        if os.path.exists(font_path_bd):
            pdf.add_font("Arial", "B", font_path_bd)
        pdf.set_font("Arial", "", 11)
    else:
        pdf.set_font("Helvetica", size=11)

    pdf.cell(0, 8, txt=f"Scenario: {scenario_name}", ln=True)
    pdf.cell(0, 8, txt=f"Type: {scenario_type}", ln=True)
    pdf.cell(0, 8, txt=f"Valid: {'Yes' if valid else 'No'}", ln=True)
    pdf.ln(4)

    def render_table(courses: list, title: str) -> None:
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 9, txt=title, ln=True)
        pdf.set_font("Arial", "", 9)
        if not courses:
            pdf.cell(0, 8, txt="  —", ln=True)
            pdf.ln(3)
            return
        with pdf.table(col_widths=(90, 10, 10, 10, 15, 25, 20), text_align="LEFT") as table:
            hdr = table.row()
            for h in ("Τίτλος Μαθήματος", "Δ", "Φ", "Ε", "ECTS", "Τομέας", "Εξάμηνο"):
                hdr.cell(h)
            for c in courses:
                info = get_course_info(c)
                row  = table.row()
                row.cell(c)
                row.cell("-")
                row.cell("-")
                row.cell("-")
                row.cell(str(info["ects"])     if info else "-")
                row.cell(info.get("direction", "-") if info else "-")
                row.cell("Χ" if info and info["semester"] == "Χειμερινό" else "Ε")
        pdf.ln(4)

    for cat_name, courses in categorized_electives.items():
        if courses:
            render_table(courses, cat_name)

    render_table(my_winter, "Χειμερινά Μαθήματα")
    render_table(my_spring, "Εαρινά Μαθήματα")

    out_path = os.path.join(base, "assets", "scenario_export.pdf")
    pdf.output(out_path)
    return out_path
