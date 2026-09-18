import os
import json
from typing import Optional
from fpdf import FPDF
from knowledge_base import get_course_info
import streamlit as st
from supabase import create_client, Client

# Initialize Supabase client
@st.cache_resource
def init_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

try:
    supabase = init_supabase()
except Exception as e:
    supabase = None
    print(f"Supabase connection error: {e}")

# ─────────────────────────────────────────────
#  PUBLIC API (SUPABASE)
# ─────────────────────────────────────────────

def load_scenarios(am: Optional[str] = None) -> dict:
    """
    If am is provided → return only that student's scenarios from Supabase.
    If am is None     → return {} (admin view not supported in supabase yet).
    """
    if not supabase or not am:
        return {}
    
    try:
        response = supabase.table("scenarios").select("scenario_name, data").eq("am", str(am)).execute()
        result = {}
        for row in response.data:
            result[row["scenario_name"]] = row["data"]
        return result
    except Exception as e:
        print(f"Error loading from Supabase: {e}")
        return {}


def save_scenario(name: str, data: dict, am: Optional[str] = None) -> None:
    """
    Save a scenario to Supabase.
    """
    if not supabase or not am:
        return
        
    try:
        # Upsert the scenario (update if it exists for this AM and Name, otherwise insert)
        supabase.table("scenarios").upsert({
            "am": str(am),
            "scenario_name": name,
            "data": data
        }).execute()
    except Exception as e:
        print(f"Error saving to Supabase: {e}")


def delete_scenario(name: str, am: str) -> None:
    if not supabase:
        return
        
    try:
        supabase.table("scenarios").delete().eq("am", str(am)).eq("scenario_name", name).execute()
    except Exception as e:
        print(f"Error deleting from Supabase: {e}")


# ─────────────────────────────────────────────
#  PDF EXPORT
# ─────────────────────────────────────────────

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "", 13)
        self.cell(0, 10, "CEID Path Advisor - Final Scenario", ln=True, align="C")
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
