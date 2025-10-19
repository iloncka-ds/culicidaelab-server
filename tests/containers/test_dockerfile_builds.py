"""
Tests for Dockerfile builds and container functionality.
Validates that all Docker images build successfully and meet security requirements.
"""

import pytest
import docker
import time
from pathlib import Path


class TestDockerfileBuilds:
    """Test suite for validating Dockerfile builds."""

    @pytest.fixture(scope="class")
    def docker_client(self):
        """Initialize Docker client."""
        try:
            client = docker.from_env()
            # Test Docker connection
            client.ping()
            return client
        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    def test_backend_dockerfile_build(self, docker_client, project_root):
        """Test that backend Dockerfile builds successfully."""

        # Build the backend image with correct context
        try:
            image, build_logs = docker_client.images.build(
                path=str(project_root),
                dockerfile="backend/Dockerfile",
                tag="culicidaelab-backend:test",
                rm=True,
                forcerm=True,
            )

            # Verify image was created
            assert image is not None
            assert "culicidaelab-backend:test" in [tag for tag in image.tags]

            # Check image labels and metadata
            config = image.attrs["Config"]
            assert config["ExposedPorts"]["8000/tcp"] == {}
            assert config["User"] == "appuser"

            # Verify health check is configured
            assert "Healthcheck" in config
            assert "curl -f http://localhost:8000/api/health" in config["Healthcheck"]["Test"][1]

        except docker.errors.BuildError as e:
            pytest.fail(f"Backend Dockerfile build failed: {e}")
        finally:
            # Clean up test image
            try:
                docker_client.images.remove("culicidaelab-backend:test", force=True)
            except:
                pass

    def test_frontend_dockerfile_build(self, docker_client, project_root):
        """Test that frontend Dockerfile builds successfully."""

        # Build the frontend image with correct context
        try:
            image, build_logs = docker_client.images.build(
                path=str(project_root),
                dockerfile="frontend/Dockerfile",
                tag="culicidaelab-frontend:test",
                rm=True,
                forcerm=True,
            )

            # Verify image was created
            assert image is not None
            assert "culicidaelab-frontend:test" in [tag for tag in image.tags]

            # Check image labels and metadata
            config = image.attrs["Config"]
            assert config["ExposedPorts"]["8765/tcp"] == {}
            assert config["User"] == "appuser"

            # Verify health check is configured
            assert "Healthcheck" in config
            assert "curl -f http://localhost:8765/" in config["Healthcheck"]["Test"][1]

        except docker.errors.BuildError as e:
            pytest.fail(f"Frontend Dockerfile build failed: {e}")
        finally:
            # Clean up test image
            try:
                docker_client.images.remove("culicidaelab-frontend:test", force=True)
            except:
                pass

    def test_nginx_dockerfile_build(self, docker_client, project_root):
        """Test that nginx Dockerfile builds successfully."""

        # Build the nginx image with correct context
        try:
            image, build_logs = docker_client.images.build(
                path=str(project_root),
                dockerfile="nginx/Dockerfile",
                tag="culicidaelab-nginx:test",
                rm=True,
                forcerm=True,
            )

            # Verify image was created
            assert image is not None
            assert "culicidaelab-nginx:test" in [tag for tag in image.tags]

            # Check image labels and metadata
            config = image.attrs["Config"]
            assert config["ExposedPorts"]["80/tcp"] == {}
            assert config["ExposedPorts"]["443/tcp"] == {}
            assert config["User"] == "nginx"

            # Verify health check is configured
            assert "Healthcheck" in config
            assert "curl -f http://localhost/health" in config["Healthcheck"]["Test"][1]

        except docker.errors.BuildError as e:
            pytest.fail(f"Nginx Dockerfile build failed: {e}")
        finally:
            # Clean up test image
            try:
                docker_client.images.remove("culicidaelab-nginx:test", force=True)
            except:
                pass

    def test_dockerfile_security_practices(self, docker_client, project_root):
        """Test that Dockerfiles follow security best practices."""

        # Test backend Dockerfile security
        backend_dockerfile = project_root / "backend" / "Dockerfile"
        backend_content = backend_dockerfile.read_text()

        # Check for non-root user
        assert "USER appuser" in backend_content
        assert "useradd" in backend_content or "adduser" in backend_content

        # Check for minimal base image
        assert "python:3.11-slim" in backend_content

        # Check for security optimizations
        assert "PYTHONDONTWRITEBYTECODE=1" in backend_content
        assert "no-new-privileges" not in backend_content  # This is in compose file

        # Test frontend Dockerfile security
        frontend_dockerfile = project_root / "frontend" / "Dockerfile"
        frontend_content = frontend_dockerfile.read_text()

        # Check for non-root user
        assert "USER appuser" in frontend_content
        assert "useradd" in frontend_content or "adduser" in frontend_content

        # Test nginx Dockerfile security
        nginx_dockerfile = project_root / "nginx" / "Dockerfile"
        nginx_content = nginx_dockerfile.read_text()

        # Check for non-root user
        assert "USER nginx" in nginx_content

        # Check for minimal base image
        assert "nginx:alpine" in nginx_content

    def test_dockerfile_optimization(self, docker_client, project_root):
        """Test that Dockerfiles are optimized for size and caching."""

        # Test backend Dockerfile optimization
        backend_dockerfile = project_root / "backend" / "Dockerfile"
        backend_content = backend_dockerfile.read_text()

        # Check for multi-stage build
        assert "FROM python:3.11-slim as builder" in backend_content
        assert "FROM python:3.11-slim as production" in backend_content

        # Check for proper layer ordering (dependencies before code)
        lines = backend_content.split("\n")
        copy_pyproject_line = next((i for i, line in enumerate(lines) if "COPY pyproject.toml" in line), -1)
        copy_backend_line = next((i for i, line in enumerate(lines) if "COPY backend/" in line), -1)

        if copy_pyproject_line != -1 and copy_backend_line != -1:
            assert copy_pyproject_line < copy_backend_line, "Dependencies should be copied before application code"

        # Check for cleanup commands
        assert "rm -rf" in backend_content
        assert "apt-get clean" in backend_content

    def test_container_resource_limits(self, docker_client, project_root):
        """Test that containers can be started with resource limits."""

        try:
            # Build backend image for testing with correct context
            image, _ = docker_client.images.build(
                path=str(project_root),
                dockerfile="backend/Dockerfile",
                tag="culicidaelab-backend:resource-test",
                rm=True,
                forcerm=True,
            )

            # Test container with resource limits
            container = docker_client.containers.run(
                "culicidaelab-backend:resource-test",
                detach=True,
                mem_limit="512m",
                cpu_period=100000,
                cpu_quota=50000,  # 0.5 CPU
                environment={
                    "CULICIDAELAB_DATABASE_PATH": "/tmp/test.db",
                },
                remove=True,
            )

            # Wait a moment for container to start
            time.sleep(2)

            # Check container is running
            container.reload()
            assert container.status == "running"

            # Stop container
            container.stop(timeout=5)

        except Exception as e:
            pytest.fail(f"Container resource limit test failed: {e}")
        finally:
            # Clean up
            try:
                docker_client.images.remove("culicidaelab-backend:resource-test", force=True)
            except:
                pass
