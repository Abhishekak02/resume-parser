import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
import joblib

# Dataset
data = {'Text': ['Python Developer', 'Data Scientist', 'Web Developer', 'Java Developer', 'AI Engineer'],
        'Category': ['Data Science', 'Data Science', 'Web Development', 'Web Development', 'AI']}
df = pd.DataFrame(data)

# Text Vectorization
vectorizer = CountVectorizer()
X = vectorizer.fit_transform(df['Text'])
y = df['Category']

# Train Model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = LogisticRegression()
model.fit(X_train, y_train)

# Save Model
joblib.dump(model, 'resume_classifier.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
print("Model Trained and Saved Successfully!")
