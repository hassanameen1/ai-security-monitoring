"""Function tools for the HR chatbot — OpenAI tools API.

DELIBERATE: no authorization checks inside the tools. That's the abuse
vector. Session 14's KQL detection catches enumeration patterns
(many sequential calls across IDs / departments) at the telemetry layer.
"""

import json
from collections import Counter
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "mock_hr_db.json"
_DB: list[dict] = json.loads(DB_PATH.read_text())
_BY_ID = {e["employee_id"]: e for e in _DB}


def list_employees(department: str | None = None) -> list[dict]:
    rows = _DB
    if department:
        rows = [e for e in _DB if e["department"].lower() == department.lower()]
    return [
        {
            "employee_id": e["employee_id"],
            "name": e["name"],
            "job_role": e["job_role"],
            "job_level": e["job_level"],
        }
        for e in rows
    ]


def get_employee_details(employee_id: int) -> dict:
    if employee_id not in _BY_ID:
        return {"error": "not_found", "employee_id": employee_id}
    return _BY_ID[employee_id]


def get_department_info(department: str) -> dict:
    rows = [e for e in _DB if e["department"].lower() == department.lower()]
    if not rows:
        return {"error": "not_found", "department": department}
    avg_tenure = round(sum(e["years_at_company"] for e in rows) / len(rows), 1)
    levels = Counter(e["job_level"] for e in rows)
    manager = next(
        (e["name"] for e in rows
         if "Manager" in e["job_role"]
         or e["job_role"] in ("CEO", "CTO", "CFO", "VP Engineering")),
        None,
    )
    return {
        "department": department,
        "employee_count": len(rows),
        "avg_tenure_years": avg_tenure,
        "level_distribution": dict(levels),
        "manager_name": manager,
    }


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_employees",
            "description": "List employees, optionally filtered by department.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {
                        "type": "string",
                        "description": "Optional department filter. One of: Engineering, HR, Finance, Operations, Executive.",
                    },
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_employee_details",
            "description": "Get the full record for one employee by ID, including contact and compensation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "employee_id": {"type": "integer", "description": "Employee ID."},
                },
                "required": ["employee_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_department_info",
            "description": "Get summary statistics for a department: employee count, average tenure, level distribution, manager.",
            "parameters": {
                "type": "object",
                "properties": {
                    "department": {"type": "string", "description": "Department name."},
                },
                "required": ["department"],
            },
        },
    },
]

TOOL_REGISTRY = {
    "list_employees": list_employees,
    "get_employee_details": get_employee_details,
    "get_department_info": get_department_info,
}
