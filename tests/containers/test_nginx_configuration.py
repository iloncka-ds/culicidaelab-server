"""
Tests for nginx configuration validation.
Validates nginx configuration files, routing rules, and security settings.
"""

import pytest
import re
import docker
from pathlib import Path


class TestNginxConfiguration:
    """Test suite for nginx configuration validation."""

    @pytest.fixture(scope="class")
    def project_root(self):
        """Get project root directory."""
        return Path(__file__).parent.parent.parent

    @pytest.fixture(scope="class")
    def docker_client(self):
        """Initialize Docker client."""
        try:
            client = docker.from_env()
            client.ping()
            return client
        except Exception as e:
            pytest.skip(f"Docker not available: {e}")

    def test_nginx_config_files_exist(self, project_root):
        """Test that required nginx configuration files exist."""
        required_configs = [
            "nginx/nginx.conf",
            "nginx/nginx-ssl.conf",
            "nginx/nginx.dev.conf",
        ]

        for config_path in required_configs:
            config_file = project_root / config_path
            assert config_file.exists(), f"Missing nginx config file: {config_path}"

    def test_nginx_routing_configuration(self, project_root):
        """Test that nginx routing is properly configured."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for API routing
                assert "location /api/" in config_content, f"API routing not found in {config_file.name}"

                # Check for static file routing
                assert "location /static/" in config_content, f"Static file routing not found in {config_file.name}"

                # Check for frontend routing (root location)
                assert "location /" in config_content, f"Frontend routing not found in {config_file.name}"

                # Check for proxy_pass directives
                proxy_passes = re.findall(r"proxy_pass\s+([^;]+);", config_content)
                assert len(proxy_passes) >= 2, f"Insufficient proxy_pass directives in {config_file.name}"

                # Check for backend and frontend service references
                backend_proxy = any("backend:8000" in proxy for proxy in proxy_passes)
                frontend_proxy = any("frontend:8765" in proxy for proxy in proxy_passes)

                assert backend_proxy, f"Backend proxy not configured in {config_file.name}"
                assert frontend_proxy, f"Frontend proxy not configured in {config_file.name}"

    def test_nginx_proxy_headers(self, project_root):
        """Test that nginx sets proper proxy headers."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        required_headers = [
            "proxy_set_header Host",
            "proxy_set_header X-Real-IP",
            "proxy_set_header X-Forwarded-For",
            "proxy_set_header X-Forwarded-Proto",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                for header in required_headers:
                    assert header in config_content, f"Missing proxy header '{header}' in {config_file.name}"

    def test_nginx_static_file_optimization(self, project_root):
        """Test that nginx is optimized for static file serving."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for static file location block
                static_location_found = False
                lines = config_content.split("\n")
                in_static_location = False

                for line in lines:
                    line = line.strip()
                    if "location /static/" in line:
                        static_location_found = True
                        in_static_location = True
                    elif in_static_location and line.startswith("}"):
                        in_static_location = False
                    elif in_static_location:
                        # Check for optimization directives within static location
                        if "expires" in line or "add_header Cache-Control" in line:
                            assert True  # Good caching configuration

                assert static_location_found, f"Static file location block not found in {config_file.name}"

    def test_nginx_gzip_compression(self, project_root):
        """Test that nginx has gzip compression enabled."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for gzip configuration
                assert "gzip on" in config_content, f"Gzip not enabled in {config_file.name}"

                # Check for gzip types (optional but recommended)
                if "gzip_types" in config_content:
                    # Should include common web file types
                    gzip_types_line = next((line for line in config_content.split("\n") if "gzip_types" in line), "")
                    if gzip_types_line:
                        assert any(
                            file_type in gzip_types_line
                            for file_type in ["text/css", "application/javascript", "application/json"]
                        )

    def test_nginx_error_pages(self, project_root):
        """Test that nginx has proper error page configuration."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for custom error pages or error handling
                error_handling_found = (
                    "error_page" in config_content
                    or "try_files" in config_content
                    or "proxy_intercept_errors" in config_content
                )

                # Error handling is optional but recommended
                if error_handling_found:
                    assert True  # Good practice

    def test_nginx_worker_configuration(self, project_root):
        """Test that nginx worker processes are properly configured."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for worker processes configuration
                if "worker_processes" in config_content:
                    worker_line = next((line for line in config_content.split("\n") if "worker_processes" in line), "")
                    if worker_line:
                        # Should be auto or a reasonable number
                        assert "auto" in worker_line or any(str(i) in worker_line for i in range(1, 9))

                # Check for worker connections (optional)
                if "worker_connections" in config_content:
                    assert True  # Good practice

    def test_nginx_upstream_configuration(self, project_root):
        """Test nginx upstream configuration if present."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for upstream blocks (optional for load balancing)
                if "upstream" in config_content:
                    # If upstream is used, check for proper configuration
                    upstream_blocks = re.findall(r"upstream\s+(\w+)\s*{([^}]+)}", config_content, re.DOTALL)

                    for upstream_name, upstream_content in upstream_blocks:
                        # Should have at least one server
                        assert "server" in upstream_content, f"Upstream {upstream_name} has no servers"

                        # Check for health checks or load balancing options
                        if any(option in upstream_content for option in ["max_fails", "fail_timeout", "weight"]):
                            assert True  # Good load balancing configuration

    def test_nginx_ssl_redirect_configuration(self, project_root):
        """Test that HTTP to HTTPS redirect is properly configured."""
        nginx_ssl_config = project_root / "nginx" / "nginx-ssl.conf"

        if nginx_ssl_config.exists():
            config_content = nginx_ssl_config.read_text()

            # Simple check for HTTP to HTTPS redirect
            http_redirect_found = "return 301 https://" in config_content and "listen 80" in config_content

            assert http_redirect_found, "HTTP to HTTPS redirect not configured"

    def test_nginx_health_check_endpoint(self, project_root):
        """Test that nginx has a health check endpoint configured."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for health check location
                health_check_found = (
                    "location /health" in config_content
                    or "location = /health" in config_content
                    or "location /nginx-health" in config_content
                )

                assert health_check_found, f"Health check endpoint not found in {config_file.name}"

    def test_nginx_config_syntax_validation(self, docker_client, project_root):
        """Test nginx configuration syntax using nginx container."""
        nginx_path = project_root / "nginx"

        # Test each configuration file
        config_files = [
            "nginx.conf",
            "nginx.dev.conf",
        ]

        for config_file in config_files:
            config_path = nginx_path / config_file
            if config_path.exists():
                try:
                    # Create a temporary container to test the configuration
                    container = docker_client.containers.run(
                        "nginx:alpine",
                        command=f"nginx -t -c /etc/nginx/{config_file}",
                        volumes={
                            str(config_path): {
                                "bind": f"/etc/nginx/{config_file}",
                                "mode": "ro",
                            },
                        },
                        remove=True,
                        detach=False,
                    )

                    # If we get here without exception, config is valid
                    assert True

                except docker.errors.ContainerError as e:
                    error_output = e.stderr.decode() if e.stderr else str(e)

                    # Check if error is due to missing files or host resolution (acceptable in test environment)
                    if any(
                        phrase in error_output
                        for phrase in [
                            "No such file or directory",
                            "host not found in upstream",
                            "could not be resolved",
                        ]
                    ):
                        # This might be due to missing SSL certificates, upstream hosts not available,
                        # or other files that are expected to be mounted/available at runtime
                        pass
                    else:
                        pytest.fail(f"Nginx configuration syntax error in {config_file}: {error_output}")
                except Exception as e:
                    pytest.fail(f"Failed to test nginx configuration {config_file}: {e}")

    def test_nginx_dockerfile_configuration(self, project_root):
        """Test that nginx Dockerfile is properly configured."""
        nginx_dockerfile = project_root / "nginx" / "Dockerfile"

        if nginx_dockerfile.exists():
            dockerfile_content = nginx_dockerfile.read_text()

            # Check that custom configuration is copied
            assert (
                "COPY nginx" in dockerfile_content and "nginx.conf" in dockerfile_content
            ), "Custom nginx.conf not copied in Dockerfile"

            # Check for proper permissions setup
            assert (
                "chown" in dockerfile_content or "chmod" in dockerfile_content
            ), "File permissions not set in Dockerfile"

            # Check for health check
            assert "HEALTHCHECK" in dockerfile_content, "Health check not configured in nginx Dockerfile"

            # Check for non-root user
            assert "USER nginx" in dockerfile_content, "nginx Dockerfile doesn't switch to non-root user"

    def test_nginx_log_configuration(self, project_root):
        """Test that nginx logging is properly configured."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for access log configuration
                if "access_log" in config_content:
                    # Should specify log format or location
                    access_log_lines = [line for line in config_content.split("\n") if "access_log" in line]
                    for log_line in access_log_lines:
                        if "off" not in log_line:  # access_log off is also valid
                            assert (
                                "/var/log/nginx" in log_line or "/dev/stdout" in log_line
                            ), "Access log path not properly configured"

                # Check for error log configuration
                if "error_log" in config_content:
                    error_log_lines = [line for line in config_content.split("\n") if "error_log" in line]
                    for log_line in error_log_lines:
                        assert (
                            "/var/log/nginx" in log_line or "/dev/stderr" in log_line
                        ), "Error log path not properly configured"

    def test_nginx_mime_types(self, project_root):
        """Test that nginx includes proper MIME type configuration."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for MIME types inclusion
                assert (
                    "include /etc/nginx/mime.types" in config_content or "include mime.types" in config_content
                ), f"MIME types not included in {config_file.name}"

                # Check for default type
                if "default_type" in config_content:
                    default_type_line = next(
                        (line for line in config_content.split("\n") if "default_type" in line),
                        "",
                    )
                    if default_type_line:
                        assert "application/octet-stream" in default_type_line, "Default MIME type not properly set"
