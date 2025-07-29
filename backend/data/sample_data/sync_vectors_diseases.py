"""
Syncs the relationship between mosquito species and the diseases they can transmit.
Ensures bidirectional consistency between species.related_diseases and disease.vectors.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Any

# Import the data
from backend.data.sample_data.species import species_list
from backend.data.sample_data.diseases import diseases_data_list


def sync_vectors_diseases() -> None:
    """
    Ensure bidirectional consistency between species.related_diseases and disease.vectors.
    Updates both lists to include all necessary references without duplicates.
    """
    # Convert lists to dicts for easier access
    species_dict: Dict[str, Dict[str, Any]] = {s["id"]: s for s in species_list}
    diseases_dict: Dict[str, Dict[str, Any]] = {d["id"]: d for d in diseases_data_list}

    # Track changes for logging
    changes_made = False

    # First pass: Ensure all diseases in species.related_diseases have the species in their vectors
    for species_id, species in species_dict.items():
        if "related_diseases" not in species:
            species["related_diseases"] = []

        for disease_id in species["related_diseases"]:
            if disease_id not in diseases_dict:
                print(f"Warning: Disease '{disease_id}' in {species_id}.related_diseases not found in diseases list")
                continue

            disease = diseases_dict[disease_id]
            if "vectors" not in disease:
                disease["vectors"] = []

            if species_id not in disease["vectors"]:
                disease["vectors"].append(species_id)
                changes_made = True
                print(f"Added {species_id} to {disease_id}.vectors")

    # Second pass: Ensure all species in disease.vectors have the disease in their related_diseases
    for disease_id, disease in diseases_dict.items():
        if "vectors" not in disease:
            disease["vectors"] = []

        for species_id in disease["vectors"]:
            if species_id not in species_dict:
                print(f"Warning: Species '{species_id}' in {disease_id}.vectors not found in species list")
                continue

            species = species_dict[species_id]
            if "related_diseases" not in species:
                species["related_diseases"] = []

            if disease_id not in species["related_diseases"]:
                species["related_diseases"].append(disease_id)
                changes_made = True
                print(f"Added {disease_id} to {species_id}.related_diseases")

    if not changes_made:
        print("No changes were needed. Data is already consistent.")
    else:
        # Save the updated data back to their respective modules
        species_path = Path(__file__).parent / "species_fixed.py"
        diseases_path = Path(__file__).parent / "diseases_fixed.py"

        # Generate the new species.py content
        species_content = f"species_list = {json.dumps(species_list, indent=4, ensure_ascii=False)}\n"
        diseases_content = f"diseases_data_list = {json.dumps(diseases_data_list, indent=4, ensure_ascii=False)}\n"

        # Write the updated files
        species_path.write_text(species_content, encoding="utf-8")
        diseases_path.write_text(diseases_content, encoding="utf-8")

        print("\nUpdated files have been saved.")
        print(f"- {species_path}")
        print(f"- {diseases_path}")
        print("\nPlease review the changes before committing them to version control.")


if __name__ == "__main__":
    sync_vectors_diseases()
