import re
import request

API_KEY = "YOURAPIKEY"  
MODEL = "dbmdz/bert-large-cased-finetuned-conll03-english" 
API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}


VALID_SKILLS = {"Python", "SQL", "Excel", "Power BI", "Github", "Git", "MySQL", "TensorFlow", 
                "Pandas", "NumPy", "Scikit-Learn", "Machine Learning", "Deep Learning",
                "Tableau", "Data Science", "AI", "Big Data", "Cloud Computing", "DBMS", "Java", "C", "C++", "C#",
                "OOPS", "Keras", "Seaborn", "Matplotlib", "Cybersecurity", "Linux"}  

def clean_skill(skill):
    """Cleans and normalizes skill names by removing extra spaces and fixing case issues."""

    # Remove extra spaces from start and end
    skill = skill.strip()

    # Remove unwanted characters (only keep letters, numbers, +, #, ., -)
    skill = re.sub(r"[^a-zA-Z0-9#+.-]", " ", skill)

    # Remove multiple spaces and trim again
    skill = re.sub(r"\s+", " ", skill).strip()

    # Convert to lowercase for comparison
    skill_lower = skill.lower()

    # Check if the cleaned skill exists in VALID_SKILLS (ignoring case)
    for valid_skill in VALID_SKILLS:
        if valid_skill.lower() == skill_lower:
            return valid_skill  # Return skill with correct formatting

    return ""  # Return empty string if the skill is not valid


def extract_skills(text):
    """Extracts skills dynamically using NLP + Regex (No Predefined Skills)."""
    
    # ✅ Step 1: Call Hugging Face API (NER Model)
    response = requests.post(API_URL, headers=HEADERS, json={"inputs": text})
    
    # ✅ Handle API errors
    if response.status_code != 200:
        return f"API Error: {response.json()}"
    
    data = response.json()
    
    try:
        words = []
        current_word = ""
        last_entity = None  # Track previous entity

        # ✅ Step 2: Extract Words from API Response
        for entity in data:
            word = entity["word"]
            entity_type = entity["entity_group"]  # Get entity type

            # ✅ Only process relevant categories (MISC + ORG)
            if entity_type not in {"MISC"}:
                continue  # Skip irrelevant entities

            # ✅ Merge subword tokens correctly
            if word.startswith("##"):
                current_word += word[2:]  # Remove "##" and merge
            else:
                if current_word:
                    words.append(current_word.strip())  # Save previous merged word
                current_word = word.strip()  # Start new word

            last_entity = entity_type  # Track last entity type

        if current_word:
            words.append(current_word)  # Append last word

        # ✅ Step 3: Clean and Filter Extracted Words
        cleaned_skills = set(clean_skill(word) for word in words if clean_skill(word))

        # ✅ Step 4: Validate Skills (Keep only known valid skills)
        final_skills = [skill for skill in cleaned_skills if skill in VALID_SKILLS]

        return final_skills  # Return unique, validated skills
    
    except Exception as e:
        return f"Error while extracting skills: {str(e)}"


# 🔥 Test with sample text
# text = "I have experience in Python, SQL, Excel, Power BI, and Machine Learning."
# skills = extract_skills(text)
# print("Extracted Skills:", skills)
