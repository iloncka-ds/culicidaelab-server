import json
import random
from datetime import datetime, timedelta
from uuid import uuid4

# --- SPECIES DATA ---
species_list = [
    {
        "id": "aedes_albopictus",
        "scientific_name": "Aedes albopictus",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Aedes_albopictus_PCSL_00000090_00.jpg/640px-Aedes_albopictus_PCSL_00000090_00.jpg",
        "common_name_en": "Asian Tiger Mosquito",
        "common_name_ru": "Азиатский тигровый комар",
        "description_en": "Known for its black and white striped legs and body. A significant vector for dengue, chikungunya, and Zika. Active during the day.",
        "description_ru": "Известен своими черно-белыми полосатыми ногами и телом. Является значимым переносчиком денге, чикунгуньи и Зика. Активен в дневное время.",
        "key_characteristics_en": [
            "Distinct white stripe on dorsal thorax",
            "Bites aggressively during the day",
            "Black and white striped legs",
        ],
        "key_characteristics_ru": [
            "Отчетливая белая полоса на спинной части груди",
            "Агрессивно кусает днем",
            "Черно-белые полосатые ноги",
        ],
        "habitat_preferences_en": ["Artificial containers", "Tree holes", "Urban and suburban areas"],
        "habitat_preferences_ru": ["Искусственные контейнеры", "Дупла деревьев", "Городские и пригородные зоны"],
        "geographic_regions": ["asia", "europe", "americas", "africa", "oceania"],
        "related_diseases": ["dengue_fever", "chikungunya", "zika_virus"],
        "related_diseases_info": [],
    },
    {
        "id": "anopheles_gambiae",
        "scientific_name": "Anopheles gambiae",
        "vector_status": "High",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a8/Anopheles_gambiae_NIAID.jpg/640px-Anopheles_gambiae_NIAID.jpg",
        "common_name_en": "African Malaria Mosquito",
        "common_name_ru": "Африканский малярийный комар",
        "description_en": "One of the primary vectors of malaria in sub-Saharan Africa. Prefers to feed on humans and rest indoors.",
        "description_ru": "Один из основных переносчиков малярии в странах Африки к югу от Сахары. Предпочитает питаться кровью людей и отдыхать в помещениях.",
        "key_characteristics_en": [
            "Palps as long as proboscis",
            "Spotted wings (in some Anopheles)",
            "Rests with abdomen pointing upwards",
        ],
        "key_characteristics_ru": [
            "Щупики такой же длины, как и хоботок",
            "Пятнистые крылья (у некоторых видов Anopheles)",
            "В состоянии покоя брюшко направлено вверх",
        ],
        "habitat_preferences_en": ["Clean, shallow, sunlit water bodies", "Temporary pools", "Rice paddies"],
        "habitat_preferences_ru": ["Чистые, мелководные, освещенные солнцем водоемы", "Временные лужи", "Рисовые поля"],
        "geographic_regions": ["sub_saharan_africa"],
        "related_diseases": ["malaria"],
        "related_diseases_info": [],
    },
]
with open("sample_species.json", "w", encoding="utf-8") as f:
    json.dump(species_list, f, indent=2, ensure_ascii=False)
print("Generated sample_species.json")


# --- REGIONS DATA ---
regions_data = [
    {"id": "asia", "name_en": "Asia", "name_ru": "Азия"},
    {"id": "europe", "name_en": "Europe", "name_ru": "Европа"},
    {"id": "americas", "name_en": "Americas", "name_ru": "Америка"},
    {"id": "africa", "name_en": "Africa", "name_ru": "Африка"},
    {"id": "oceania", "name_en": "Oceania", "name_ru": "Океания"},
    {"id": "sub_saharan_africa", "name_en": "Sub-Saharan Africa", "name_ru": "Африка к югу от Сахары"},
]
with open("sample_regions.json", "w", encoding="utf-8") as f:
    json.dump(regions_data, f, indent=2, ensure_ascii=False)
print("Generated sample_regions.json")

# --- DATA SOURCES DATA ---
data_sources = [
    {"id": "gbif", "name_en": "GBIF", "name_ru": "GBIF"},
    {"id": "inatuarlist", "name_en": "iNaturalist", "name_ru": "iNaturalist"},
    {"id": "vectorbase", "name_en": "VectorBase", "name_ru": "VectorBase"},
    {"id": "local_survey_a", "name_en": "Local Survey Team A", "name_ru": "Местная исследовательская группа А"},
    {"id": "research_xyz", "name_en": "Research Study XYZ", "name_ru": "Научное исследование XYZ"},
]
with open("sample_data_sources.json", "w", encoding="utf-8") as f:
    json.dump(data_sources, f, indent=2, ensure_ascii=False)
print("Generated sample_data_sources.json")


# --- DISEASES DATA ---
diseases_data_list = [
    {
        "id": "dengue_fever",
        "name_en": "Dengue Fever",
        "name_ru": "Лихорадка денге",
        "description_en": "Viral infection causing high fever, severe headache, and joint/muscle pain.",
        "description_ru": "Вирусная инфекция, вызывающая высокую температуру, сильную головную боль и боли в суставах/мышцах.",
        "symptoms_en": "High fever, severe headache, pain behind the eyes, joint and muscle pain, rash, mild bleeding",
        "symptoms_ru": "Высокая температура, сильная головная боль, боль за глазами, боли в суставах и мышцах, сыпь, легкое кровотечение",
        "treatment_en": "No specific treatment. Rest, fluids, pain relievers (avoiding aspirin). Severe cases require hospitalization.",
        "treatment_ru": "Специфического лечения нет. Покой, обильное питье, обезболивающие (избегая аспирина). Тяжелые случаи требуют госпитализации.",
        "prevention_en": "Avoid mosquito bites, eliminate breeding sites, use repellents, wear protective clothing",
        "prevention_ru": "Избегать укусов комаров, уничтожать места их размножения, использовать репелленты, носить защитную одежду",
        "prevalence_en": "Tropical and subtropical regions, affecting up to 400 million people annually",
        "prevalence_ru": "Тропические и субтропические регионы, ежегодно поражает до 400 миллионов человек",
        "image_url": "assets/images/dengue.jpg",
        "vectors": ["aedes_aegypti", "aedes_albopictus"],
    },
    {
        "id": "malaria",
        "name_en": "Malaria",
        "name_ru": "Малярия",
        "description_en": "Parasitic infection causing cycles of fever, chills, and sweating.",
        "description_ru": "Паразитарная инфекция, вызывающая циклы лихорадки, озноба и потоотделения.",
        "symptoms_en": "Fever, chills, sweating, headache, nausea, vomiting, body aches, general malaise",
        "symptoms_ru": "Лихорадка, озноб, потливость, головная боль, тошнота, рвота, ломота в теле, общее недомогание",
        "treatment_en": "Antimalarial drugs based on the type of malaria and severity. Early treatment is essential.",
        "treatment_ru": "Противомалярийные препараты в зависимости от типа малярии и тяжести заболевания. Крайне важно раннее лечение.",
        "prevention_en": "Antimalarial medications, insecticide-treated bed nets, indoor residual spraying, eliminating breeding sites",
        "prevention_ru": "Противомалярийные препараты, обработанные инсектицидами сетки для кроватей, опрыскивание помещений инсектицидами, уничтожение мест размножения",
        "prevalence_en": "Tropical and subtropical regions, particularly in Africa, with over 200 million cases annually",
        "prevalence_ru": "Тропические и субтропические регионы, особенно в Африке, с более чем 200 миллионами случаев в год",
        "image_url": "assets/images/malaria.jpg",
        "vectors": ["anopheles_gambiae"],
    },
]
with open("sample_diseases.json", "w", encoding="utf-8") as f:
    json.dump(diseases_data_list, f, indent=2, ensure_ascii=False)
print(f"Generated {'sample_diseases.json'}")

filter_options = {
    "species": [s["scientific_name"] for s in species_list],
    "regions": [r["id"] for r in regions_data],
    "data_sources": data_sources,
}
with open("sample_filter_options.json", "w") as f:
    json.dump(filter_options, f, indent=2)
print("Generated sample_filter_options.json")


europe_bbox = {"min_lon": -10, "max_lon": 40, "min_lat": 35, "max_lat": 70}
se_asia_bbox = {"min_lon": 90, "max_lon": 140, "min_lat": -10, "max_lat": 30}


def random_point_in_bbox(bbox):
    return [random.uniform(bbox["min_lat"], bbox["max_lat"]), random.uniform(bbox["min_lon"], bbox["max_lon"])]


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
                "id": str(uuid4()),
                "species_scientific_name": species_name,
                "observed_at": random_date(),
                "count": random.randint(1, 20),
                "observer_id": str(uuid4()),
                "location_accuracy_m": random.choice([None, 5, 10, 50, 100]),
                "notes": random.choice(["", "Near standing water.", "Adult female found.", "Larvae collected."]),
                "data_source": random.choice(data_sources),
                "image_filename": f"obs_{random.randint(100,999)}.jpg",
                "model_id": random.choice([None, "model_1", "model_2"]),
                "confidence": random.uniform(0, 1),
                "metadata": {
                    "model_id": random.choice([None, "model_1", "model_2"]),
                    "confidence": random.uniform(0, 1),
                    "species_scientific_name": species_name,
                },
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


