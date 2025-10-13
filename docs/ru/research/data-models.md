# Модели Данных

Этот документ предоставляет исчерпывающую документацию схемы базы данных и структур данных, используемых в платформе CulicidaeLab Server.

## Обзор

CulicidaeLab использует LanceDB в качестве основной базы данных для хранения данных исследований комаров. Система использует схемы PyArrow для определения структурированных моделей данных, которые поддерживают как векторные операции, так и традиционные реляционные запросы.

## Архитектура Базы Данных

### Конфигурация LanceDB

Система использует LanceDB, векторную базу данных, оптимизированную для ИИ приложений, со следующей конфигурацией:

- **Путь к Базе Данных**: Настраивается через переменную окружения `CULICIDAELAB_DATABASE_PATH` (по умолчанию: `.lancedb`)
- **Определение Схемы**: Схемы PyArrow для безопасности типов и производительности
- **Управление Соединениями**: Асинхронный пул соединений с автоматическим переподключением

### Основные Модели Данных

## Модель Данных Видов

Таблица видов хранит исчерпывающую информацию о видах комаров, включая многоязычную поддержку и статус переносчика.

```python
SPECIES_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("scientific_name", pa.string()),
    pa.field("image_url", pa.string()),
    pa.field("vector_status", pa.string()),
    # Локализованные поля (английский/русский)
    pa.field("common_name_en", pa.string()),
    pa.field("common_name_ru", pa.string()),
    pa.field("description_en", pa.string()),
    pa.field("description_ru", pa.string()),
    pa.field("key_characteristics_en", pa.list_(pa.string())),
    pa.field("key_characteristics_ru", pa.list_(pa.string())),
    pa.field("habitat_preferences_en", pa.list_(pa.string())),
    pa.field("habitat_preferences_ru", pa.list_(pa.string())),
    # Реляционные поля
    pa.field("geographic_regions", pa.list_(pa.string())),
    pa.field("related_diseases", pa.list_(pa.string())),
    pa.field("related_diseases_info", pa.list_(pa.string())),
])
```

### Ключевые Особенности:
- **Многоязычная Поддержка**: Локализация на английском и русском языках для всех описательных полей
- **Статус Переносчика**: Классификация риска передачи заболеваний (Высокий, Умеренный, Низкий)
- **Географическое Распространение**: Список регионов, где встречается вид
- **Связи с Заболеваниями**: Ссылки на заболевания, передаваемые видом

### Пример Записи Вида:
```json
{
  "id": "aedes_aegypti",
  "scientific_name": "Aedes aegypti",
  "vector_status": "High",
  "common_name_en": "Yellow Fever Mosquito",
  "common_name_ru": "Комар желтой лихорадки",
  "geographic_regions": ["asia", "americas", "africa", "oceania"],
  "related_diseases": ["dengue_fever", "yellow_fever", "chikungunya", "zika_virus"]
}
```

## Модель Данных Заболеваний

Таблица заболеваний содержит информацию о заболеваниях, переносимых комарами, с многоязычными описаниями и связями с переносчиками.

```python
DISEASES_SCHEMA = pa.schema([
    pa.field("id", pa.string(), nullable=False),
    pa.field("image_url", pa.string()),
    # Локализованные поля
    pa.field("name_en", pa.string()),
    pa.field("name_ru", pa.string()),
    pa.field("description_en", pa.string()),
    pa.field("description_ru", pa.string()),
    pa.field("symptoms_en", pa.string()),
    pa.field("symptoms_ru", pa.string()),
    pa.field("treatment_en", pa.string()),
    pa.field("treatment_ru", pa.string()),
    pa.field("prevention_en", pa.string()),
    pa.field("prevention_ru", pa.string()),
    pa.field("prevalence_en", pa.string()),
    pa.field("prevalence_ru", pa.string()),
    # Связи с переносчиками
    pa.field("vectors", pa.list_(pa.string())),
])
```

### Ключевые Особенности:
- **Исчерпывающая Медицинская Информация**: Симптомы, лечение и профилактика на нескольких языках
- **Эпидемиологические Данные**: Информация о распространенности и географическом распределении
- **Картирование Переносчиков**: Ссылки на виды комаров, которые передают заболевание

## Модель Данных Наблюдений

Таблица наблюдений хранит данные полевых наблюдений с геопространственной информацией и метаданными предсказаний.

```python
OBSERVATIONS_SCHEMA = pa.schema([
    pa.field("type", pa.string()),
    pa.field("id", pa.string(), nullable=False),
    pa.field("species_scientific_name", pa.string()),
    pa.field("observed_at", pa.string()),
    pa.field("count", pa.int32()),
    pa.field("observer_id", pa.string()),
    pa.field("location_accuracy_m", pa.float32()),
    pa.field("notes", pa.string()),
    pa.field("data_source", pa.string()),
    pa.field("image_filename", pa.string()),
    pa.field("model_id", pa.string()),
    pa.field("confidence", pa.float32()),
    pa.field("geometry_type", pa.string()),
    pa.field("coordinates", pa.list_(pa.float32())),
    pa.field("metadata", pa.string()),
])
```

### Ключевые Особенности:
- **Геопространственные Данные**: Хранение координат, совместимое с GeoJSON
- **Интеграция ИИ**: Предсказания модели с оценками уверенности
- **Происхождение Данных**: Отслеживание источника и информации о наблюдателе
- **Гибкие Метаданные**: JSON хранение для дополнительных деталей наблюдения

## Модели Схемы API

Система использует модели Pydantic для валидации запросов/ответов API и документации.

### Модели Наблюдений

```python
class Location(BaseModel):
    """Модель географического местоположения."""
    lat: float
    lng: float

class ObservationBase(BaseModel):
    """Базовые данные наблюдения."""
    type: str = "Feature"
    species_scientific_name: str
    count: int = Field(..., gt=0)
    location: Location
    observed_at: str
    notes: str | None = None
    user_id: str | None = None
    location_accuracy_m: int | None = None
    data_source: str | None = None

class Observation(ObservationBase):
    """Полное наблюдение с системными полями."""
    id: UUID = Field(default_factory=uuid4)
    image_filename: str | None = None
    model_id: str | None = None
    confidence: float | None = None
    metadata: dict[str, Any] | None = {}
```

### Модели Предсказаний

```python
class PredictionResult(BaseModel):
    """Результат предсказания ИИ модели."""
    id: str
    scientific_name: str
    probabilities: dict[str, float]
    model_id: str
    confidence: float
    image_url_species: str | None = None
```

### Модели Видов

```python
class SpeciesBase(BaseModel):
    """Базовая информация о виде."""
    id: str
    scientific_name: str
    common_name: str | None = None
    vector_status: str | None = None
    image_url: str | None = None

class SpeciesDetail(SpeciesBase):
    """Расширенная информация о виде."""
    description: str | None = None
    key_characteristics: list[str] | None = None
    geographic_regions: list[str] | None = None
    related_diseases: list[str] | None = None
    habitat_preferences: list[str] | None = None
```

## Связи Данных

### Связи Вид-Заболевание
- **Многие-ко-Многим**: Виды могут передавать множественные заболевания, заболевания могут передаваться множественными видами
- **Реализация**: Поля массивов в записях как видов, так и заболеваний
- **Двунаправленность**: Связи поддерживаются в обоих направлениях для эффективности запросов

### Связи Наблюдение-Вид
- **Многие-к-Одному**: Множественные наблюдения могут ссылаться на один и тот же вид
- **Внешний Ключ**: Поле `species_scientific_name` связывает с таблицей видов
- **Валидация**: Слой API обеспечивает существование вида перед созданием наблюдений

### Географические Связи
- **Иерархические**: Регионы могут содержать подрегионы
- **Гибкие**: Строковые идентификаторы регионов позволяют различные географические масштабы
- **Расширяемые**: Новые регионы могут быть добавлены без изменений схемы

## Валидация Данных и Ограничения

### Валидация Полей
- **Обязательные Поля**: Поля, не допускающие null, принудительно применяются на уровне схемы
- **Безопасность Типов**: Схемы PyArrow обеспечивают согласованность типов
- **Валидация Диапазона**: Модели Pydantic предоставляют дополнительную валидацию (например, count > 0)

### Целостность Данных
- **Генерация UUID**: Автоматическая генерация уникальных идентификаторов для наблюдений
- **Валидация Временных Меток**: Строки datetime в формате ISO
- **Валидация Координат**: Проверка границ географических координат

### Многоязычная Согласованность
- **Парность Полей**: Английские и русские поля поддерживаются вместе
- **Логика Отката**: Слой API предоставляет откат к английскому, если локализованный контент отсутствует
- **Валидация**: Обеспечивает существование хотя бы одной языковой версии для обязательных полей

## Соображения Производительности

### Стратегия Индексирования
- **Первичные Ключи**: Автоматическое индексирование полей ID
- **Географические Запросы**: Пространственное индексирование для поисков на основе координат
- **Текстовый Поиск**: Полнотекстовое индексирование названий и описаний видов

### Оптимизация Запросов
- **Пакетные Операции**: Операции массовой вставки/обновления для больших наборов данных
- **Ленивая Загрузка**: Поддержка пагинации для больших наборов результатов
- **Кэширование**: Кэширование на уровне приложения для часто запрашиваемых данных

### Эффективность Хранения
- **Колоночное Хранение**: Колоночный формат LanceDB оптимизирует для аналитических запросов
- **Сжатие**: Автоматическое сжатие для текстовых и массивных полей
- **Векторное Хранение**: Оптимизированное хранение для вложений ИИ модели (будущее улучшение)