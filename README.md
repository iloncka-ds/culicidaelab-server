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

### Installation & Setup
#### Using pip
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/iloncka-ds/culicidaelab-server.git
    cd culicidaelab-server
    ```

2.  **Install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    python -m pip install -e .
    ```

3.  **Generate Sample Data:**
    This script creates the JSON/GeoJSON files that the backend's `initialize_db` script might use, and that the frontend might load directly or via the API.
    ```bash
    cd backend/data/sample_data
    python generate_sample_data.py
    cd ../../../
    ```
    This will create files like `sample_species.json`, `sample_observations.geojson`, etc., in the `sample_data/` directory.

4.  **Initialize the Backend Database:**
    This script sets up LanceDB tables and populates them using the generated sample JSON files.
    *(Ensure the paths in `backend/scripts/initialize_db.py` point to the correct location of `sample_species.json` and `sample_diseases.json`, likely `../sample_data/` if run from `backend/scripts/` or adjusted accordingly).*
    ```bash
    python backend/scripts/populate_lancedb.py
    ```
    Check if generation successful by checking the LanceDB database.
    ```bash
    python backend/scripts/query_lancedb.py observations --limit 5
    ```

### Running the Application

1.  **Run the Backend API Server:**
    Navigate to the project root (or ensure paths in `uvicorn` command are correct).
    ```bash
    uvicorn backend.main:app --reload --port 8000
    ```
    The API will be accessible at `http://localhost:8000`.
    *   Swagger UI: `http://localhost:8000/docs`
    *   ReDoc: `http://localhost:8000/redoc`

2.  **Run the Frontend Application:**
    In a new terminal, navigate to the project root.
    ```bash
    solara run frontend.main:Page --port 8765
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
