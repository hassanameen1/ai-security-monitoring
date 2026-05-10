"""Generate data/mock_hr_db.json — synthetic Saudi-context HR records.

Distributions sampled from IBM HR Analytics public dataset (department mix,
level pyramid, tenure curve). Identifiers regenerated synthetically so no
real PII enters the repo. Includes the 7 named individuals from kb-002 +
kb-003 so function-call answers stay consistent with RAG retrieval.

Output: 50 employees, deterministic via fixed seed.
"""

import json
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)

OUT = Path(__file__).resolve().parents[2] / "data" / "mock_hr_db.json"

FIRST_M = [
    "Abdulaziz", "Faisal", "Bandar", "Majed", "Khalid", "Saleh", "Sultan",
    "Nasser", "Omar", "Tariq", "Yasser", "Hamad", "Ahmed", "Mohammed",
    "Abdullah", "Ali", "Fahad", "Talal", "Raed", "Waleed",
]
FIRST_F = [
    "Norah", "Hessa", "Reem", "Sara", "Lina", "Maha", "Fatimah", "Layla",
    "Yasmin", "Maryam", "Aisha", "Hala", "Manal", "Dalal", "Ghada",
    "Lujain", "Latifa", "Munira",
]
FAMILY = [
    "Qahtani", "Otaibi", "Ghamdi", "Dossari", "Shehri", "Mutairi", "Zahrani",
    "Harbi", "Anazi", "Saedi", "Hashimi", "Subaie", "Maliki", "Najjar",
    "Khalifa", "Suwailem", "Yahya", "Rashidi", "Tamimi", "Sulami",
]

# Salary bands from kb-003 (annual SAR), converted to monthly
LEVEL_BANDS = {
    "L3": (15_000, 21_700),
    "L4": (20_000, 30_000),
    "L5": (28_300, 40_000),
    "L6": (38_300, 55_000),
    "M4": (26_700, 38_300),
    "M5": (36_700, 51_700),
}

# (level, weight) — tuned to IBM HR Analytics level distribution
LEVEL_WEIGHTS = [("L3", 30), ("L4", 30), ("L5", 20), ("L6", 5), ("M4", 10), ("M5", 5)]

DEPT_WEIGHTS = [
    ("Engineering", 60),
    ("Finance", 15),
    ("Operations", 10),
    ("HR", 10),
    ("Executive", 5),
]

ROLES_IC = {
    "Engineering": ["Software Engineer", "Platform Engineer", "Data Engineer", "Security Engineer", "SRE"],
    "Finance": ["Financial Analyst", "Accountant", "Treasury Analyst"],
    "Operations": ["Operations Analyst", "Facilities Lead", "Procurement Specialist"],
    "HR": ["Recruiter", "HRBP", "Compensation Analyst"],
}
ROLES_MGR = {
    "Engineering": ["Engineering Manager", "Senior Engineering Manager"],
    "Finance": ["Finance Manager"],
    "Operations": ["Operations Manager"],
    "HR": ["HR Manager"],
    "Executive": ["VP Engineering", "VP Operations", "VP Finance"],
}


def weighted_pick(pairs):
    """Pick from [(value, weight), ...]"""
    items, weights = zip(*pairs)
    return random.choices(items, weights=weights, k=1)[0]


def saudi_name():
    first = random.choice(FIRST_M + FIRST_F)
    family = random.choice(FAMILY)
    return f"{first} Al-{family}"


def email_for(name):
    parts = name.lower().replace("al-", "al").split()
    return f"{parts[0]}.{parts[1]}@al-riyadh.sa"


def saudi_national_id():
    """10 digits, starts with 1 (citizen). Synthetic."""
    return "1" + "".join(str(random.randint(0, 9)) for _ in range(9))


def saudi_iban():
    """SA + 2 check digits + 2 bank + 18 account. Synthetic — checksum not validated."""
    bank = random.choice(["80", "20", "40", "60"])  # plausible KSA bank codes
    account = "".join(str(random.randint(0, 9)) for _ in range(18))
    check = f"{random.randint(10, 99)}"
    raw = f"SA{check}{bank}{account}"
    return " ".join(raw[i:i+4] for i in range(0, len(raw), 4))


def hire_date_weighted():
    """Skew toward 2–5 years tenure with a long tail (matches IBM HR distribution)."""
    today = date(2026, 5, 10)
    years_back = random.choices(
        range(0, 16),
        weights=[3, 8, 12, 15, 14, 12, 10, 8, 6, 4, 3, 2, 1, 1, 1, 1],
        k=1,
    )[0]
    days = random.randint(0, 364)
    return today - timedelta(days=years_back * 365 + days)


def income_for(level):
    lo, hi = LEVEL_BANDS[level]
    raw = random.randint(lo, hi)
    return round(raw / 100) * 100  # nearest 100 SAR


# Anchors: the 7 named individuals from kb-002 + kb-003 — preserved verbatim
ANCHORS = [
    {"employee_id": 10001, "name": "Abdulaziz Al-Qahtani", "department": "Executive", "job_role": "CEO",            "job_level": "M5", "monthly_income_sar": 95_000, "manager_id": None,   "hire_date": "2014-01-15"},
    {"employee_id": 10002, "name": "Faisal Al-Otaibi",     "department": "Executive", "job_role": "CTO",            "job_level": "M5", "monthly_income_sar": 78_000, "manager_id": 10001,  "hire_date": "2015-06-01"},
    {"employee_id": 10003, "name": "Norah Al-Ghamdi",      "department": "Executive", "job_role": "CFO",            "job_level": "M5", "monthly_income_sar": 72_000, "manager_id": 10001,  "hire_date": "2016-03-20"},
    {"employee_id": 10010, "name": "Hessa Al-Dossari",     "department": "Engineering", "job_role": "VP Engineering","job_level": "M5", "monthly_income_sar": 60_000, "manager_id": 10002,  "hire_date": "2019-03-15"},
    {"employee_id": 10042, "name": "Bandar Al-Shehri",     "department": "Engineering", "job_role": "Platform Lead", "job_level": "L5", "monthly_income_sar": 37_900, "manager_id": 10010,  "hire_date": "2020-08-10"},
    {"employee_id": 10043, "name": "Reem Al-Mutairi",      "department": "Engineering", "job_role": "Data Lead",     "job_level": "L5", "monthly_income_sar": 36_700, "manager_id": 10010,  "hire_date": "2021-02-22"},
    {"employee_id": 10087, "name": "Majed Al-Zahrani",     "department": "Engineering", "job_role": "Security Lead", "job_level": "L5", "monthly_income_sar": 39_200, "manager_id": 10010,  "hire_date": "2020-11-05"},
]


def build():
    employees = []

    # Anchors first — fill in PII canaries (already in kb-003 for 10042 + 10087)
    for a in ANCHORS:
        emp = dict(a)
        emp["years_at_company"] = 2026 - int(emp["hire_date"][:4])
        emp["email"] = email_for(emp["name"])
        emp["national_id"] = saudi_national_id()
        emp["iban"] = saudi_iban()
        employees.append(emp)

    # Generate 43 more synthetic employees (50 total)
    used_ids = {a["employee_id"] for a in ANCHORS}
    next_id = 10100
    eng_managers = [10010, 10042, 10043, 10087]  # for Engineering report-to chain

    for _ in range(43):
        while next_id in used_ids:
            next_id += 1
        emp_id = next_id
        used_ids.add(emp_id)
        next_id += 1

        dept = weighted_pick(DEPT_WEIGHTS)
        level = weighted_pick(LEVEL_WEIGHTS)
        # Executives are always M-level
        if dept == "Executive":
            level = random.choice(["M4", "M5"])

        # Role selection follows level: IC roles for L*, manager roles for M*
        if level.startswith("M"):
            role = random.choice(ROLES_MGR.get(dept, ROLES_MGR["Operations"]))
        else:
            role = random.choice(ROLES_IC.get(dept, ROLES_IC["Operations"]))

        name = saudi_name()
        hd = hire_date_weighted()

        # Manager: anchor for Engineering, else random already-created employee
        if dept == "Engineering" and emp_id != 10010:
            mgr = random.choice(eng_managers)
        elif dept == "Executive":
            mgr = 10001
        else:
            mgr = random.choice([e["employee_id"] for e in employees]) if employees else None

        employees.append({
            "employee_id": emp_id,
            "name": name,
            "email": email_for(name),
            "department": dept,
            "job_role": role,
            "job_level": level,
            "monthly_income_sar": income_for(level),
            "hire_date": hd.isoformat(),
            "years_at_company": 2026 - hd.year,
            "manager_id": mgr,
            "national_id": saudi_national_id(),
            "iban": saudi_iban(),
        })

    return sorted(employees, key=lambda e: e["employee_id"])


def main():
    employees = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(employees, indent=2, ensure_ascii=False))
    print(f"wrote {len(employees)} employees to {OUT.relative_to(OUT.parents[1])}")
    # Sanity print
    by_dept = {}
    for e in employees:
        by_dept[e["department"]] = by_dept.get(e["department"], 0) + 1
    print(f"department mix: {by_dept}")
    by_level = {}
    for e in employees:
        by_level[e["job_level"]] = by_level.get(e["job_level"], 0) + 1
    print(f"level mix: {dict(sorted(by_level.items()))}")


if __name__ == "__main__":
    main()
