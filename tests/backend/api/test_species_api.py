"""Tests for species API endpoints.

This module contains tests for the species router endpoints,
focusing on species listing, detail retrieval, and vector species functionality.
"""

from unittest.mock import MagicMock, patch
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from backend.schemas.species_schemas import SpeciesBase, SpeciesDetail, SpeciesListResponse


class TestSpeciesAPI:
    """Test cases for species API endpoints."""

    def test_get_species_list_success(self, client: TestClient, mock_fastapi_request):
        """Test successful retrieval of species list."""
        mock_species_list = [
            SpeciesBase(
                id="aedes_aegypti",
                scientific_name="Aedes aegypti",
                common_name="Yellow fever mosquito",
                vector_status="Primary",
                image_url="http://testserver/static/species/aedes_aegypti.jpg"
            ),
            SpeciesBase(
                id="culex_pipiens",
                scientific_name="Culex pipiens",
                common_name="Common house mosquito",
                vector_status="Secondary",
                image_url="http://testserver/static/species/culex_pipiens.jpg"
            )
        ]

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_all_species.return_value = mock_species_list
            
            response = client.get("/api/species?limit=50&lang=en")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 2
        assert len(data["species"]) == 2
        assert data["species"][0]["scientific_name"] == "Aedes aegypti"
        assert data["species"][1]["scientific_name"] == "Culex pipiens"

    def test_get_species_list_with_search(self, client: TestClient):
        """Test species list with search parameter."""
        mock_species_list = [
            SpeciesBase(
                id="aedes_aegypti",
                scientific_name="Aedes aegypti",
                common_name="Yellow fever mosquito",
                vector_status="Primary",
                image_url="http://testserver/static/species/aedes_aegypti.jpg"
            )
        ]

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_all_species.return_value = mock_species_list
            
            response = client.get("/api/species?search=aedes&limit=25&lang=en")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["count"] == 1
        assert data["species"][0]["scientific_name"] == "Aedes aegypti"
        
        # Verify service was called with correct parameters
        mock_service.get_all_species.assert_called_once()
        call_args = mock_service.get_all_species.call_args
        assert call_args[1]["search"] == "aedes"
        assert call_args[1]["limit"] == 25
        assert call_args[1]["lang"] == "en"

    def test_get_species_list_pagination_limits(self, client: TestClient):
        """Test species list with various pagination parameters."""
        mock_species_list = []

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_all_species.return_value = mock_species_list
            
            # Test minimum limit
            response = client.get("/api/species?limit=1")
            assert response.status_code == status.HTTP_200_OK
            
            # Test maximum limit
            response = client.get("/api/species?limit=200")
            assert response.status_code == status.HTTP_200_OK
            
            # Test limit exceeding maximum (should be rejected by FastAPI validation)
            response = client.get("/api/species?limit=300")
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_species_detail_success(self, client: TestClient):
        """Test successful retrieval of species detail."""
        mock_species_detail = SpeciesDetail(
            id="aedes_aegypti",
            scientific_name="Aedes aegypti",
            common_name="Yellow fever mosquito",
            vector_status="Primary",
            image_url="http://testserver/static/species/aedes_aegypti.jpg",
            description="A small, dark mosquito with white markings on legs and body.",
            key_characteristics=["White markings on legs", "Lyre-shaped pattern on thorax"],
            geographic_regions=["Tropical", "Subtropical"],
            related_diseases=["Yellow fever", "Dengue", "Zika", "Chikungunya"],
            habitat_preferences=["Urban areas", "Standing water", "Containers"]
        )

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db, \
             patch("backend.routers.species.get_region_cache") as mock_region_cache:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_region_cache.return_value = {}
            mock_service.get_species_by_id.return_value = mock_species_detail
            
            response = client.get("/api/species/aedes_aegypti?lang=en")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == "aedes_aegypti"
        assert data["scientific_name"] == "Aedes aegypti"
        assert data["description"] == "A small, dark mosquito with white markings on legs and body."
        assert len(data["key_characteristics"]) == 2
        assert len(data["related_diseases"]) == 4
        assert "Yellow fever" in data["related_diseases"]

    def test_get_species_detail_not_found(self, client: TestClient):
        """Test species detail retrieval for non-existent species."""
        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db, \
             patch("backend.routers.species.get_region_cache") as mock_region_cache:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_region_cache.return_value = {}
            mock_service.get_species_by_id.return_value = None
            
            response = client.get("/api/species/nonexistent_species?lang=en")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Species not found"

    def test_get_species_detail_different_languages(self, client: TestClient):
        """Test species detail retrieval with different language parameters."""
        mock_species_detail = SpeciesDetail(
            id="aedes_aegypti",
            scientific_name="Aedes aegypti",
            common_name="Mosquito de la fiebre amarilla",  # Spanish name
            vector_status="Primario",
            image_url="http://testserver/static/species/aedes_aegypti.jpg",
            description="Un mosquito pequeño y oscuro con marcas blancas en las patas y el cuerpo.",
            key_characteristics=["Marcas blancas en las patas"],
            geographic_regions=["Tropical", "Subtropical"],
            related_diseases=["Fiebre amarilla", "Dengue"],
            habitat_preferences=["Áreas urbanas"]
        )

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db, \
             patch("backend.routers.species.get_region_cache") as mock_region_cache:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_region_cache.return_value = {}
            mock_service.get_species_by_id.return_value = mock_species_detail
            
            response = client.get("/api/species/aedes_aegypti?lang=es")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["common_name"] == "Mosquito de la fiebre amarilla"
        
        # Verify service was called with Spanish language
        mock_service.get_species_by_id.assert_called_once()
        call_args = mock_service.get_species_by_id.call_args
        assert call_args[0][2] == "es"  # lang parameter

    def test_get_vector_species_all(self, client: TestClient):
        """Test retrieval of all vector species."""
        mock_vector_species = [
            SpeciesBase(
                id="aedes_aegypti",
                scientific_name="Aedes aegypti",
                common_name="Yellow fever mosquito",
                vector_status="Primary",
                image_url="http://testserver/static/species/aedes_aegypti.jpg"
            ),
            SpeciesBase(
                id="anopheles_gambiae",
                scientific_name="Anopheles gambiae",
                common_name="African malaria mosquito",
                vector_status="Primary",
                image_url="http://testserver/static/species/anopheles_gambiae.jpg"
            )
        ]

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_vector_species.return_value = mock_vector_species
            
            response = client.get("/api/vector-species?lang=en")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        assert data[0]["vector_status"] == "Primary"
        assert data[1]["vector_status"] == "Primary"

    def test_get_vector_species_by_disease(self, client: TestClient):
        """Test retrieval of vector species filtered by disease."""
        mock_malaria_vectors = [
            SpeciesBase(
                id="anopheles_gambiae",
                scientific_name="Anopheles gambiae",
                common_name="African malaria mosquito",
                vector_status="Primary",
                image_url="http://testserver/static/species/anopheles_gambiae.jpg"
            )
        ]

        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_vector_species.return_value = mock_malaria_vectors
            
            response = client.get("/api/vector-species?disease_id=malaria&lang=en")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["scientific_name"] == "Anopheles gambiae"
        
        # Verify service was called with disease filter
        mock_service.get_vector_species.assert_called_once()
        call_args = mock_service.get_vector_species.call_args
        assert call_args[1]["disease_id"] == "malaria"

    def test_get_vector_species_empty_result(self, client: TestClient):
        """Test vector species endpoint with no results."""
        with patch("backend.routers.species.species_service") as mock_service, \
             patch("backend.routers.species.database.get_db") as mock_get_db:
            
            mock_db = MagicMock()
            mock_get_db.return_value = mock_db
            mock_service.get_vector_species.return_value = []
            
            response = client.get("/api/vector-species?disease_id=nonexistent_disease")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 0