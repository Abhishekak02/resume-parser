from extract_details import extract_details, print_structured_details
from flask import Flask, request, jsonify, render_template
import os
import pandas as pd
import traceback
import re
import requests
from parser import parse_resume  
from recommendation import recommend_jobs
from skill_extraction import extract_all_skills  

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Load predefined JD CSV (columns: role, skills)
JD_CSV_PATH = "/home/archie/programs/resume_parser/backend/tech_job_descriptions.csv"
jd_df = pd.read_csv(JD_CSV_PATH)
jd_df.columns = jd_df.columns.str.strip()  # Ensure column names have no leading/trailing spaces

def find_skill_gap(jd_skills, resume_skills):
    return list(set(jd_skills) - set(resume_skills))

# ---------------------------
# Static Resources Mapping
# ---------------------------
static_skill_resources = {
    "Power BI": [
        "https://www.youtube.com/playlist?list=PLrRPvpgDmw0nZXL5xjmEooD1WkA8U8Dsv",
        "https://radacad.com/power-bi-from-rookie-to-rock-star",
        "https://www.udemy.com/course/microsoft-power-bi-up-running-with-power-bi-desktop/"
    ],
    "SQL": [
        "https://www.w3schools.com/sql/",
        "https://www.youtube.com/playlist?list=PLillGF-RfqbbiTGgA77tGO426V3hRF9iE",
        "https://www.khanacademy.org/computing/computer-programming/sql"
    ],
    "Natural Language Processing": [
        "https://www.coursera.org/learn/language-processing",
        "https://www.youtube.com/playlist?list=PLZyvi_9gamL-EE3zQJbU5N5z6LbMmhz3m",
        "https://nlp.stanford.edu/IR-book/"
    ],
    "Docker": [
        "https://www.youtube.com/playlist?list=PL9ooVrP1hQOGvX4bOSAmMWvQj2mY3t-7L",
        "https://docs.docker.com/get-started/",
        "https://www.udemy.com/course/docker-mastery/"
    ],
    "Time Series Forecasting": [
        "https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF",
        "https://otexts.com/fpp3/",
        "https://www.machinelearningplus.com/time-series/time-series-analysis-python/"
    ],
    "Tableau" : [
        "https://www.youtube.com/watch?v=-Aj8IlC0IEA",
        "https://www.tableau.com/learn",
        "https://www.youtube.com/watch?v=GbszEsOY3wo"
    ],
    "Statistics" : [
        "https://www.datacamp.com/blog/learn-statistics",
        "https://www.youtube.com/watch?v=hMaWsrSRhFE",
        "https://www.coursera.org/courses?query=statistics"
    ],
    "Data Visualization" : [
        "https://www.coursera.org/courses?query=data%20visualization",
        "https://www.youtube.com/watch?v=7kPqESo1vRw",
        "https://www.kaggle.com/learn/data-visualization"
    ],
    "Communication" : [
        "https://www.coursera.org/courses?query=communication%20skills",
        "https://professional.dce.harvard.edu/blog/8-ways-you-can-improve-your-communication-skills/",
        "https://www.youtube.com/watch?v=YJXUOJKtn8o"
    ],
    "Problem Solving" : [
        "https://asq.org/quality-resources/problem-solving",
        "https://www.youtube.com/watch?v=6DxTQiJuAoc",
        "https://dev.to/rithmschool/5-resources-to-improve-your-problem-solving-skills-2h3n"
    ],
    "ETL" : [
        "https://www.coursera.org/courses?query=etl",
        "https://www.youtube.com/watch?v=wDTzxdShbd8",
        "https://www.rudderstack.com/learn/etl/etl-guide/"

    ],
    "Python": [
        "https://www.learnpython.org/",
        "https://www.youtube.com/playlist?list=PLsyeobzWxl7p-I9FwwC7FmpmZz1tRHsde",
        "https://realpython.com/"
    ],
    "JavaScript": [
        "https://www.javascript.info/",
        "https://www.youtube.com/playlist?list=PLillGF-RfqbbiTGgA77tGO426V3hRF9iE",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide"
    ],
    "React": [
        "https://reactjs.org/docs/getting-started.html",
        "https://www.youtube.com/playlist?list=PLillGF-RfqbYJVXBgZ_nA7FTAAEpp_IAc",
        "https://scrimba.com/learn/learnreact"
    ],
    "Node.js": [
        "https://nodejs.dev/en/learn/",
        "https://www.youtube.com/playlist?list=PLz5rnvLVJX5U-RHxxK3oNQFAf8RyoYWkM",
        "https://nodesource.com/blog/node-js-at-scale-introduction"
    ],
    "MongoDB": [
        "https://university.mongodb.com/",
        "https://www.youtube.com/playlist?list=PLillGF-RfqbZ2ybcoD2OaabW2P7Ws8CWu",
        "https://www.tutorialspoint.com/mongodb/index.htm"
    ],
    "HTML & CSS": [
        "https://www.freecodecamp.org/learn/responsive-web-design/",
        "https://developer.mozilla.org/en-US/docs/Web/HTML",
        "https://www.youtube.com/playlist?list=PLr6-GrHUlVf9si6B3QasdZ9t3_gCHez4v"
    ],
    "Kubernetes": [
        "https://kubernetes.io/docs/home/",
        "https://www.youtube.com/playlist?list=PLy7NrYWoggjziYQIDorlXjTvvwweTYoNC",
        "https://www.udemy.com/course/learn-kubernetes/"
    ],
    "Linux": [
        "https://linuxjourney.com/",
        "https://www.youtube.com/playlist?list=PLS1QulWo1RIb9WVQGJ_vh-RQusbZgO_As",
        "https://ubuntu.com/tutorials"
    ],
    "Git & GitHub": [
        "https://www.youtube.com/playlist?list=PLg7s6cbtAD17Gw5u8644bgKhgRLiJXdX4",
        "https://www.atlassian.com/git/tutorials",
        "https://docs.github.com/en/get-started/quickstart"
    ],
    "Machine Learning": [
        "https://www.coursera.org/learn/machine-learning",
        "https://www.youtube.com/playlist?list=PLblh5JKOoLUICTaGLRoHQDuF_7q2GfuJF",
        "https://www.kaggle.com/learn/intro-to-machine-learning"
    ],
    "Deep Learning": [
        "https://www.deeplearning.ai/",
        "https://www.youtube.com/playlist?list=PL1w8k37X_6L_h08MB7C41zRYn0q0VZXbW",
        "https://cs231n.github.io/"
    ],
    "Flask": [
        "https://flask.palletsprojects.com/en/2.2.x/",
        "https://www.youtube.com/playlist?list=PL1A2CSdiySGJQKniw4S3q0DhlSNLc7dCX",
        "https://realpython.com/tutorials/flask/"
    ],
    "Django": [
        "https://docs.djangoproject.com/en/stable/",
        "https://www.youtube.com/playlist?list=PLLRM7ROnmA9GdD5m5lY7gkXRpFWtEn9c9",
        "https://www.djangoproject.com/start/"
    ],
    "AWS": [
        "https://aws.amazon.com/training/",
        "https://www.youtube.com/playlist?list=PLB5jA40tNf3tRMmtKpH6DtWqajD_MO0TY",
        "https://aws.amazon.com/getting-started/hands-on/"
    ],
    "Azure": [
        "https://learn.microsoft.com/en-us/training/azure/",
        "https://www.youtube.com/playlist?list=PLLasX02E8BPCNCK6P-2TUTJz3aWo2fRsb",
        "https://www.udemy.com/course/70532-azure/"
    ],
    "Google Cloud": [
        "https://cloud.google.com/training",
        "https://www.youtube.com/playlist?list=PLgxF613RsGoUuKDz2rL_5vNvDLwS7g1Ks",
        "https://www.coursera.org/professional-certificates/cloud-engineering-gcp"
    ],
    "NLP": [
        "https://www.coursera.org/learn/language-processing",
        "https://www.youtube.com/playlist?list=PLZyvi_9gamL-EE3zQJbU5N5z6LbMmhz3m",
        "https://nlp.stanford.edu/IR-book/"
    ],
    "R": [
    "https://www.datacamp.com/courses/free-introduction-to-r",
    "https://www.youtube.com/playlist?list=PLjgj6kdf_snYZt0R8BLZ1sNCz2iJOxW5j",
    "https://cran.r-project.org/manuals.html"
    ],
    "PyTorch": [
    "https://pytorch.org/tutorials/",
    "https://www.udemy.com/course/pytorch-for-deep-learning/",
    "https://www.youtube.com/playlist?list=PLqnslRFeH2UrcDBWF5mfPGpqQDSta6VK4"
    ],
    "Data Structures": [
    "https://www.geeksforgeeks.org/data-structures/",
    "https://www.youtube.com/playlist?list=PLqM7alHXFySGg6GSRmE2UIyD9b8iYmlkS",
    "https://www.coursera.org/specializations/data-structures-algorithms"
    ],
    "System Design": [
    "https://github.com/donnemartin/system-design-primer",
    "https://www.youtube.com/playlist?list=PLTCrU9sGyburBw9wNOHebv9SjlE4Elv5a",
    "https://www.educative.io/courses/grokking-the-system-design-interview"
    ],
    "Algorithms": [
    "https://visualgo.net/en",
    "https://www.youtube.com/playlist?list=PL2_aWCzGMAwLL-mEB4ef20f3iqWMGWa25",
    "https://www.khanacademy.org/computing/computer-science/algorithms"
    ],
    "REST API": [
    "https://restfulapi.net/",
    "https://www.youtube.com/playlist?list=PLzMcBGfZo4-mFu00qxl0a67RhjjZj3jXm",
    "https://www.codecademy.com/learn/learn-api-development"
    ],
    "C++": [
    "https://www.learncpp.com/",
    "https://www.youtube.com/playlist?list=PLfqMhTWNBTe0b2nM6JHVCnAkhQRGiZMSJ",
    "https://www.udemy.com/course/beginning-c-plus-plus-programming/"
    ],
    "OOP": [
    "https://www.youtube.com/playlist?list=PLsyeobzWxl7rG4g-8SEk2kbfCz-79O8Z_",
    "https://www.geeksforgeeks.org/object-oriented-programming-in-cpp/",
    "https://www.freecodecamp.org/news/object-oriented-programming-concepts-21bb035f7260/"
    ],
    "Computer Vision": [
    "https://opencv.org/",
    "https://www.youtube.com/playlist?list=PLKV3nJrKYgGzR8hTqqHeZ2G1RTOk5Ai-B",
    "https://www.udemy.com/course/python-for-computer-vision-with-opencv-and-deep-learning/"
    ],
    "Cloud Computing": [
    "https://www.ibm.com/cloud/learn/cloud-computing",
    "https://www.youtube.com/playlist?list=PL9ooVrP1hQOG33YtVOd9PZzZxzdz9d4kL",
    "https://www.coursera.org/specializations/cloud-computing"
    ],
    "Feature Engineering": [
    "https://www.analyticsvidhya.com/blog/2020/10/what-is-feature-engineering/",
    "https://www.coursera.org/learn/feature-engineering",
    "https://www.youtube.com/playlist?list=PLZoTAELRMXVOk1Hyx1Q4H8uG2o3rNbXhE"
    ],
    "Cloud": [
    "https://aws.amazon.com/what-is-cloud-computing/",
    "https://www.youtube.com/playlist?list=PLWKjhJtqVAblStefaz_YOVpDWqcRScc2s",
    "https://www.udemy.com/course/cloud-computing-fundamentals/"
    ],
    "Data Processing": [
    "https://spark.apache.org/docs/latest/",
    "https://www.youtube.com/playlist?list=PLQVvvaa0QuDeAams7fkdcwOGBpGdHpXln",
    "https://www.udemy.com/course/big-data-processing/"
    ],
    "Scikit Learn": [
    "https://scikit-learn.org/stable/tutorial/index.html",
    "https://www.youtube.com/playlist?list=PLKnIA16_Rmvbr7zKYQuBfsVkjoLcJgxHH",
    "https://www.datacamp.com/courses/supervised-learning-with-scikit-learn"
    ],
    "NoSQL": [
    "https://www.mongodb.com/nosql-explained",
    "https://www.youtube.com/playlist?list=PL0zVEGEvSaeEd9hlmCXrk5yUyqUag-n84",
    "https://www.coursera.org/learn/nosql-databases"
    ],
    "API Development": [
    "https://www.youtube.com/playlist?list=PLS1QulWo1RIb8mVcK4P-vhX6YjC0ZxKiP",
    "https://www.udemy.com/course/the-complete-guide-to-api-development/",
    "https://rapidapi.com/learn"
    ],
    "Microservices": [
    "https://microservices.io/",
    "https://www.youtube.com/playlist?list=PLqq-6Pq4lTTZSKAFG6aCDVDP86Qx4lNas",
    "https://www.udemy.com/course/microservices-architecture-and-implementation-on-dotnet/"
    ],
    "TypeScript": [
    "https://www.typescriptlang.org/docs/",
    "https://www.youtube.com/playlist?list=PLillGF-RfqbaEmlPcX5e_ejaKxjyI1UZU",
    "https://www.udemy.com/course/understanding-typescript/"
    ],
    "Angular": [
    "https://angular.io/docs",
    "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gZD-Tvwfod2gaISzfRiP9d",
    "https://www.udemy.com/course/the-complete-guide-to-angular-2/"
    ],
    "Web Performance": [
    "https://web.dev/learn/performance/",
    "https://www.udemy.com/course/web-performance-optimization/",
    "https://developer.mozilla.org/en-US/docs/Web/Performance"
    ],
    "Redux": [
    "https://redux.js.org/introduction/getting-started",
    "https://www.youtube.com/playlist?list=PL0Zuz27SZ-6M1U0zE4vJmJZ7zO_G5xF07",
    "https://www.udemy.com/course/react-redux/"
    ],
    "UI/UX": [
    "https://www.interaction-design.org/literature/topics/ui-design",
    "https://www.youtube.com/playlist?list=PLn2GH4dN5i2ByvE_qYBHSfsXz1aSzG-tz",
    "https://www.coursera.org/specializations/ui-ux-design"
    ],
    "Vue.js": [
    "https://vuejs.org/guide/introduction.html",
    "https://www.youtube.com/playlist?list=PL4cUxeGkcC9gZD-Tvwfod2gaISzfRiP9d",
    "https://www.udemy.com/course/vuejs-2-the-complete-guide/"
    ],
    "CSS": [
    "https://developer.mozilla.org/en-US/docs/Web/CSS",
    "https://www.youtube.com/playlist?list=PL0Zuz27SZ-6PrE9srvEn8nbhOOyxnWXfp",
    "https://www.freecodecamp.org/learn/responsive-web-design/"
    ],
    "Express.js": [
    "https://expressjs.com/en/starter/installing.html",
    "https://www.youtube.com/playlist?list=PL4cUxeGkcC9jsz4LDYc6kv3ymONOKxwBU",
    "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/"
    ],
    "Terraform": [
    "https://developer.hashicorp.com/terraform/intro",
    "https://www.youtube.com/playlist?list=PLqq-6Pq4lTTanfgsbnFzfWUhhAz3tIezU",
    "https://www.udemy.com/course/learn-devops-infrastructure-automation-with-terraform/"
    ],
    "CI/CD": [
    "https://www.redhat.com/en/topics/devops/what-is-ci-cd",
    "https://www.youtube.com/playlist?list=PL34sAs7_26wNBRWM6BDhnonoA5FMERax0",
    "https://www.udemy.com/course/devops-ci-cd-with-jenkins-ansible-docker-kubernetes/"
    ],
    "Security": [
    "https://www.coursera.org/specializations/it-security",
    "https://www.youtube.com/playlist?list=PLBf0hzazHTGOEuhPQSnq-EjzUUjZG0u8M",
    "https://owasp.org/"
    ],
    "Networking": [
    "https://www.geeksforgeeks.org/computer-network-tutorials/",
    "https://www.youtube.com/playlist?list=PLWKjhJtqVAbleDe3_ZA8h3AO2rXar-q2V",
    "https://www.udemy.com/course/comptia-network-certification-n10-007-the-total-course/"
    ],
    "DevOps": [
    "https://www.atlassian.com/devops",
    "https://www.youtube.com/playlist?list=PL9ooVrP1hQOGvNnJc_wRA5nQtbkyV0p-j",
    "https://www.udemy.com/course/devops-practices-and-tools/"
    ],
    "Jenkins": [
    "https://www.jenkins.io/doc/",
    "https://www.youtube.com/playlist?list=PL6flErFppaj0Iu-uAYk8dRT2cWvZs0zJL",
    "https://www.udemy.com/course/jenkins-from-zero-to-hero/"
    ],
    "Monitoring": [
    "https://www.datadoghq.com/solutions/infrastructure-monitoring/",
    "https://www.youtube.com/playlist?list=PL34sAs7_26wPkwFzH0hLFxfEX2elv1fX6",
    "https://www.udemy.com/course/prometheus-monitoring/"
    ],
    "Bash": [
    "https://ryanstutorials.net/bash-scripting-tutorial/",
    "https://www.youtube.com/playlist?list=PLS1QulWo1RIaRoN4vQQCYHWDuubEU7fU4",
    "https://www.udemy.com/course/linux-shell-scripting-projects/"
    ],
    "Compliance": [
    "https://www.coursera.org/learn/compliance-frameworks",
    "https://www.youtube.com/playlist?list=PLx-q4INfd95FxPtJZok-JV-i3kWnWJ_F0",
    "https://www.sans.org/"
    ],
    "Cryptography": [
    "https://www.khanacademy.org/computing/computer-science/cryptography",
    "https://www.youtube.com/playlist?list=PLoROMvodv4rNiJRchCzutFw5ItR_Z27CM",
    "https://www.udemy.com/course/cryptography-theory-and-practice/"
    ],
    "Risk Analysis": [
    "https://www.coursera.org/learn/risk-analysis",
    "https://www.youtube.com/playlist?list=PLzK8YH_kkUXUvML8lQfd4ffMYE3UgY5Un",
    "https://www.udemy.com/course/financial-risk-management/"
    ],
    "SIEM": [
    "https://www.splunk.com/en_us/solutions/solution-areas/siem.html",
    "https://www.youtube.com/playlist?list=PLoZ4XnVFo5vgaC96sNE6Im9j9-7s1q6Id",
    "https://www.udemy.com/course/introduction-to-siem/"
    ],
    "Ethical Hacking": [
    "https://www.eccouncil.org/ethical-hacking/",
    "https://www.youtube.com/playlist?list=PLBf0hzazHTGNR3rGoIf8HqQY0u8t84bHN",
    "https://www.udemy.com/course/learn-ethical-hacking-from-scratch/"
    ],
    "IDS/IPS": [
    "https://www.imperva.com/learn/application-security/intrusion-detection-prevention-systems-idps/",
    "https://www.youtube.com/playlist?list=PLJbE2Yu2zumAKyUshbxzLgG3vpYCRjzME",
    "https://www.udemy.com/course/intrusion-detection-and-prevention-systems/"
    ],
    "Penetration Testing": [
    "https://www.kali.org/",
    "https://www.youtube.com/playlist?list=PLBf0hzazHTGNR3rGoIf8HqQY0u8t84bHN",
    "https://www.udemy.com/course/practical-ethical-hacking/"
    ],
    "Network Security": [
    "https://www.geeksforgeeks.org/network-security/",
    "https://www.youtube.com/playlist?list=PL7BRSnZGzG6a_JFMRxSffdw7Hj2q1wLSK",
    "https://www.udemy.com/course/network-security/"
    ],
    "MySQL": [
    "https://www.mysqltutorial.org/",
    "https://www.youtube.com/playlist?list=PL8dDSKArO2-n8A8FwqNGRmtDbUckQYhID",
    "https://www.udemy.com/course/sql-mysql/"
    ],
    "Indexing": [
    "https://www.geeksforgeeks.org/sql-indexes/",
    "https://use-the-index-luke.com/",
    "https://www.youtube.com/watch?v=HGuBgdMxJjA"
    ],
    "PostgreSQL": [
    "https://www.postgresql.org/docs/",
    "https://www.youtube.com/playlist?list=PLS1QulWo1RIYmaxcEqw5JhK3b-6rgdWO_",
    "https://www.udemy.com/course/sql-and-postgresql/"
    ],
    "Query Optimisation": [
    "https://learnsql.com/blog/sql-query-optimization/",
    "https://use-the-index-luke.com/",
    "https://www.udemy.com/course/query-optimization/"
    ],
    "Database Optimization": [
    "https://www.geeksforgeeks.org/sql-query-optimization-tips-tricks/",
    "https://www.youtube.com/watch?v=LyVHzsKjYP8",
    "https://www.udemy.com/course/database-performance-tuning/"
    ],
    "Backup and Recovery": [
    "https://www.oracle.com/database/technologies/backup-recovery.html",
    "https://www.youtube.com/playlist?list=PLsyeobzWxl7r3ZlbGJ8aXCp1p4YdC40jw",
    "https://www.udemy.com/course/database-backup-recovery/"
    ]
    
    
    # Extend this mapping as needed
}

def get_static_learning_resources(skill_gap_list):
    """
    For each missing skill in skill_gap_list, return the list of static learning resources.
    """
    resources = {}
    for skill in skill_gap_list:
        resources[skill] = static_skill_resources.get(skill, ["No static resources found."])
    return resources

# ---------------------------
# Flask Routes
# ---------------------------
@app.route("/")
def index():
    roles = jd_df["role"].dropna().unique().tolist()
    return render_template("index.html", roles=roles)

@app.route("/upload", methods=["POST"])
def upload():
    try:
        resume_file = request.files.get("resume")
        jd_file = request.files.get("jd")
        selected_role = request.form.get("role")

        if not resume_file or resume_file.filename == "":
            return jsonify({"message": "Resume is required!"}), 400

        # Save and parse resume
        resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
        resume_file.save(resume_path)
        resume_text = parse_resume(resume_path)
        resume_details = extract_details(resume_text)
        print_structured_details(resume_details)
        resume_skills = extract_all_skills(resume_text)

        # Case 1: JD file is uploaded
        if jd_file and jd_file.filename != "":
            jd_path = os.path.join(app.config["UPLOAD_FOLDER"], jd_file.filename)
            jd_file.save(jd_path)
            jd_text = parse_resume(jd_path)
            jd_skills = extract_all_skills(jd_text)
        # Case 2: JD not uploaded, use selected role
        elif selected_role:
            jd_row = jd_df[jd_df['role'].str.lower() == selected_role.lower()]
            if jd_row.empty:
                return jsonify({"message": f"No JD found for selected role: {selected_role}"}), 400

            jd_text = jd_row['skills'].values[0]
            if not isinstance(jd_text, str) or not jd_text.strip():
                return jsonify({"message": f"No skills found for selected role: {selected_role}"}), 400

            jd_skills = [skill.strip() for skill in jd_text.split(',') if skill.strip()]
        else:
            return jsonify({"message": "Either JD file or job role selection is required!"}), 400

        missing_skills = find_skill_gap(jd_skills, resume_skills)
        recommended_jobs = recommend_jobs(resume_text)
        learning_resources = get_static_learning_resources(missing_skills)

        print("\n=== Static Learning Resources ===")
        for skill, links in learning_resources.items():
            print(f"\nSkill: {skill}")
            for link in links:
                print(f"  - {link}")


        return jsonify({
            "message": "Upload successful!",
            "resume_content": resume_text,
            "jd_content": jd_text,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "missing_skills": missing_skills,
            "recommended_jobs": recommended_jobs,
            "learning_resources": learning_resources,
            "resume_details": resume_details
        })

    except Exception as e:
        traceback.print_exc()  # Print detailed traceback in console
        return jsonify({"message": "Error processing the files", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
