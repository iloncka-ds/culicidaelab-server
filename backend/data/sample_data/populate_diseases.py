import sys
import os
import json
import pandas as pd
import lancedb
import argparse
from pathlib import Path

# Add the parent directory to sys.path to import backend modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.services.database import get_db_connection


def create_disease_table(db_conn: lancedb.DBConnection):
    """Create the diseases table in LanceDB."""

    # Define the disease data
    diseases = [
        {
            'id': '1',
            'name': 'Dengue Fever',
            'description': 'Viral infection causing high fever, severe headache, and joint/muscle pain.',
            'symptoms': 'High fever, severe headache, pain behind the eyes, joint and muscle pain, rash, mild bleeding',
            'treatment': 'No specific treatment. Rest, fluids, pain relievers (avoiding aspirin). Severe cases require hospitalization.',
            'prevention': 'Avoid mosquito bites, eliminate breeding sites, use repellents, wear protective clothing',
            'prevalence': 'Tropical and subtropical regions, affecting up to 400 million people annually',
            'image_url': 'assets/images/dengue.jpg',
            'vectors': ['aedes_aegypti', 'aedes_albopictus']  # Vector species IDs
        },
        {
            'id': '2',
            'name': 'Malaria',
            'description': 'Parasitic infection causing cycles of fever, chills, and sweating.',
            'symptoms': 'Fever, chills, sweating, headache, nausea, vomiting, body aches, general malaise',
            'treatment': 'Antimalarial drugs based on the type of malaria and severity. Early treatment is essential.',
            'prevention': 'Antimalarial medications, insecticide-treated bed nets, indoor residual spraying, eliminating breeding sites',
            'prevalence': 'Tropical and subtropical regions, particularly in Africa, with over 200 million cases annually',
            'image_url': 'assets/images/malaria.jpg',
            'vectors': ['anopheles_gambiae']  # Vector species IDs
        },
        {
            'id': '3',
            'name': 'Zika Virus',
            'description': 'Viral infection that can cause birth defects if contracted during pregnancy.',
            'symptoms': 'Mild fever, rash, joint pain, conjunctivitis, muscle pain, headache. Often asymptomatic.',
            'treatment': 'No specific treatment. Rest, fluids, acetaminophen for pain and fever.',
            'prevention': 'Avoid mosquito bites, use repellents, wear protective clothing, practice safe sex',
            'prevalence': 'Tropical and subtropical regions, with outbreaks in the Americas, Africa, and Asia',
            'image_url': 'assets/images/zika.jpg',
            'vectors': ['aedes_aegypti', 'aedes_albopictus']  # Vector species IDs
        },
    ]

    # Convert to DataFrame
    df = pd.DataFrame(diseases)

    # Create or recreate the table
    if "diseases" in db_conn.table_names():
        print("Dropping existing diseases table...")
        db_conn.drop_table("diseases")

    print("Creating diseases table...")
    table = db_conn.create_table("diseases", df)

    print(f"Successfully created diseases table with {len(diseases)} records")
    return table


def main():
    parser = argparse.ArgumentParser(description="Set up the diseases table in LanceDB")
    parser.add_argument("--db_path", default="./backend/data/.lancedb", help="Path to the LanceDB database")
    args = parser.parse_args()

    # Create database connection
    db_conn = get_db_connection(args.db_path)

    # Create diseases table
    create_disease_table(db_conn)

    # Create disease-species associations
    print("Disease data has been populated successfully.")


if __name__ == "__main__":
    main()