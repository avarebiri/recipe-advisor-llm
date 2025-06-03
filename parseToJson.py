import re
import json

# Read from file
with open("./extracted_text.txt", 'r', encoding='utf-8') as file:
    raw_data = file.read()

# Clean up and normalize line endings
raw_data = raw_data.replace('\r\n', '\n').strip()

# Split into raw recipe blocks
raw_recipes = re.split(r'\n(?=\w[\w\sçğıöşüİĞÖŞÜÇ]+\s+-\s+\d+)', raw_data)

recipes = []

for recipe_text in raw_recipes:
    title_match = re.match(r'([\w\sçğıöşüİĞÖŞÜÇ]+)\s+-\s+(\d+)', recipe_text)
    if not title_match:
        continue

    title = title_match.group(1).strip()
    recipe_id = int(title_match.group(2).strip())

    cuisine_match = re.search(r'Mutfak:\s*(.*)', recipe_text)
    duration_match = re.search(r'Süre:\s*(.*)', recipe_text)
    ingredients_match = re.search(r'MALZEMELER(.*?)YAPILIŞ TARİFİ', recipe_text, re.DOTALL)
    instructions_match = re.search(r'YAPILIŞ TARİFİ(.*)', recipe_text, re.DOTALL)

    ingredients = (
        [line.strip() for line in ingredients_match.group(1).strip().split('\n') if line.strip()]
        if ingredients_match else None
    )

    recipes.append({
        "title": title,
        "id": recipe_id,
        "cuisine": cuisine_match.group(1).strip() if cuisine_match else None,
        "duration": duration_match.group(1).strip() if duration_match else None,
        "ingredients": ingredients,
        "instructions": instructions_match.group(1).strip() if instructions_match else None
    })

# Save to JSON
with open("recipes.json", "w", encoding="utf-8") as f:
    json.dump(recipes, f, ensure_ascii=False, indent=2)
