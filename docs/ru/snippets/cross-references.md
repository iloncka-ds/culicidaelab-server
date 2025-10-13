<!-- Шаблоны перекрестных ссылок для общих связей между страницами -->

<!-- Перекрестные ссылки для раздела "Начало работы" -->
{% set getting_started_refs = [
    ("Руководство по быстрому старту", "getting-started/quick-start.md"),
    ("Конфигурация", "getting-started/configuration.md"),
    ("Справочник API", "developer-guide/api-reference/index.md")
] %}

<!-- Перекрестные ссылки для руководства разработчика -->
{% set developer_refs = [
    ("Обзор архитектуры", "developer-guide/architecture.md"),
    ("Справочник API", "developer-guide/api-reference/index.md"),
    ("Руководство по тестированию", "developer-guide/testing.md"),
    ("Участие в разработке", "developer-guide/contributing.md")
] %}

<!-- Перекрестные ссылки для руководства пользователя -->
{% set user_guide_refs = [
    ("Обзор платформы", "user-guide/overview.md"),
    ("Предсказание видов", "user-guide/species-prediction.md"),
    ("Визуализация карты", "user-guide/map-visualization.md"),
    ("Устранение неполадок", "user-guide/troubleshooting.md")
] %}

<!-- Перекрестные ссылки для развертывания -->
{% set deployment_refs = [
    ("Развертывание в продакшене", "deployment/production.md"),
    ("Настройка Docker", "deployment/docker.md"),
    ("Мониторинг", "deployment/monitoring.md"),
    ("Справочник по конфигурации", "reference/configuration.md")
] %}

<!-- Перекрестные ссылки для исследований -->
{% set research_refs = [
    ("Модели данных", "research/data-models.md"),
    ("ИИ модели", "research/ai-models.md"),
    ("Наборы данных", "research/datasets.md"),
    ("Интеграция API", "developer-guide/api-reference/index.md")
] %}

<!-- Макрос для отображения перекрестных ссылок -->
{% macro render_cross_refs(refs, title="Связанные страницы") %}
<div class="cross-reference">
    <div class="cross-reference__title">{{ title }}</div>
    <ul class="cross-reference__list">
    {% for ref_title, ref_url in refs %}
        <li class="cross-reference__item">
            <a href="{{ ref_url }}" class="cross-reference__link">{{ ref_title }}</a>
        </li>
    {% endfor %}
    </ul>
</div>
{% endmacro %}