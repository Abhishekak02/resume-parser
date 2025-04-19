from parser import parse_resume
import nltk
import re

# nltk.download('punkt_tab')
from nltk.tokenize import sent_tokenize

# Soft and Hard Skills
SOFT_SKILLS = [
    "communication", "teamwork", "leadership", "problem-solving", "adaptability",
    "creativity", "work ethic", "critical thinking", "time management",
    "interpersonal", "collaboration", "empathy", "decision-making"
    'Data analysis', 'predictive modeling', 'statistical reasoning', 'computational modeling', 'project collaboration' 
]

HARD_SKILLS = [
    "python", "java", "sql", "excel", "machine learning", "data analysis",
    "data visualization", "nlp", "power bi", "tableau", "deep learning",
    "pandas", "numpy", "matplotlib", "keras", "tensorflow", "spark",
    "statistics", "regression", "classification", 
    "html", "css", "javascript", "linux", "docker", "git"
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
                experience_entry = f"🔹 {current_exp_title}"
                for bullet in current_exp_bullets:
                    experience_entry += f"\n   • {bullet}"
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
    if current_exp_title:
        experience_entry = f"🔹 {current_exp_title}"
        for bullet in current_exp_bullets:
            experience_entry += f"\n   • {bullet}"
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

    edu_text = " ".join(education_lines)

    # Normalize formatting
    edu_text = re.sub(r'\s{2,}', ' ', edu_text)
    edu_text = re.sub(r'\bC\s?G\s?P\s?A\b.*?(?=( |$))', '', edu_text, flags=re.IGNORECASE)
    edu_text = re.sub(r'Percentage\s*:\s*\d+(\.\d+)?%', '', edu_text, flags=re.IGNORECASE)
    edu_text = re.sub(r'(April|June|December|March)[^0-9]*\d{4}.*?(?=\s|$)', '', edu_text, flags=re.IGNORECASE)

    # Extract institution names using common patterns
    institution_pattern = r'(Guru Tegh Bahadur Institute of Technology.*?|Pusa Institute of Technology.*?|National Institute of Open School.*?|Government Co-ed Senior Secondary School.*?Dwarka New Delhi)'

    institutions = re.findall(institution_pattern, edu_text, re.IGNORECASE)
    return [inst.strip() for inst in institutions]



def format_project_section(text):
    lines = text.split('\n')
    capture = False
    projects = []
    current_project_title = None
    project_content = ""

    # Keywords
    start_keywords = ["projects"]
    stop_keywords = ["experience", "certification", "education", "skills", "contact", "soft"]
    title_keywords = ["project", "analysis", "dashboard", "developed", "created", "built", "designed", "implemented"]

    # Regex patterns
    bullet_pattern = re.compile(r'^[•\-–—\s]+')
    date_pattern = re.compile(
        r'(\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s*\d{2,4})|'
        r'(\b\d{1,2}[/-]\d{2,4})|'
        r'(\b\d{4}[/-]?\d{0,2})|'
        r'(\b20\d{2}\b)',
        flags=re.IGNORECASE
    )

    for line in lines:
        line_clean = line.strip()
        line_lower = line_clean.lower()

        if any(start_kw in line_lower for start_kw in start_keywords):
            capture = True
            continue

        if capture and any(stop_kw in line_lower for stop_kw in stop_keywords):
            break

        if capture:
            # Clean line
            line_clean = bullet_pattern.sub('', line_clean)
            line_clean = date_pattern.sub('', line_clean)
            line_clean = re.sub(r'\([^)]*\)', '', line_clean)  # remove text inside parentheses
            line_clean = re.sub(r'\s{2,}', ' ', line_clean).strip()

            # Heading logic: if line contains title keywords and <= 10 words, it's likely a title
            if any(word in line_lower for word in title_keywords) and 3 <= len(line_clean.split()) <= 12:
                if current_project_title:  # if already exists, save previous
                    projects.append((current_project_title, project_content.strip()))
                current_project_title = f"• {line_clean}"
                project_content = ""
            elif current_project_title:
                project_content += " " + line_clean

    # Append last project
    if current_project_title:
        projects.append((current_project_title, project_content.strip()))

    # Format output
    output_lines = []
    for title, content in projects:
        output_lines.append(title)
        sentences = sent_tokenize(content)
        for sentence in sentences:
            clean_sentence = sentence.strip()
            if clean_sentence:
                output_lines.append(f"   - {clean_sentence}")

    return output_lines


def extract_certifications(text):
    cert_keywords = ['certification', 'certifications', 'certificate', 'completed', 'course', 'linkedin learning', 'introduction']

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
        print("   •", edu)

    
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
        print("   •", hs)

    print("\n🤝 Soft Skills:")
    for ss in details.get("soft_skills", []):
        print("   •", ss)

# 🧪 Test Run
# if __name__ == "__main__":
#     text = parse_resume('/home/archie/Documents/Abhishek_CV-2.pdf')
#     details = extract_details(text)
#     print_structured_details(details)