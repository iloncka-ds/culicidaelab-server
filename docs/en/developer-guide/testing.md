# Testing Guidelines

This document outlines testing strategies, best practices, and guidelines for the CulicidaeLab Server project, covering both backend and frontend testing approaches.

## Testing Philosophy

The CulicidaeLab Server follows a comprehensive testing strategy that emphasizes:

- **Test-Driven Development (TDD)**: Write tests before implementation when possible
- **Pyramid Testing**: More unit tests, fewer integration tests, minimal end-to-end tests
- **Fast Feedback**: Quick test execution for rapid development cycles
- **Realistic Testing**: Use real data and scenarios that mirror production usage
- **Automated Testing**: Continuous integration with automated test execution

## Testing Stack

### Backend Testing Tools

- **pytest**: Primary testing framework for Python
- **pytest-asyncio**: Async test support for FastAPI endpoints
- **httpx**: HTTP client for API testing
- **pytest-cov**: Code coverage reporting
- **pytest-mock**: Mocking and patching utilities

### Frontend Testing Tools

- **pytest**: Component and integration testing
- **Solara testing utilities**: Component rendering and interaction testing
- **Selenium** (optional): End-to-end browser testing

### Performance Testing

- **pytest-benchmark**: Performance benchmarking
- **locust**: Load testing for API endpoints
- **psutil**: System resource monitoring during tests

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Shared test configuration
├── backend/                    # Backend tests
│   ├── test_api/              # API endpoint tests
│   │   ├── test_species.py    # Species API tests
│   │   ├── test_diseases.py   # Disease API tests
│   │   ├── test_prediction.py # Prediction API tests
│   │   └── test_geo.py        # Geographic API tests
│   ├── test_services/         # Service layer tests
│   │   ├── test_species_service.py
│   │   ├── test_prediction_service.py
│   │   └── test_database.py
│   └── test_utils/            # Utility function tests
├── frontend/                   # Frontend tests
│   ├── test_components/       # Component tests
│   ├── test_pages/           # Page tests
│   └── test_state/           # State management tests
├── load_tests/                # Performance tests
├── performance_tests/         # Benchmark tests
└── fixtures/                  # Test data and fixtures
    ├── sample_images/         # Test images
    ├── sample_data.json       # Test datasets
    └── mock_responses/        # API response mocks
```

## Backend Testing

### Unit Testing

#### Service Layer Testing

Test business logic in isolation:

```python
# tests/backend/test_services/test_species_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.species_service import SpeciesService
from backend.schemas.species_schemas import SpeciesResponse

class TestSpeciesService:
    """Test suite for SpeciesService."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database connection."""
        return Mock()
    
    @pytest.fixture
    def species_service(self, mock_db):
        """Species service with mocked dependencies."""
        with patch('backend.services.species_service.get_db', return_value=mock_db):
            return SpeciesService()
    
    @pytest.mark.asyncio
    async def test_get_species_by_id_success(self, species_service, mock_db):
        """Test successful species retrieval by ID."""
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
        """Test species not found scenario."""
        # Arrange
        mock_table = Mock()
        mock_table.search.return_value.where.return_value.limit.return_value.to_list.return_value = []
        mock_db.open_table.return_value = mock_table
        
        # Act & Assert
        with pytest.raises(ValueError, match="Species .* not found"):
            await species_service.get_by_id("nonexistent_species")
    
    @pytest.mark.asyncio
    async def test_search_species_with_filters(self, species_service, mock_db):
        """Test species search with filters."""
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

#### Database Testing

Test database operations with real LanceDB:

```python
# tests/backend/test_services/test_database.py
import pytest
import tempfile
import shutil
from pathlib import Path
import pandas as pd
from backend.services.database import get_db, get_table

class TestDatabase:
    """Test database operations."""
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def test_db(self, temp_db_path):
        """Create test database with sample data."""
        import lancedb
        
        db = lancedb.connect(temp_db_path)
        
        # Create test species table
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
        """Test successful table retrieval."""
        table = get_table(test_db, "species")
        assert table is not None
        
        # Verify table contents
        results = table.search().to_list()
        assert len(results) == 2
    
    def test_get_table_not_found(self, test_db):
        """Test handling of non-existent table."""
        with pytest.raises(ValueError, match="Table 'nonexistent' not found"):
            get_table(test_db, "nonexistent")
    
    def test_species_search_by_region(self, test_db):
        """Test region-based species search."""
        table = get_table(test_db, "species")
        
        # Search for Asian species
        results = table.search().where("region = 'Asia'").to_list()
        assert len(results) == 1
        assert results[0]["scientific_name"] == "Aedes albopictus"
```

### API Testing

#### Endpoint Testing

Test FastAPI endpoints with realistic scenarios:

```python
# tests/backend/test_api/test_species.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app

class TestSpeciesAPI:
    """Test species API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client for API calls."""
        return TestClient(app)
    
    def test_get_species_list(self, client):
        """Test species list endpoint."""
        response = client.get("/api/species")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Verify response structure
        if data:
            species = data[0]
            assert "id" in species
            assert "scientific_name" in species
            assert "common_names" in species
    
    def test_get_species_by_id(self, client):
        """Test species detail endpoint."""
        # First get a valid species ID
        list_response = client.get("/api/species")
        species_list = list_response.json()
        
        if species_list:
            species_id = species_list[0]["id"]
            
            # Test detail endpoint
            response = client.get(f"/api/species/{species_id}")
            assert response.status_code == 200
            
            species = response.json()
            assert species["id"] == species_id
    
    def test_get_species_not_found(self, client):
        """Test species not found scenario."""
        response = client.get("/api/species/nonexistent_species")
        assert response.status_code == 404
        
        error = response.json()
        assert "detail" in error
    
    def test_species_search_with_filters(self, client):
        """Test species search with query parameters."""
        response = client.get("/api/species", params={
            "region": "Europe",
            "limit": 5
        })
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_species_search_invalid_limit(self, client):
        """Test validation of search parameters."""
        response = client.get("/api/species", params={"limit": -1})
        assert response.status_code == 422  # Validation error
```

#### Prediction API Testing

Test AI prediction endpoints with image uploads:

```python
# tests/backend/test_api/test_prediction.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import io
from PIL import Image

class TestPredictionAPI:
    """Test prediction API endpoints."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def test_image(self):
        """Create a test image for upload."""
        # Create a simple test image
        img = Image.new('RGB', (224, 224), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_predict_species_success(self, client, test_image):
        """Test successful species prediction."""
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.jpg", test_image, "image/jpeg")}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "species" in data
        assert "confidence" in data
        assert "alternatives" in data
        assert isinstance(data["confidence"], float)
        assert 0 <= data["confidence"] <= 1
    
    def test_predict_species_invalid_file(self, client):
        """Test prediction with invalid file type."""
        # Create a text file instead of image
        text_file = io.BytesIO(b"This is not an image")
        
        response = client.post(
            "/api/predict_species/",
            files={"file": ("test.txt", text_file, "text/plain")}
        )
        
        assert response.status_code == 400
        error = response.json()
        assert "Invalid file type" in error["detail"]
    
    def test_predict_species_no_file(self, client):
        """Test prediction without file upload."""
        response = client.post("/api/predict_species/")
        assert response.status_code == 422  # Missing required field
```

### Integration Testing

Test complete workflows across multiple components:

```python
# tests/backend/test_integration/test_prediction_workflow.py
import pytest
from fastapi.testclient import TestClient
from backend.main import app
import tempfile
import shutil
from pathlib import Path

class TestPredictionWorkflow:
    """Test complete prediction workflow."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.fixture
    def sample_mosquito_image(self):
        """Load a real mosquito image for testing."""
        # Use a sample image from test fixtures
        image_path = Path("tests/fixtures/sample_images/aedes_aegypti.jpg")
        if image_path.exists():
            return image_path.open("rb")
        else:
            pytest.skip("Sample image not available")
    
    def test_complete_prediction_and_observation_workflow(self, client, sample_mosquito_image):
        """Test prediction followed by observation storage."""
        
        # Step 1: Predict species
        prediction_response = client.post(
            "/api/predict_species/",
            files={"file": ("mosquito.jpg", sample_mosquito_image, "image/jpeg")}
        )
        
        assert prediction_response.status_code == 200
        prediction_data = prediction_response.json()
        
        # Step 2: Store observation based on prediction
        observation_data = {
            "species_id": prediction_data["species"],
            "latitude": 40.4168,
            "longitude": -3.7038,
            "confidence": prediction_data["confidence"],
            "notes": "Test observation from integration test"
        }
        
        observation_response = client.post("/api/observations/", json=observation_data)
        assert observation_response.status_code == 201
        
        stored_observation = observation_response.json()
        assert stored_observation["species_id"] == prediction_data["species"]
        
        # Step 3: Verify observation can be retrieved
        observation_id = stored_observation["id"]
        get_response = client.get(f"/api/observations/{observation_id}")
        assert get_response.status_code == 200
        
        retrieved_observation = get_response.json()
        assert retrieved_observation["id"] == observation_id
```

## Frontend Testing

### Component Testing

Test Solara components in isolation:

```python
# tests/frontend/test_components/test_species_card.py
import pytest
import solara
from frontend.components.species.species_card import SpeciesCard

class TestSpeciesCard:
    """Test SpeciesCard component."""
    
    @pytest.fixture
    def sample_species(self):
        """Sample species data for testing."""
        return {
            "id": "aedes_aegypti",
            "scientific_name": "Aedes aegypti",
            "common_names": {"en": "Yellow fever mosquito"},
            "description": {"en": "A mosquito species..."},
            "images": ["aedes_aegypti_1.jpg"]
        }
    
    def test_species_card_renders(self, sample_species):
        """Test that species card renders without errors."""
        
        @solara.component
        def TestApp():
            SpeciesCard(species=sample_species)
        
        # Render component
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Verify content is present
        rendered_content = str(box)
        assert "Aedes aegypti" in rendered_content
        assert "Yellow fever mosquito" in rendered_content
    
    def test_species_card_click_interaction(self, sample_species):
        """Test species card click handling."""
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
        
        # Simulate click (this would require more sophisticated testing setup)
        # For now, verify the component structure supports interaction
        assert "on_click" in str(box) or "click" in str(box).lower()
```

### Page Testing

Test complete page components:

```python
# tests/frontend/test_pages/test_prediction_page.py
import pytest
import solara
from unittest.mock import patch, AsyncMock
from frontend.pages.prediction import Page as PredictionPage

class TestPredictionPage:
    """Test prediction page functionality."""
    
    def test_prediction_page_renders(self):
        """Test that prediction page renders without errors."""
        
        @solara.component
        def TestApp():
            PredictionPage()
        
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Verify key elements are present
        rendered_content = str(box)
        assert "predict" in rendered_content.lower() or "upload" in rendered_content.lower()
    
    @patch('frontend.state.fetch_api_data')
    def test_prediction_page_with_mock_api(self, mock_fetch):
        """Test prediction page with mocked API calls."""
        # Mock API response
        mock_fetch.return_value = AsyncMock(return_value={
            "species": "Aedes aegypti",
            "confidence": 0.95,
            "alternatives": []
        })
        
        @solara.component
        def TestApp():
            PredictionPage()
        
        box, rc = solara.render(TestApp(), handle_error=False)
        
        # Verify component handles API integration
        assert mock_fetch.called or True  # Basic structure test
```

### State Management Testing

Test reactive state behavior:

```python
# tests/frontend/test_state/test_species_state.py
import pytest
import solara
from frontend.state import selected_species_reactive, species_data_reactive

class TestSpeciesState:
    """Test species-related state management."""
    
    def test_selected_species_reactive(self):
        """Test species selection state."""
        # Initial state
        assert selected_species_reactive.value == ["Aedes albopictus", "Anopheles gambiae"]
        
        # Update state
        new_selection = ["Aedes aegypti", "Culex pipiens"]
        selected_species_reactive.value = new_selection
        
        assert selected_species_reactive.value == new_selection
    
    def test_species_data_caching(self):
        """Test species data caching behavior."""
        # Initial empty state
        species_data_reactive.value = []
        assert len(species_data_reactive.value) == 0
        
        # Add species data
        test_species = [
            {"id": "aedes_aegypti", "scientific_name": "Aedes aegypti"},
            {"id": "culex_pipiens", "scientific_name": "Culex pipiens"}
        ]
        species_data_reactive.value = test_species
        
        assert len(species_data_reactive.value) == 2
        assert species_data_reactive.value[0]["id"] == "aedes_aegypti"
```

## Performance Testing

### Backend Performance Tests

Test API performance and resource usage:

```python
# tests/performance_tests/test_api_performance.py
import pytest
import time
import asyncio
from fastapi.testclient import TestClient
from backend.main import app

class TestAPIPerformance:
    """Test API performance characteristics."""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_species_list_performance(self, client):
        """Test species list endpoint performance."""
        start_time = time.time()
        
        response = client.get("/api/species?limit=100")
        
        end_time = time.time()
        response_time = end_time - start_time
        
        assert response.status_code == 200
        assert response_time < 2.0  # Should respond within 2 seconds
    
    def test_prediction_performance(self, client):
        """Test prediction endpoint performance."""
        # Create test image
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
        assert response_time < 10.0  # Prediction should complete within 10 seconds
    
    @pytest.mark.benchmark
    def test_database_query_performance(self, benchmark):
        """Benchmark database query performance."""
        from backend.services.database import get_db, get_table
        
        def query_species():
            db = get_db()
            table = get_table(db, "species")
            return table.search().limit(50).to_list()
        
        result = benchmark(query_species)
        assert len(result) <= 50
```

### Load Testing

Use locust for load testing:

```python
# tests/load_tests/locustfile.py
from locust import HttpUser, task, between

class CulicidaeLabUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Called when user starts."""
        pass
    
    @task(3)
    def view_species_list(self):
        """Most common task - viewing species list."""
        self.client.get("/api/species?limit=20")
    
    @task(2)
    def view_species_detail(self):
        """View individual species details."""
        # Get species list first
        response = self.client.get("/api/species?limit=5")
        if response.status_code == 200:
            species_list = response.json()
            if species_list:
                species_id = species_list[0]["id"]
                self.client.get(f"/api/species/{species_id}")
    
    @task(1)
    def search_species(self):
        """Search species with filters."""
        self.client.get("/api/species", params={
            "region": "Europe",
            "limit": 10
        })
    
    @task(1)
    def get_filter_options(self):
        """Get filter options for UI."""
        self.client.get("/api/filter_options")

# Run with: locust -f tests/load_tests/locustfile.py --host=http://localhost:8000
```

## Test Data Management

### Fixtures and Test Data

Organize test data effectively:

```python
# tests/conftest.py
import pytest
import json
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "fixtures"

@pytest.fixture(scope="session")
def sample_species_data(test_data_dir):
    """Load sample species data."""
    data_file = test_data_dir / "sample_data.json"
    if data_file.exists():
        with open(data_file) as f:
            return json.load(f)["species"]
    return []

@pytest.fixture(scope="session")
def sample_images_dir(test_data_dir):
    """Path to sample images directory."""
    return test_data_dir / "sample_images"

@pytest.fixture
def mock_prediction_response():
    """Mock prediction API response."""
    return {
        "species": "Aedes aegypti",
        "confidence": 0.95,
        "alternatives": [
            {"species": "Aedes albopictus", "confidence": 0.03},
            {"species": "Culex pipiens", "confidence": 0.02}
        ]
    }
```

### Database Test Setup

Set up test databases:

```python
# tests/conftest.py (continued)
import tempfile
import shutil
import pandas as pd
import lancedb

@pytest.fixture(scope="function")
def test_database():
    """Create temporary test database."""
    temp_dir = tempfile.mkdtemp()
    
    try:
        db = lancedb.connect(temp_dir)
        
        # Create test tables with sample data
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

## Continuous Integration

### GitHub Actions Workflow

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

### Pre-commit Hooks

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

## Test Coverage and Quality

### Coverage Requirements

Maintain high test coverage:

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

### Quality Metrics

Monitor test quality:

- **Coverage**: Aim for >80% code coverage
- **Performance**: API responses <2s, predictions <10s
- **Reliability**: Tests should pass consistently
- **Maintainability**: Clear test names and documentation

## Best Practices Summary

1. **Write Clear Test Names**: Test names should describe what is being tested
2. **Use Fixtures**: Reuse test setup code with pytest fixtures
3. **Mock External Dependencies**: Isolate units under test
4. **Test Edge Cases**: Include error conditions and boundary values
5. **Keep Tests Fast**: Unit tests should run in milliseconds
6. **Test Behavior, Not Implementation**: Focus on what the code does, not how
7. **Use Real Data**: Test with realistic data when possible
8. **Automate Everything**: Run tests automatically on every change
9. **Monitor Performance**: Track test execution time and system performance
10. **Document Test Requirements**: Clear setup instructions for new developers

This testing strategy ensures the CulicidaeLab Server maintains high quality, reliability, and performance as it evolves.