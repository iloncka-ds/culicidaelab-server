# Prediction API

The Prediction API provides machine learning-based species identification and prediction services for mosquito classification.

## Router Implementation

::: backend.routers.prediction
    options:
      show_root_heading: false
      show_source: true
      members_order: source
      docstring_style: google

## Data Schemas

The Prediction API uses Pydantic schemas for prediction request/response validation:

::: backend.schemas.prediction_schemas
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Service Layer

The Prediction API integrates with machine learning service layers:

::: backend.services.prediction_service
    options:
      show_root_heading: true
      show_source: false
      members_order: source

## Example Usage

### Species Prediction

```python
import httpx

async with httpx.AsyncClient() as client:
    # Upload image for species prediction
    with open("mosquito_image.jpg", "rb") as image_file:
        files = {"image": image_file}
        response = await client.post(
            "http://localhost:8000/api/v1/predict",
            files=files,
            data={"confidence_threshold": 0.7}
        )
        prediction = response.json()
        
    print(f"Predicted species: {prediction['species']}")
    print(f"Confidence: {prediction['confidence']}")
```

### Batch Prediction

```python
# Submit multiple images for batch prediction
files = [
    ("images", open("image1.jpg", "rb")),
    ("images", open("image2.jpg", "rb")),
    ("images", open("image3.jpg", "rb"))
]

response = await client.post(
    "http://localhost:8000/api/v1/predict/batch",
    files=files
)
batch_predictions = response.json()
```