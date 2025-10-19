"""
Tests for Docker Compose configurations.
Validates that Docker Compose files are properly structured and services can be orchestrated.
"""

import pytest
import yaml
import subprocess
from pathlib import Path


class TestDockerCompose:
    """Test suite for validating Docker Compose configurations."""

    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture(scope="class")
    def compose_prod_config(self, project_root):
        """Load production Docker Compose configuration."""
        compose_file = project_root / "docker-compose.prod.yml"
        with open(compose_file) as f:
            return yaml.safe_load(f)

    @pytest.fixture(scope="class")
    def compose_dev_config(self, project_root):
        """Load development Docker Compose configuration."""
        compose_file = project_root / "docker-compose.dev.yml"
        with open(compose_file) as f:
            return yaml.safe_load(f)

    def test_compose_file_syntax(self, project_root):
        """Test that Docker Compose files have valid syntax."""
        compose_files = [
            "docker-compose.prod.yml",
            "docker-compose.dev.yml",
        ]

        for compose_file in compose_files:
            file_path = project_root / compose_file
            if file_path.exists():
                try:
                    result = subprocess.run(
                        ["docker-compose", "-f", str(file_path), "config"],
                        capture_output=True,
                        text=True,
                        cwd=project_root,
                    )
                    assert result.returncode == 0, f"Invalid syntax in {compose_file}: {result.stderr}"
                except FileNotFoundError:
                    pytest.skip("docker-compose not available")

    def test_production_compose_structure(self, compose_prod_config):
        """Test production Docker Compose file structure."""
        # Check version
        assert compose_prod_config.get("version") == "3.8"

        # Check required services
        services = compose_prod_config.get("services", {})
        required_services = ["backend", "frontend", "nginx", "certbot"]

        for service in required_services:
            assert service in services, f"Missing required service: {service}"

        # Check backend service configuration
        backend = services["backend"]
        assert "build" in backend
        assert "restart" in backend
        assert backend["restart"] == "unless-stopped"
        assert "healthcheck" in backend
        assert "logging" in backend

        # Check frontend service configuration
        frontend = services["frontend"]
        assert "build" in frontend
        assert "restart" in frontend
        assert "depends_on" in frontend
        assert "backend" in frontend["depends_on"]

        # Check nginx service configuration
        nginx = services["nginx"]
        assert "ports" in nginx
        assert "80:80" in nginx["ports"]
        assert "443:443" in nginx["ports"]
        assert "volumes" in nginx

        # Check certbot service configuration
        certbot = services["certbot"]
        assert "image" in certbot
        assert "certbot/certbot" in certbot["image"]
        assert "volumes" in certbot

    def test_development_compose_structure(self, compose_dev_config):
        """Test development Docker Compose file structure."""
        # Check version
        assert compose_dev_config.get("version") == "3.8"

        # Check required services
        services = compose_dev_config.get("services", {})
        required_services = ["backend", "frontend", "nginx"]

        for service in required_services:
            assert service in services, f"Missing required service: {service}"

        # Check development-specific configurations
        backend = services["backend"]
        assert "volumes" in backend
        assert any("./backend" in vol for vol in backend["volumes"])
        assert backend.get("restart") == "no"

        # Check port exposure for development
        assert "ports" in backend
        assert "8000:8000" in backend["ports"]

        frontend = services["frontend"]
        assert "volumes" in frontend
        assert any("./frontend" in vol for vol in frontend["volumes"])
        assert "ports" in frontend
        assert "8765:8765" in frontend["ports"]

    def test_compose_networks(self, compose_prod_config, compose_dev_config):
        """Test that Docker Compose files define proper networks."""
        # Test production networks
        prod_networks = compose_prod_config.get("networks", {})
        assert "culicidaelab_network" in prod_networks

        prod_services = compose_prod_config.get("services", {})
        for service_name, service_config in prod_services.items():
            if service_name != "certbot":  # certbot might not need network access
                assert "networks" in service_config
                assert "culicidaelab_network" in service_config["networks"]

        # Test development networks
        dev_networks = compose_dev_config.get("networks", {})
        assert "culicidaelab_network" in dev_networks

        dev_services = compose_dev_config.get("services", {})
        for service_name, service_config in dev_services.items():
            if "networks" in service_config:
                assert "culicidaelab_network" in service_config["networks"]

    def test_compose_volumes(self, compose_prod_config):
        """Test that Docker Compose files define proper volumes."""
        volumes = compose_prod_config.get("volumes", {})

        required_volumes = [
            "letsencrypt_certs",
            "letsencrypt_www",
            "backend_data",
            "backend_static",
        ]

        for volume in required_volumes:
            assert volume in volumes, f"Missing required volume: {volume}"

    def test_compose_environment_variables(self, compose_prod_config, compose_dev_config):
        """Test that services have proper environment variable configurations."""
        # Test production environment variables
        prod_services = compose_prod_config.get("services", {})

        backend_env = prod_services["backend"].get("environment", [])
        backend_env_dict = {}
        for env_var in backend_env:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                backend_env_dict[key] = value

        assert "CULICIDAELAB_DATABASE_PATH" in backend_env_dict
        assert "CULICIDAELAB_BACKEND_CORS_ORIGINS" in backend_env_dict

        frontend_env = prod_services["frontend"].get("environment", [])
        frontend_env_dict = {}
        for env_var in frontend_env:
            if "=" in env_var:
                key, value = env_var.split("=", 1)
                frontend_env_dict[key] = value

        assert "BACKEND_URL" in frontend_env_dict
        assert frontend_env_dict["BACKEND_URL"] == "http://backend:8000"

        # Test development environment variables
        dev_services = compose_dev_config.get("services", {})
        dev_backend_env = dev_services["backend"].get("environment", [])

        # Check for development-specific variables
        dev_env_vars = [env.split("=")[0] if "=" in env else env for env in dev_backend_env]
        assert "DEBUG" in dev_env_vars or "FASTAPI_ENV" in dev_env_vars

    def test_compose_health_checks(self, compose_prod_config):
        """Test that services have proper health check configurations."""
        services = compose_prod_config.get("services", {})

        health_check_services = ["backend", "frontend", "nginx"]

        for service_name in health_check_services:
            service = services[service_name]
            assert "healthcheck" in service, f"Missing health check for {service_name}"

            healthcheck = service["healthcheck"]
            assert "test" in healthcheck
            assert "interval" in healthcheck
            assert "timeout" in healthcheck
            assert "retries" in healthcheck

    def test_compose_security_configurations(self, compose_prod_config):
        """Test that services have proper security configurations."""
        services = compose_prod_config.get("services", {})

        # Check for security options
        for service_name, service_config in services.items():
            if service_name != "certbot":  # certbot might have different security requirements
                if "security_opt" in service_config:
                    security_opts = service_config["security_opt"]
                    assert "no-new-privileges:true" in security_opts

    def test_compose_resource_limits(self, compose_prod_config):
        """Test that services have resource limits configured."""
        services = compose_prod_config.get("services", {})

        resource_limited_services = ["backend", "frontend", "nginx"]

        for service_name in resource_limited_services:
            service = services[service_name]
            if "deploy" in service:
                deploy_config = service["deploy"]
                if "resources" in deploy_config:
                    resources = deploy_config["resources"]
                    assert "limits" in resources
                    limits = resources["limits"]
                    assert "memory" in limits
                    assert "cpus" in limits

    def test_compose_logging_configuration(self, compose_prod_config):
        """Test that services have proper logging configurations."""
        services = compose_prod_config.get("services", {})

        for service_name, service_config in services.items():
            if "logging" in service_config:
                logging_config = service_config["logging"]
                assert "driver" in logging_config
                assert logging_config["driver"] == "json-file"

                if "options" in logging_config:
                    options = logging_config["options"]
                    assert "max-size" in options
                    assert "max-file" in options

    def test_compose_service_dependencies(self, compose_prod_config):
        """Test that service dependencies are properly configured."""
        services = compose_prod_config.get("services", {})

        # Frontend should depend on backend
        frontend = services["frontend"]
        assert "depends_on" in frontend
        depends_on = frontend["depends_on"]

        if isinstance(depends_on, dict):
            assert "backend" in depends_on
            if "condition" in depends_on["backend"]:
                assert depends_on["backend"]["condition"] == "service_healthy"
        elif isinstance(depends_on, list):
            assert "backend" in depends_on

        # Nginx should depend on backend and frontend in production
        nginx = services["nginx"]
        if "depends_on" in nginx:
            nginx_depends = nginx["depends_on"]
            if isinstance(nginx_depends, list):
                assert "backend" in nginx_depends or "frontend" in nginx_depends
            elif isinstance(nginx_depends, dict):
                assert "backend" in nginx_depends or "frontend" in nginx_depends
