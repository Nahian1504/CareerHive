from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Job titles for comparison
JOB_TITLES = [
    # Technology / IT
    "Data Analyst",
    "Machine Learning Engineer",
    "Software Engineer",
    "Backend Developer",
    "Frontend Developer",
    "DevOps Engineer",
    "Cloud Engineer",
    "Data Scientist",
    "Full Stack Developer",
    "AI Research Intern",
    "QA Engineer",
    "System Administrator",
    "Cybersecurity Analyst",
    "Network Engineer",
    "Mobile App Developer",
    
    # Business / Management
    "Product Manager",
    "Project Manager",
    "Business Analyst",
    "Operations Manager",
    "Strategy Consultant",
    "Marketing Manager",
    "Sales Executive",
    "HR Specialist",
    "Account Manager",
    
    # Design / Creative
    "UI/UX Designer",
    "Graphic Designer",
    "Motion Designer",
    "Content Writer",
    "Copywriter",
    "Video Editor",
    
    # Finance / Accounting
    "Financial Analyst",
    "Accountant",
    "Auditor",
    "Investment Analyst",
    "Risk Analyst",
    
    # Healthcare
    "Nurse",
    "Medical Assistant",
    "Lab Technician",
    "Pharmacist",
    "Clinical Research Coordinator",
    
    # Science / Research
    "Biologist",
    "Chemist",
    "Research Assistant",
    "Laboratory Technician",
    
    # Education / Teaching
    "Teacher",
    "Tutor",
    "Academic Counselor",
    
    # Other
    "Customer Support Specialist",
    "Logistics Coordinator",
    "Operations Analyst",
    "Recruiter",
    "Event Coordinator",
]


def suggest_jobs(skills):
    if not skills:
        return []

    skill_text = " ".join(skills[:20])  
    skill_embedding = model.encode(skill_text, convert_to_tensor=True)
    job_embeddings = model.encode(JOB_TITLES, convert_to_tensor=True)

    # Compute cosine similarity between user skills and job titles
    similarities = util.cos_sim(skill_embedding, job_embeddings)[0]

    # Rank jobs by similarity score
    ranked_jobs = sorted(
        zip(JOB_TITLES, similarities.tolist()), 
        key=lambda x: x[1], reverse=True
    )

    return [job for job, score in ranked_jobs[:10]]

