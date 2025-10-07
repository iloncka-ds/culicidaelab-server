<!-- Cross-reference templates for common page relationships -->

<!-- Getting Started Cross-References -->
{% set getting_started_refs = [
    ("Quick Start Guide", "getting-started/quick-start.md"),
    ("Configuration", "getting-started/configuration.md"),
    ("API Reference", "developer-guide/api-reference/index.md")
] %}

<!-- Developer Guide Cross-References -->
{% set developer_refs = [
    ("Architecture Overview", "developer-guide/architecture.md"),
    ("API Reference", "developer-guide/api-reference/index.md"),
    ("Testing Guidelines", "developer-guide/testing.md"),
    ("Contributing", "developer-guide/contributing.md")
] %}

<!-- User Guide Cross-References -->
{% set user_guide_refs = [
    ("Platform Overview", "user-guide/overview.md"),
    ("Species Prediction", "user-guide/species-prediction.md"),
    ("Map Visualization", "user-guide/map-visualization.md"),
    ("Troubleshooting", "user-guide/troubleshooting.md")
] %}

<!-- Deployment Cross-References -->
{% set deployment_refs = [
    ("Production Deployment", "deployment/production.md"),
    ("Docker Setup", "deployment/docker.md"),
    ("Monitoring", "deployment/monitoring.md"),
    ("Configuration Reference", "reference/configuration.md")
] %}

<!-- Research Cross-References -->
{% set research_refs = [
    ("Data Models", "research/data-models.md"),
    ("AI Models", "research/ai-models.md"),
    ("Datasets", "research/datasets.md"),
    ("API Integration", "developer-guide/api-reference/index.md")
] %}

<!-- Macro for rendering cross-references -->
{% macro render_cross_refs(refs, title="Related Pages") %}
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