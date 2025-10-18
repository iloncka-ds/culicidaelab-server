# Contributing Guidelines

Welcome to the CulicidaeLab Server project! We appreciate your interest in contributing to this open-source mosquito research and analysis platform. This guide will help you get started with contributing effectively.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](https://github.com/iloncka-ds/culicidaelab-server/blob/main/CODE_OF_CONDUCT.md). Please read it to understand the standards we expect from all contributors.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- Python 3.11 or higher
- Git installed and configured
- Basic knowledge of FastAPI and Solara frameworks
- Understanding of mosquito research domain (helpful but not required)

### Development Environment Setup

1. **Fork and Clone the Repository**
```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/culicidaelab-server.git
cd culicidaelab-server

# Add upstream remote
git remote add upstream https://github.com/iloncka-ds/culicidaelab-server.git
```

2. **Set Up Development Environment**
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
# Or with uv: uv sync -p 3.11

# Install development dependencies
pip install -e ".[dev]"
```

3. **Initialize Database**
```bash
# Generate sample data
python -m backend.data.sample_data.generate_sample_data

# Populate database
python -m backend.scripts.populate_lancedb

# Verify setup
python -m backend.scripts.query_lancedb observations --limit 5
```

4. **Run Tests**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov=frontend
```

5. **Start Development Servers**
```bash
# Terminal 1: Backend
uvicorn backend.main:app --port 8000 --reload

# Terminal 2: Frontend
solara run frontend.main --port 8765
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Help us identify and fix issues
- **Feature Requests**: Suggest new functionality
- **Code Contributions**: Implement features or fix bugs
- **Documentation**: Improve or add documentation
- **Testing**: Add or improve test coverage
- **Performance**: Optimize existing code
- **Translations**: Add support for new languages

### Reporting Issues

When reporting bugs or requesting features:

1. **Search Existing Issues**: Check if the issue already exists
2. **Use Issue Templates**: Follow the provided templates
3. **Provide Details**: Include steps to reproduce, expected behavior, and environment info
4. **Add Labels**: Use appropriate labels to categorize the issue

#### Bug Report Template

```markdown
**Bug Description**
A clear description of the bug.

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What you expected to happen.

**Actual Behavior**
What actually happened.

**Environment**
- OS: [e.g., Windows 11, Ubuntu 22.04]
- Python Version: [e.g., 3.11.5]
- Browser: [e.g., Chrome 118]

**Additional Context**
Screenshots, logs, or other relevant information.
```

### Making Code Changes

#### Workflow

1. **Create a Branch**
```bash
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

2. **Make Changes**
   - Follow the coding standards (see below)
   - Write or update tests
   - Update documentation if needed
   - Ensure all tests pass

3. **Commit Changes**
```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: add species prediction caching

- Implement LRU cache for prediction results
- Add cache invalidation on model updates
- Improve prediction response time by 40%

Closes #123"
```

4. **Push and Create Pull Request**
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

#### Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api): add species similarity search endpoint
fix(frontend): resolve map rendering issue on mobile
docs(readme): update installation instructions
test(backend): add integration tests for prediction service
```

## Coding Standards

### Python Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **mypy**: Type checking
- **flake8**: Linting

#### Setup Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run hooks manually
pre-commit run --all-files
```

#### Code Formatting

```python
# Good: Clear, well-documented function
async def predict_species(
    image_path: str,
    confidence_threshold: float = 0.5
) -> PredictionResult:
    """Predict mosquito species from image.

    Args:
        image_path: Path to the image file
        confidence_threshold: Minimum confidence for prediction

    Returns:
        Prediction result with species and confidence

    Raises:
        ValueError: If image cannot be processed
        FileNotFoundError: If image file doesn't exist
    """
    if not Path(image_path).exists():
        raise FileNotFoundError(f"Image not found: {image_path}")

    try:
        result = await predictor.predict(image_path)
        if result.confidence < confidence_threshold:
            logger.warning(f"Low confidence prediction: {result.confidence}")

        return PredictionResult(
            species=result.species,
            confidence=result.confidence,
            alternatives=result.alternatives
        )
    except Exception as e:
        logger.error(f"Prediction failed for {image_path}: {e}")
        raise ValueError(f"Failed to predict species: {e}")
```

#### Type Hints

Use type hints throughout the codebase:

```python
from typing import List, Dict, Optional, Union
from pydantic import BaseModel

class SpeciesInfo(BaseModel):
    """Species information model."""
    id: str
    scientific_name: str
    common_names: Dict[str, str]
    distribution: Optional[List[str]] = None

async def get_species_by_region(
    region: str,
    limit: int = 10
) -> List[SpeciesInfo]:
    """Get species found in a specific region."""
    # Implementation here
    pass
```

### Frontend Code Style

#### Solara Component Guidelines

```python
import solara
from typing import Callable, Optional

@solara.component
def SpeciesCard(
    species: dict,
    on_click: Optional[Callable[[str], None]] = None,
    show_details: bool = True
):
    """Reusable species card component.

    Args:
        species: Species information dictionary
        on_click: Callback when card is clicked
        show_details: Whether to show detailed information
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

        # Display common names
        common_names = species.get("common_names", {})
        if common_names:
            for lang, name in common_names.items():
                solara.Text(f"{lang.upper()}: {name}")
```

#### State Management

```python
# Good: Clear state organization
import solara
from typing import List, Optional

# Global application state
current_user_id: solara.Reactive[Optional[str]] = solara.reactive(None)
selected_species: solara.Reactive[List[str]] = solara.reactive([])
loading_states = {
    'species': solara.reactive(False),
    'predictions': solara.reactive(False)
}

@solara.component
def use_species_data():
    """Hook for managing species data."""
    data, set_data = solara.use_state([])
    error, set_error = solara.use_state(None)

    async def fetch_data():
        loading_states['species'].value = True
        set_error(None)

        try:
            # Fetch data logic
            result = await api_client.get_species()
            set_data(result)
        except Exception as e:
            set_error(str(e))
        finally:
            loading_states['species'].value = False

    return data, fetch_data, error
```

### Database Guidelines

#### LanceDB Best Practices

```python
# Good: Efficient database operations
from backend.services.database import get_db, get_table
from typing import List, Dict, Any

class SpeciesRepository:
    """Repository for species data operations."""

    def __init__(self):
        self.db = get_db()
        self.table = get_table(self.db, "species")

    async def search_by_region(
        self,
        region: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search species by region with efficient querying."""
        try:
            results = (
                self.table
                .search()
                .where(f"region = '{region}'")
                .limit(limit)
                .select(["id", "scientific_name", "common_names"])  # Select only needed fields
                .to_list()
            )
            return results
        except Exception as e:
            logger.error(f"Failed to search species by region {region}: {e}")
            raise

    async def similarity_search(
        self,
        query_vector: List[float],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Perform vector similarity search."""
        try:
            results = (
                self.table
                .search(query_vector)
                .limit(limit)
                .to_list()
            )
            return results
        except Exception as e:
            logger.error(f"Similarity search failed: {e}")
            raise
```

## Testing Requirements

### Test Coverage

All contributions must include appropriate tests:

- **New Features**: Comprehensive test coverage (>90%)
- **Bug Fixes**: Tests that reproduce the bug and verify the fix
- **Refactoring**: Existing tests must continue to pass

### Test Types

1. **Unit Tests**: Test individual functions/methods
2. **Integration Tests**: Test component interactions
3. **API Tests**: Test endpoint functionality
4. **Frontend Tests**: Test component behavior

### Example Test Structure

```python
# tests/backend/test_services/test_species_service.py
import pytest
from unittest.mock import Mock, patch
from backend.services.species_service import SpeciesService

class TestSpeciesService:
    """Test suite for SpeciesService."""

    @pytest.fixture
    def species_service(self):
        """Create species service with mocked dependencies."""
        with patch('backend.services.species_service.get_db'):
            return SpeciesService()

    @pytest.mark.asyncio
    async def test_get_species_by_id_success(self, species_service):
        """Test successful species retrieval."""
        # Arrange
        expected_species = {"id": "aedes_aegypti", "name": "Aedes aegypti"}

        # Act
        result = await species_service.get_by_id("aedes_aegypti")

        # Assert
        assert result is not None
        assert result.id == "aedes_aegypti"

    @pytest.mark.asyncio
    async def test_get_species_not_found(self, species_service):
        """Test handling of non-existent species."""
        with pytest.raises(ValueError, match="Species .* not found"):
            await species_service.get_by_id("nonexistent")
```

## Documentation Standards

### Code Documentation

- **Docstrings**: All public functions, classes, and modules
- **Type Hints**: Use throughout the codebase
- **Comments**: Explain complex logic, not obvious code
- **README Updates**: Update relevant documentation

### API Documentation

- **OpenAPI**: Ensure FastAPI generates accurate API docs
- **Examples**: Include request/response examples
- **Error Codes**: Document all possible error responses

### User Documentation

- **Feature Documentation**: Document new user-facing features
- **Screenshots**: Include visual guides where helpful
- **Tutorials**: Step-by-step guides for complex features

## Pull Request Process

### Before Submitting

1. **Rebase on Latest Main**
```bash
git fetch upstream
git rebase upstream/main
```

2. **Run Full Test Suite**
```bash
pytest --cov=backend --cov=frontend
```

3. **Check Code Quality**
```bash
black .
isort .
mypy backend/ frontend/
flake8 backend/ frontend/
```

4. **Update Documentation**
   - Update relevant docs
   - Add docstrings for new functions
   - Update API documentation if needed

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained or improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings introduced

## Related Issues
Closes #123
Related to #456
```

### Review Process

1. **Automated Checks**: CI/CD pipeline runs tests and quality checks
2. **Code Review**: Maintainers review code for quality and design
3. **Feedback**: Address reviewer comments and suggestions
4. **Approval**: At least one maintainer approval required
5. **Merge**: Maintainer merges after all checks pass

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

1. Update version numbers
2. Update CHANGELOG.md
3. Create release notes
4. Tag release
5. Deploy to production

## Community Guidelines

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas


### Getting Help

- **Documentation**: Check existing docs first
- **Search Issues**: Look for similar problems
- **Ask Questions**: Create a discussion for help
- **Be Patient**: Maintainers are volunteers

### Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes
- Project documentation
- Annual contributor highlights

## Security

### Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Instead, email culicidaelab@gmail.com with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or API keys
- Validate all user inputs
- Use parameterized queries
- Follow OWASP guidelines
- Keep dependencies updated

## License

By contributing to CulicidaeLab Server, you agree that your contributions will be licensed under the AGPL-3.0 License. See [LICENSE](https://github.com/iloncka-ds/culicidaelab-server/blob/main/LICENSE) for details.

## Questions?

If you have questions about contributing:

1. Check the [FAQ](../user-guide/troubleshooting.md)
2. Search existing [GitHub Issues](https://github.com/iloncka-ds/culicidaelab-server/issues)
3. Create a new [Discussion](https://github.com/iloncka-ds/culicidaelab-server/discussions)
4. Contact maintainers via email

Thank you for contributing to CulicidaeLab Server! Your efforts help advance mosquito research and public health initiatives worldwide.
