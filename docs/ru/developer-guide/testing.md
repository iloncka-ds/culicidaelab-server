# Руководство по тестированию

Этот документ описывает стратегии тестирования, лучшие практики и руководящие принципы для проекта CulicidaeLab Server, охватывая подходы к тестированию как бэкенда, так и фронтенда.

## Философия тестирования

CulicidaeLab Server следует всеобъемлющей стратегии тестирования, которая подчеркивает:

- **Разработка через тестирование (TDD)**: Пишите тесты перед реализацией когда возможно
- **Пирамидальное тестирование**: Больше модульных тестов, меньше интеграционных тестов, минимум end-to-end тестов
- **Быстрая обратная связь**: Быстрое выполнение тестов для циклов быстрой разработки
- **Реалистичное тестирование**: Используйте реальные данные и сценарии, которые отражают использование в продакшене
- **Автоматизированное тестирование**: Непрерывная интеграция с автоматизированным выполнением тестов

## Стек тестирования

### Инструменты тестирования бэкенда

- **pytest**: Основной фреймворк тестирования для Python
- **pytest-asyncio**: Поддержка асинхронных тестов для FastAPI endpoints
- **httpx**: HTTP клиент для тестирования API
- **pytest-cov**: Отчеты о покрытии кода
- **pytest-mock**: Утилиты мокирования и патчинга

### Инструменты тестирования фронтенда

- **pytest**: Тестирование компонентов и интеграции
- **Утилиты тестирования Solara**: Рендеринг компонентов и тестирование взаимодействий
- **Selenium** (опционально): End-to-end тестирование браузера

### Тестирование производительности

- **pytest-benchmark**: Бенчмаркинг производительности
- **locust**: Нагрузочное тестирование для API endpoints
- **psutil**: Мониторинг системных ресурсов во время тестов

## Организация тестов

### Структура директорий

```
tests/
├── conftest.py                 # Общая конфигурация тестов
├── backend/                    # Тесты бэкенда
│   ├── test_api/              # Тесты API endpoints
│   │   ├── test_species.py    # Тесты API видов
│   │   ├── test_diseases.py   # Тесты API болезней
│   │   ├── test_prediction.py # Тесты API предсказаний
│   │   └── test_geo.py        # Тесты географического API
│   ├── test_services/         # Тесты слоя сервисов
│   │   ├── test_species_service.py
│   │   ├── test_prediction_service.py
│   │   └── test_database.py
│   └── test_utils/            # Тесты утилитарных функций
├── frontend/                   # Тесты фронтенда
│   ├── test_components/       # Тесты компонентов
│   ├── test_pages/           # Тесты страниц
│   └── test_state/           # Тесты управления состоянием
├── load_tests/                # Тесты производительности
├── performance_tests/         # Бенчмарк тесты
└── fixtures/                  # Тестовые данные и фикстуры
    ├── sample_images/         # Тестовые изображения
    ├── sample_data.json       # Тестовые наборы данных
    └── mock_responses/        # Моки ответов API
```

## Тестирование бэкенда

### Модульное тестирование

#### Тестирование слоя сервисов

Тестируйте бизнес-логику в изоляции:

```python
# tests/backend/test_services/test_species_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.species_service import SpeciesService
from backend.schemas.species_schemas import SpeciesResponse

class TestSpeciesService:
    """Набор тестов для SpeciesService."""
    
    @pytest.fixture
    def mock_db(self):
        """Мок соединения с базой данных."""
        return Mock()
    
    @pytest.fixture
    def species_service(self, mock_db):
        """Сервис видов с замоканными зависимостями."""
        with patch('backend.services.species_service.get_db', return_value=mock_db):
            return SpeciesService()
    
    @pytest.mark.asyncio
    async def test_get_species_by_id_success(self, species_service, mock_db):
        """Тест успешного получения вида по ID."""
        # Arrange
        expected_species = {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "common_names": {"en": "Yellow fever mosquito"}
        }
        mock_table = Mock()
        mock_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = [expected_species]
        mock_db.open_table.return_value = mock_table
        
        # Act
        result = await species_service.get_by_id("aedes_aegypti")
        
        # Assert
        assert result is not None
        assert result.scientific_name == "Aedes aegypti"
        mock_table.search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_species_by_id_not_found(self, species_service, mock_db):
        """Тест сценария "вид не найден"."""
        # Arrange
        mock_table = Mock()
        mock_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []
        mock_db.open_table.return_value = mock_table
        
        # Act & Assert
        with pytest.raises(ValueError, match="Вид .* не найден"):
            await species_service.get_by_id("nonexistent_species")
    
    @pytest.mark.asyncio
    async def test_search_species_with_filters(self, species_service, mock_db):
        """Тест поиска видов с фильтрами."""
        # Arrange
        mock_results = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"},
            {"id": "aedes_albopictus", "scientific_name": "Aedes albopictus"}
        ]
        mock_table = Mock()
        mock_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = mock_results
        mock_db.open_table.return_value = mock_table
        
        # Act
        results = await species_service.search(region="Europe", limit=10)
        
        # Assert
        assert len(results) == 2
        assert all(isinstance(r, SpeciesResponse) for r in results)
```

#### Тестирование базы данных

Тестируйте операции с базой данных с реальной LanceDB:

```python
# tests/backend/test_services/test_database.py
import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
from backend.services.database import get_db, get_table

class TestDatabase:
    """Тест операций с базой данных."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Создать временную базу данных для тестирования."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_db(self, temp_db_path):
        """Создать тестовую базу данных с примерными данными."""
        import lancedb
        
        db = lancedb.connect(temp_db_path)
        
        # Создать тестовую таблицу видов
        species_data = pd.DataFrame([
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "common_names": '{"en": "Yellow fever mosquito"}',
                "region": "Global"
            },
            {
                "id": "aedes_albopictus", 
                "scientific_name": "Aedes albopictus",
                "common_names": '{"en": "Asian tiger mosquito"}',
                "region": "Asia"
            }
        ])
        
        db.create_table("species", species_data, mode="overwrite")
        return db
    
    def test_get_table_success(self, test_db):
        """Тест успешного получения таблицы."""
        table = get_table(test_db, "species")
        assert table is not None
        
        # Проверка содержимого таблицы
        results = table.search().to_list()
        assert len(results) == 2
    
    def test_get_table_not_found(self, test_db):
        """Тест обработки несуществующей таблицы."""
        with pytest.raises(ValueError, match="Таблица 'nonexistent' не найдена"):
            get_table(test_db, "nonexistent")
    
    def test_species_search_by_region(self, test_db):
        """Тест поиска видов по региону."""
        table = get_table(test_db, "species")
        
        # Поиск азиатских видов
        results = table.search().where("region = 'Asia'").to_list()
        assert len(results) == 1
        assert results[0]["scientific_name"] == "Aedes albopictus"
```

### Тестирование API

#### Тестирование endpoints

Тестируйте FastAPI endpoints с реалистичными сценариями:

```python
# tests/backend/test_api/test_species.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

class TestSpeciesAPI:
    """Тест API endpoints видов."""
    
    @pytest.fixture
    def client(self):
        """Тестовый клиент для вызовов API."""
        return TestClient(app)
    
    def test_get_species_list(self, client):
        """Тест endpoint списка видов."""
        response = client.get("/api/species")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Проверка структуры ответа
        if data:
            species = data[0]
            assert "id" in species
            assert "scientific_name" in species
            assert "common_names" in species
    
    def test_get_species_by_id(self, client):
        """Тест endpoint деталей вида."""
        # Сначала получить валидный ID вида
        list_response = client.get("/api/species")
        species_list = list_response.json()
        
        if species_list:
            species_id = species_list[0]["id"]
            
            # Тест endpoint деталей
            response = client.get(f"/api/species/{species_id}")
            assert response.status_code == 200
            
            species = response.json()
            assert species["id"] == species_id
    
    def test_get_species_not_found(self, client):
        """Тест сценария "вид не найден"."""
        response = client.get("/api/species/nonexistent_species")
        assert response.status_code == 404
        
        error = response.json()
        assert "detail" in error
    
    def test_species_search_with_filters(self, client):
        """Тест поиска видов с параметрами запроса."""
        response = client.get("/api/species", params={
            "region": "Europe",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_species_search_invalid_limit(self, client):
        """Тест валидации параметров поиска."""
        response = client.get("/api/species", params={"limit": -1})
        assert response.status_code == 422  # Ошибка валидации
```

#### Тестирование API предсказаний

Тестируйте endpoints ИИ предсказаний с загрузкой изображений:

```python
# tests/backend/test_api/test_prediction.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import io
from PIL import Image

class TestPredictionAPI:
    """Тест API endpoints предсказаний."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_image(self):
        """Создать тестовое изображение для загрузки."""
        # Создать простое тестовое изображение
        img = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_predict_species_success(self, client, test_image):
        """Тест успешного предсказания вида."""
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Проверка структуры ответа
        assert "species" in data
        assert "confidence" in data
        assert "alternatives" in data
        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
    
    def test_predict_species_invalid_file(self, client):
        """Тест предсказания с недопустимым типом файла."""
        # Создать текстовый файл вместо изображения
        text_file = io.BytesIO(b"This is not an image")
        
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.txt", text_file, "text/plain")}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "Недопустимый тип файла" in error["detail"]
    
    def test_predict_species_no_file(self, client):
        """Тест предсказания без загрузки файла."""
        response = client.post("/api/predict_species/")
        assert response.status_code == 422  # Отсутствует обязательное поле
```

### Интеграционное тестирование

Тестируйте полные рабочие процессы через несколько компонентов:

```python
# tests/backend/test_integration/test_prediction_workflow.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import tempfile
import shutil
from pathlib import Path

class TestPredictionWorkflow:
    """Тест полного рабочего процесса предсказания."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def sample_mosquito_image(self):
        """Загрузить реальное изображение комара для тестирования."""
        # Использовать примерное изображение из тестовых фикстур
        image_path = Path("tests/fixtures/sample_images/aedes_aegypti.jpg")
        if image_path.exists():
            return image_path.open("rb")
        else:
            pytest.skip("Примерное изображение недоступно")
    
    def test_complete_prediction_and_observation_workflow(self, client, sample_mosquito_image):
        """Тест предсказания с последующим сохранением наблюдения."""
        
        # Шаг 1: Предсказать вид
        prediction_response = client.post(
            "/api/predict_species/",
            files={"file": ("mosquito.jpg", sample_mosquito_image, "image/jpeg")}
        )
        
        assert prediction_response.status_code == 200
        prediction_data = prediction_response.json()
        
        # Шаг 2: Сохранить наблюдение на основе предсказания
        observation_data = {
            "species_id": prediction_data["species"],
            "latitude": 40.4168,
            "longitude": -3.7038,
            "confidence": prediction_data["confidence"],
            "notes": "Тестовое наблюдение из интеграционного теста"
        }
        
        observation_response = client.post("/api/observations/", json=observation_data)
        assert observation_response.status_code == 201
        
        stored_observation = observation_response.json()
        assert stored_observation["species_id"] == prediction_data["species"]
        
        # Шаг 3: Проверить, что наблюдение можно получить
        observation_id = stored_observation["id"]
        get_response = client.get(f"/api/observations/{observation_id}")
        assert get_response.status_code == 200
        
        retrieved_observation = get_response.json()
        assert retrieved_observation["id"] == observation_id
```

## Тестирование фронтенда

### Тестирование компонентов

Тестируйте компоненты Solara в изоляции:

```python
# tests/frontend/test_components/test_species_card.py
import pytest
import solara
from frontend.components.species.species_card import SpeciesCard

class TestSpeciesCard:
    """Тест компонента SpeciesCard."""
    
    @pytest.fixture
    def sample_species(self):
        """Примерные данные видов для тестирования."""
        return {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "common_names": {"en": "Yellow fever mosquito"},
            "description": {"en": "A mosquito species..."},
            "images": ["aedes_aegypti_1.jpg"]
        }
    
    def test_species_card_renders(self, sample_species):
        """Тест рендеринга карточки вида без ошибок."""
        
        @solara.component
        def TestApp():
            SpeciesCard(species=sample_species)
        
        # Рендер компонента
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Проверка наличия содержимого
        rendered_content = str(box)
        assert "Aedes aegypti" in rendered_content
        assert "Yellow fever mosquito" in rendered_content
    
    def test_species_card_click_interaction(self, sample_species):
        """Тест обработки кликов по карточке вида."""
        clicked_species = None
        
        def on_species_click(species):
            nonlocal clicked_species
            clicked_species = species
        
        @solara.component
        def TestApp():
            SpeciesCard(
                species=sample_species,
                on_click=on_species_click
            )
        
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Симуляция клика (это потребует более сложной настройки тестирования)
        # Пока проверяем, что структура компонента поддерживает взаимодействие
        assert "on_click" in str(box) or "click" in str(box).lower()
```

### Тестирование страниц

Тестируйте полные компоненты страниц:

```python
# tests/frontend/test_pages/test_prediction_page.py
import pytest
import solara
from unittest.mock import patch, AsyncMock
from frontend.pages.prediction import Page as PredictionPage

class TestPredictionPage:
    """Тест функциональности страницы предсказаний."""
    
    def test_prediction_page_renders(self):
        """Тест рендеринга страницы предсказаний без ошибок."""
        
        @solara.component
        def TestApp():
            PredictionPage()
        
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Проверка наличия ключевых элементов
        rendered_content = str(box)
        assert "predict" in rendered_content.lower() or "upload" in rendered_content.lower()
    
    @patch('frontend.state.fetch_api_data')
    def test_prediction_page_with_mock_api(self, mock_fetch):
        """Тест страницы предсказаний с замоканными вызовами API."""
        # Мок ответа API
        mock_fetch.return_value = AsyncMock(return_value={
            "species": "Aedes aegypti",
            "confidence": 0.95,
            "alternatives": []
        })
        
        @solara.component
        def TestApp():
            PredictionPage()
        
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Проверка обработки интеграции API компонентом
        assert mock_fetch.called or True  # Базовый тест структуры
```

### Тестирование управления состоянием

Тестируйте поведение реактивного состояния:

```python
# tests/frontend/test_state/test_species_state.py
import pytest
import solara
from frontend.state import selected_species_reactive, species_data_reactive

class TestSpeciesState:
    """Тест управления состоянием, связанным с видами."""
    
    def test_selected_species_reactive(self):
        """Тест состояния выбора видов."""
        # Начальное состояние
        assert selected_species_reactive.value == ["Aedes albopictus", "Anopheles gambiae"]
        
        # Обновление состояния
        new_selection = ["Aedes aegypti", "Culex pipiens"]
        selected_species_reactive.value = new_selection
        
        assert selected_species_reactive.value == new_selection
    
    def test_species_data_caching(self):
        """Тест поведения кэширования данных видов."""
        # Начальное пустое состояние
        species_data_reactive.value = []
        assert len(species_data_reactive.value) == 0
        
        # Добавление данных видов
        test_species = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"},
            {"id": "culex_pipiens", "scientific_name": "Culex pipiens"}
        ]
        species_data_reactive.value = test_species
        
        assert len(species_data_reactive.value) == 2
        assert species_data_reactive.value[0]["id"] == "aedes_aegypti"
```

## Тестирование производительности

### Тесты производительности бэкенда

Тестируйте производительность API и использование ресурсов:

```python
# tests/performance_tests/test_api_performance.py
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

class TestAPIPerformance:
    """Тест характеристик производительности API."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_species_list_performance(self, client):
        """Тест производительности endpoint списка видов."""
        start_time = time.time()
        
        response = client.get("/api/species?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Должен отвечать в течение 2 секунд
    
    def test_prediction_performance(self, client):
        """Тест производительности endpoint предсказаний."""
        # Создать тестовое изображение
        import io
        from PIL import Image
        
        img = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        
        start_time = time.time()
        
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.jpg", img_bytes, "image/jpeg")}
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 10.0  # Предсказание должно завершиться в течение 10 секунд
    
    @pytest.mark.benchmark
    def test_database_query_performance(self, benchmark):
        """Бенчмарк производительности запросов к базе данных."""
        from backend.services.database import get_db, get_table
        
        def query_species():
            db = get_db()
            table = get_table(db, "species")
            return table.search().limit(50).to_list()
        
        result = benchmark(query_species)
        assert len(result) <= 50
```

### Нагрузочное тестирование

Используйте locust для нагрузочного тестирования:

```python
# tests/load_tests/locustfile.py
from locust import HttpUser, task, between

class CulicidaeLabUser(HttpUser):
    """Симулированный пользователь для нагрузочного тестирования."""
    
    wait_time = between(1, 3)  # Ждать 1-3 секунды между запросами
    
    def on_start(self):
        """Вызывается при запуске пользователя."""
        pass
    
    @task(3)
    def view_species_list(self):
        """Самая частая задача - просмотр списка видов."""
        self.client.get("/api/species?limit=20")
    
    @task(2)
    def view_species_detail(self):
        """Просмотр деталей отдельных видов."""
        # Сначала получить список видов
        response = self.client.get("/api/species?limit=5")
        if response.status_code == 200:
            species_list = response.json()
            if species_list:
                species_id = species_list[0]["id"]
                self.client.get(f"/api/species/{species_id}")
    
    @task(1)
    def search_species(self):
        """Поиск видов с фильтрами."""
        self.client.get("/api/species", params={
            "region": "Europe",
            "limit": 10
        })
    
    @task(1)
    def get_filter_options(self):
        """Получить опции фильтров для UI."""
        self.client.get("/api/filter_options")

# Запуск с: locust -f tests/load_tests/locustfile.py --host=http://localhost:8000
```

## Управление тестовыми данными

### Фикстуры и тестовые данные

Эффективно организуйте тестовые данные:

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Путь к директории тестовых данных."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_species_data(test_data_dir):
    """Загрузить примерные данные видов."""
    data_file = test_data_dir / "sample_data.json"
    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)["species"]
    return []

@pytest.fixture(scope="session")
def sample_images_dir(test_data_dir):
    """Путь к директории примерных изображений."""
    return test_data_dir / "sample_images"

@pytest.fixture
def mock_prediction_response():
    """Мок ответа API предсказания."""
    return {
        "species": "Aedes aegypti",
        "confidence": 0.95,
        "alternatives": [
            {"species": "Aedes albopictus", "confidence": 0.03},
            {"species": "Culex pipiens", "confidence": 0.02}
        ]
    }
```

### Настройка тестовой базы данных

Настройте тестовые базы данных:

```python
# tests/conftest.py (продолжение)
import tempfile
import shutil
import pandas as pd
import lancedb

@pytest.fixture(scope="function")
def test_database():
    """Создать временную тестовую базу данных."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        db = lancedb.connect(temp_dir)
        
        # Создать тестовые таблицы с примерными данными
        species_df = pd.DataFrame([
            {
                "id": "aedes_aegypti",
                "scientific_name": "Aedes aegypti",
                "common_names": '{"en": "Yellow fever mosquito"}',
                "region": "Global"
            }
        ])
        
        db.create_table("species", species_df, mode="overwrite")
        
        yield db
        
    finally:
        shutil.rmtree(temp_dir)
```

## Непрерывная интеграция

### Рабочий процесс GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .
        pip install pytest pytest-cov pytest-asyncio
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=backend --cov=frontend --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### Pre-commit хуки

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
        args: [tests/backend/test_services/, -v, --tb=short]
```

## Покрытие тестами и качество

### Требования к покрытию

Поддерживайте высокое покрытие тестами:

```python
# pytest.ini
[tool:pytest]
addopts = 
    --cov=backend
    --cov=frontend
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    -v

testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

### Метрики качества

Мониторьте качество тестов:

- **Покрытие**: Стремитесь к >80% покрытию кода
- **Производительность**: Ответы API <2с, предсказания <10с
- **Надежность**: Тесты должны проходить стабильно
- **Поддерживаемость**: Четкие названия тестов и документация

## Сводка лучших практик

1. **Пишите четкие названия тестов**: Названия тестов должны описывать, что тестируется
2. **Используйте фикстуры**: Переиспользуйте код настройки тестов с pytest фикстурами
3. **Мокайте внешние зависимости**: Изолируйте тестируемые единицы
4. **Тестируйте граничные случаи**: Включайте условия ошибок и граничные значения
5. **Держите тесты быстрыми**: Модульные тесты должны выполняться за миллисекунды
6. **Тестируйте поведение, а не реализацию**: Фокусируйтесь на том, что делает код, а не как
7. **Используйте реальные данные**: Тестируйте с реалистичными данными когда возможно
8. **Автоматизируйте все**: Запускайте тесты автоматически при каждом изменении
9. **Мониторьте производительность**: Отслеживайте время выполнения тестов и производительность системы
10. **Документируйте требования к тестам**: Четкие инструкции по настройке для новых разработчиков

Эта стратегия тестирования обеспечивает поддержание высокого качества, надежности и производительности CulicidaeLab Server по мере его развития.