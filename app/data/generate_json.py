import os
import json

BASE_DIR = "family_photos"
OUTPUT_FILE = "families.json"

families = []

for family_id in os.listdir(BASE_DIR):
    family_path = os.path.join(BASE_DIR, family_id)
    if not os.path.isdir(family_path):
        continue

    members = []
    for file in os.listdir(family_path):
        if file.lower().endswith((".jpg", ".jpeg", ".png")):
            members.append({
                "name": os.path.splitext(file)[0],
                "photo": f"{family_path}/{file}",
                "sospechoso": "_sospechoso" in file.lower()
            })

    families.append({
        "id": family_id,
        "display_name": f"Familia {family_id.capitalize()}",
        "members": members
    })

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"families": families}, f, indent=2, ensure_ascii=False)

print(f"JSON generado: {OUTPUT_FILE}")
