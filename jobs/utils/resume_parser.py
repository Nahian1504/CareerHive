import re
import PyPDF2
import docx2txt

# Define common skills keywords (can be expanded)
SKILL_KEYWORDS = [
    # Programming Languages
    "python", "java", "c++", "c#", "javascript", "typescript", "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "perl",

    # Web / Frontend
    "html", "css", "react", "angular", "vue", "bootstrap", "tailwind", "jquery", "sass",

    # Backend / Frameworks
    "django", "flask", "spring", "node.js", "express", "fastapi", "laravel", "rails",

    # Databases
    "sql", "mysql", "postgresql", "mongodb", "oracle", "sqlite", "redis", "cassandra",

    # Cloud / DevOps
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins", "ci/cd", "ansible", "gitlab", "github actions",

    # Data / AI / ML
    "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "matplotlib", "seaborn",
    "data analysis", "data science", "nlp", "computer vision", "reinforcement learning", "opencv", "keras", "xgboost",

    # Mobile Development
    "android", "ios", "react native", "flutter", "swift", "kotlin",

    # Other Tools & Skills
    "git", "jira", "agile", "scrum", "testing", "selenium", "postman", "rest api", "graphql", "microservices",

    # Soft / General Skills
    "communication", "teamwork", "problem solving", "leadership", "critical thinking", "time management", "adaptability"
]


def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def extract_text_from_docx(file_path):
    text = docx2txt.process(file_path)
    return text

def extract_skills(text):
    text = text.lower()
    skills_found = []
    for skill in SKILL_KEYWORDS:
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            skills_found.append(skill)
    return skills_found

def parse_resume(file_path):
    if file_path.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        text = extract_text_from_docx(file_path)
    else:
        raise ValueError("Unsupported file type. Only PDF and DOCX are allowed.")
    
    skills = extract_skills(text)
    return skills
