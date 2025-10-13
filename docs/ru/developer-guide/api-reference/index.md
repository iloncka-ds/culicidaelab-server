---
tags:
  - api
  - reference
  - development
  - backend
  - fastapi
---

# Справочник API

Всеобъемлющая документация API для бэкенд сервисов CulicidaeLab Server.

## Обзор

CulicidaeLab Server предоставляет RESTful API, построенный с FastAPI для исследования комаров, наблюдения и анализа данных. API предлагает endpoints для идентификации видов, отслеживания болезней, управления географическими данными и записи наблюдений.

## Базовый URL

```
http://localhost:8000/api/v1
```

## Аутентификация

В настоящее время API не требует аутентификации для большинства endpoints. Будущие версии могут реализовать аутентификацию по API ключу или OAuth2.

## Формат ответа

Все ответы API следуют согласованному JSON формату с соответствующими HTTP кодами состояния:

- `200 OK`: Успешный запрос
- `404 Not Found`: Ресурс не найден
- `422 Unprocessable Entity`: Ошибка валидации
- `500 Internal Server Error`: Ошибка сервера

## Интерактивная документация API

Для интерактивного исследования API посетите автоматически сгенерированную документацию:

- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Модули API

### Основное приложение

::: backend.main
    options:
      show_root_heading: true
      show_source: false
      members_order: source
      
### Управление видами

API видов предоставляет endpoints для получения информации о видах комаров, включая детальные данные о видах и информацию о переносчиках болезней.

::: backend.routers.species
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Информация о болезнях

API болезней управляет данными, связанными с болезнями, и предоставляет endpoints для получения информации о болезнях, переносимых комарами.

::: backend.routers.diseases
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Географические данные

Географический API обрабатывает данные на основе местоположения и предоставляет endpoints для получения географической информации и региональных данных.

::: backend.routers.geo
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Сервисы предсказаний

API предсказаний предоставляет сервисы идентификации видов и предсказаний на основе машинного обучения.

::: backend.routers.prediction
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Управление наблюдениями

API наблюдений обрабатывает данные наблюдений комаров, включая запись и получение записей наблюдений.

::: backend.routers.observation
    options:
      show_root_heading: true
      show_source: false
      members_order: source

### Фильтрация данных

API фильтров предоставляет endpoints для получения опций фильтров и управления возможностями фильтрации данных.

::: backend.routers.filters
    options:
      show_root_heading: true
      show_source: false
      members_order: source