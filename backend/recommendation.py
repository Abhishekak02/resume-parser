import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

jobs_df = pd.read_csv("jobs.csv")

# ✅ Fix column name (Use "Category" instead of "Description")
correct_col = "Category"

def recommend_jobs(text):
    try:
        # print("Received Text for Recommendation:", text)  # Debug

        tfidf = TfidfVectorizer()
        tfidf_matrix = tfidf.fit_transform(jobs_df[correct_col])  

        user_vector = tfidf.transform([text])
        similarity = cosine_similarity(user_vector, tfidf_matrix)

        top_jobs = similarity.argsort()[0][-3:][::-1]
        recommended = jobs_df.iloc[top_jobs]["Job Role"].tolist()

        # print("Recommended Jobs:", recommended)  # Debug Print
        return recommended
    
    except Exception as e:
        print("Error in recommend_jobs:", str(e))
        return []
