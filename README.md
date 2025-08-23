# CulicidaeLab: Mosquito Tracking & Analysis Platform

CulicidaeLab is a comprehensive platform for mosquito research, surveillance, and data analysis. It combines a Python-based backend API (FastAPI) with a dynamic frontend (Solara) to provide tools for species prediction, data visualization, and information retrieval related to mosquitoes and vector-borne diseases.

## ✨ Key Features

*   **AI-Powered Species Prediction:** Upload mosquito images for species identification.
*   **Interactive Map Visualization:** Explore mosquito distribution and observations on a map.
*   **Species Database:** Access detailed information about various mosquito species.
*   **Disease Information Hub:** Learn about mosquito-borne diseases, their vectors, symptoms, and prevention.
*   **Sample Data Generation:** Includes scripts to populate the application with realistic sample data for demonstration and testing.

## 🔧 Tech Stack

*   **Backend:**
    *   FastAPI: High-performance web framework for building APIs.
    *   Uvicorn: ASGI server.
    *   LanceDB: Vector database for efficient similarity search and data storage.

*   **Frontend:**
    *   Solara: Pure Python web framework for building reactive web applications.
    *   ipyleaflet - map components for Solara.
*   **Data Formats:**
    *   JSON, GeoJSON

## 📂 Project Structure


## 🚀 Getting Started

### Prerequisites

*   Python 3.11+
*   uv or pip for Python packages installation
*   Git
*  libgl1 (for linux)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/iloncka-ds/culicidaelab-server.git
    cd culicidaelab-server
    ```

2.  **Install dependencies with pip:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: venv\Scripts\activate
    python -m pip install -e .
    ```

**Note:** If you are using uv, you can install dependencies with [uv](https://docs.astral.sh/uv/):
    ```bash
    uv venv -p 3.11
    source .venv/bin/activate
    # On Windows: .venv\Scripts\activate or .venv\Scripts\activate.ps1
    uv sync -p 3.11
    uv pip install -e .
    uv cache clean
    ```

3.  **Generate Sample Data:**
    This script creates the JSON/GeoJSON files that the backend's `initialize_db` script might use, and that the frontend might load directly or via the API.
    ```bash
    python -m backend.data.sample_data.generate_sample_data
    ```
    This will create files like `sample_species.json`, `sample_observations.geojson`, etc., in the `sample_data/` directory.

4.  **Initialize the Backend Database:**
    This script sets up LanceDB tables and populates them using the generated sample JSON files.
    *(Ensure the paths in `backend/scripts/initialize_db.py` point to the correct location of `sample_species.json` and `sample_diseases.json`, likely `../sample_data/` if run from `backend/scripts/` or adjusted accordingly).*
    ```bash
    python -m backend.scripts.populate_lancedb
    ```
    Check if generation successful by checking the LanceDB database.
    ```bash
    python -m backend.scripts.query_lancedb observations --limit 5
    ```

#### Running the Application

1.  **Run the Backend API Server:**
    Navigate to the project root (or ensure paths in `uvicorn` command are correct).
    ```bash
    cd culicidaelab-server
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    uvicorn backend.main:app --port 8000 --host 127.0.0.1
    ```
    The API will be accessible at `http://localhost:8000`.
    *   Swagger UI: `http://localhost:8000/docs`
    *   ReDoc: `http://localhost:8000/redoc`

2.  **Run the Frontend Application:**
    In a new terminal, navigate to the project root.
    ```bash
    cd culicidaelab-server
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    solara run frontend.main
    ```
    The frontend application will be accessible at `http://localhost:8765` (or the port Solara defaults to/you specify).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs, feature requests, or improvements.

1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

## 📜 License

This project is licensed under the AGPL-3.0 License - see the [LICENSE](https://github.com/iloncka-ds/culicidaelab-server/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

CulicidaeLab development is  supported by a grant from the [**Foundation for Assistance to Small Innovative Enterprises (FASIE)**](https://fasie.ru/).
