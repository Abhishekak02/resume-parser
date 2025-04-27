import pandas as pd
import re
from parser import parse_resume  # Ensure parser.py exists
from test import extract_all_skills, extract_skills, extract_keywords, extract_skills_with_ner  

# ✅ Load Job Descriptions from CSV
jd_df = pd.read_csv("tech_job_descriptions.csv")  # Replace with your CSV file
jd_df['Skills_Extracted'] = jd_df['Job_Description'].apply(lambda x: extract_all_skills(str(x)))

# ✅ Read Resume and Extract Skills
resume_text = parse_resume("/home/archie/Downloads/sehaj_cv.pdf")  # Replace with your resume file
resume_skills = extract_all_skills(resume_text)

# ✅ Extract Unique Job Roles from CSV
job_roles = jd_df['Job_Title'].unique()
print("\nAvailable Job Roles:")
for idx, role in enumerate(job_roles, start=1):
    print(f"{idx}. {role}")

# ✅ Ask User to Select a Role
selected_idx = int(input("\nEnter the number corresponding to your desired job role: ")) - 1
if selected_idx < 0 or selected_idx >= len(job_roles):
    print("❌ Invalid selection. Exiting...")
    exit()

selected_role = job_roles[selected_idx]
print(f"\n🔹 Selected Job Role: {selected_role}")

# ✅ Filter JD for Selected Role
jd_selected = jd_df.loc[jd_df['Job_Title'] == selected_role].copy()  # Ensure it's a copy

# ✅ Compare JD Skills with Resume Skills
def find_skill_gap(jd_skills, resume_skills):
    missing_skills = set(jd_skills) - set(resume_skills)  # Convert both lists to sets before subtracting
    return list(missing_skills)  # Convert back to a list for consistent output

# ✅ Assign missing skills using .loc to avoid SettingWithCopyWarning
jd_df.loc[jd_selected.index, 'Missing_Skills'] = jd_selected['Skills_Extracted'].apply(
    lambda x: find_skill_gap(x, resume_skills)
)

# ✅ Fetch updated rows again to ensure modifications persist
jd_selected = jd_df.loc[jd_selected.index]

# ✅ Display Skill Gap Analysis
for index, row in jd_selected.iterrows():
    print(f"\n🔹 Job Role: {row['Job_Title']}")
    print(f"✅ Required Skills: {row['Skills_Extracted']}")
    print(f"❌ Missing Skills: {row['Missing_Skills']}")
