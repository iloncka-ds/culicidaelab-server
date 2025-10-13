# API видов

API видов предоставляет всеобъемлющие endpoints для получения информации о видах комаров, включая списки видов, детальные данные о видах и информацию о переносчиках болезней.

## Обзор endpoints

| Метод | Endpoint | Описание |
|-------|----------|----------|
| GET | `/species` | Получить пагинированный список видов с опциональным поиском |
| GET | `/species/{species_id}` | Получить детальную информацию для конкретного вида |
| GET | `/vector-species` | Получить виды, которые являются переносчиками болезней |

## Реализация роутера

::: backend.routers.species
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

API видов использует следующие Pydantic схемы для валидации запросов/ответов:

### Схема SpeciesBase

::: backend.schemas.species_schemas.SpeciesBase
    options:
      show_root_heading: true
      show_source: false

### Схема SpeciesDetail

::: backend.schemas.species_schemas.SpeciesDetail
    options:
      show_root_heading: true
      show_source: false

### Схема SpeciesListResponse

::: backend.schemas.species_schemas.SpeciesListResponse
    options:
      show_root_heading: true
      show_source: false

## Слой сервисов

API видов интегрируется со слоем сервисов видов для бизнес-логики:

::: backend.services.species_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Получить список видов

```python
import httpx

async with httpx.AsyncClient() as client:
    response = await client.get(
        "http://localhost:8000/api/v1/species",
        params={"limit": 25, "lang": "ru"}
    )
    species_data = response.json()
    print(f"Найдено {species_data['count']} видов")
```

### Поиск видов

```python
response = await client.get(
    "http://localhost:8000/api/v1/species",
    params={"search": "aedes", "limit": 10, "lang": "ru"}
)
```

### Получить детали вида

```python
response = await client.get(
    "http://localhost:8000/api/v1/species/aedes-aegypti",
    params={"lang": "ru"}
)
species = response.json()
```

### Получить виды-переносчики

```python
response = await client.get(
    "http://localhost:8000/api/v1/vector-species",
    params={"lang": "ru"}
)
vector_species = response.json()
```