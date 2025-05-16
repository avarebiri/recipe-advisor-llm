import json
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

with open("recipe.json", "r", encoding="utf-8") as f:
    data = json.load(f)

model = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    item["ingredients"] + " " + item["instructions"]
    for item in data
    if "ingredients" in item and "instructions" in item
]
embeddings = model.encode(texts, convert_to_numpy=True)

faiss.normalize_L2(embeddings)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings)

def search_recipe(query_text, k=3):
    query_vec = model.encode([query_text], convert_to_numpy=True)
    faiss.normalize_L2(query_vec)
    D, I = index.search(query_vec, k)
    return [data[i] for i in I[0]]

results = search_recipe("yoğurt, salatalık, sarımsak")
for i, r in enumerate(results, 1):
    print(f"{i}. Tarif: {r['name']}\n{r['instructions']}\n{'-'*60}")
