import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

jobs_df = pd.read_csv("jobs.csv")

def recommend_jobs(text):
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(jobs_df["Description"])
    
    user_vector = tfidf.transform([text])
    similarity = cosine_similarity(user_vector, tfidf_matrix)
    
    top_jobs = similarity.argsort()[0][-3:][::-1]
    return jobs_df.iloc[top_jobs]["Title"].tolist()
