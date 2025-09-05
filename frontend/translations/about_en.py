MARKDOWN_CONTENT_EN = r"""

CulicidaeLab (server) is a comprehensive platform for mosquito research, surveillance, and data analysis. It combines a Python-based backend API (FastAPI) with a dynamic frontend (Solara) to provide tools for species prediction, data visualization, and information retrieval related to mosquitoes and vector-borne diseases.

## CulicidaeLab Ecosystem Architecture

An open-source system for mosquito research and analysis includes components:

- **Data**:

    - Base [diversity dataset (46 species, 3139 images](https://huggingface.co/datasets/iloncka/mosquito_dataset_46_3139)) under CC-BY-SA-4.0 license.
    - Specialized derivatives: [classification](https://huggingface.co/datasets/iloncka/mosquito-species-classification-dataset), [detection](https://huggingface.co/datasets/iloncka/mosquito-species-detection-dataset), and [segmentation](https://huggingface.co/datasets/iloncka/mosquito-species-segmentation-dataset) datasets under CC-BY-SA-4.0 licenses.

- **Models**:

    - Top-1 models (see reports), used as default by `culicidaelab` library: [classification (Apache 2.0)](https://huggingface.co/iloncka/culico-net-cls-v1), [detection (AGPL-3.0)](https://huggingface.co/iloncka/culico-net-det-v1), [segmentation (Apache 2.0)](https://huggingface.co/iloncka/culico-net-segm-v1-nano)
    - [Top-5 classification models collection](https://huggingface.co/collections/iloncka/mosquito-classification-17-top-5-68945bf60bca2c482395efa8) with accuracy >90% for 17 mosquito species.

- **Protocols**:

    All training parameters and metrics available at:

    - [Detection model reports](https://gitlab.com/mosquitoscan/experiments-reports-detection-models)
    - [Segmentation model reports](https://gitlab.com/mosquitoscan/experiments-reports-segmentation-models)
    - [Classification experiment reports - 1st round](https://gitlab.com/iloncka/mosal-reports)
    - [Classification experiment reports - 2nd round](https://gitlab.com/mosquitoscan/experiments-reports)

- **Applications**:

    - [Python library (AGPL-3.0)](https://github.com/iloncka-ds/culicidaelab) providing core ML functionality
    - [Web server (AGPL-3.0)](https://github.com/iloncka-ds/culicidaelab-server) hosting API services
    - Mobile apps (AGPL-3.0): [mosquitoscan](https://gitlab.com/mosquitoscan/mosquitoscan-app) for independent use with optimized models and [culicidaelab-mobile](https://gitlab.com/iloncka-ds/culicidaelab-mobile) for educational and research purposes as part of the CulicidaeLab Ecosystem.

These components form a cohesive ecosystem where datasets used for training models that power applications, the Python library provides core functionality to the web server, and the server exposes services consumed by the mobile application. All components are openly licensed, promoting transparency and collaboration.

This integrated approach enables comprehensive mosquito research, from data collection to analysis and visualization, supporting both scientific research and public health initiatives.
"""
