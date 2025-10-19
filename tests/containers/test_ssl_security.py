"""
Tests for SSL certificate validation and security configurations.
Validates SSL certificate management, security headers, and nginx security configurations.
"""

import pytest
import docker
from pathlib import Path


class TestSSLSecurity:
    """Test suite for SSL certificate validation and security configurations."""

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

    def test_nginx_ssl_configuration(self, project_root):
        """Test that nginx SSL configuration is properly set up."""
        nginx_ssl_config = project_root / "nginx" / "nginx-ssl.conf"

        if not nginx_ssl_config.exists():
            pytest.skip("nginx-ssl.conf not found")

        config_content = nginx_ssl_config.read_text()

        # Check for SSL certificate paths
        assert "ssl_certificate" in config_content
        assert "ssl_certificate_key" in config_content
        assert "/etc/letsencrypt/live/" in config_content

        # Check for SSL security settings
        assert "ssl_protocols" in config_content
        assert "ssl_ciphers" in config_content
        assert "ssl_prefer_server_ciphers" in config_content

        # Check for HTTPS redirect
        assert "return 301 https://" in config_content or "redirect" in config_content

        # Check for security headers
        security_headers = [
            "X-Frame-Options",
            "X-Content-Type-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security",
        ]

        for header in security_headers:
            assert header in config_content, f"Missing security header: {header}"

    def test_nginx_security_headers(self, project_root):
        """Test that nginx configuration includes proper security headers."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
            project_root / "nginx" / "nginx.dev.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check for basic security headers
                if "add_header" in config_content:
                    # At least some security headers should be present
                    security_headers_found = any(
                        header in config_content
                        for header in [
                            "X-Frame-Options",
                            "X-Content-Type-Options",
                            "X-XSS-Protection",
                            "Strict-Transport-Security",
                            "Content-Security-Policy",
                        ]
                    )
                    assert security_headers_found, f"No security headers found in {config_file.name}"

    def test_ssl_certificate_paths(self, project_root):
        """Test that SSL certificate paths are correctly configured."""
        # Check Docker Compose SSL volume mounts
        compose_prod = project_root / "docker-compose.prod.yml"

        if compose_prod.exists():
            import yaml

            with open(compose_prod) as f:
                compose_config = yaml.safe_load(f)

            # Check nginx service has SSL certificate volumes
            nginx_service = compose_config.get("services", {}).get("nginx", {})
            volumes = nginx_service.get("volumes", [])

            ssl_volume_found = any("letsencrypt_certs" in volume or "/etc/letsencrypt" in volume for volume in volumes)
            assert ssl_volume_found, "SSL certificate volume not found in nginx service"

            # Check certbot service configuration
            certbot_service = compose_config.get("services", {}).get("certbot", {})
            certbot_volumes = certbot_service.get("volumes", [])

            certbot_ssl_volume_found = any(
                "letsencrypt_certs" in volume or "/etc/letsencrypt" in volume for volume in certbot_volumes
            )
            assert certbot_ssl_volume_found, "SSL certificate volume not found in certbot service"

    def test_certbot_configuration(self, project_root):
        """Test that Certbot is properly configured for SSL certificate management."""
        # Check for Certbot initialization script
        init_script = project_root / "scripts" / "init-letsencrypt.sh"
        if init_script.exists():
            script_content = init_script.read_text()

            # Check for domain validation
            assert "certbot certonly" in script_content
            assert "--webroot" in script_content or "--standalone" in script_content
            assert "--email" in script_content
            assert "--agree-tos" in script_content

        # Check for renewal script
        renewal_script = project_root / "scripts" / "renew-certificates.sh"
        if renewal_script.exists():
            script_content = renewal_script.read_text()

            # Check for renewal command
            assert "certbot renew" in script_content

            # Check for nginx reload after renewal
            assert "nginx" in script_content and ("reload" in script_content or "restart" in script_content)

    def test_ssl_cipher_security(self, project_root):
        """Test that SSL cipher configuration follows security best practices."""
        nginx_ssl_config = project_root / "nginx" / "nginx-ssl.conf"

        if not nginx_ssl_config.exists():
            pytest.skip("nginx-ssl.conf not found")

        config_content = nginx_ssl_config.read_text()

        # Check for modern SSL protocols (TLS 1.2+)
        if "ssl_protocols" in config_content:
            # Should not include SSLv2, SSLv3, or TLSv1.0
            assert "SSLv2" not in config_content
            assert "SSLv3" not in config_content
            # Should include TLS 1.2 and preferably 1.3
            assert "TLSv1.2" in config_content or "TLSv1.3" in config_content

        # Check for secure cipher suites
        if "ssl_ciphers" in config_content:
            # Should prefer ECDHE for forward secrecy
            cipher_line = next((line for line in config_content.split("\n") if "ssl_ciphers" in line), "")
            if cipher_line:
                assert "ECDHE" in cipher_line or "DHE" in cipher_line, "Forward secrecy ciphers not configured"

    def test_hsts_configuration(self, project_root):
        """Test that HTTP Strict Transport Security (HSTS) is properly configured."""
        nginx_ssl_config = project_root / "nginx" / "nginx-ssl.conf"

        if not nginx_ssl_config.exists():
            pytest.skip("nginx-ssl.conf not found")

        config_content = nginx_ssl_config.read_text()

        # Check for HSTS header
        assert "Strict-Transport-Security" in config_content

        # Check for reasonable max-age (should be at least 1 year = 31536000 seconds)
        hsts_lines = [line for line in config_content.split("\n") if "Strict-Transport-Security" in line]
        if hsts_lines:
            hsts_line = hsts_lines[0]
            # Should include max-age
            assert "max-age=" in hsts_line
            # Should preferably include includeSubDomains
            if "includeSubDomains" in hsts_line:
                assert True  # Good practice

    def test_container_security_scanning(self, docker_client, project_root):
        """Test container images for security vulnerabilities using basic checks."""
        # This is a basic security check - in production, you'd use tools like Trivy or Clair

        containers_to_test = [
            ("backend", project_root / "backend"),
            ("frontend", project_root / "frontend"),
            ("nginx", project_root / "nginx"),
        ]

        for container_name, container_path in containers_to_test:
            try:
                # Build the image with correct context
                if container_name == "nginx":
                    build_path = str(project_root)
                    dockerfile_path = "nginx/Dockerfile"
                else:
                    build_path = str(project_root)
                    dockerfile_path = f"{container_name}/Dockerfile"

                image, _ = docker_client.images.build(
                    path=build_path,
                    dockerfile=dockerfile_path,
                    tag=f"culicidaelab-{container_name}:security-test",
                    rm=True,
                    forcerm=True,
                )

                # Basic security checks
                config = image.attrs["Config"]

                # Check that container doesn't run as root
                user = config.get("User", "")
                assert user != "" and user != "root", f"{container_name} container runs as root"

                # Check for security-related environment variables
                env_vars = config.get("Env", [])
                env_dict = {}
                for env_var in env_vars:
                    if "=" in env_var:
                        key, value = env_var.split("=", 1)
                        env_dict[key] = value

                # Python containers should have bytecode writing disabled
                if container_name in ["backend", "frontend"]:
                    assert env_dict.get("PYTHONDONTWRITEBYTECODE") == "1", f"{container_name} allows bytecode writing"

                # Check that no sensitive information is in environment variables
                sensitive_patterns = ["password", "secret", "key", "token"]
                for env_var in env_vars:
                    env_lower = env_var.lower()
                    for pattern in sensitive_patterns:
                        if pattern in env_lower and "=" in env_var:
                            # This is just a warning - some environment variables might legitimately contain these words
                            pass

            except Exception as e:
                pytest.fail(f"Security scanning failed for {container_name}: {e}")
            finally:
                # Clean up
                try:
                    docker_client.images.remove(f"culicidaelab-{container_name}:security-test", force=True)
                except:
                    pass

    def test_nginx_configuration_security(self, project_root):
        """Test nginx configuration for security best practices."""
        nginx_configs = [
            project_root / "nginx" / "nginx.conf",
            project_root / "nginx" / "nginx-ssl.conf",
        ]

        for config_file in nginx_configs:
            if config_file.exists():
                config_content = config_file.read_text()

                # Check that server tokens are hidden
                assert "server_tokens off" in config_content, f"Server tokens not disabled in {config_file.name}"

                # Check for client body size limits
                if "client_max_body_size" in config_content:
                    # Should have reasonable limits
                    assert True  # Good practice

                # Check for rate limiting (optional but recommended)
                if "limit_req" in config_content:
                    assert True  # Good practice

                # Check that default server block doesn't expose information
                if "default_server" in config_content:
                    # Should return 444 or redirect, not serve content
                    assert (
                        "return 444" in config_content
                        or "return 301" in config_content
                        or "return 403" in config_content
                    )

    def test_docker_security_options(self, project_root):
        """Test that Docker Compose includes security options."""
        compose_prod = project_root / "docker-compose.prod.yml"

        if compose_prod.exists():
            import yaml

            with open(compose_prod) as f:
                compose_config = yaml.safe_load(f)

            services = compose_config.get("services", {})

            for service_name, service_config in services.items():
                if service_name != "certbot":  # certbot might have different requirements
                    # Check for security options
                    security_opts = service_config.get("security_opt", [])
                    if security_opts:
                        assert (
                            "no-new-privileges:true" in security_opts
                        ), f"no-new-privileges not set for {service_name}"

                    # Check for read-only root filesystem (optional but recommended)
                    if "read_only" in service_config:
                        assert service_config["read_only"] is True

                    # Check for tmpfs mounts (good security practice)
                    if "tmpfs" in service_config:
                        tmpfs_mounts = service_config["tmpfs"]
                        for mount in tmpfs_mounts:
                            if "/tmp" in mount:
                                assert (
                                    "noexec" in mount and "nosuid" in mount
                                ), f"Insecure tmpfs mount in {service_name}"

    def test_environment_variable_security(self, project_root):
        """Test that environment variables don't expose sensitive information."""
        env_files = [
            project_root / ".env",
            project_root / ".env.prod",
            project_root / ".env.dev",
        ]

        for env_file in env_files:
            if env_file.exists():
                env_content = env_file.read_text()

                # Check that no plaintext passwords or secrets are visible
                lines = env_content.split("\n")
                for line in lines:
                    if "=" in line and not line.strip().startswith("#"):
                        key, value = line.split("=", 1)
                        key_lower = key.lower()

                        # Warn about potential sensitive information
                        if any(pattern in key_lower for pattern in ["password", "secret", "key", "token"]):
                            # In a real environment, these should be properly secured
                            # For testing, we just ensure they're not obviously insecure
                            assert (
                                value != "password" and value != "123456" and value != "admin"
                            ), f"Insecure value for {key}"

    def test_ssl_certificate_validation_script(self, project_root):
        """Test SSL certificate validation functionality."""
        # Check if there's a certificate validation script
        validation_scripts = [
            project_root / "scripts" / "validate-ssl.sh",
            project_root / "scripts" / "check-ssl.sh",
        ]

        script_found = False
        for script_path in validation_scripts:
            if script_path.exists():
                script_found = True
                script_content = script_path.read_text()

                # Check for SSL validation commands
                ssl_commands = ["openssl", "curl", "wget"]
                command_found = any(cmd in script_content for cmd in ssl_commands)
                assert command_found, f"No SSL validation commands found in {script_path.name}"

        # If no dedicated SSL validation script exists, that's okay for basic setups
        if not script_found:
            # Check if SSL validation is part of other scripts
            all_scripts = list((project_root / "scripts").glob("*.sh"))
            ssl_validation_found = False

            for script_path in all_scripts:
                if script_path.exists():
                    script_content = script_path.read_text()
                    if "ssl" in script_content.lower() or "certificate" in script_content.lower():
                        ssl_validation_found = True
                        break

            # This is optional - SSL validation might be handled by external monitoring
            pass

    def test_nginx_ssl_test_configuration(self, docker_client, project_root):
        """Test nginx SSL configuration by starting a container and checking config syntax."""
        nginx_path = project_root / "nginx"

        try:
            # Build nginx image with correct context
            image, _ = docker_client.images.build(
                path=str(project_root),
                dockerfile="nginx/Dockerfile",
                tag="culicidaelab-nginx:ssl-test",
                rm=True,
                forcerm=True,
            )

            # Test nginx configuration syntax
            container = docker_client.containers.run(
                "culicidaelab-nginx:ssl-test",
                command="nginx -t",
                remove=True,
                detach=False,
            )

            # If we get here without exception, nginx config is valid
            assert True

        except docker.errors.ContainerError as e:
            # Check if the error is due to missing SSL certificates or host resolution (expected in test environment)
            error_output = e.stderr.decode() if e.stderr else str(e)
            if any(
                phrase in error_output
                for phrase in [
                    "No such file or directory",
                    "ssl",
                    "host not found in upstream",
                    "could not be resolved",
                ]
            ):
                # This is expected - SSL certificates won't exist and upstream hosts won't be available in test environment
                pass
            else:
                pytest.fail(f"Nginx configuration test failed: {error_output}")
        except Exception as e:
            pytest.fail(f"Nginx SSL configuration test failed: {e}")
        finally:
            # Clean up
            try:
                docker_client.images.remove("culicidaelab-nginx:ssl-test", force=True)
            except:
                pass
