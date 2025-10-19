#!/usr/bin/env python3
"""Log aggregation script for CulicidaeLab Docker deployment.

This script aggregates and formats logs from all Docker containers
for easier monitoring and debugging.
"""

import json
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import argparse
import re


class LogAggregator:
    """Log aggregation and formatting class."""
    
    def __init__(self, compose_file: str = "docker-compose.dev.yml"):
        """Initialize log aggregator.
        
        Args:
            compose_file: Docker Compose file to use.
        """
        self.compose_file = compose_file
        self.services = self._get_services()
        
    def _get_services(self) -> List[str]:
        """Get list of services from Docker Compose file.
        
        Returns:
            List of service names.
        """
        try:
            result = subprocess.run(
                ["docker-compose", "-f", self.compose_file, "config", "--services"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip().split('\n')
        except subprocess.CalledProcessError as e:
            print(f"Error getting services: {e}")
            return []
    
    def _parse_log_line(self, line: str, service: str) -> Optional[Dict]:
        """Parse a log line and extract structured information.
        
        Args:
            line: Raw log line.
            service: Service name.
            
        Returns:
            Parsed log entry or None if parsing fails.
        """
        if not line.strip():
            return None
            
        # Try to parse as JSON first
        try:
            # Remove Docker Compose prefix if present
            if '|' in line:
                _, log_content = line.split('|', 1)
                log_content = log_content.strip()
            else:
                log_content = line.strip()
            
            # Try to parse as JSON
            if log_content.startswith('{') and log_content.endswith('}'):
                data = json.loads(log_content)
                data['source_service'] = service
                return data
        except json.JSONDecodeError:
            pass
        
        # Parse as plain text with timestamp extraction
        timestamp_match = re.match(r'^(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})', line)
        
        return {
            "timestamp": timestamp_match.group(1) if timestamp_match else datetime.utcnow().isoformat(),
            "level": "INFO",
            "service": service,
            "source_service": service,
            "message": line.strip(),
            "raw": True
        }
    
    def _format_log_entry(self, entry: Dict) -> str:
        """Format a log entry for display.
        
        Args:
            entry: Parsed log entry.
            
        Returns:
            Formatted log string.
        """
        timestamp = entry.get('timestamp', datetime.utcnow().isoformat())
        level = entry.get('level', 'INFO')
        service = entry.get('source_service', entry.get('service', 'unknown'))
        message = entry.get('message', '')
        
        # Color coding for different log levels
        colors = {
            'DEBUG': '\033[36m',    # Cyan
            'INFO': '\033[32m',     # Green
            'WARNING': '\033[33m',  # Yellow
            'ERROR': '\033[31m',    # Red
            'CRITICAL': '\033[35m', # Magenta
        }
        reset_color = '\033[0m'
        
        color = colors.get(level.upper(), '')
        
        # Format timestamp
        try:
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            formatted_time = dt.strftime('%H:%M:%S')
        except:
            formatted_time = timestamp[:8] if len(timestamp) >= 8 else timestamp
        
        # Format service name with fixed width
        service_name = f"{service:<12}"
        
        # Format level with fixed width
        level_name = f"{level:<8}"
        
        formatted = f"{formatted_time} {color}{level_name}{reset_color} {service_name} {message}"
        
        # Add extra fields if present and not raw
        if not entry.get('raw', False):
            extra_fields = []
            for key, value in entry.items():
                if key not in ['timestamp', 'level', 'service', 'source_service', 'message', 'raw']:
                    if isinstance(value, (dict, list)):
                        extra_fields.append(f"{key}={json.dumps(value, separators=(',', ':'))}")
                    else:
                        extra_fields.append(f"{key}={value}")
            
            if extra_fields:
                formatted += f" | {' '.join(extra_fields)}"
        
        return formatted
    
    def follow_logs(self, services: Optional[List[str]] = None, since: str = "1m"):
        """Follow logs from Docker containers.
        
        Args:
            services: List of services to follow (None for all).
            since: Time period to show logs from.
        """
        if services is None:
            services = self.services
        
        # Build docker-compose logs command
        cmd = [
            "docker-compose", "-f", self.compose_file,
            "logs", "-f", "--tail=50", f"--since={since}"
        ] + services
        
        print(f"Following logs for services: {', '.join(services)}")
        print("=" * 80)
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            for line in process.stdout:
                # Extract service name from Docker Compose log format
                service_match = re.match(r'^([^|]+)\s*\|', line)
                service = service_match.group(1).strip() if service_match else 'unknown'
                
                # Parse and format the log entry
                entry = self._parse_log_line(line, service)
                if entry:
                    formatted = self._format_log_entry(entry)
                    print(formatted)
                    sys.stdout.flush()
                    
        except KeyboardInterrupt:
            print("\nLog following stopped by user")
            process.terminate()
        except Exception as e:
            print(f"Error following logs: {e}")
    
    def get_service_logs(self, service: str, lines: int = 100) -> List[Dict]:
        """Get recent logs for a specific service.
        
        Args:
            service: Service name.
            lines: Number of recent lines to retrieve.
            
        Returns:
            List of parsed log entries.
        """
        cmd = [
            "docker-compose", "-f", self.compose_file,
            "logs", "--tail", str(lines), service
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            entries = []
            for line in result.stdout.split('\n'):
                entry = self._parse_log_line(line, service)
                if entry:
                    entries.append(entry)
            
            return entries
            
        except subprocess.CalledProcessError as e:
            print(f"Error getting logs for {service}: {e}")
            return []


def main():
    """Main function for the log aggregator."""
    parser = argparse.ArgumentParser(description="Log aggregator for CulicidaeLab Docker deployment")
    parser.add_argument("-f", "--compose-file", default="docker-compose.dev.yml",
                       help="Docker Compose file to use (default: docker-compose.dev.yml)")
    parser.add_argument("-s", "--services", nargs="+",
                       help="Services to follow (default: all services)")
    parser.add_argument("--since", default="1m",
                       help="Show logs since this time (default: 1m)")
    parser.add_argument("--lines", type=int, default=100,
                       help="Number of lines to show initially (default: 100)")
    parser.add_argument("--service", 
                       help="Show logs for a specific service only (non-following mode)")
    
    args = parser.parse_args()
    
    aggregator = LogAggregator(compose_file=args.compose_file)
    
    if args.service:
        # Show logs for specific service
        entries = aggregator.get_service_logs(args.service, args.lines)
        for entry in entries:
            formatted = aggregator._format_log_entry(entry)
            print(formatted)
    else:
        # Follow logs
        aggregator.follow_logs(services=args.services, since=args.since)


if __name__ == "__main__":
    main()