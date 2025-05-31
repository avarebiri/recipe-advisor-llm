import streamlit as st
import json
import os

# --- Load recipe data safely ---
@st.cache_data
def load_data():
    try:
        file_path = "3000_yemek_tarifleri.json"
        if not os.path.exists(file_path):
            st.error("❌ Tarif dosyası bulunamadı!")
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"🚨 Dosya okunurken hata oluştu: {e}")
        return []

data = load_data()
if not data:
    st.stop()

# --- Extract all valid food word tokens ---
def get_food_word_tokens(data):
    food_words = set()
    for item in data:
        ingredients = item.get("ingredients", [])
        if not isinstance(ingredients, list):
            continue
        for ing in ingredients:
            tokens = ing.lower().replace(",", "").replace(".", "").split()
            food_words.update(tokens)
    return food_words

valid_food_words = get_food_word_tokens(data)

# --- Best match finder (exact token overlap) ---
def find_best_matching_recipe(user_ingredients, data):
    best_match = None
    best_score = 0
    best_length = float("inf")

    for item in data:
        ingredients = item.get("ingredients", [])
        if not isinstance(ingredients, list):
            continue

        all_tokens = set()
        for ing in ingredients:
            tokens = ing.lower().replace(",", "").replace(".", "").split()
            all_tokens.update(tokens)

        score = sum(1 for ing in user_ingredients if ing in all_tokens)

        if score > best_score or (score == best_score and len(ingredients) < best_length):
            best_score = score
            best_length = len(ingredients)
            best_match = item

    return best_match

# --- Streamlit UI ---
st.title("Tarif Önerici")
query = st.text_input("Elindeki malzemeleri yaz (virgülle ayır):")

if st.button("Öneri Al"):
    if not query.strip():
        st.warning("⚠️ Lütfen en az bir malzeme giriniz.")
    else:
        input_ingredients = [i.strip().lower() for i in query.split(",") if i.strip()]
        invalids = [i for i in input_ingredients if i not in valid_food_words]

        if invalids:
            st.error(f"❌ Geçersiz malzeme(ler): {', '.join(invalids)}. Lütfen geçerli malzemeler giriniz.")
        else:
            best_recipe = find_best_matching_recipe(input_ingredients, data)
            if best_recipe:
                st.subheader(best_recipe.get("title", "[isimsiz tarif]").capitalize())
                st.markdown(f"**Malzemeler:** {best_recipe.get('ingredients', '')}")
                st.markdown(f"**Yapılış:** {best_recipe.get('instructions', '')}")
            else:
                st.warning("Uygun tarif bulunamadı.")
