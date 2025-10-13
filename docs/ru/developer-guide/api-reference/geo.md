# API географических данных

Географический API обрабатывает данные на основе местоположения и предоставляет endpoints для получения географической информации и региональных данных.

## Реализация роутера

::: backend.routers.geo
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

Географический API использует Pydantic схемы для валидации географических данных:

::: backend.schemas.geo_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Слой сервисов

Географический API интегрируется со слоями географических сервисов:

::: backend.services.geo_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Получение географических данных

```python
import httpx

async with httpx.AsyncClient() as client:
    # Получить региональные данные
    response = await client.get(
        "http://localhost:8000/api/v1/regions",
        params={"lang": "ru"}
    )
    regions = response.json()
    
    # Получить информацию о странах
    response = await client.get(
        "http://localhost:8000/api/v1/countries",
        params={"lang": "ru"}
    )
    countries = response.json()
```