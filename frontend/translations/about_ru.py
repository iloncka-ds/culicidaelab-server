MARKDOWN_CONTENT_RU = r"""
# Платформа для отслеживания и анализа комаров

CulicidaeLab — это комплексная платформа для исследований, надзора и анализа данных о комарах. Она сочетает в себе бэкенд-API на Python (FastAPI) с динамическим фронтендом (Solara) для предоставления инструментов для определения видов, визуализации данных и получения информации, связанной с комарами и переносимыми ими заболеваниями.

## Архитектура экосистемы CulicidaeLab

Система с открытым исходным кодом для исследования и анализа комаров включает следующие компоненты:

- **Данные**:

    - Базовый [набор данных о разнообразии (46 видов, 3139 изображений)](https://huggingface.co/datasets/iloncka/mosquito_dataset_46_3139) под лицензией CC-BY-SA-4.0.
    - Специализированные производные наборы данных: для [классификации](https://huggingface.co/datasets/iloncka/mosquito-species-classification-dataset), [детекции](https://huggingface.co/datasets/iloncka/mosquito-species-detection-dataset) и [сегментации](https://huggingface.co/datasets/iloncka/mosquito-species-segmentation-dataset) под лицензиями CC-BY-SA-4.0.

- **Модели**:

    - Топ-1 модели (см. отчеты), используемые по умолчанию библиотекой `culicidaelab`: [классификация (Apache 2.0)](https://huggingface.co/iloncka/culico-net-cls-v1), [детекция (AGPL-3.0)](https://huggingface.co/iloncka/culico-net-det-v1), [сегментация (Apache 2.0)](https://huggingface.co/iloncka/culico-net-segm-v1-nano)
    - [Коллекция Топ-5 моделей классификации](https://huggingface.co/collections/iloncka/mosquito-classification-17-top-5-68945bf60bca2c482395efa8) с точностью >90% для 17 видов комаров.

- **Протоколы**:

    Все параметры обучения и метрики доступны по адресам:

    - [Отчеты по моделям детекции](https://gitlab.com/mosquitoscan/experiments-reports-detection-models)
    - [Отчеты по моделям сегментации](https://gitlab.com/mosquitoscan/experiments-reports-segmentation-models)
    - [Отчеты по экспериментам классификации - 1-й раунд](https://gitlab.com/iloncka/mosal-reports)
    - [Отчеты по экспериментам классификации - 2-й раунд](https://gitlab.com/mosquitoscan/experiments-reports)

- **Приложения**:

    - [Библиотека Python (AGPL-3.0)](https://github.com/iloncka-ds/culicidaelab), предоставляющая основной функционал машинного обучения.
    - [Веб-сервер (AGPL-3.0)](https://github.com/iloncka-ds/culicidaelab-server), предоставляющий API-сервисы.
    - Мобильные приложения (AGPL-3.0): [mosquitoscan](https://gitlab.com/mosquitoscan/mosquitoscan-app) для независимого использования с оптимизированными моделями и [culicidaelab-mobile](https://gitlab.com/iloncka-ds/culicidaelab-mobile) для образовательных и исследовательских целей в рамках экосистемы CulicidaeLab.

Эти компоненты образуют единую экосистему, в которой наборы данных используются для обучения моделей, на которых работают приложения. Библиотека Python обеспечивает основную функциональность веб-сервера, а сервер предоставляет сервисы, используемые мобильным приложением. Все компоненты имеют открытые лицензии, что способствует прозрачности и сотрудничеству.

Такой комплексный подход обеспечивает всесторонние исследования комаров, от сбора данных до их анализа и визуализации, поддерживая как научные исследования, так и инициативы в области общественного здравоохранения.
"""
