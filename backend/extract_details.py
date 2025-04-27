from parser import parse_resume
import nltk
import re

nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

# Soft and Hard Skills
SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem-solving", "adaptability",
    "creativity", "work ethic", "critical thinking", "time management",
    "interpersonal", "collaboration", "empathy", "decision-making"
    'Data analysis', 'predictive modeling', 'statistical reasoning', 'computational modeling', 'project collaboration' 
]


HARD_SKILLS = [
    "python", "java", "sql", "excel", "power bi",
    "pandas", "numpy", "keras", "tensorflow", "c", "c++",
    "html", "css", "git", "github", "dashboard creation", 
    "opencv", "pivot table", "scikit learn", "django"
]

# Cleaning utility
def clean_text(text):
    text = re.sub(r'[•●▪️\-]', '', text)
    return text.strip().lower()

# Extracting skills
def extract_soft_skills(text):
    text = clean_text(text)
    return [skill for skill in SOFT_SKILLS if skill.lower() in text]

def extract_hard_skills(text):
    text = clean_text(text)
    return [skill for skill in HARD_SKILLS if skill.lower() in text]

def extract_all_skills(text):
    lines = text.split('\n')
    all_soft_skills = set()
    all_hard_skills = set()

    for line in lines:
        all_soft_skills.update(extract_soft_skills(line))
        all_hard_skills.update(extract_hard_skills(line))

    return {
        "hard_skills": list(all_hard_skills),
        "soft_skills": list(all_soft_skills)
    }

# Other detail extractors

def extract_name(text):
    for line in text.split('\n'):
        if line.strip() and len(line.split()) <= 5 and all(word[0].isupper() for word in line.split() if word):
            return line.strip()
    return ""

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else ""

def extract_phone(text):
    match = re.search(r'\b(\+?\d[\d\-\s]{8,}\d)\b', text)
    return match.group(0) if match else ""

def extract_location(text):
    locations = ['Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Pune', 'Kolkata', 'Noida']
    for loc in locations:
        if loc.lower() in text.lower():
            return loc
    return ""

def extract_section(text, keywords):
    lines = text.split('\n')
    return [line.strip() for line in lines if any(keyword.lower() in line.lower() for keyword in keywords)]

def extract_experience(text):
    experience_keywords = ['experience', 'internship', 'worked', 'company', 'organization']
    stop_keywords = [
        'technical skills', 'certification', 'certifications', 'skills', 
        'projects', 'education', 'contact', 'languages', 'summary', 'objective'
    ]

    lines = text.split('\n')
    experiences = []
    capture = False
    current_exp_title = ""
    current_exp_bullets = []

    date_pattern = re.compile(
        r'\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}\s*[-–to]+\s*'
        r'(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+\d{4}',
        re.IGNORECASE
    )

    for line in lines:
        line_clean = line.strip()

        # End capturing if a stop keyword is found
        if any(stop_kw in line_clean.lower() for stop_kw in stop_keywords):
            if current_exp_title:
                experience_entry = f" {current_exp_title}"
                for bullet in current_exp_bullets:
                    experience_entry += f"\n    {bullet}"
                experiences.append(experience_entry)
                current_exp_title = ""
                current_exp_bullets = []
            capture = False
            continue

        # Start capturing if an experience keyword is found (section heading)
        if any(keyword in line_clean.lower() for keyword in experience_keywords) and not capture:
            capture = True
            continue

        if capture:
            if not current_exp_title and line_clean:
                current_exp_title = date_pattern.sub('', line_clean).strip('• ').strip()
            elif line_clean:
                if line_clean.startswith('•') or line_clean.startswith('-') or line_clean.startswith('*'):
                    # New bullet point
                    current_exp_bullets.append(line_clean.strip('•-* ').strip())
                else:
                    # Line continuation of previous bullet point
                    if current_exp_bullets:
                        current_exp_bullets[-1] += ' ' + line_clean.strip()
                    else:
                        current_exp_bullets.append(line_clean.strip())

    # Add final experience block
    # if current_exp_title:
    #     experience_entry = f"🔹 {current_exp_title}"
    #     for bullet in current_exp_bullets:
    #         experience_entry += f"\n   • {bullet}"
    #     experiences.append(experience_entry)

    # return experiences

    if current_exp_title:
        experience_entry = f" {current_exp_title}"
        for bullet in current_exp_bullets:
            experience_entry += f"\n    {bullet}"
        experiences.append(experience_entry)

    return experiences



def extract_education(text):
    lines = text.split('\n')
    education_lines = []
    capture = False

    start_keywords = ['education']
    stop_keywords = ['experience', 'project', 'certification', 'skills', 'summary', 'objective']

    for line in lines:
        line_lower = line.lower().strip()

        if any(stop in line_lower for stop in stop_keywords) and capture:
            break
        if any(start in line_lower for start in start_keywords):
            capture = True
            continue

        if capture and line.strip():
            education_lines.append(line.strip())

    # Combine continuation lines together
    combined_lines = []
    buffer = ""
    for line in education_lines:
        if re.search(r'(University|Institute|College|School|Academy|Faculty|Polytechnic)', line, re.IGNORECASE):
            if buffer:
                combined_lines.append(buffer)
                buffer = ""
            buffer = line
        else:
            buffer += " " + line
    if buffer:
        combined_lines.append(buffer)

    edu_text = " ".join(combined_lines)

    # Clean
    edu_text = re.sub(r'\s{2,}', ' ', edu_text)
    edu_text = re.sub(r'\bC\s?G\s?P\s?A\b.*?(?=( |$))', '', edu_text, flags=re.IGNORECASE)
    edu_text = re.sub(r'Percentage\s*:\s*\d+(\.\d+)?%', '', edu_text, flags=re.IGNORECASE)
    edu_text = re.sub(r'(April|June|December|March|Jan|Feb|Mar|Jul|Aug|Sep|Oct|Nov)[^0-9]*\d{4}.*?(?=\s|$)', '', edu_text, flags=re.IGNORECASE)
    edu_text = re.sub(r'\d{4}', '', edu_text)  # Remove years like 2020, 2021

    # Improved regex to match full names
    institution_pattern = r'''
        \b
        (?:[A-Z][a-z.&,-]+(?:\s[A-Z][a-z.&,-]+)*\s)?
        (University|College|School|Institute|Academy|Faculty|Polytechnic)
        (?:\s(?:of|for|and|at)\s[A-Z][a-z.&,-]+(?:\s[A-Z][a-z.&,-]+)*)?
        |
        Class\s*(?:10|12|X|XII)(?:th)?|
        Secondary\s+(?:School|Education)|
        Senior\s+Secondary|
        High\s+School|
        CBSE|ICSE
        \b
    '''

    institutions = re.findall(institution_pattern, edu_text, re.VERBOSE | re.IGNORECASE)

    # Clean up and reformat output
    final_output = []
    for inst in combined_lines:
        if any(keyword.lower() in inst.lower() for keyword in ['school', 'college', 'university', 'institute', 'academy', 'faculty', 'polytechnic', 'cbse', 'icse']):
            final_output.append(" " + inst.strip())

    return list(set(final_output))


def format_project_section(text):
    lines = text.split('\n')
    capture = False
    output_lines = []

    # Broad matching keywords
    start_keywords = [
        "projects", "project work", "academic projects",
        "personal projects", "major projects", "minor projects"
    ]
    stop_keywords = [
        "experience", "certification", "education", "skills",
        "contact", "languages", "summary", "profile", "about"
    ]

    for line in lines:
        line_lower = line.strip().lower()

        if any(start_kw in line_lower for start_kw in start_keywords):
            capture = True
            continue

        if capture and any(stop_kw in line_lower for stop_kw in stop_keywords):
            break

        if capture:
            output_lines.append(line.strip())

    return output_lines





def extract_certifications(text):
    cert_keywords = ['certification', 'certifications', 'certificate', 'course', 'linkedin learning', 'introduction', 'analyst', 'TCS', 'scaler', '[CO]', '[EC-COUNCIL]', '[UDEMY]', '[GEEKS FOR GEEKS]']

    # Get all lines from the certification section
    lines = extract_section(text, cert_keywords)

    # Filter out header lines like "CERTIFICATIONS", "CERTIFICATION", etc.
    clean_lines = []
    for line in lines:
        line_clean = line.strip().lower()
        if line_clean in ['certifications', 'certification', 'certificate']:
            continue  # skip lines that are just section titles
        clean_lines.append(line.strip())

    return clean_lines


# Main extractor
def extract_details(text):
    skills = extract_all_skills(text)
    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "location": extract_location(text),
        "education": extract_education(text),
        "experience": extract_experience(text), 
        "projects": format_project_section(text),
        "certifications": extract_certifications(text),
        "hard_skills": skills["hard_skills"],
        "soft_skills": skills["soft_skills"]
    }

# 🔸 Pretty Print
def print_structured_details(details):
    print("\n🔹 Name:", details.get("name", ""))
    print("🔹 Email:", details.get("email", ""))
    print("🔹 Phone:", details.get("phone", ""))
    print("🔹 Location:", details.get("location", ""))


    # education = extract_education(text)
    education = details.get("education", [])


    print("📚 Education:")
    for edu in education:
        print("   ", edu)

    
    print("\n💼 Experience:")
    for exp in details.get("experience", []):
        print("   ", exp)

    print("\n🚀 Projects:")
    for project in details.get("projects", []):
        print(project)

    print("\n📜 Certifications:")
    for cert in details.get("certifications", []):
        print("   ", cert)

    print("\n🛠️ Hard Skills:")
    for hs in details.get("hard_skills", []):
        print("   ", hs)

    print("\n🤝 Soft Skills:")
    for ss in details.get("soft_skills", []):
        print("   ", ss)
