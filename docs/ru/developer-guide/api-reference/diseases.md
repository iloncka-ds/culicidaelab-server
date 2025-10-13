# API болезней

API болезней управляет данными, связанными с болезнями, и предоставляет endpoints для получения информации о болезнях, переносимых комарами.

## Реализация роутера

::: backend.routers.diseases
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

API болезней использует Pydantic схемы для валидации запросов/ответов:

::: backend.schemas.diseases_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Слой сервисов

API болезней интегрируется со слоем сервисов болезней:

::: backend.services.disease_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Базовое получение информации о болезнях

```python
import httpx

async with httpx.AsyncClient() as client:
    # Получить список болезней
    response = await client.get(
        "http://localhost:8000/api/v1/diseases",
        params={"lang": "ru"}
    )
    diseases = response.json()
    
    # Получить детали конкретной болезни
    response = await client.get(
        "http://localhost:8000/api/v1/diseases/malaria",
        params={"lang": "ru"}
    )
    disease_detail = response.json()
```