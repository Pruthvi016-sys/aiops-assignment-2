import joblib
import pandas as pd
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

df = pd.read_csv("spam_dataset.csv")

pipeline = Pipeline([
    ("tfidf", TfidfVectorizer()),
    ("clf", MultinomialNB()),
])
pipeline.fit(df["text"], df["label"])

joblib.dump(pipeline, "model.joblib")
print("Saved model.joblib")