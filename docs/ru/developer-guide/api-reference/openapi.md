# Интеграция OpenAPI

CulicidaeLab Server автоматически генерирует всеобъемлющую документацию OpenAPI, используя встроенные возможности FastAPI.

## Интерактивная документация

FastAPI предоставляет два интерактивных интерфейса документации из коробки:

### Swagger UI
Доступ к Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)

Swagger UI предоставляет:
- Интерактивное исследование API
- Примеры запросов/ответов
- Валидацию схем
- Функциональность "попробовать"
- Тестирование аутентификации (когда реализовано)

### ReDoc
Доступ к ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

ReDoc предлагает:
- Чистую, читаемую документацию
- Детальную информацию о схемах
- Примеры кода на нескольких языках
- Адаптивный дизайн для мобильных устройств

## Спецификация OpenAPI

### Формат JSON
Полная спецификация OpenAPI доступна в формате JSON:
```
http://localhost:8000/api/v1/openapi.json
```

### Формат YAML
Вы также можете получить спецификацию в формате YAML, добавив заголовок Accept:
```bash
curl -H "Accept: application/x-yaml" http://localhost:8000/api/v1/openapi.json
```

## Использование спецификации OpenAPI

### Генерация кода

Генерируйте клиентские библиотеки используя спецификацию OpenAPI:

#### Python клиент с openapi-generator
```bash
# Установить openapi-generator
npm install @openapitools/openapi-generator-cli -g

# Сгенерировать Python клиент
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/openapi.json \
  -g python \
  -o ./culicidae-client-python \
  --package-name culicidae_client
```

#### JavaScript клиент
```bash
# Сгенерировать JavaScript/TypeScript клиент
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/openapi.json \
  -g typescript-axios \
  -o ./culicidae-client-js
```

### Тестирование API с Postman

1. Импортировать спецификацию OpenAPI в Postman:
   - Открыть Postman
   - Нажать "Import"
   - Ввести URL: `http://localhost:8000/api/v1/openapi.json`
   - Postman создаст коллекцию со всеми endpoints

2. Настроить переменные окружения:
   ```json
   {
     "base_url": "http://localhost:8000",
     "api_version": "v1"
   }
   ```

### Создание мок-сервера

Создайте мок-сервер используя спецификацию OpenAPI:

#### Использование Prism
```bash
# Установить Prism
npm install -g @stoplight/prism-cli

# Запустить мок-сервер
prism mock http://localhost:8000/api/v1/openapi.json
```

#### Использование WireMock
```bash
# Скачать WireMock
curl -o wiremock.jar https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-jre8-standalone/2.35.0/wiremock-jre8-standalone-2.35.0.jar

# Запустить с OpenAPI
java -jar wiremock.jar --port 8080 --global-response-templating \
  --extensions com.github.tomakehurst.wiremock.extension.responsetemplating.ResponseTemplateTransformer
```

## Настройка документации OpenAPI

### Добавление метаданных

Документацию OpenAPI можно настроить в главном приложении FastAPI:

```python
from fastapi import FastAPI

app = FastAPI(
    title="API CulicidaeLab Server",
    description="Сложная веб-платформа для исследования комаров, наблюдения и анализа данных",
    version="1.0.0",
    terms_of_service="https://culicidaelab.org/terms/",
    contact={
        "name": "Команда CulicidaeLab",
        "url": "https://culicidaelab.org/contact/",
        "email": "contact@culicidaelab.org",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Виды",
            "description": "Операции с данными видов комаров",
        },
        {
            "name": "Болезни",
            "description": "Информация о болезнях и связях с переносчиками",
        },
        {
            "name": "Предсказание",
            "description": "Идентификация видов с помощью ИИ",
        },
    ]
)
```

### Добавление примеров к endpoints

Улучшите документацию endpoints примерами:

```python
from fastapi import FastAPI, Query
from pydantic import BaseModel

class SpeciesResponse(BaseModel):
    id: str
    scientific_name: str
    common_name: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "aedes-aegypti",
                "scientific_name": "Aedes aegypti",
                "common_name": "Комар желтой лихорадки"
            }
        }

@app.get(
    "/species/{species_id}",
    response_model=SpeciesResponse,
    responses={
        200: {
            "description": "Вид найден успешно",
            "content": {
                "application/json": {
                    "example": {
                        "id": "aedes-aegypti",
                        "scientific_name": "Aedes aegypti",
                        "common_name": "Комар желтой лихорадки",
                        "vector_status": "Основной переносчик"
                    }
                }
            }
        },
        404: {
            "description": "Вид не найден",
            "content": {
                "application/json": {
                    "example": {"detail": "Вид не найден"}
                }
            }
        }
    }
)
async def get_species(species_id: str):
    pass
```

## Настройка Swagger UI

### Пользовательские CSS и JavaScript

Добавьте пользовательскую стилизацию к Swagger UI, обслуживая пользовательские файлы:

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None)  # Отключить документацию по умолчанию
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
        swagger_ui_parameters={"defaultModelsExpandDepth": -1}
    )
```

## Интеграция с MkDocs

### Встраивание Swagger UI

Вы можете встроить Swagger UI прямо в документацию MkDocs:

```markdown
# Документация API

<div id="swagger-ui"></div>

<script src="https://unpkg.com/swagger-ui-dist@3.52.5/swagger-ui-bundle.js"></script>
<script>
SwaggerUIBundle({
  url: 'http://localhost:8000/api/v1/openapi.json',
  dom_id: '#swagger-ui',
  presets: [
    SwaggerUIBundle.presets.apis,
    SwaggerUIBundle.presets.standalone
  ]
});
</script>
```

### Использование плагина swagger-ui-tag

Плагин `swagger-ui-tag` позволяет встраивать Swagger UI простым тегом:

```markdown
# Документация API

{% swagger_ui %}
http://localhost:8000/api/v1/openapi.json
{% endswagger_ui %}
```

## Валидация и тестирование

### Валидация схемы

Используйте спецификацию OpenAPI для валидации запросов/ответов:

```python
import requests
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

# Валидировать спецификацию OpenAPI
spec_dict = requests.get('http://localhost:8000/api/v1/openapi.json').json()
validate_spec(spec_dict)
```

### Автоматизированное тестирование

Генерируйте тестовые случаи из спецификации OpenAPI:

```python
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/api/v1/openapi.json")

@schema.parametrize()
def test_api(case):
    case.call_and_validate()
```

## Лучшие практики

### Руководящие принципы документации

1. **Всеобъемлющие Docstrings**: Пишите детальные docstrings для всех endpoints
2. **Примеры ответов**: Предоставляйте реалистичные примеры для всех ответов
3. **Документация ошибок**: Документируйте все возможные условия ошибок
4. **Описания схем**: Добавляйте описания ко всем полям Pydantic моделей
5. **Теги и организация**: Используйте теги для логической организации endpoints

### Соображения производительности

1. **Кэширование**: Кэшируйте спецификацию OpenAPI для продакшена
2. **Сжатие**: Включите gzip сжатие для спецификации
3. **CDN**: Обслуживайте ресурсы Swagger UI из CDN
4. **Ленивая загрузка**: Загружайте документацию по требованию

### Безопасность

1. **Чувствительные данные**: Никогда не раскрывайте чувствительную информацию в примерах
2. **Аутентификация**: Четко документируйте требования аутентификации
3. **Ограничение скорости**: Документируйте политики ограничения скорости
4. **CORS**: Настройте CORS соответствующим образом для доступа к документации