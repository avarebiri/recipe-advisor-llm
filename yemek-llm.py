import streamlit as st
import json
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

@st.cache_data
def load_data():
    with open("3000_yemek_tarifleri.json", "r", encoding="utf-8") as f:
        return json.load(f)

data = load_data()

def clean_ingredient(raw):
    tokens = raw.strip().lower().split()
    return tokens[-1] if tokens else ""

# --- VERI HAZIRLAMA ---
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

@st.cache_data
def train_model():
    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("clf", MultinomialNB())
    ])
    pipeline.fit(df["ingredients"], df["title"])
    return pipeline

model = train_model()
joblib.dump(model, "tarif_model.pkl")

st.title("Tarif Önerici")
query = st.text_input("Elindeki malzemeleri yaz (virgülle ayır):")

if st.button("Öneri Al") and query:
    input_text = query.lower()
    predicted = model.predict([input_text])[0]

    # Eşleşen tarifin detayını bul
    match = next((item for item in data if item.get("title") == predicted), None)
    if match:
        st.subheader(match.get("title", "[isimsiz tarif]"))
        st.markdown(f"**Malzemeler:** {match.get('ingredients', '')}")
        st.markdown(f"**Yapılış:** {match.get('instructions', '')}")
    else:
        st.info(f"Tahmin edilen tarif: {predicted}, ancak detaylar bulunamadı.")

