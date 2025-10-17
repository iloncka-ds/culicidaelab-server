# Руководство по участию в проекте

Добро пожаловать в проект CulicidaeLab Server! Мы ценим ваш интерес к участию в этой открытой платформе для исследования и анализа комаров. Это руководство поможет вам начать эффективно участвовать в проекте.

## Кодекс поведения

Участвуя в этом проекте, вы соглашаетесь соблюдать наш [Кодекс поведения](https://github.com/iloncka-ds/culicidaelab-server/blob/main/CODE_OF_CONDUCT.md). Пожалуйста, прочитайте его, чтобы понимать стандарты, которых мы ожидаем от всех участников.

## Начало работы

### Предварительные требования

Перед участием убедитесь, что у вас есть:

- Python 3.11 или выше
- Установленный и настроенный Git
- Базовые знания фреймворков FastAPI и Solara
- Понимание области исследования комаров (полезно, но не обязательно)

### Настройка среды разработки

1. **Форк и клонирование репозитория**
```bash
# Сделайте форк репозитория на GitHub, затем клонируйте ваш форк
git clone https://github.com/YOUR_USERNAME/culicidaelab-server.git
cd culicidaelab-server

# Добавьте upstream remote
git remote add upstream https://github.com/iloncka-ds/culicidaelab-server.git
```

2. **Настройка среды разработки**
```bash
# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # На Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -e .
# Или с uv: uv sync -p 3.11

# Установка зависимостей разработки
pip install -e ".[dev]"
```

3. **Инициализация базы данных**
```bash
# Генерация примерных данных
python -m backend.data.sample_data.generate_sample_data

# Заполнение базы данных
python -m backend.scripts.populate_lancedb

# Проверка настройки
python -m backend.scripts.query_lancedb observations --limit 5
```

4. **Запуск тестов**
```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=backend --cov=frontend
```

5. **Запуск серверов разработки**
```bash
# Терминал 1: Бэкенд
uvicorn backend.main:app --port 8000 --reload

# Терминал 2: Фронтенд
solara run frontend.main --port 8765
```

## Как участвовать

### Типы вкладов

Мы приветствуем различные типы вкладов:

- **Отчеты об ошибках**: Помогите нам выявить и исправить проблемы
- **Запросы функций**: Предложите новую функциональность
- **Вклады в код**: Реализуйте функции или исправьте ошибки
- **Документация**: Улучшите или добавьте документацию
- **Тестирование**: Добавьте или улучшите покрытие тестами
- **Производительность**: Оптимизируйте существующий код
- **Переводы**: Добавьте поддержку новых языков

### Сообщение о проблемах

При сообщении об ошибках или запросе функций:

1. **Поиск существующих проблем**: Проверьте, не существует ли уже проблема
2. **Используйте шаблоны проблем**: Следуйте предоставленным шаблонам
3. **Предоставьте детали**: Включите шаги воспроизведения, ожидаемое поведение и информацию об окружении
4. **Добавьте метки**: Используйте соответствующие метки для категоризации проблемы

#### Шаблон отчета об ошибке

```markdown
**Описание ошибки**
Четкое описание ошибки.

**Шаги воспроизведения**
1. Перейдите к '...'
2. Нажмите на '...'
3. Увидьте ошибку

**Ожидаемое поведение**
Что вы ожидали увидеть.

**Фактическое поведение**
Что произошло на самом деле.

**Окружение**
- ОС: [например, Windows 11, Ubuntu 22.04]
- Версия Python: [например, 3.11.5]
- Браузер: [например, Chrome 118]

**Дополнительный контекст**
Скриншоты, логи или другая релевантная информация.
```

### Внесение изменений в код

#### Рабочий процесс

1. **Создание ветки**
```bash
# Обновление вашего форка
git fetch upstream
git checkout main
git merge upstream/main

# Создание ветки функции
git checkout -b feature/your-feature-name
# или
git checkout -b fix/issue-number-description
```

2. **Внесение изменений**
   - Следуйте стандартам кодирования (см. ниже)
   - Напишите или обновите тесты
   - Обновите документацию при необходимости
   - Убедитесь, что все тесты проходят

3. **Коммит изменений**
```bash
# Добавление изменений в индекс
git add .

# Коммит с описательным сообщением
git commit -m "feat: добавить кэширование предсказаний видов

- Реализовать LRU кэш для результатов предсказаний
- Добавить инвалидацию кэша при обновлении модели
- Улучшить время ответа предсказаний на 40%

Closes #123"
```

4. **Отправка и создание Pull Request**
```bash
# Отправка в ваш форк
git push origin feature/your-feature-name

# Создание pull request на GitHub
```

#### Соглашение о сообщениях коммитов

Мы следуем спецификации [Conventional Commits](https://www.conventionalcommits.org/):

```
<тип>[опциональная область]: <описание>

[опциональное тело]

[опциональные подвалы]
```

**Типы:**
- `feat`: Новая функция
- `fix`: Исправление ошибки
- `docs`: Изменения документации
- `style`: Изменения стиля кода (форматирование и т.д.)
- `refactor`: Рефакторинг кода
- `test`: Добавление или обновление тестов
- `chore`: Задачи обслуживания

**Примеры:**
```bash
feat(api): добавить endpoint поиска сходства видов
fix(frontend): исправить проблему отрисовки карты на мобильных
docs(readme): обновить инструкции по установке
test(backend): добавить интеграционные тесты для сервиса предсказаний
```

## Стандарты кодирования

### Стиль кода Python

Мы используем несколько инструментов для поддержания качества кода:

- **Black**: Форматирование кода
- **isort**: Сортировка импортов
- **mypy**: Проверка типов
- **flake8**: Линтинг

#### Настройка Pre-commit хуков

```bash
# Установка pre-commit
pip install pre-commit

# Установка хуков
pre-commit install

# Ручной запуск хуков
pre-commit run --all-files
```

#### Форматирование кода

```python
# Хорошо: Четкая, хорошо документированная функция
async def predict_species(
    image_path: str,
    confidence_threshold: float = 0.5
) -> PredictionResult:
    """Предсказать вид комара по изображению.

    Args:
        image_path: Путь к файлу изображения
        confidence_threshold: Минимальная уверенность для предсказания

    Returns:
        Результат предсказания с видом и уверенностью

    Raises:
        ValueError: Если изображение не может быть обработано
        FileNotFoundError: Если файл изображения не существует
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Изображение не найдено: {image_path}")

    try:
        result = await predictor.predict(image_path)
        if result.confidence < confidence_threshold:
            logger.warning(f"Предсказание с низкой уверенностью: {result.confidence}")

        return PredictionResult(
            species=result.species,
            confidence=result.confidence,
            alternatives=result.alternatives
        )
    except Exception as e:
        logger.error(f"Предсказание не удалось для {image_path}: {e}")
        raise ValueError(f"Не удалось предсказать вид: {e}")
```

#### Аннотации типов

Используйте аннотации типов по всей кодовой базе:

```python
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

class SpeciesInfo(BaseModel):
    """Модель информации о виде."""
    id: str
    scientific_name: str
    common_names: Dict[str, str]
    distribution: Optional[List[str]] = None

async def get_species_by_region(
    region: str,
    limit: int = 10
) -> List[SpeciesInfo]:
    """Получить виды, найденные в определенном регионе."""
    # Реализация здесь
    pass
```

### Стиль кода фронтенда

#### Руководящие принципы компонентов Solara

```python
import solara
from typing import Callable, Optional

@solara.component
def SpeciesCard(
    species: dict,
    on_click: Optional[Callable[[str], None]] = None,
    show_details: bool = True
):
    """Переиспользуемый компонент карточки вида.

    Args:
        species: Словарь информации о виде
        on_click: Callback при клике на карточку
        show_details: Показывать ли детальную информацию
    """

    def handle_click():
        if on_click:
            on_click(species["id"])

    with solara.Card(
        title=species["scientific_name"],
        on_click=handle_click if on_click else None
    ):
        if show_details:
            solara.Text(species.get("description", ""))

        # Отображение общих названий
        common_names = species.get("common_names", {})
        if common_names:
            for lang, name in common_names.items():
                solara.Text(f"{lang.upper()}: {name}")
```

#### Управление состоянием

```python
# Хорошо: Четкая организация состояния
import solara
from typing import List, Optional

# Глобальное состояние приложения
current_user_id: solara.Reactive[Optional[str]] = solara.reactive(None)
selected_species: solara.Reactive[List[str]] = solara.reactive([])
loading_states = {
    'species': solara.reactive(False),
    'predictions': solara.reactive(False)
}

@solara.component
def use_species_data():
    """Хук для управления данными видов."""
    data, set_data = solara.use_state([])
    error, set_error = solara.use_state(None)

    async def fetch_data():
        loading_states['species'].value = True
        set_error(None)

        try:
            # Логика получения данных
            result = await api_client.get_species()
            set_data(result)
        except Exception as e:
            set_error(str(e))
        finally:
            loading_states['species'].value = False

    return data, fetch_data, error
```

### Руководящие принципы базы данных

#### Лучшие практики LanceDB

```python
# Хорошо: Эффективные операции с базой данных
from backend.services.database import get_db, get_table
from typing import List, Dict, Any

class SpeciesRepository:
    """Репозиторий для операций с данными видов."""

    def __init__(self):
        self.db = get_db()
        self.table = get_table(self.db, "species")

    async def search_by_region(
        self,
        region: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Поиск видов по региону с эффективными запросами."""
        try:
            results = (
                self.table
                .search()
                .where(f"region = '{region}'")
                .limit(limit)
                .select(["id", "scientific_name", "common_names"])  # Выбрать только нужные поля
                .to_list()
            )
            return results
        except Exception as e:
            logger.error(f"Не удалось найти виды по региону {region}: {e}")
            raise

    async def similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Выполнить векторный поиск по сходству."""
        try:
            results = (
                self.table
                .search(query_vector)
                .limit(limit)
                .to_list()
            )
            return results
        except Exception as e:
            logger.error(f"Поиск по сходству не удался: {e}")
            raise
```

## Требования к тестированию

### Покрытие тестами

Все вклады должны включать соответствующие тесты:

- **Новые функции**: Всестороннее покрытие тестами (>90%)
- **Исправления ошибок**: Тесты, которые воспроизводят ошибку и проверяют исправление
- **Рефакторинг**: Существующие тесты должны продолжать проходить

### Типы тестов

1. **Модульные тесты**: Тестирование отдельных функций/методов
2. **Интеграционные тесты**: Тестирование взаимодействий компонентов
3. **API тесты**: Тестирование функциональности endpoints
4. **Тесты фронтенда**: Тестирование поведения компонентов

### Пример структуры теста

```python
# tests/backend/test_services/test_species_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.species_service import SpeciesService

class TestSpeciesService:
    """Набор тестов для SpeciesService."""

    @pytest.fixture
    def species_service(self):
        """Создать сервис видов с замоканными зависимостями."""
        with patch('backend.services.species_service.get_db'):
            return SpeciesService()

    @pytest.mark.asyncio
    async def test_get_species_by_id_success(self, species_service):
        """Тест успешного получения вида."""
        # Arrange
        expected_species = {"id": "aedes_aegypti", "name": "Aedes aegypti"}

        # Act
        result = await species_service.get_by_id("aedes_aegypti")

        # Assert
        assert result is not None
        assert result.id == "aedes_aegypti"

    @pytest.mark.asyncio
    async def test_get_species_not_found(self, species_service):
        """Тест обработки несуществующего вида."""
        with pytest.raises(ValueError, match="Вид .* не найден"):
            await species_service.get_by_id("nonexistent")
```

## Стандарты документации

### Документация кода

- **Docstrings**: Все публичные функции, классы и модули
- **Аннотации типов**: Использовать по всей кодовой базе
- **Комментарии**: Объяснять сложную логику, а не очевидный код
- **Обновления README**: Обновлять релевантную документацию

### Документация API

- **OpenAPI**: Убедиться, что FastAPI генерирует точную документацию API
- **Примеры**: Включать примеры запросов/ответов
- **Коды ошибок**: Документировать все возможные ответы с ошибками

### Пользовательская документация

- **Документация функций**: Документировать новые пользовательские функции
- **Скриншоты**: Включать визуальные руководства где полезно
- **Туториалы**: Пошаговые руководства для сложных функций

## Процесс Pull Request

### Перед отправкой

1. **Rebase на последний Main**
```bash
git fetch upstream
git rebase upstream/main
```

2. **Запуск полного набора тестов**
```bash
pytest --cov=backend --cov=frontend
```

3. **Проверка качества кода**
```bash
black .
isort .
mypy backend/ frontend/
flake8 backend/ frontend/
```

4. **Обновление документации**
   - Обновить релевантную документацию
   - Добавить docstrings для новых функций
   - Обновить документацию API при необходимости

### Шаблон Pull Request

```markdown
## Описание
Краткое описание внесенных изменений.

## Тип изменения
- [ ] Исправление ошибки (неразрушающее изменение, которое исправляет проблему)
- [ ] Новая функция (неразрушающее изменение, которое добавляет функциональность)
- [ ] Разрушающее изменение (исправление или функция, которая приведет к неработоспособности существующей функциональности)
- [ ] Обновление документации

## Тестирование
- [ ] Тесты проходят локально
- [ ] Новые тесты добавлены для новой функциональности
- [ ] Покрытие тестами поддерживается или улучшается

## Чек-лист
- [ ] Код следует руководящим принципам стиля проекта
- [ ] Самопроверка завершена
- [ ] Документация обновлена
- [ ] Новые предупреждения не введены

## Связанные проблемы
Closes #123
Related to #456
```

### Процесс рецензирования

1. **Автоматические проверки**: CI/CD пайплайн запускает тесты и проверки качества
2. **Рецензирование кода**: Мейнтейнеры рецензируют код на качество и дизайн
3. **Обратная связь**: Обработать комментарии и предложения рецензентов
4. **Одобрение**: Требуется одобрение как минимум одного мейнтейнера
5. **Слияние**: Мейнтейнер сливает после прохождения всех проверок

## Процесс релиза

### Версионирование

Мы следуем [Семантическому версионированию](https://semver.org/):

- **MAJOR**: Разрушающие изменения
- **MINOR**: Новые функции (обратно совместимые)
- **PATCH**: Исправления ошибок (обратно совместимые)

### Чек-лист релиза

1. Обновить номера версий
2. Обновить CHANGELOG.md
3. Создать заметки о релизе
4. Пометить релиз тегом
5. Развернуть в продакшн

## Руководящие принципы сообщества

### Коммуникация

- **GitHub Issues**: Отчеты об ошибках и запросы функций
- **Discussions**: Общие вопросы и идеи


### Получение помощи

- **Документация**: Сначала проверьте существующую документацию
- **Поиск проблем**: Ищите похожие проблемы
- **Задавайте вопросы**: Создайте обсуждение для получения помощи
- **Будьте терпеливы**: Мейнтейнеры - волонтеры

### Признание

Участники признаются в:
- Файле CONTRIBUTORS.md
- Заметках о релизе
- Документации проекта
- Ежегодных обзорах участников

## Безопасность

### Сообщение о проблемах безопасности

**Не сообщайте об уязвимостях безопасности через публичные GitHub issues.**

Вместо этого отправьте email на security@culicidaelab.org с:
- Описанием уязвимости
- Шагами воспроизведения
- Потенциальным воздействием
- Предлагаемым исправлением (если есть)

### Лучшие практики безопасности

- Никогда не коммитьте секреты или API ключи
- Валидируйте все пользовательские входные данные
- Используйте параметризованные запросы
- Следуйте руководящим принципам OWASP
- Поддерживайте зависимости в актуальном состоянии

## Лицензия

Участвуя в CulicidaeLab Server, вы соглашаетесь, что ваши вклады будут лицензированы под лицензией AGPL-3.0. См. [LICENSE](https://github.com/iloncka-ds/culicidaelab-server/blob/main/LICENSE) для деталей.

## Вопросы?

Если у вас есть вопросы об участии:

1. Проверьте [FAQ](../user-guide/troubleshooting.md)
2. Поищите существующие [GitHub Issues](https://github.com/iloncka-ds/culicidaelab-server/issues)
3. Создайте новое [Обсуждение](https://github.com/iloncka-ds/culicidaelab-server/discussions)
4. Свяжитесь с мейнтейнерами по email

Спасибо за участие в CulicidaeLab Server! Ваши усилия помогают продвигать исследования комаров и инициативы общественного здравоохранения по всему миру.
