#!/usr/bin/env python3
"""
Container Security Validation Script
Validates Docker containers against security best practices
"""

import json
import subprocess
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Any
import argparse


class SecurityValidator:
    """Validates container security configurations"""
    
    def __init__(self, config_path: str = None):
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "docker/security/security-policy.yaml"
        self.load_security_policy()
        
    def load_security_policy(self):
        """Load security policy configuration"""
        try:
            with open(self.config_path, 'r') as f:
                self.policy = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"Warning: Security policy file not found at {self.config_path}")
            self.policy = {}
    
    def validate_dockerfile(self, dockerfile_path: Path) -> Dict[str, Any]:
        """Validate Dockerfile against security best practices"""
        results = {
            'file': str(dockerfile_path),
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
        if not dockerfile_path.exists():
            results['failed'].append(f"Dockerfile not found: {dockerfile_path}")
            return results
        
        content = dockerfile_path.read_text()
        lines = content.split('\n')
        
        # Check for root user
        has_user_directive = any('USER ' in line and 'USER root' not in line for line in lines)
        if has_user_directive:
            results['passed'].append("Non-root user specified")
        else:
            results['failed'].append("No non-root USER directive found")
        
        # Check for specific version tags
        from_lines = [line for line in lines if line.strip().startswith('FROM ')]
        for line in from_lines:
            if ':latest' in line or not ':' in line.split()[-1]:
                results['failed'].append(f"Using latest or no tag: {line.strip()}")
            else:
                results['passed'].append(f"Specific version tag used: {line.strip()}")
        
        # Check for package updates
        update_commands = ['apt-get update', 'apk update', 'yum update']
        has_update = any(any(cmd in line for cmd in update_commands) for line in lines)
        if has_update:
            results['passed'].append("Package updates included")
        else:
            results['warnings'].append("No package updates found")
        
        # Check for cleanup commands
        cleanup_commands = ['rm -rf /var/lib/apt/lists/*', 'rm -rf /tmp/*', 'apk del']
        has_cleanup = any(any(cmd in line for cmd in cleanup_commands) for line in lines)
        if has_cleanup:
            results['passed'].append("Cleanup commands found")
        else:
            results['failed'].append("No cleanup commands found")
        
        # Check for health checks
        has_healthcheck = any('HEALTHCHECK' in line for line in lines)
        if has_healthcheck:
            results['passed'].append("Health check configured")
        else:
            results['warnings'].append("No health check found")
        
        # Check for exposed ports
        expose_lines = [line for line in lines if line.strip().startswith('EXPOSE ')]
        for line in expose_lines:
            try:
                port = int(line.split()[1])
                if port < 1024:
                    results['failed'].append(f"Privileged port exposed: {port}")
                else:
                    results['passed'].append(f"Non-privileged port exposed: {port}")
            except (IndexError, ValueError):
                results['warnings'].append(f"Invalid EXPOSE directive: {line.strip()}")
        
        return results
    
    def validate_compose_security(self, compose_path: Path) -> Dict[str, Any]:
        """Validate Docker Compose security configuration"""
        results = {
            'file': str(compose_path),
            'passed': [],
            'failed': [],
            'warnings': []
        }
        
        if not compose_path.exists():
            results['failed'].append(f"Compose file not found: {compose_path}")
            return results
        
        try:
            with open(compose_path, 'r') as f:
                compose_config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            results['failed'].append(f"Invalid YAML: {e}")
            return results
        
        services = compose_config.get('services', {})
        
        for service_name, service_config in services.items():
            # Check for privileged mode
            if service_config.get('privileged', False):
                results['failed'].append(f"Service {service_name} runs in privileged mode")
            else:
                results['passed'].append(f"Service {service_name} not privileged")
            
            # Check for user specification
            if 'user' in service_config:
                user = service_config['user']
                if user == 'root' or user == '0':
                    results['failed'].append(f"Service {service_name} runs as root")
                else:
                    results['passed'].append(f"Service {service_name} runs as non-root user")
            else:
                results['warnings'].append(f"Service {service_name} has no user specified")
            
            # Check for resource limits
            if 'deploy' in service_config and 'resources' in service_config['deploy']:
                results['passed'].append(f"Service {service_name} has resource limits")
            else:
                results['warnings'].append(f"Service {service_name} has no resource limits")
            
            # Check for read-only root filesystem
            if service_config.get('read_only', False):
                results['passed'].append(f"Service {service_name} has read-only root filesystem")
            else:
                results['warnings'].append(f"Service {service_name} root filesystem is writable")
            
            # Check for security options
            security_opts = service_config.get('security_opt', [])
            if 'no-new-privileges:true' in security_opts:
                results['passed'].append(f"Service {service_name} has no-new-privileges")
            else:
                results['warnings'].append(f"Service {service_name} missing no-new-privileges")
        
        return results
    
    def check_image_vulnerabilities(self, image_name: str) -> Dict[str, Any]:
        """Check image for known vulnerabilities using trivy"""
        results = {
            'image': image_name,
            'vulnerabilities': [],
            'summary': {}
        }
        
        try:
            # Run trivy scan
            cmd = ['trivy', 'image', '--format', 'json', '--quiet', image_name]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                scan_data = json.loads(result.stdout)
                
                # Process vulnerability data
                for target in scan_data.get('Results', []):
                    vulnerabilities = target.get('Vulnerabilities', [])
                    for vuln in vulnerabilities:
                        results['vulnerabilities'].append({
                            'id': vuln.get('VulnerabilityID'),
                            'severity': vuln.get('Severity'),
                            'package': vuln.get('PkgName'),
                            'version': vuln.get('InstalledVersion'),
                            'fixed_version': vuln.get('FixedVersion'),
                            'title': vuln.get('Title', '')
                        })
                
                # Create summary
                severities = [v['severity'] for v in results['vulnerabilities']]
                results['summary'] = {
                    'total': len(results['vulnerabilities']),
                    'critical': severities.count('CRITICAL'),
                    'high': severities.count('HIGH'),
                    'medium': severities.count('MEDIUM'),
                    'low': severities.count('LOW')
                }
            else:
                results['error'] = f"Trivy scan failed: {result.stderr}"
                
        except subprocess.TimeoutExpired:
            results['error'] = "Trivy scan timed out"
        except FileNotFoundError:
            results['error'] = "Trivy not found - please install trivy"
        except json.JSONDecodeError:
            results['error'] = "Invalid JSON output from trivy"
        
        return results
    
    def generate_report(self, validation_results: List[Dict[str, Any]]) -> str:
        """Generate security validation report"""
        report_lines = [
            "Container Security Validation Report",
            "=" * 40,
            f"Generated: {Path(__file__).name}",
            ""
        ]
        
        total_passed = 0
        total_failed = 0
        total_warnings = 0
        
        for result in validation_results:
            report_lines.append(f"File: {result['file']}")
            report_lines.append("-" * len(f"File: {result['file']}"))
            
            if result['passed']:
                report_lines.append("✓ PASSED:")
                for item in result['passed']:
                    report_lines.append(f"  - {item}")
                total_passed += len(result['passed'])
            
            if result['failed']:
                report_lines.append("✗ FAILED:")
                for item in result['failed']:
                    report_lines.append(f"  - {item}")
                total_failed += len(result['failed'])
            
            if result['warnings']:
                report_lines.append("⚠ WARNINGS:")
                for item in result['warnings']:
                    report_lines.append(f"  - {item}")
                total_warnings += len(result['warnings'])
            
            report_lines.append("")
        
        # Summary
        report_lines.extend([
            "Summary",
            "=" * 20,
            f"Total Passed: {total_passed}",
            f"Total Failed: {total_failed}",
            f"Total Warnings: {total_warnings}",
            "",
            "Recommendations:",
            "- Address all failed security checks",
            "- Review and resolve warnings where applicable",
            "- Implement regular security scanning in CI/CD",
            "- Keep base images updated with security patches"
        ])
        
        return "\n".join(report_lines)


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Validate container security')
    parser.add_argument('--config', help='Security policy configuration file')
    parser.add_argument('--output', help='Output report file')
    parser.add_argument('--dockerfile', action='append', help='Dockerfile to validate')
    parser.add_argument('--compose', action='append', help='Compose file to validate')
    
    args = parser.parse_args()
    
    validator = SecurityValidator(args.config)
    results = []
    
    # Validate Dockerfiles
    dockerfiles = args.dockerfile or [
        'backend/Dockerfile',
        'frontend/Dockerfile',
        'nginx/Dockerfile'
    ]
    
    for dockerfile in dockerfiles:
        dockerfile_path = Path(dockerfile)
        if not dockerfile_path.is_absolute():
            dockerfile_path = validator.project_root / dockerfile_path
        
        result = validator.validate_dockerfile(dockerfile_path)
        results.append(result)
    
    # Validate Compose files
    compose_files = args.compose or [
        'docker-compose.prod.yml',
        'docker-compose.dev.yml'
    ]
    
    for compose_file in compose_files:
        compose_path = Path(compose_file)
        if not compose_path.is_absolute():
            compose_path = validator.project_root / compose_path
        
        result = validator.validate_compose_security(compose_path)
        results.append(result)
    
    # Generate report
    report = validator.generate_report(results)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Security validation report written to: {args.output}")
    else:
        print(report)
    
    # Exit with error code if any failures
    total_failures = sum(len(r.get('failed', [])) for r in results)
    sys.exit(1 if total_failures > 0 else 0)


if __name__ == '__main__':
    main()