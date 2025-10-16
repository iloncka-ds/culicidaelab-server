# API предсказаний

API предсказаний предоставляет сервисы идентификации видов и предсказаний на основе машинного обучения для классификации комаров.

## Реализация роутера

::: backend.routers.prediction
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Схемы данных

API предсказаний использует Pydantic схемы для валидации запросов/ответов предсказаний:

::: backend.schemas.prediction_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Слой сервисов

API предсказаний интегрируется со слоями сервисов машинного обучения:

::: backend.services.prediction_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Примеры использования

### Предсказание видов

```python
import httpx

async with httpx.AsyncClient() as client:
    # Загрузить изображение для предсказания видов
    with open("mosquito_image.jpg", "rb") as image_file:
        files = {"image": image_file}
        response = await client.post(
            "http://localhost:8000/api/v1/predict",
            files=files,
            data={"confidence_threshold": 0.7}
        )
        prediction = response.json()
        
    print(f"Предсказанный вид: {prediction['species']}")
    print(f"Уверенность: {prediction['confidence']}")
```
