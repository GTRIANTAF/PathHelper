from mcp.server.fastmcp import FastMCP
import json
import os
import sys

# προσθήκη του τρέχοντος φακέλου στο path για να κάνει import το knowledge_base
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from knowledge_base import get_course_info, get_all_available_courses, CEID_COURSES

mcp = FastMCP("CEID_PathHelper_Server")

@mcp.tool()
def fetch_course_details(course_name: str) -> str:
    """
    Given an exact course name in Greek, returns its ECTS and the semester it belongs to.
    """
    info = get_course_info(course_name)
    if info:
        return json.dumps(info, ensure_ascii=False)
    return f"Δεν βρέθηκε μάθημα με το όνομα: {course_name}"

@mcp.tool()
def list_all_courses() -> str:
    """
    Returns a massive list of every single course available in the CEID department.
    """
    courses = get_all_available_courses()
    return json.dumps(courses, ensure_ascii=False)

@mcp.tool()
def get_courses_for_direction(direction_name: str) -> str:
    """
    Returns the Group A and Group B courses for a given direction.
    Valid directions: 'Κ1', 'Κ2', 'Κ3', 'Κ4', 'Κ5', 'Κ6'
    """
    # Find the full key name
    matched_key = None
    for key in CEID_COURSES.keys():
        if key.startswith(direction_name):
            matched_key = key
            break
            
    if not matched_key:
        return f"Μη έγκυρη κατεύθυνση: {direction_name}"
        
    return json.dumps(CEID_COURSES[matched_key], ensure_ascii=False)

if __name__ == "__main__":
    mcp.run()
