import re
import PyPDF2

TECH_SKILLS = [
    "python", "java", "django", "flask", "sql",
    "html", "css", "javascript", "react", "node",
    "git", "api"
]

# ---------- EMAIL CHECK ----------
def check_email(text):
    pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
    return bool(re.search(pattern, text))

# ---------- PHONE CHECK ----------
def check_phone(text):
    pattern = r'\b\d{10}\b'
    return bool(re.search(pattern, text))

# ---------- STRUCTURE CHECK ----------
def check_structure(text):
    required = ["education", "experience", "project", "skills"]
    found = [i for i in required if i in text]
    return found

# ---------- PDF EXTRACT ----------
def extract_text_from_pdf(file_path):
    

    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += " " + page_text

    return text.lower()

# ---------- MAIN ANALYZER ----------
def analyze_resume(text):
    text = text.lower()

    errors = []
    score = 100

    # EMAIL
    if not check_email(text):
        errors.append("❌ Invalid or missing email")
        score -= 20

    # PHONE
    if not check_phone(text):
        errors.append("❌ Invalid or missing phone number")
        score -= 20

    # STRUCTURE
    structure = check_structure(text)
    if len(structure) < 3:
        errors.append("❌ Resume structure incomplete (missing sections)")
        score -= 20

    # ONLY MISSING TECH SKILLS
    missing_skills = []

    for skill in TECH_SKILLS:
        if skill not in text:
            missing_skills.append(skill)

    score -= len(missing_skills) * 2

    score = max(0, min(score, 100))

    return {
        "score": score,
        "errors": errors,
        "missing_skills": missing_skills[:6]
    }