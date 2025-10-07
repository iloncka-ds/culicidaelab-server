# Frontend Development Guide

This guide covers frontend development for the CulicidaeLab Server using Solara, a pure Python reactive web framework that enables building modern web applications without JavaScript.

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Backend server running (see [Backend Development Guide](backend-development.md))
- Modern web browser for testing

### Frontend Setup

1. **Ensure backend is running:**
```bash
# In one terminal, start the backend
uvicorn backend.main:app --port 8000 --host 127.0.0.1 --reload
```

2. **Start the frontend development server:**
```bash
# In another terminal
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
solara run frontend.main --host 127.0.0.1 --port 8765
```

The frontend will be available at http://localhost:8765

### Hot Reloading

Solara supports hot reloading for rapid development:
- Changes to Python files automatically reload the application
- State is preserved across reloads when possible
- Browser automatically refreshes to show changes

## Project Structure

```
frontend/
├── main.py                 # Application entry point and routing
├── config.py              # Configuration and styling
├── state.py               # Global state management
├── pages/                 # Page components
│   ├── home.py            # Landing page
│   ├── prediction.py      # Species prediction interface
│   ├── map_visualization.py # Interactive map
│   ├── species.py         # Species gallery and details
│   ├── diseases.py        # Disease information
│   └── about.py           # About page
├── components/            # Reusable UI components
│   ├── common/            # Shared components
│   ├── prediction/        # Prediction-specific components
│   ├── map_module/        # Map components
│   ├── species/           # Species-related components
│   └── diseases/          # Disease-related components
├── translations/          # Internationalization files
│   ├── home.en.yml        # English translations
│   ├── home.ru.yml        # Russian translations
│   └── ...
└── assets/                # Static assets
    ├── custom.css         # Custom styles
    └── theme.js           # Theme configuration
```

## Solara Framework Fundamentals

### Component Architecture

Solara uses a component-based architecture similar to React:

```python
import solara

@solara.component
def MyComponent(title: str, items: list[str]):
    """A simple component example.
    
    Args:
        title: Component title
        items: List of items to display
    """
    with solara.Card(title):
        for item in items:
            solara.Text(item)

# Usage
@solara.component  
def Page():
    MyComponent("My List", ["Item 1", "Item 2", "Item 3"])
```

### Reactive State Management

Solara uses reactive variables for state management:

```python
import solara

# Global reactive state
counter = solara.reactive(0)
selected_items = solara.reactive([])

@solara.component
def Counter():
    """Component with reactive state."""
    
    def increment():
        counter.value += 1
    
    def decrement():
        counter.value -= 1
    
    with solara.Row():
        solara.Button("−", on_click=decrement)
        solara.Text(f"Count: {counter.value}")
        solara.Button("+", on_click=increment)
```

### Hooks and Effects

Use hooks for side effects and lifecycle management:

```python
import solara
import httpx

@solara.component
def DataLoader():
    """Component that loads data on mount."""
    data, set_data = solara.use_state(None)
    loading, set_loading = solara.use_state(True)
    
    async def load_data():
        set_loading(True)
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("/api/data")
                set_data(response.json())
        finally:
            set_loading(False)
    
    # Load data when component mounts
    solara.use_effect(load_data, [])
    
    if loading:
        solara.SpinnerSolara()
    elif data:
        solara.Text(f"Loaded {len(data)} items")
    else:
        solara.Text("No data available")
```

## Application Architecture

### Routing System

The main application defines routes and layout:

```python
# main.py
import solara
from frontend.pages import home, prediction, species

@solara.component
def Layout(children):
    """Main application layout."""
    route_current, routes_all = solara.use_route()
    
    with solara.AppLayout(toolbar_dark=True):
        with solara.AppBar():
            with solara.AppBarTitle():
                solara.Text("CulicidaeLab")
            
            # Navigation buttons
            for route in routes_all:
                with solara.Link(route):
                    solara.Button(route.label)
        
        # Page content
        with solara.Column(children=children):
            pass

# Route configuration
routes = [
    solara.Route("/", component=home.Home, label="Home", layout=Layout),
    solara.Route("predict", component=prediction.Page, label="Predict"),
    solara.Route("species", component=species.Page, label="Species"),
]
```

### State Management Pattern

Global state is managed in `state.py`:

```python
# state.py
import solara
from typing import Optional

# Application state
current_user_id = solara.reactive(None)
selected_species = solara.reactive([])
map_center = solara.reactive((40.4168, -3.7038))
loading_states = {
    'species': solara.reactive(False),
    'predictions': solara.reactive(False),
    'observations': solara.reactive(False)
}

# API data caches
species_data = solara.reactive([])
filter_options = solara.reactive({})

async def fetch_species_data():
    """Fetch and cache species data."""
    if loading_states['species'].value:
        return
        
    loading_states['species'].value = True
    try:
        # API call logic
        async with httpx.AsyncClient() as client:
            response = await client.get("/api/species")
            species_data.value = response.json()
    finally:
        loading_states['species'].value = False
```

## Component Development Patterns

### Page Components

Page components represent full application views:

```python
# pages/species.py
import solara
from frontend.components.species import SpeciesGallery, SpeciesDetail
from frontend.state import selected_species_item_id

@solara.component
def Page():
    """Species page with gallery and detail views."""
    route_current, _ = solara.use_route()
    species_id = route_current.params.get("species_id")
    
    if species_id:
        # Show species detail
        SpeciesDetail(species_id=species_id)
    else:
        # Show species gallery
        SpeciesGallery()
```

### Reusable Components

Create modular, reusable components:

```python
# components/common/loading_spinner.py
import solara

@solara.component
def LoadingSpinner(message: str = "Loading..."):
    """Reusable loading spinner component."""
    with solara.Column(align="center"):
        solara.SpinnerSolara()
        solara.Text(message, style={"margin-top": "1rem"})

# components/common/error_message.py
@solara.component  
def ErrorMessage(error: str, retry_callback=None):
    """Reusable error message component."""
    with solara.Card():
        solara.Error(f"Error: {error}")
        if retry_callback:
            solara.Button("Retry", on_click=retry_callback)
```

### Form Components

Handle user input with form components:

```python
# components/prediction/upload_form.py
import solara
from typing import Optional

@solara.component
def ImageUploadForm(on_upload_complete=None):
    """Image upload form for species prediction."""
    uploaded_file, set_uploaded_file = solara.use_state(None)
    uploading, set_uploading = solara.use_state(False)
    
    def handle_file_upload(file_info):
        set_uploaded_file(file_info)
    
    async def submit_prediction():
        if not uploaded_file:
            return
            
        set_uploading(True)
        try:
            # Upload and predict
            async with httpx.AsyncClient() as client:
                files = {"file": uploaded_file["file_obj"]}
                response = await client.post("/api/predict_species/", files=files)
                result = response.json()
                
                if on_upload_complete:
                    on_upload_complete(result)
        finally:
            set_uploading(False)
    
    with solara.Card("Upload Image for Prediction"):
        solara.FileDrop(
            on_file=handle_file_upload,
            accept=".jpg,.jpeg,.png",
            multiple=False
        )
        
        if uploaded_file:
            solara.Text(f"Selected: {uploaded_file['name']}")
            
        solara.Button(
            "Predict Species",
            on_click=submit_prediction,
            disabled=not uploaded_file or uploading
        )
        
        if uploading:
            LoadingSpinner("Analyzing image...")
```

## Working with Maps

### Interactive Maps with ipyleaflet

The application uses ipyleaflet for interactive mapping:

```python
# components/map_module/observation_map.py
import solara
import ipyleaflet
from frontend.state import current_map_center, observations_data

@solara.component
def ObservationMap():
    """Interactive map showing mosquito observations."""
    
    # Create map widget
    map_widget = ipyleaflet.Map(
        center=current_map_center.value,
        zoom=5,
        scroll_wheel_zoom=True
    )
    
    # Add observation markers
    def update_markers():
        # Clear existing markers
        map_widget.layers = [map_widget.layers[0]]  # Keep base layer
        
        # Add observation markers
        for obs in observations_data.value:
            marker = ipyleaflet.Marker(
                location=(obs['latitude'], obs['longitude']),
                popup=ipyleaflet.Popup(
                    child=solara.HTML(f"""
                        <div>
                            <h4>{obs['species']}</h4>
                            <p>Confidence: {obs['confidence']:.2%}</p>
                            <p>Date: {obs['date']}</p>
                        </div>
                    """)
                )
            )
            map_widget.add_layer(marker)
    
    # Update markers when data changes
    solara.use_effect(update_markers, [observations_data.value])
    
    # Handle map interactions
    def on_map_click(**kwargs):
        location = kwargs.get('coordinates')
        if location:
            # Handle map click
            print(f"Clicked at: {location}")
    
    map_widget.on_interaction(on_map_click)
    
    # Display map
    solara.display(map_widget)
```

## Data Visualization

### Plotly Integration

Use Plotly for interactive charts and graphs:

```python
# components/species/distribution_chart.py
import solara
import plotly.graph_objects as go
from frontend.state import species_data

@solara.component
def SpeciesDistributionChart():
    """Chart showing species distribution by region."""
    
    def create_chart():
        if not species_data.value:
            return go.Figure()
        
        # Process data for chart
        regions = {}
        for species in species_data.value:
            for region in species.get('regions', []):
                regions[region] = regions.get(region, 0) + 1
        
        # Create bar chart
        fig = go.Figure(data=[
            go.Bar(
                x=list(regions.keys()),
                y=list(regions.values()),
                marker_color='#009688'
            )
        ])
        
        fig.update_layout(
            title="Species Distribution by Region",
            xaxis_title="Region",
            yaxis_title="Number of Species",
            template="plotly_white"
        )
        
        return fig
    
    chart = create_chart()
    solara.FigurePlotly(chart)
```

## Internationalization (i18n)

### Translation System

The application supports multiple languages:

```python
# Using translations in components
import i18n

@solara.component
def WelcomeMessage():
    """Component with internationalized text."""
    
    # Load translations
    title = i18n.t("home.welcome_title")
    description = i18n.t("home.welcome_description")
    
    with solara.Column():
        solara.Markdown(f"# {title}")
        solara.Text(description)

# Translation files (translations/home.en.yml)
# home:
#   welcome_title: "Welcome to CulicidaeLab"
#   welcome_description: "Mosquito research and analysis platform"

# Translation files (translations/home.ru.yml)  
# home:
#   welcome_title: "Добро пожаловать в CulicidaeLab"
#   welcome_description: "Платформа для исследования и анализа комаров"
```

### Language Switching

Implement language switching:

```python
# components/common/locale_selector.py
import solara
import i18n
from frontend.state import current_locale

@solara.component
def LocaleSelector():
    """Language selection component."""
    
    languages = [
        ("en", "English"),
        ("ru", "Русский")
    ]
    
    def change_language(new_locale):
        current_locale.value = new_locale
        i18n.set("locale", new_locale)
    
    with solara.Select(
        label="Language",
        value=current_locale.value,
        values=[lang[0] for lang in languages],
        on_value=change_language
    ):
        for code, name in languages:
            solara.Option(code, name)
```

## Styling and Theming

### Material Design Theme

The application uses Material Design components:

```python
# config.py - Theme configuration
import solara.lab

def load_themes(theme):
    """Configure Material Design theme."""
    theme.themes.light.primary = "#009688"
    theme.themes.light.secondary = "#B2DFDB"
    theme.themes.light.accent = "#00796B"
    
    theme.themes.dark.primary = "#009688"
    theme.themes.dark.secondary = "#B2DFDB"
    theme.themes.dark.accent = "#00796B"
    
    return theme

# Apply theme at startup
theme = load_themes(solara.lab.theme)
```

### Custom Styling

Add custom CSS for enhanced styling:

```python
# Using inline styles
@solara.component
def StyledCard():
    card_style = {
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "color": "white",
        "border-radius": "12px",
        "padding": "2rem"
    }
    
    with solara.Card(style=card_style):
        solara.Text("Styled content")

# Using CSS classes (assets/custom.css)
"""
.prediction-card {
    border: 2px solid #009688;
    border-radius: 8px;
    transition: transform 0.2s;
}

.prediction-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
"""

@solara.component
def PredictionCard():
    with solara.Card(classes=["prediction-card"]):
        solara.Text("Prediction result")
```

## Performance Optimization

### Efficient State Updates

Minimize unnecessary re-renders:

```python
import solara

# Use local state for UI-only changes
@solara.component
def SearchBox():
    query, set_query = solara.use_state("")
    
    # Debounce search to avoid excessive API calls
    def debounced_search():
        if len(query) >= 3:
            # Trigger search after delay
            pass
    
    solara.use_effect(debounced_search, [query])
    
    solara.InputText(
        label="Search species",
        value=query,
        on_value=set_query
    )

# Memoize expensive computations
@solara.component
def ExpensiveChart(data: list):
    # Only recalculate when data changes
    processed_data = solara.use_memo(
        lambda: process_chart_data(data),
        [data]
    )
    
    chart = create_chart(processed_data)
    solara.FigurePlotly(chart)
```

### Lazy Loading

Implement lazy loading for better performance:

```python
@solara.component
def LazySpeciesGallery():
    """Species gallery with lazy loading."""
    page, set_page = solara.use_state(1)
    species_list, set_species_list = solara.use_state([])
    
    async def load_more_species():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"/api/species?page={page}")
            new_species = response.json()
            set_species_list(species_list + new_species)
            set_page(page + 1)
    
    # Initial load
    solara.use_effect(load_more_species, [])
    
    # Display species
    for species in species_list:
        SpeciesCard(species=species)
    
    # Load more button
    solara.Button("Load More", on_click=load_more_species)
```

## Testing Frontend Components

### Component Testing

Test components in isolation:

```python
# tests/test_components.py
import pytest
import solara
from frontend.components.common.loading_spinner import LoadingSpinner

def test_loading_spinner():
    """Test loading spinner component."""
    
    @solara.component
    def TestApp():
        LoadingSpinner("Test message")
    
    # Test component renders without errors
    box, rc = solara.render(TestApp(), handle_error=False)
    
    # Verify component structure
    assert "Test message" in str(box)

def test_species_card():
    """Test species card component."""
    test_species = {
        "id": "aedes_aegypti",
        "scientific_name": "Aedes aegypti",
        "common_names": {"en": "Yellow fever mosquito"}
    }
    
    @solara.component
    def TestApp():
        SpeciesCard(species=test_species)
    
    box, rc = solara.render(TestApp(), handle_error=False)
    assert "Aedes aegypti" in str(box)
```

### Integration Testing

Test component interactions:

```python
def test_prediction_workflow():
    """Test complete prediction workflow."""
    
    @solara.component
    def TestPredictionPage():
        PredictionPage()
    
    box, rc = solara.render(TestPredictionPage(), handle_error=False)
    
    # Simulate file upload
    # Test prediction results display
    # Verify state updates
```

## Debugging and Development Tools

### Debug Mode

Enable debug mode for development:

```python
# Run with debug mode
solara run frontend.main --debug

# Add debug prints in components
@solara.component
def DebugComponent():
    data, set_data = solara.use_state([])
    
    # Debug state changes
    def debug_effect():
        print(f"Data updated: {len(data)} items")
    
    solara.use_effect(debug_effect, [data])
```

### Browser Developer Tools

Use browser tools for debugging:
- **React DevTools**: Inspect component hierarchy
- **Network Tab**: Monitor API calls
- **Console**: View JavaScript errors and logs
- **Performance Tab**: Profile rendering performance

This guide provides the foundation for frontend development with Solara. The framework's Python-first approach makes it accessible to backend developers while providing the power and flexibility needed for modern web applications.