# Details

Date : 2025-05-19 19:12:42

Directory c:\\Users\\lenova\\culicidaelab-server

Total : 79 files,  11283 codes, 895 comments, 1080 blanks, all 13258 lines

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)

## Files
| filename | language | code | comment | blank | total |
| :--- | :--- | ---: | ---: | ---: | ---: |
| [.env](/.env) | env | 1 | 0 | 1 | 2 |
| [.flake8](/.flake8) | Ini | 5 | 0 | 1 | 6 |
| [.isort.cfg](/.isort.cfg) | Properties | 6 | 2 | 1 | 9 |
| [.pre-commit-config.yaml](/.pre-commit-config.yaml) | YAML | 65 | 2 | 2 | 69 |
| [.ruff.toml](/.ruff.toml) | TOML | 10 | 0 | 2 | 12 |
| [README.md](/README.md) | Markdown | 0 | 0 | 1 | 1 |
| [backend/.env](/backend/.env) | env | 1 | 0 | 0 | 1 |
| [backend/\_\_init\_\_.py](/backend/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/config.py](/backend/config.py) | Python | 17 | 12 | 12 | 41 |
| [backend/data/mock\_modeled\_prob.geojson](/backend/data/mock_modeled_prob.geojson) | JSON | 0 | 0 | 1 | 1 |
| [backend/data/mock\_observations.json](/backend/data/mock_observations.json) | JSON | 0 | 0 | 1 | 1 |
| [backend/data/mock\_species\_dist.geojson](/backend/data/mock_species_dist.geojson) | JSON | 0 | 0 | 1 | 1 |
| [backend/data/sample\_data/generate\_sample\_data.py](/backend/data/sample_data/generate_sample_data.py) | Python | 238 | 15 | 20 | 273 |
| [backend/data/sample\_data/populate\_diseases.py](/backend/data/sample_data/populate_diseases.py) | Python | 62 | 8 | 16 | 86 |
| [backend/data/sample\_data/sample\_breeding\_sites.geojson](/backend/data/sample_data/sample_breeding_sites.geojson) | JSON | 1,405 | 0 | 0 | 1,405 |
| [backend/data/sample\_data/sample\_distribution.geojson](/backend/data/sample_data/sample_distribution.geojson) | JSON | 190 | 0 | 0 | 190 |
| [backend/data/sample\_data/sample\_filter\_options.json](/backend/data/sample_data/sample_filter_options.json) | JSON | 26 | 0 | 0 | 26 |
| [backend/data/sample\_data/sample\_modeled.geojson](/backend/data/sample_data/sample_modeled.geojson) | JSON | 365 | 0 | 0 | 365 |
| [backend/data/sample\_data/sample\_observations.geojson](/backend/data/sample_data/sample_observations.geojson) | JSON | 1,905 | 0 | 0 | 1,905 |
| [backend/data/sample\_data/sample\_species.json](/backend/data/sample_data/sample_species.json) | JSON | 136 | 0 | 0 | 136 |
| [backend/database\_utils/\_\_init\_\_.py](/backend/database_utils/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/database\_utils/lancedb\_manager.py](/backend/database_utils/lancedb_manager.py) | Python | 78 | 14 | 16 | 108 |
| [backend/dependencies.py](/backend/dependencies.py) | Python | 3 | 0 | 3 | 6 |
| [backend/main.py](/backend/main.py) | Python | 24 | 74 | 29 | 127 |
| [backend/models.py](/backend/models.py) | Python | 47 | 6 | 24 | 77 |
| [backend/readme.md](/backend/readme.md) | Markdown | 34 | 0 | 15 | 49 |
| [backend/routers/\_\_init\_\_.py](/backend/routers/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/routers/diseases.py](/backend/routers/diseases.py) | Python | 27 | 11 | 9 | 47 |
| [backend/routers/filters.py](/backend/routers/filters.py) | Python | 9 | 3 | 4 | 16 |
| [backend/routers/geo.py](/backend/routers/geo.py) | Python | 40 | 6 | 8 | 54 |
| [backend/routers/geo\_data\_router.py](/backend/routers/geo_data_router.py) | Python | 0 | 64 | 15 | 79 |
| [backend/routers/mosquito\_info\_router.py](/backend/routers/mosquito_info_router.py) | Python | 0 | 30 | 9 | 39 |
| [backend/routers/species.py](/backend/routers/species.py) | Python | 27 | 9 | 6 | 42 |
| [backend/schemas/\_\_init\_\_.py](/backend/schemas/__init__.py) | Python | 0 | 0 | 2 | 2 |
| [backend/schemas/diseases\_schemas.py](/backend/schemas/diseases_schemas.py) | Python | 18 | 0 | 7 | 25 |
| [backend/schemas/geo\_schemas.py](/backend/schemas/geo_schemas.py) | Python | 13 | 1 | 7 | 21 |
| [backend/schemas/species\_schemas.py](/backend/schemas/species_schemas.py) | Python | 20 | 0 | 8 | 28 |
| [backend/scripts/\_\_init\_\_.py](/backend/scripts/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/scripts/populate\_lancedb.py](/backend/scripts/populate_lancedb.py) | Python | 79 | 17 | 22 | 118 |
| [backend/scripts/setup\_lancedb.py](/backend/scripts/setup_lancedb.py) | Python | 257 | 51 | 34 | 342 |
| [backend/scripts/setup\_sqlite\_database.py](/backend/scripts/setup_sqlite_database.py) | Python | 132 | 25 | 27 | 184 |
| [backend/services/\_\_init\_\_.py](/backend/services/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [backend/services/database.py](/backend/services/database.py) | Python | 19 | 5 | 5 | 29 |
| [backend/services/disease\_service.py](/backend/services/disease_service.py) | Python | 23 | 17 | 14 | 54 |
| [backend/services/filter\_service.py](/backend/services/filter_service.py) | Python | 20 | 29 | 9 | 58 |
| [backend/services/geo\_service.py](/backend/services/geo_service.py) | Python | 86 | 110 | 49 | 245 |
| [backend/services/species\_service.py](/backend/services/species_service.py) | Python | 111 | 20 | 23 | 154 |
| [frontend/\_\_init\_\_.py](/frontend/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/assets/custom.css](/frontend/assets/custom.css) | PostCSS | 388 | 16 | 84 | 488 |
| [frontend/assets/theme.js](/frontend/assets/theme.js) | JavaScript | 8 | 1 | 2 | 11 |
| [frontend/components/\_\_init\_\_.py](/frontend/components/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/components/common/\_\_init\_\_.py](/frontend/components/common/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/components/common/app\_layout.py](/frontend/components/common/app_layout.py) | Python | 39 | 4 | 16 | 59 |
| [frontend/components/diseases/disease\_card.py](/frontend/components/diseases/disease_card.py) | Python | 48 | 5 | 7 | 60 |
| [frontend/components/map\_module/\_\_init\_\_.py](/frontend/components/map_module/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/components/map\_module/filter\_panel.py](/frontend/components/map_module/filter_panel.py) | Python | 147 | 40 | 35 | 222 |
| [frontend/components/map\_module/info\_panel.py](/frontend/components/map_module/info_panel.py) | Python | 90 | 9 | 16 | 115 |
| [frontend/components/map\_module/layer\_control.py](/frontend/components/map_module/layer_control.py) | Python | 9 | 7 | 4 | 20 |
| [frontend/components/map\_module/legend\_component.py](/frontend/components/map_module/legend_component.py) | Python | 59 | 39 | 11 | 109 |
| [frontend/components/map\_module/map\_component.py](/frontend/components/map_module/map_component.py) | Python | 178 | 10 | 29 | 217 |
| [frontend/components/prediction/\_\_init\_\_.py](/frontend/components/prediction/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/components/prediction/file\_upload.py](/frontend/components/prediction/file_upload.py) | Python | 36 | 10 | 8 | 54 |
| [frontend/components/prediction/location.py](/frontend/components/prediction/location.py) | Python | 91 | 8 | 17 | 116 |
| [frontend/components/prediction/observation\_form.py](/frontend/components/prediction/observation_form.py) | Python | 126 | 14 | 23 | 163 |
| [frontend/components/species/\_\_init\_\_.py](/frontend/components/species/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/components/species/species\_card.py](/frontend/components/species/species_card.py) | Python | 53 | 5 | 7 | 65 |
| [frontend/config.py](/frontend/config.py) | Python | 106 | 11 | 23 | 140 |
| [frontend/main.py](/frontend/main.py) | Python | 63 | 49 | 23 | 135 |
| [frontend/pages/\_\_init\_\_.py](/frontend/pages/__init__.py) | Python | 0 | 0 | 1 | 1 |
| [frontend/pages/disease\_detail.py](/frontend/pages/disease_detail.py) | Python | 234 | 11 | 33 | 278 |
| [frontend/pages/disease\_gallery.py](/frontend/pages/disease_gallery.py) | Python | 126 | 3 | 19 | 148 |
| [frontend/pages/home.py](/frontend/pages/home.py) | Python | 15 | 1 | 7 | 23 |
| [frontend/pages/map\_visualization.py](/frontend/pages/map_visualization.py) | Python | 67 | 21 | 10 | 98 |
| [frontend/pages/prediction.py](/frontend/pages/prediction.py) | Python | 206 | 23 | 33 | 262 |
| [frontend/pages/species\_detail.py](/frontend/pages/species_detail.py) | Python | 173 | 6 | 26 | 205 |
| [frontend/pages/species\_gallery.py](/frontend/pages/species_gallery.py) | Python | 128 | 59 | 30 | 217 |
| [frontend/state.py](/frontend/state.py) | Python | 110 | 12 | 16 | 138 |
| [pyproject.toml](/pyproject.toml) | TOML | 40 | 0 | 2 | 42 |
| [uv.lock](/uv.lock) | TOML | 3,244 | 0 | 183 | 3,427 |

[Summary](results.md) / Details / [Diff Summary](diff.md) / [Diff Details](diff-details.md)