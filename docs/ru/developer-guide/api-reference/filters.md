# API фильтров

API фильтров предоставляет endpoints для получения опций фильтров и управления возможностями фильтрации данных на платформе CulicidaeLab.

## Реализация роутера

::: backend.routers.filters
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

API фильтров использует Pydantic схемы для валидации данных фильтров:

::: backend.schemas.filter_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Слой сервисов

API фильтров интегрируется со слоями сервисов фильтров:

::: backend.services.filter_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Получить доступные фильтры

```python
import httpx

async with httpx.AsyncClient() as client:
    # Получить все доступные опции фильтров
    response = await client.get(
        "http://localhost:8000/api/v1/filters",
        params={"lang": "ru"}
    )
    filters = response.json()
    
    print("Доступные фильтры:")
    for filter_type, options in filters.items():
        print(f"- {filter_type}: {len(options)} опций")
```

### Получить конкретный тип фильтра

```python
# Получить опции фильтра видов
response = await client.get(
    "http://localhost:8000/api/v1/filters/species",
    params={"lang": "ru"}
)
species_filters = response.json()

# Получить опции фильтра регионов
response = await client.get(
    "http://localhost:8000/api/v1/filters/regions",
    params={"lang": "ru"}
)
region_filters = response.json()

# Получить опции фильтра болезней
response = await client.get(
    "http://localhost:8000/api/v1/filters/diseases",
    params={"lang": "ru"}
)
disease_filters = response.json()
```

### Применить фильтры к запросам данных

```python
# Использовать фильтры в запросах видов
response = await client.get(
    "http://localhost:8000/api/v1/species",
    params={
        "region": "north-america",
        "vector_status": "primary",
        "disease": "malaria",
        "lang": "ru"
    }
)
filtered_species = response.json()
```