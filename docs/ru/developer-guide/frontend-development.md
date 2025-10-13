# Руководство по разработке фронтенда

Это руководство охватывает разработку фронтенда для CulicidaeLab Server с использованием Solara, чисто Python реактивного веб-фреймворка, который позволяет создавать современные веб-приложения без JavaScript.

## Настройка среды разработки

### Предварительные требования

- Python 3.11+
- Запущенный сервер бэкенда (см. [Руководство по разработке бэкенда](backend-development.md))
- Современный веб-браузер для тестирования

### Настройка фронтенда

1. **Убедитесь, что бэкенд запущен:**
```bash
# В одном терминале запустите бэкенд
uvicorn backend.main:app --port 8000 --host 127.0.0.1 --reload
```

2. **Запустите сервер разработки фронтенда:**
```bash
# В другом терминале
source .venv/bin/activate  # На Windows: .venv\Scripts\activate
solara run frontend.main --host 127.0.0.1 --port 8765
```

Фронтенд будет доступен по адресу http://localhost:8765

### Горячая перезагрузка

Solara поддерживает горячую перезагрузку для быстрой разработки:
- Изменения в Python файлах автоматически перезагружают приложение
- Состояние сохраняется между перезагрузками когда возможно
- Браузер автоматически обновляется для отображения изменений

## Структура проекта

```
frontend/
├── main.py                 # Точка входа приложения и маршрутизация
├── config.py              # Конфигурация и стилизация
├── state.py               # Глобальное управление состоянием
├── pages/                 # Компоненты страниц
│   ├── home.py            # Главная страница
│   ├── prediction.py      # Интерфейс предсказания видов
│   ├── map_visualization.py # Интерактивная карта
│   ├── species.py         # Галерея и детали видов
│   ├── diseases.py        # Информация о болезнях
│   └── about.py           # Страница "О проекте"
├── components/            # Переиспользуемые UI компоненты
│   ├── common/            # Общие компоненты
│   ├── prediction/        # Компоненты для предсказаний
│   ├── map_module/        # Компоненты карты
│   ├── species/           # Компоненты, связанные с видами
│   └── diseases/          # Компоненты, связанные с болезнями
├── translations/          # Файлы интернационализации
│   ├── home.en.yml        # Английские переводы
│   ├── home.ru.yml        # Русские переводы
│   └── ...
└── assets/                # Статические ресурсы
    ├── custom.css         # Пользовательские стили
    └── theme.js           # Конфигурация темы
```

## Основы фреймворка Solara

### Архитектура компонентов

Solara использует компонентную архитектуру, похожую на React:

```python
import solara

@solara.component
def MyComponent(title: str, items: list[str]):
    """Простой пример компонента.
    
    Args:
        title: Заголовок компонента
        items: Список элементов для отображения
    """
    with solara.Card(title):
        for item in items:
            solara.Text(item)

# Использование
@solara.component  
def Page():
    MyComponent("Мой список", ["Элемент 1", "Элемент 2", "Элемент 3"])
```

### Управление реактивным состоянием

Solara использует реактивные переменные для управления состоянием:

```python
import solara

# Глобальное реактивное состояние
counter = solara.reactive(0)
selected_items = solara.reactive([])

@solara.component
def Counter():
    """Компонент с реактивным состоянием."""
    
    def increment():
        counter.value += 1
    
    def decrement():
        counter.value -= 1
    
    with solara.Row():
        solara.Button("−", on_click=decrement)
        solara.Text(f"Счетчик: {counter.value}")
        solara.Button("+", on_click=increment)
```

### Хуки и эффекты

Используйте хуки для побочных эффектов и управления жизненным циклом:

```python
import solara
import httpx

@solara.component
def DataLoader():
    """Компонент, который загружает данные при монтировании."""
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
    
    # Загрузка данных при монтировании компонента
    solara.use_effect(load_data, [])
    
    if loading:
        solara.SpinnerSolara()
    elif data:
        solara.Text(f"Загружено {len(data)} элементов")
    else:
        solara.Text("Данные недоступны")
```

## Архитектура приложения

### Система маршрутизации

Главное приложение определяет маршруты и макет:

```python
# main.py
import solara
from frontend.pages import home, prediction, species

@solara.component
def Layout(children):
    """Основной макет приложения."""
    route_current, routes_all = solara.use_route()
    
    with solara.AppLayout(toolbar_dark=True):
        with solara.AppBar():
            with solara.AppBarTitle():
                solara.Text("CulicidaeLab")
            
            # Кнопки навигации
            for route in routes_all:
                with solara.Link(route):
                    solara.Button(route.label)
        
        # Содержимое страницы
        with solara.Column(children=children):
            pass

# Конфигурация маршрутов
routes = [
    solara.Route("/", component=home.Home, label="Главная", layout=Layout),
    solara.Route("predict", component=prediction.Page, label="Предсказать"),
    solara.Route("species", component=species.Page, label="Виды"),
]
```

### Паттерн управления состоянием

Глобальное состояние управляется в `state.py`:

```python
# state.py
import solara
from typing import Optional

# Состояние приложения
current_user_id = solara.reactive(None)
selected_species = solara.reactive([])
map_center = solara.reactive((40.4168, -3.7038))
loading_states = {
    'species': solara.reactive(False),
    'predictions': solara.reactive(False),
    'observations': solara.reactive(False)
}

# Кэши данных API
species_data = solara.reactive([])
filter_options = solara.reactive({})

async def fetch_species_data():
    """Получить и кэшировать данные видов."""
    if loading_states['species'].value:
        return
        
    loading_states['species'].value = True
    try:
        # Логика вызова API
        async with httpx.AsyncClient() as client:
            response = await client.get("/api/species")
            species_data.value = response.json()
    finally:
        loading_states['species'].value = False
```

## Паттерны разработки компонентов

### Компоненты страниц

Компоненты страниц представляют полные представления приложения:

```python
# pages/species.py
import solara
from frontend.components.species import SpeciesGallery, SpeciesDetail
from frontend.state import selected_species_item_id

@solara.component
def Page():
    """Страница видов с галереей и детальными представлениями."""
    route_current, _ = solara.use_route()
    species_id = route_current.params.get("species_id")
    
    if species_id:
        # Показать детали вида
        SpeciesDetail(species_id=species_id)
    else:
        # Показать галерею видов
        SpeciesGallery()
```

### Переиспользуемые компоненты

Создавайте модульные, переиспользуемые компоненты:

```python
# components/common/loading_spinner.py
import solara

@solara.component
def LoadingSpinner(message: str = "Загрузка..."):
    """Переиспользуемый компонент спиннера загрузки."""
    with solara.Column(align="center"):
        solara.SpinnerSolara()
        solara.Text(message, style={"margin-top": "1rem"})

# components/common/error_message.py
@solara.component  
def ErrorMessage(error: str, retry_callback=None):
    """Переиспользуемый компонент сообщения об ошибке."""
    with solara.Card():
        solara.Error(f"Ошибка: {error}")
        if retry_callback:
            solara.Button("Повторить", on_click=retry_callback)
```

### Компоненты форм

Обрабатывайте пользовательский ввод с компонентами форм:

```python
# components/prediction/upload_form.py
import solara
from typing import Optional

@solara.component
def ImageUploadForm(on_upload_complete=None):
    """Форма загрузки изображения для предсказания видов."""
    uploaded_file, set_uploaded_file = solara.use_state(None)
    uploading, set_uploading = solara.use_state(False)
    
    def handle_file_upload(file_info):
        set_uploaded_file(file_info)
    
    async def submit_prediction():
        if not uploaded_file:
            return
            
        set_uploading(True)
        try:
            # Загрузка и предсказание
            async with httpx.AsyncClient() as client:
                files = {"file": uploaded_file["file_obj"]}
                response = await client.post("/api/predict_species/", files=files)
                result = response.json()
                
                if on_upload_complete:
                    on_upload_complete(result)
        finally:
            set_uploading(False)
    
    with solara.Card("Загрузить изображение для предсказания"):
        solara.FileDrop(
            on_file=handle_file_upload,
            accept=".jpg,.jpeg,.png",
            multiple=False
        )
        
        if uploaded_file:
            solara.Text(f"Выбрано: {uploaded_file['name']}")
            
        solara.Button(
            "Предсказать вид",
            on_click=submit_prediction,
            disabled=not uploaded_file or uploading
        )
        
        if uploading:
            LoadingSpinner("Анализ изображения...")
```

## Работа с картами

### Интерактивные карты с ipyleaflet

Приложение использует ipyleaflet для интерактивного картографирования:

```python
# components/map_module/observation_map.py
import solara
import ipyleaflet
from frontend.state import current_map_center, observations_data

@solara.component
def ObservationMap():
    """Интерактивная карта, показывающая наблюдения комаров."""
    
    # Создание виджета карты
    map_widget = ipyleaflet.Map(
        center=current_map_center.value,
        zoom=5,
        scroll_wheel_zoom=True
    )
    
    # Добавление маркеров наблюдений
    def update_markers():
        # Очистка существующих маркеров
        map_widget.layers = [map_widget.layers[0]]  # Сохранить базовый слой
        
        # Добавление маркеров наблюдений
        for obs in observations_data.value:
            marker = ipyleaflet.Marker(
                location=(obs['latitude'], obs['longitude']),
                popup=ipyleaflet.Popup(
                    child=solara.HTML(f"""
                        <div>
                            <h4>{obs['species']}</h4>
                            <p>Уверенность: {obs['confidence']:.2%}</p>
                            <p>Дата: {obs['date']}</p>
                        </div>
                    """)
                )
            )
            map_widget.add_layer(marker)
    
    # Обновление маркеров при изменении данных
    solara.use_effect(update_markers, [observations_data.value])
    
    # Обработка взаимодействий с картой
    def on_map_click(**kwargs):
        location = kwargs.get('coordinates')
        if location:
            # Обработка клика по карте
            print(f"Клик по: {location}")
    
    map_widget.on_interaction(on_map_click)
    
    # Отображение карты
    solara.display(map_widget)
```

## Визуализация данных

### Интеграция Plotly

Используйте Plotly для интерактивных графиков и диаграмм:

```python
# components/species/distribution_chart.py
import solara
import plotly.graph_objects as go
from frontend.state import species_data

@solara.component
def SpeciesDistributionChart():
    """График, показывающий распределение видов по регионам."""
    
    def create_chart():
        if not species_data.value:
            return go.Figure()
        
        # Обработка данных для графика
        regions = {}
        for species in species_data.value:
            for region in species.get('regions', []):
                regions[region] = regions.get(region, 0) + 1
        
        # Создание столбчатой диаграммы
        fig = go.Figure(data=[
            go.Bar(
                x=list(regions.keys()),
                y=list(regions.values()),
                marker_color='#009688'
            )
        ])
        
        fig.update_layout(
            title="Распределение видов по регионам",
            xaxis_title="Регион",
            yaxis_title="Количество видов",
            template="plotly_white"
        )
        
        return fig
    
    chart = create_chart()
    solara.FigurePlotly(chart)
```

## Интернационализация (i18n)

### Система переводов

Приложение поддерживает несколько языков:

```python
# Использование переводов в компонентах
import i18n

@solara.component
def WelcomeMessage():
    """Компонент с интернационализированным текстом."""
    
    # Загрузка переводов
    title = i18n.t("home.welcome_title")
    description = i18n.t("home.welcome_description")
    
    with solara.Column():
        solara.Markdown(f"# {title}")
        solara.Text(description)

# Файлы переводов (translations/home.en.yml)
# home:
#   welcome_title: "Welcome to CulicidaeLab"
#   welcome_description: "Mosquito research and analysis platform"

# Файлы переводов (translations/home.ru.yml)  
# home:
#   welcome_title: "Добро пожаловать в CulicidaeLab"
#   welcome_description: "Платформа для исследования и анализа комаров"
```

### Переключение языка

Реализуйте переключение языка:

```python
# components/common/locale_selector.py
import solara
import i18n
from frontend.state import current_locale

@solara.component
def LocaleSelector():
    """Компонент выбора языка."""
    
    languages = [
        ("en", "English"),
        ("ru", "Русский")
    ]
    
    def change_language(new_locale):
        current_locale.value = new_locale
        i18n.set("locale", new_locale)
    
    with solara.Select(
        label="Язык",
        value=current_locale.value,
        values=[lang[0] for lang in languages],
        on_value=change_language
    ):
        for code, name in languages:
            solara.Option(code, name)
```

## Стилизация и темизация

### Тема Material Design

Приложение использует компоненты Material Design:

```python
# config.py - Конфигурация темы
import solara.lab

def load_themes(theme):
    """Настроить тему Material Design."""
    theme.themes.light.primary = "#009688"
    theme.themes.light.secondary = "#B2DFDB"
    theme.themes.light.accent = "#00796B"
    
    theme.themes.dark.primary = "#009688"
    theme.themes.dark.secondary = "#B2DFDB"
    theme.themes.dark.accent = "#00796B"
    
    return theme

# Применение темы при запуске
theme = load_themes(solara.lab.theme)
```

### Пользовательская стилизация

Добавьте пользовательский CSS для улучшенной стилизации:

```python
# Использование встроенных стилей
@solara.component
def StyledCard():
    card_style = {
        "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
        "color": "white",
        "border-radius": "12px",
        "padding": "2rem"
    }
    
    with solara.Card(style=card_style):
        solara.Text("Стилизованное содержимое")

# Использование CSS классов (assets/custom.css)
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
        solara.Text("Результат предсказания")
```

## Оптимизация производительности

### Эффективные обновления состояния

Минимизируйте ненужные перерисовки:

```python
import solara

# Используйте локальное состояние для изменений только UI
@solara.component
def SearchBox():
    query, set_query = solara.use_state("")
    
    # Дебаунс поиска для избежания избыточных вызовов API
    def debounced_search():
        if len(query) >= 3:
            # Запуск поиска после задержки
            pass
    
    solara.use_effect(debounced_search, [query])
    
    solara.InputText(
        label="Поиск видов",
        value=query,
        on_value=set_query
    )

# Мемоизация дорогих вычислений
@solara.component
def ExpensiveChart(data: list):
    # Пересчитывать только при изменении данных
    processed_data = solara.use_memo(
        lambda: process_chart_data(data),
        [data]
    )
    
    chart = create_chart(processed_data)
    solara.FigurePlotly(chart)
```

### Ленивая загрузка

Реализуйте ленивую загрузку для лучшей производительности:

```python
@solara.component
def LazySpeciesGallery():
    """Галерея видов с ленивой загрузкой."""
    page, set_page = solara.use_state(1)
    species_list, set_species_list = solara.use_state([])
    
    async def load_more_species():
        async with httpx.AsyncClient() as client:
            response = await client.get(f"/api/species?page={page}")
            new_species = response.json()
            set_species_list(species_list + new_species)
            set_page(page + 1)
    
    # Первоначальная загрузка
    solara.use_effect(load_more_species, [])
    
    # Отображение видов
    for species in species_list:
        SpeciesCard(species=species)
    
    # Кнопка загрузки еще
    solara.Button("Загрузить еще", on_click=load_more_species)
```

## Тестирование компонентов фронтенда

### Тестирование компонентов

Тестируйте компоненты в изоляции:

```python
# tests/test_components.py
import pytest
import solara
from frontend.components.common.loading_spinner import LoadingSpinner

def test_loading_spinner():
    """Тест компонента спиннера загрузки."""
    
    @solara.component
    def TestApp():
        LoadingSpinner("Тестовое сообщение")
    
    # Тест рендеринга компонента без ошибок
    box, rc = solara.render(TestApp(), handle_error=False)
    
    # Проверка структуры компонента
    assert "Тестовое сообщение" in str(box)

def test_species_card():
    """Тест компонента карточки вида."""
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

### Интеграционное тестирование

Тестируйте взаимодействия компонентов:

```python
def test_prediction_workflow():
    """Тест полного рабочего процесса предсказания."""
    
    @solara.component
    def TestPredictionPage():
        PredictionPage()
    
    box, rc = solara.render(TestPredictionPage(), handle_error=False)
    
    # Симуляция загрузки файла
    # Тест отображения результатов предсказания
    # Проверка обновлений состояния
```

## Отладка и инструменты разработки

### Режим отладки

Включите режим отладки для разработки:

```python
# Запуск с режимом отладки
solara run frontend.main --debug

# Добавление отладочных принтов в компонентах
@solara.component
def DebugComponent():
    data, set_data = solara.use_state([])
    
    # Отладка изменений состояния
    def debug_effect():
        print(f"Данные обновлены: {len(data)} элементов")
    
    solara.use_effect(debug_effect, [data])
```

### Инструменты разработчика браузера

Используйте инструменты браузера для отладки:
- **React DevTools**: Инспектирование иерархии компонентов
- **Вкладка Network**: Мониторинг вызовов API
- **Консоль**: Просмотр JavaScript ошибок и логов
- **Вкладка Performance**: Профилирование производительности рендеринга

Это руководство предоставляет основу для разработки фронтенда с Solara. Python-первый подход фреймворка делает его доступным для разработчиков бэкенда, обеспечивая при этом мощность и гибкость, необходимые для современных веб-приложений.