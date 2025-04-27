from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

categories = ['Data Science', 'Web Development', 'Marketing', 'HR']

# Load Pre-trained Model
model = joblib.load("resume_classifier.pkl")
vectorizer = joblib.load("vectorizer.pkl")

def classify_resume(text):
    X = vectorizer.transform([text])
    category = model.predict(X)[0]
    return categories[category]
