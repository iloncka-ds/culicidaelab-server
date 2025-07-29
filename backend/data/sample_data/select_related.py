import json
from backend.data.sample_data.species import species_list
from backend.data.sample_data.diseases import diseases_data_list

related_diseases = []
for s in species_list:
    related_diseases.extend(s["related_diseases"])

with open("related_diseases.json", "w", encoding="utf-8") as f:
    json.dump(list(set(related_diseases)), f, indent=2, ensure_ascii=False)
print("Generated related_diseases.json")

vectors = []
for d in diseases_data_list:
    vectors.extend(d["vectors"])

with open("vectors.json", "w", encoding="utf-8") as f:
    json.dump(list(set(vectors)), f, indent=2, ensure_ascii=False)
print("Generated vectors.json")
