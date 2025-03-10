# from flask import Flask, request, jsonify, render_template
# import os
# from parser import parse_resume  # Import parse_resume function

# app = Flask(__name__)

# # Ensure uploads folder exists
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# @app.route("/")
# def index():
#     return render_template("index.html")  # Serve frontend

# @app.route("/upload", methods=["POST"])
# def upload():
#     if "file" not in request.files:
#         return jsonify({"message": "No file part"}), 400

#     file = request.files["file"]

#     if file.filename == "":
#         return jsonify({"message": "No selected file"}), 400

#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(file_path)  # Save file to uploads folder

#     # Parse the resume
#     parsed_content = parse_resume(file_path)

#     return render_template("result.html", content=parsed_content)  # Show parsed text

# if __name__ == "__main__":
#     app.run(debug=True)

# from fastapi import FastAPI, UploadFile, File, Request
# from fastapi.responses import HTMLResponse
# import pdfplumber
# import io
# import textwrap
# import nltk
# from nltk.tokenize import word_tokenize, sent_tokenize
# from jinja2 import Template
# import os

# # Google Drive API Imports
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload



# from flask import Flask, request, jsonify, render_template
# import os
# from parser import parse_resume

# app = Flask(__name__, template_folder="templates")

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# @app.route("/")
# def index():
#     return render_template("index.html")  # Serve the frontend

# @app.route("/upload", methods=["POST"])
# def upload():
#     print("📥 File upload request received!")  # Debugging

#     if "file" not in request.files:
#         print("❌ No file part in request.")  # Debugging
#         return jsonify({"message": "No file part"}), 400

#     file = request.files["file"]
#     print(f"📂 Received file: {file.filename}")  # Debugging

#     if file.filename == "":
#         print("❌ No selected file.")  # Debugging
#         return jsonify({"message": "No selected file"}), 400

#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(file_path)  # Save file to uploads folder
#     print(f"✅ File saved at: {file_path}")  # Debugging

#     # Parse the resume
#     parsed_content = parse_resume(file_path)
#     print(f"📜 Parsed content: {parsed_content[:100]}")  # Debugging, prints first 100 chars

#     return render_template("result.html", content=parsed_content)  # Show parsed text

# if __name__ == "__main__":
#     app.run(debug=True)







# from flask import Flask, request, jsonify, render_template
# import os
# from parser import parse_resume

# app = Flask(__name__, template_folder="templates")

# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)
# app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/upload", methods=["POST"])
# def upload():
#     if "file" not in request.files:
#         return jsonify({"message": "No file part"}), 400

#     file = request.files["file"]
#     if file.filename == "":
#         return jsonify({"message": "No selected file"}), 400

#     file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
#     file.save(file_path)

#     # Parse the resume using parser.py
#     parsed_content = parse_resume(file_path)

#     return render_template("result.html", content=parsed_content)

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify, render_template
import os
from parser import parse_resume  # Ensure parser.py exists

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"message": "No file part"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"message": "No selected file"}), 400

    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)

    try:
        # Parse the resume text
        parsed_content = parse_resume(file_path)

        return jsonify({"message": "Upload successful!", "content": parsed_content})
    
    except Exception as e:
        return jsonify({"message": "Error processing the file", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
