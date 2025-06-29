import json
import random
from datetime import datetime, timedelta


species_list = [
    {
        "id": "aedes_albopictus",
        "scientific_name": "Aedes albopictus",
        "common_name": "Asian Tiger Mosquito",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Aedes_albopictus_PCSL_00000090_00.jpg/640px-Aedes_albopictus_PCSL_00000090_00.jpg",
        "description": "Known for its black and white striped legs and body. A significant vector for dengue, chikungunya, and Zika. Active during the day.",
        "key_characteristics": [
            "Distinct white stripe on dorsal thorax",
            "Bites aggressively during the day",
            "Black and white striped legs",
        ],
        "geographic_regions": ["Asia", "Europe", "Americas", "Africa", "Oceania"],
        "related_diseases": ["dengue", "chikungunya", "zika_virus"],
        "related_diseases_info": [],
        "habitat_preferences": ["Artificial containers", "Tree holes", "Urban and suburban areas"],
    },
    {
        "id": "aedes_aegypti",
        "scientific_name": "Aedes aegypti",
        "common_name": "Yellow Fever Mosquito",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/54/Aedes_Aegypti_Feeding.jpg/640px-Aedes_Aegypti_Feeding.jpg",
        "description": "Primary vector for yellow fever, dengue, chikungunya, and Zika. Prefers urban habitats and human blood.",
        "key_characteristics": [
            "Lyre-shaped silver markings on thorax",
            "Prefers to feed on humans",
            "Dark body with white markings",
        ],
        "geographic_regions": ["Tropics Worldwide", "Subtropics Worldwide"],
        "related_diseases": ["yellow_fever", "dengue", "chikungunya", "zika_virus"],
        "related_diseases_info": [],
        "habitat_preferences": ["Water storage containers", "Flower pots", "Discarded tires", "Indoors"],
    },
    {
        "id": "culex_pipiens",
        "scientific_name": "Culex pipiens",
        "common_name": "Common House Mosquito",
        "vector_status": "Medium",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/CulexPipiens.jpg/640px-CulexPipiens.jpg",
        "description": "Vector for West Nile virus and St. Louis encephalitis. Often breeds in stagnant, polluted water. Bites at dusk and night.",
        "key_characteristics": [
            "Brownish body with crossbands on abdomen",
            "Primarily bites at dusk and night",
            "Rounded abdomen tip",
        ],
        "geographic_regions": ["Worldwide (Temperate and Tropical)"],
        "related_diseases": ["west_nile_virus", "st_louis_encephalitis", "avian_malaria"],
        "related_diseases_info": [],
        "habitat_preferences": ["Stagnant water (ditches, ponds, catch basins)", "Polluted water sources"],
    },
    {
        "id": "anopheles_gambiae",
        "scientific_name": "Anopheles gambiae",
        "common_name": "African Malaria Mosquito",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Anopheles_gambiae_NIAID.jpg/640px-Anopheles_gambiae_NIAID.jpg",
        "description": "One of the primary vectors of malaria in sub-Saharan Africa. Prefers to feed on humans and rest indoors.",
        "key_characteristics": [
            "Palps as long as proboscis",
            "Spotted wings (in some Anopheles)",
            "Rests with abdomen pointing upwards",
        ],
        "geographic_regions": ["Sub-Saharan Africa"],
        "related_diseases": ["malaria"],
        "related_diseases_info": [],
        "habitat_preferences": ["Clean, shallow, sunlit water bodies", "Temporary pools", "Rice paddies"],
    },
    {
        "id": "culiseta_annulata",
        "scientific_name": "Culiseta annulata",
        "common_name": "Banded Mosquito",
        "vector_status": "Low",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c0/Culiseta.annulata.jpg/640px-Culiseta.annulata.jpg",
        "description": "A large mosquito with banded legs and abdomen. Less significant as a disease vector to humans compared to others.",
        "key_characteristics": ["Large size", "Banded legs and abdomen", "Dark wing scales"],
        "geographic_regions": ["Europe", "North Africa", "Asia Minor"],
        "related_diseases": [],
        "related_diseases_info": ["Potentially some arboviruses (minor role)"],
        "habitat_preferences": [
            "Various water bodies, including slightly brackish",
            "Caves",
            "Cellars (for overwintering)",
        ],
    },
]
with open("sample_species.json", "w") as f:
    json.dump(species_list, f, indent=2)
print("Generated sample_species.json")

regions = [
    "Asia",
    "Europe",
    "Americas",
    "Africa",
    "Oceania",
    "Tropics Worldwide",
    "Subtropics Worldwide",
    "Sub-Saharan Africa",
]
data_sources = ["GBIF", "iNaturalist", "VectorBase", "Local Survey Team A", "Research Study XYZ"]

filter_options = {
    "species": [s["scientific_name"] for s in species_list],
    "regions": list(set(regions)),
    "data_sources": data_sources,
}
with open("sample_filter_options.json", "w") as f:
    json.dump(filter_options, f, indent=2)
print("Generated sample_filter_options.json")



europe_bbox = {"min_lon": -10, "max_lon": 40, "min_lat": 35, "max_lat": 70}
se_asia_bbox = {"min_lon": 90, "max_lon": 140, "min_lat": -10, "max_lat": 30}


def random_point_in_bbox(bbox):
    return [random.uniform(bbox["min_lon"], bbox["max_lon"]), random.uniform(bbox["min_lat"], bbox["max_lat"])]


def random_date(start_days_ago=365, end_days_ago=0):
    return (datetime.now() - timedelta(days=random.randint(end_days_ago, start_days_ago))).strftime("%Y-%m-%d")

species_regions_map = {
    "Aedes albopictus": europe_bbox,
    "Aedes aegypti": se_asia_bbox,
    "Culex pipiens": europe_bbox,
    "Anopheles gambiae": {"min_lon": -20, "max_lon": 50, "min_lat": -35, "max_lat": 15},
    "Culiseta annulata": europe_bbox,
}

observations_data = []
for _ in range(100):
    species_obj = random.choice(species_list)
    species_name = species_obj["scientific_name"]
    bbox = species_regions_map.get(species_name, europe_bbox)
    point = random_point_in_bbox(bbox)
    observations_data.append(
        {
            "type": "Feature",
            "properties": {
                "species": species_name,
                "observation_date": random_date(),
                "count": random.randint(1, 20),
                "observer_id": f"obs_{random.randint(100,999)}",
                "data_source": random.choice(data_sources),
                "location_accuracy_m": random.choice([None, 5, 10, 50, 100]),
                "notes": random.choice(["", "Near standing water.", "Adult female found.", "Larvae collected."]),
            },
            "geometry": {
                "type": "Point",
                "coordinates": point,
            },
        }
    )
with open("sample_observations.geojson", "w") as f:
    json.dump({"type": "FeatureCollection", "features": observations_data}, f, indent=2)
print("Generated sample_observations.geojson")


diseases_data_list = [
    {
        "id": "dengue_fever",
        "name": "Dengue Fever",
        "description": "Viral infection causing high fever, severe headache, and joint/muscle pain.",
        "symptoms": "High fever, severe headache, pain behind the eyes, joint and muscle pain, rash, mild bleeding",
        "treatment": "No specific treatment. Rest, fluids, pain relievers (avoiding aspirin). Severe cases require hospitalization.",
        "prevention": "Avoid mosquito bites, eliminate breeding sites, use repellents, wear protective clothing",
        "prevalence": "Tropical and subtropical regions, affecting up to 400 million people annually",
        "image_url": "assets/images/dengue.jpg",
        "vectors": ["aedes_aegypti", "aedes_albopictus"],
    },
    {
        "id": "malaria",
        "name": "Malaria",
        "description": "Parasitic infection causing cycles of fever, chills, and sweating.",
        "symptoms": "Fever, chills, sweating, headache, nausea, vomiting, body aches, general malaise",
        "treatment": "Antimalarial drugs based on the type of malaria and severity. Early treatment is essential.",
        "prevention": "Antimalarial medications, insecticide-treated bed nets, indoor residual spraying, eliminating breeding sites",
        "prevalence": "Tropical and subtropical regions, particularly in Africa, with over 200 million cases annually",
        "image_url": "assets/images/malaria.jpg",
        "vectors": ["anopheles_gambiae"],
    },
    {
        "id": "zika_virus",
        "name": "Zika Virus",
        "description": "Viral infection that can cause birth defects if contracted during pregnancy.",
        "symptoms": "Mild fever, rash, joint pain, conjunctivitis, muscle pain, headache. Often asymptomatic.",
        "treatment": "No specific treatment. Rest, fluids, acetaminophen for pain and fever.",
        "prevention": "Avoid mosquito bites, use repellents, wear protective clothing, practice safe sex",
        "prevalence": "Tropical and subtropical regions, with outbreaks in the Americas, Africa, and Asia",
        "image_url": "assets/images/zika.jpg",
        "vectors": ["aedes_aegypti", "aedes_albopictus"],
    },
    {
        "id": "west_nile_virus",
        "name": "West Nile Virus",
        "description": "Viral infection primarily transmitted by Culex mosquitoes, can cause neurological disease.",
        "symptoms": "Often asymptomatic. Febrile illness (fever, headache, body aches), skin rash, swollen lymph glands. Severe cases: encephalitis, meningitis.",
        "treatment": "No specific vaccine or treatment. Supportive care for severe cases.",
        "prevention": "Avoid mosquito bites, use repellents, eliminate standing water.",
        "prevalence": "Africa, Europe, Middle East, North America, West Asia. Outbreaks occur sporadically.",
        "image_url": "assets/images/west_nile.jpg",
        "vectors": ["culex_pipiens"],
    },
    {
        "id": "chikungunya",
        "name": "Chikungunya",
        "description": "Viral illness transmitted by Aedes mosquitoes, causing severe joint pain.",
        "symptoms": "Sudden onset of fever, severe joint pain (often debilitating), muscle pain, headache, nausea, fatigue, rash.",
        "treatment": "No specific antiviral treatment. Symptomatic relief for pain and fever.",
        "prevention": "Avoid mosquito bites, eliminate breeding sites, use repellents.",
        "prevalence": "Africa, Asia, Europe, Indian and Pacific Oceans, Americas. Has caused large outbreaks.",
        "image_url": "assets/images/chikungunya.jpg",
        "vectors": ["aedes_aegypti", "aedes_albopictus"],
    },
]
with open( "sample_diseases.json", "w") as f:
    json.dump(diseases_data_list, f, indent=2)

print(f"Generated {'sample_diseases.json'}")
