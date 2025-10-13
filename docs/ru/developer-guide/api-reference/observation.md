# API наблюдений

API наблюдений обрабатывает данные наблюдений комаров, включая запись новых наблюдений и получение существующих записей наблюдений.

## Реализация роутера

::: backend.routers.observation
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

API наблюдений использует Pydantic схемы для валидации данных наблюдений:

::: backend.schemas.observation_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Слой сервисов

API наблюдений интегрируется со слоями сервисов наблюдений:

::: backend.services.observation_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Создать новое наблюдение

```python
import httpx
from datetime import datetime

async with httpx.AsyncClient() as client:
    observation_data = {
        "species_id": "aedes-aegypti",
        "location": {
            "latitude": 40.7128,
            "longitude": -74.0060
        },
        "observed_at": datetime.now().isoformat(),
        "observer_name": "Д-р Смит",
        "notes": "Найден в городской зоне рядом со стоячей водой"
    }
    
    response = await client.post(
        "http://localhost:8000/api/v1/observations",
        json=observation_data
    )
    observation = response.json()
    print(f"Создано наблюдение ID: {observation['id']}")
```

### Получить наблюдения

```python
# Получить список наблюдений с фильтрами
response = await client.get(
    "http://localhost:8000/api/v1/observations",
    params={
        "species_id": "aedes-aegypti",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31",
        "limit": 50
    }
)
observations = response.json()

# Получить детали конкретного наблюдения
response = await client.get(
    "http://localhost:8000/api/v1/observations/12345"
)
observation_detail = response.json()
```

### Обновить наблюдение

```python
# Обновить существующее наблюдение
update_data = {
    "notes": "Обновленные заметки с дополнительными деталями",
    "verified": True
}

response = await client.patch(
    "http://localhost:8000/api/v1/observations/12345",
    json=update_data
)
updated_observation = response.json()
```