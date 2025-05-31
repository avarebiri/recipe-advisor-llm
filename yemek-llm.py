import streamlit as st
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib

@st.cache_data
def load_data():
    with open("3000_yemek_tarifleri.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

def clean_ingredient(raw):
    tokens = raw.strip().lower().split()
    return tokens[-1] if tokens else ""

@st.cache_data
def prepare_dataset():
    rows = []
    for item in data:
        ingredients = item.get("ingredients", [])
        title = item.get("title", "")
        if isinstance(ingredients, list) and title:
            cleaned = [clean_ingredient(ing) for ing in ingredients]
            joined = " ".join(cleaned)
            rows.append((joined, title))
    return pd.DataFrame(rows, columns=["ingredients", "title"])

df = prepare_dataset()

@st.cache_resource
def train_model():
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", MultinomialNB())
    ])
    pipeline.fit(df["ingredients"], df["title"])
    return pipeline

model = train_model()

st.title("Makine Öğrenmesiyle Tarif Tahmin")
query = st.text_input("Elindeki malzemeleri yaz (virgülle ayır):")

if st.button("Tahmin Et"):
    if not query.strip():
        st.error("Lütfen en az bir malzeme giriniz.")
    else:
        input_text = " ".join([clean_ingredient(token) for token in query.split(",") if token.strip()])
        try:
            proba = model.predict_proba([input_text])[0]
            top_indices = proba.argsort()[-3:][::-1]
            top_predictions = [(model.classes_[i], proba[i]) for i in top_indices if proba[i] >= 0.0012]
        except Exception:
            top_predictions = []
        
        if top_predictions:
            for title, score in top_predictions:
                match = next((item for item in data if item.get("title") == title), None)
                if match:
                    st.subheader(match.get("title", "[isimsiz tarif]"))
                    st.markdown(f"**Malzemeler:** {match.get('ingredients', '')}")
                    st.markdown(f"**Yapılış:** {match.get('instructions', '')}")
                    st.markdown("---")
        else:
            st.error("Uygun tarif bulunamadı. Lütfen farklı malzemeler deneyin.")
