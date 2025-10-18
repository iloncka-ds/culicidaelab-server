# Справочник API

Полная справочная документация по API для CulicidaeLab Server.

## Быстрый старт

API CulicidaeLab Server — это RESTful сервис, построенный с помощью FastAPI, который предоставляет конечные точки для исследования комаров, наблюдения и анализа данных.

### Базовый URL
```
http://localhost:8000/api/v1
```

### Тип контента
Все конечные точки API принимают и возвращают данные JSON:
```
Content-Type: application/json
```

## Интерактивная документация

FastAPI автоматически генерирует интерактивную документацию API:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs) - Интерактивный обозреватель API
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc) - Альтернативный формат документации

## Спецификация OpenAPI

Полная спецификация OpenAPI доступна по адресу:
```
http://localhost:8000/api/v1/openapi.json
```

Вы можете использовать эту спецификацию с любым инструментом, совместимым с OpenAPI, для:
- Генерации кода
- Тестирования API
- Генерации документации
- Создания мок-сервера

## Обзор конечных точек API

### Управление видами
- `GET /species` - Список видов комаров с поиском и пагинацией
- `GET /species/{species_id}` - Получить подробную информацию о виде
- `GET /vector-species` - Список видов-переносчиков болезней

### Информация о болезнях
- `GET /diseases` - Список болезней, переносимых комарами
- `GET /diseases/{disease_id}` - Получить подробную информацию о болезни

### Географические данные
- `GET /regions` - Список географических регионов
- `GET /countries` - Список стран с данными о комарах

### Сервисы предсказания
- `POST /predict` - Предсказать вид комара по изображению
- `POST /predict/batch` - Пакетное предсказание для нескольких изображений

### Управление наблюдениями
- `GET /observations` - Список наблюдений комаров
- `POST /observations` - Создать новое наблюдение
- `GET /observations/{observation_id}` - Получить детали наблюдения
- `PATCH /observations/{observation_id}` - Обновить наблюдение

### Фильтрация данных
- `GET /filters` - Получить доступные опции фильтров
- `GET /filters/{filter_type}` - Получить опции конкретного типа фильтра

## Аутентификация

В настоящее время API не требует аутентификации. Будущие версии могут реализовать:
- Аутентификацию по API-ключу
- OAuth2 с JWT токенами
- Контроль доступа на основе ролей

## Ограничение скорости

В настоящее время ограничение скорости не реализовано. Продакшн развертывания должны рассмотреть:
- Ограничение скорости запросов по IP
- Квоты на основе API-ключей
- Защиту от всплесков

## Обработка ошибок

API использует стандартные коды состояния HTTP:

| Код состояния | Описание |
|---------------|----------|
| 200 | Успех |
| 201 | Создано |
| 400 | Неверный запрос |
| 404 | Не найдено |
| 422 | Ошибка валидации |
| 500 | Внутренняя ошибка сервера |

### Формат ответа об ошибке

```json
{
  "detail": "Описание ошибки",
  "type": "тип_ошибки",
  "errors": [
    {
      "loc": ["поле", "имя"],
      "msg": "Ошибка валидации поля",
      "type": "value_error"
    }
  ]
}
```

## Пагинация

Конечные точки списков поддерживают пагинацию с параметрами запроса:

- `limit`: Максимальное количество результатов (по умолчанию: 50, макс: 200)
- `offset`: Количество результатов для пропуска (по умолчанию: 0)

### Формат ответа пагинации

```json
{
  "count": 150,
  "results": [...],
  "next": "http://localhost:8000/api/v1/species?limit=50&offset=50",
  "previous": null
}
```

## Интернационализация

API поддерживает несколько языков через параметр запроса `lang`:

- `en`: Английский (по умолчанию)
- `es`: Испанский
- `ru`: Русский
- `fr`: Французский

Пример:
```
GET /api/v1/species?lang=ru
```

## Форматы данных

### Координаты
Географические координаты используют десятичные градусы:
```json
{
  "latitude": 40.7128,
  "longitude": -74.0060
}
```

### Даты
Даты и временные метки используют формат ISO 8601:
```json
{
  "observed_at": "2024-01-15T14:30:00Z",
  "created_at": "2024-01-15T14:30:00.123456Z"
}
```

### Изображения
Загрузка изображений поддерживает:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- Максимальный размер: 10МБ
- Рекомендуемое разрешение: от 224x224 до 1024x1024 пикселей

## SDK и клиентские библиотеки

### Пример Python клиента

```python
import httpx
import asyncio

async def get_species_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/species",
            params={"limit": 25, "lang": "ru"}
        )
        return response.json()

# Запуск примера
species_data = asyncio.run(get_species_list())
print(f"Найдено {species_data['count']} видов")
```

### Пример JavaScript/Node.js клиента

```javascript
const axios = require('axios');

async function getSpeciesList() {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/species', {
      params: {
        limit: 25,
        lang: 'ru'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Ошибка получения видов:', error.response.data);
  }
}

// Использование
getSpeciesList().then(data => {
  console.log(`Найдено ${data.count} видов`);
});
```

## Тестирование API

### Использование curl

```bash
# Получить список видов
curl -X GET "http://localhost:8000/api/v1/species?limit=10&lang=ru"

# Получить конкретный вид
curl -X GET "http://localhost:8000/api/v1/species/aedes-aegypti?lang=ru"

# Загрузить изображение для предсказания
curl -X POST "http://localhost:8000/api/v1/predict" \
  -F "image=@mosquito.jpg" \
  -F "confidence_threshold=0.7"
```

### Использование HTTPie

```bash
# Получить список видов
http GET localhost:8000/api/v1/species limit==10 lang==ru

# Создать наблюдение
http POST localhost:8000/api/v1/observations \
  species_id=aedes-aegypti \
  location:='{"latitude": 40.7128, "longitude": -74.0060}' \
  observer_name="Д-р Смит"
```

## Подробная документация API

Для подробной документации каждой конечной точки API, включая схемы запросов/ответов и примеры, см.:

- [API видов](../../developer-guide/api-reference/species.md)
- [API болезней](../../developer-guide/api-reference/diseases.md)
- [Географический API](../../developer-guide/api-reference/geo.md)
- [API предсказаний](../../developer-guide/api-reference/prediction.md)
- [API наблюдений](../../developer-guide/api-reference/observation.md)
- [API фильтров](../../developer-guide/api-reference/filters.md)
