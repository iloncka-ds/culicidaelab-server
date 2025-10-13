# OpenAPI Integration

The CulicidaeLab Server automatically generates comprehensive OpenAPI documentation using FastAPI's built-in capabilities.

## Interactive Documentation

FastAPI provides two interactive documentation interfaces out of the box:

### Swagger UI
Access the Swagger UI at: [http://localhost:8000/docs](http://localhost:8000/docs)

The Swagger UI provides:
- Interactive API exploration
- Request/response examples
- Schema validation
- Try-it-out functionality
- Authentication testing (when implemented)

### ReDoc
Access ReDoc at: [http://localhost:8000/redoc](http://localhost:8000/redoc)

ReDoc offers:
- Clean, readable documentation
- Detailed schema information
- Code samples in multiple languages
- Responsive design for mobile devices

## OpenAPI Specification

### JSON Format
The complete OpenAPI specification is available in JSON format:
```
http://localhost:8000/api/v1/openapi.json
```

### YAML Format
You can also retrieve the specification in YAML format by adding the Accept header:
```bash
curl -H "Accept: application/x-yaml" http://localhost:8000/api/v1/openapi.json
```

## Using the OpenAPI Specification

### Code Generation

Generate client libraries using the OpenAPI specification:

#### Python Client with openapi-generator
```bash
# Install openapi-generator
npm install @openapitools/openapi-generator-cli -g

# Generate Python client
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/openapi.json \
  -g python \
  -o ./culicidae-client-python \
  --package-name culicidae_client
```

#### JavaScript Client
```bash
# Generate JavaScript/TypeScript client
openapi-generator-cli generate \
  -i http://localhost:8000/api/v1/openapi.json \
  -g typescript-axios \
  -o ./culicidae-client-js
```

### API Testing with Postman

1. Import the OpenAPI specification into Postman:
   - Open Postman
   - Click "Import"
   - Enter URL: `http://localhost:8000/api/v1/openapi.json`
   - Postman will create a collection with all endpoints

2. Set up environment variables:
   ```json
   {
     "base_url": "http://localhost:8000",
     "api_version": "v1"
   }
   ```

### Mock Server Creation

Create a mock server using the OpenAPI specification:

#### Using Prism
```bash
# Install Prism
npm install -g @stoplight/prism-cli

# Start mock server
prism mock http://localhost:8000/api/v1/openapi.json
```

#### Using WireMock
```bash
# Download WireMock
curl -o wiremock.jar https://repo1.maven.org/maven2/com/github/tomakehurst/wiremock-jre8-standalone/2.35.0/wiremock-jre8-standalone-2.35.0.jar

# Start with OpenAPI
java -jar wiremock.jar --port 8080 --global-response-templating \
  --extensions com.github.tomakehurst.wiremock.extension.responsetemplating.ResponseTemplateTransformer
```

## Customizing OpenAPI Documentation

### Adding Metadata

The OpenAPI documentation can be customized in the main FastAPI application:

```python
from fastapi import FastAPI

app = FastAPI(
    title="CulicidaeLab Server API",
    description="A sophisticated web platform for mosquito research, surveillance, and data analysis",
    version="1.0.0",
    terms_of_service="https://culicidaelab.org/terms/",
    contact={
        "name": "CulicidaeLab Team",
        "url": "https://culicidaelab.org/contact/",
        "email": "contact@culicidaelab.org",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Species",
            "description": "Operations with mosquito species data",
        },
        {
            "name": "Diseases",
            "description": "Disease information and vector relationships",
        },
        {
            "name": "Prediction",
            "description": "AI-powered species identification",
        },
    ]
)
```

### Adding Examples to Endpoints

Enhance endpoint documentation with examples:

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
                "common_name": "Yellow fever mosquito"
            }
        }

@app.get(
    "/species/{species_id}",
    response_model=SpeciesResponse,
    responses={
        200: {
            "description": "Species found successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "aedes-aegypti",
                        "scientific_name": "Aedes aegypti",
                        "common_name": "Yellow fever mosquito",
                        "vector_status": "Primary vector"
                    }
                }
            }
        },
        404: {
            "description": "Species not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Species not found"}
                }
            }
        }
    }
)
async def get_species(species_id: str):
    pass
```

## Swagger UI Customization

### Custom CSS and JavaScript

Add custom styling to Swagger UI by serving custom files:

```python
from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

app = FastAPI(docs_url=None)  # Disable default docs
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

## Integration with MkDocs

### Embedding Swagger UI

You can embed the Swagger UI directly in MkDocs documentation:

```markdown
# API Documentation

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

### Using swagger-ui-tag Plugin

The `swagger-ui-tag` plugin allows embedding Swagger UI with a simple tag:

```markdown
# API Documentation

{% swagger_ui %}
http://localhost:8000/api/v1/openapi.json
{% endswagger_ui %}
```

## Validation and Testing

### Schema Validation

Use the OpenAPI specification for request/response validation:

```python
import requests
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename

# Validate the OpenAPI specification
spec_dict = requests.get('http://localhost:8000/api/v1/openapi.json').json()
validate_spec(spec_dict)
```

### Automated Testing

Generate test cases from the OpenAPI specification:

```python
import schemathesis

schema = schemathesis.from_uri("http://localhost:8000/api/v1/openapi.json")

@schema.parametrize()
def test_api(case):
    case.call_and_validate()
```

## Best Practices

### Documentation Guidelines

1. **Comprehensive Docstrings**: Write detailed docstrings for all endpoints
2. **Response Examples**: Provide realistic examples for all responses
3. **Error Documentation**: Document all possible error conditions
4. **Schema Descriptions**: Add descriptions to all Pydantic model fields
5. **Tags and Organization**: Use tags to organize endpoints logically

### Performance Considerations

1. **Caching**: Cache the OpenAPI specification for production
2. **Compression**: Enable gzip compression for the specification
3. **CDN**: Serve Swagger UI assets from a CDN
4. **Lazy Loading**: Load documentation on demand

### Security

1. **Sensitive Data**: Never expose sensitive information in examples
2. **Authentication**: Document authentication requirements clearly
3. **Rate Limiting**: Document rate limiting policies
4. **CORS**: Configure CORS appropriately for documentation access