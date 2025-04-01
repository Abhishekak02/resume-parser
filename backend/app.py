from flask import Flask, request, jsonify, render_template
import os
from parser import parse_resume  
from recommendation import recommend_jobs
from skill_extraction import extract_all_skills  

app = Flask(__name__, template_folder="templates")

def extract_text_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as file:
        return file.read()

# Function to find missing skills
def find_skill_gap(jd_skills, resume_skills):
    return list(set(jd_skills) - set(resume_skills))  # JD skills - Resume skills

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "resume" not in request.files or "jd" not in request.files:
        return jsonify({"message": "Both resume and JD files are required!"}), 400

    resume_file = request.files["resume"]
    jd_file = request.files["jd"]

    if resume_file.filename == "" or jd_file.filename == "":
        return jsonify({"message": "Both files must be selected!"}), 400

    # Save files
    resume_path = os.path.join(app.config["UPLOAD_FOLDER"], resume_file.filename)
    jd_path = os.path.join(app.config["UPLOAD_FOLDER"], jd_file.filename)
    resume_file.save(resume_path)
    jd_file.save(jd_path)

    try:
        # Extract text
        resume_text = parse_resume(resume_path)
        jd_text = parse_resume(jd_path) if jd_path.endswith(".pdf") else extract_text_from_txt(jd_path)

        if not resume_text.strip() or not jd_text.strip():
            return jsonify({"message": "Could not extract content from one or both files."}), 400

        # Extract skills
        resume_skills = extract_all_skills(resume_text)
        jd_skills = extract_all_skills(jd_text)

        # Skill gap analysis
        missing_skills = find_skill_gap(jd_skills, resume_skills)

        # Job recommendations
        recommended_jobs = recommend_jobs(resume_text)

        return jsonify({
            "message": "Upload successful!",
            "resume_content": resume_text,
            "jd_content": jd_text,
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "missing_skills": missing_skills,
            "recommended_jobs": recommended_jobs
        })
    except Exception as e:
        return jsonify({"message": "Error processing the files", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)