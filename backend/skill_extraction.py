import spacy  # NLP Model
from keybert import KeyBERT  # Keyword Extraction
import re

# Load spaCy Model
nlp = spacy.load("en_core_web_sm")
kw_model = KeyBERT()

# ✅ Predefined List of Data Analyst Skills
skill_list = [
 "Python", "Java", "JavaScript", "C", "C++", "C#", "Swift", "Kotlin", "PHP", "Ruby", "TypeScript", "R", "Go",
    "Rust", "Dart", "SQL", "HTML", "CSS", "Shell Scripting", "Bash", "MySQL", "PostgreSQL", "SQLite", 
    "Microsoft SQL Server", "MongoDB", "Firebase", "Cassandra", "Oracle Database", "Redis", "Apache Hive", 
    "Apache HBase", "CouchDB", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "Keras", "PyTorch", "OpenCV", 
    "Natural Language Processing", "Transformers", "Computer Vision", "Generative AI", "Reinforcement Learning", 
    "Deep Learning", "Neural Networks", "XGBoost", "LightGBM", "Random Forest", "AutoML", "Apache Spark", 
    "Apache Hadoop", "Airflow", "Kafka", "Data Warehousing", "ETL Pipelines", "BigQuery", "AWS Glue", "Snowflake",
    "Azure Synapse Analytics", "React.js", "Angular", "Vue.js", "Next.js", "Express.js", "Django", "Flask", 
    "Spring Boot", "Node.js", "GraphQL", "RESTful APIs", "WebSockets", "WebAssembly", "Tailwind CSS", "Bootstrap", 
    "Docker", "Kubernetes", "CI/CD", "Terraform", "Ansible", "AWS", "Azure", "Google Cloud Platform", "OpenShift",
    "Cloud Security", "Network Security", "Penetration Testing", "OWASP", "Burp Suite", "Metasploit", "Kali Linux",
    "Reverse Engineering", "Cryptography", "Web Security", "SIEM", "Data Structures & Algorithms", "OOP","OOPS"
    "Design Patterns", "SOLID Principles", "Microservices Architecture", "Distributed Systems", "Parallel Computing",
    "Event-Driven Architecture", "Solidity", "Smart Contracts", "Ethereum", "Hyperledger", "IPFS", "DeFi", "NFT",
    "Unity", "Unreal Engine", "Cocos2D", "Blender", "Three.js", "ARKit", "ARCore", "Oculus", "OpenXR", "Selenium",
    "Cypress", "JUnit", "TestNG", "Jest", "PyTest", "JMeter", "Postman", "Linux System Administration",
    "Windows Server Management", "Networking Protocols", "Firewall Configuration", "Virtualization", "Nagios",
    "Zabbix", "Apache Flink", "Hadoop", "Spark Streaming", "Elasticsearch", "Kibana", "Tableau", "Power BI", "Looker",
    "Google Analytics", "Agile", "Scrum", "Kanban", "Design Thinking", "UX/UI Design", "Technical Writing", 
    "Code Reviews", "Pair Programming", "Public Speaking", "Time Management","Excel", "Git", "GitHub", "Data Cleaning", 
    "Dashboard Creation", "VLOOKUP", "XLOOKUP", "Pivot Tables" ,"Linux" 
]

# ✅ Step 1: Extract Skills using Predefined List (Fast & Accurate)
def extract_skills(text, skills):
    extracted_skills = [skill for skill in skills if re.search(rf"\b{re.escape(skill)}\b", text, re.IGNORECASE)]
    return list(set(extracted_skills))  # Remove duplicates

# ✅ Step 2: Extract Skills Using NLP (spaCy) - Only Extract Relevant Terms
def extract_skills_with_ner(text):
    doc = nlp(text)
    skills = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT"]]
    # Only return skills that match predefined skills (avoid noise)
    return [skill for skill in skills if skill in skill_list]

# ✅ Step 3: Extract Skills Using KeyBERT (Keyword Extraction)
def extract_keywords(text):
    keywords = kw_model.extract_keywords(text, keyphrase_ngram_range=(1, 2), stop_words="english", top_n=10)
    return [kw[0] for kw in keywords if kw[0] in skill_list]  # Filter only known skills

# ✅ Step 4: Merge & Normalize Skills from All Methods
def extract_all_skills(text):
    # Extract skills using different methods
    matched_skills = extract_skills(text, skill_list)
    ner_skills = extract_skills_with_ner(text)
    keyword_skills = extract_keywords(text)

    # Combine all extracted skills
    all_skills = sorted(set(matched_skills + ner_skills + keyword_skills))
    return all_skills