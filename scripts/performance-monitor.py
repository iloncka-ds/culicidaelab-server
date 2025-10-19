#!/usr/bin/env python3
"""
Performance Monitoring Script for CulicidaeLab
Monitors container performance metrics and generates reports
"""

import json
import time
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any
import argparse
import requests


class PerformanceMonitor:
    """Monitors container performance and resource usage"""
    
    def __init__(self, prometheus_url: str = "http://localhost:9090"):
        self.prometheus_url = prometheus_url
        self.project_root = Path(__file__).parent.parent
        self.reports_dir = self.project_root / "performance-reports"
        self.reports_dir.mkdir(exist_ok=True)
        
    def query_prometheus(self, query: str, time_range: str = "5m") -> Dict[str, Any]:
        """Query Prometheus for metrics"""
        try:
            url = f"{self.prometheus_url}/api/v1/query"
            params = {
                'query': query,
                'time': datetime.now().isoformat()
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            return response.json()
        except requests.RequestException as e:
            print(f"Error querying Prometheus: {e}")
            return {'status': 'error', 'data': {'result': []}}
    
    def get_container_metrics(self) -> Dict[str, Any]:
        """Get container performance metrics"""
        metrics = {}
        
        # CPU usage by container
        cpu_query = 'rate(container_cpu_usage_seconds_total[5m]) * 100'
        cpu_data = self.query_prometheus(cpu_query)
        metrics['cpu_usage'] = self.parse_metric_data(cpu_data)
        
        # Memory usage by container
        memory_query = '(container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100'
        memory_data = self.query_prometheus(memory_query)
        metrics['memory_usage'] = self.parse_metric_data(memory_data)
        
        # Network I/O by container
        network_query = 'rate(container_network_receive_bytes_total[5m]) + rate(container_network_transmit_bytes_total[5m])'
        network_data = self.query_prometheus(network_query)
        metrics['network_io'] = self.parse_metric_data(network_data)
        
        # Disk I/O by container
        disk_query = 'rate(container_fs_reads_bytes_total[5m]) + rate(container_fs_writes_bytes_total[5m])'
        disk_data = self.query_prometheus(disk_query)
        metrics['disk_io'] = self.parse_metric_data(disk_data)
        
        return metrics
    
    def get_application_metrics(self) -> Dict[str, Any]:
        """Get application-specific performance metrics"""
        metrics = {}
        
        # HTTP request rate
        request_rate_query = 'sum(rate(http_requests_total[5m])) by (job)'
        request_data = self.query_prometheus(request_rate_query)
        metrics['request_rate'] = self.parse_metric_data(request_data)
        
        # HTTP error rate
        error_rate_query = 'sum(rate(http_requests_total{status=~"5.."}[5m])) by (job) / sum(rate(http_requests_total[5m])) by (job)'
        error_data = self.query_prometheus(error_rate_query)
        metrics['error_rate'] = self.parse_metric_data(error_data)
        
        # Response time percentiles
        p95_query = 'histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (job, le))'
        p95_data = self.query_prometheus(p95_query)
        metrics['response_time_p95'] = self.parse_metric_data(p95_data)
        
        return metrics
    
    def parse_metric_data(self, prometheus_response: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse Prometheus response data"""
        if prometheus_response.get('status') != 'success':
            return []
        
        results = []
        for result in prometheus_response.get('data', {}).get('result', []):
            metric_info = {
                'labels': result.get('metric', {}),
                'value': float(result.get('value', [0, '0'])[1]) if result.get('value') else 0,
                'timestamp': result.get('value', [0, '0'])[0] if result.get('value') else 0
            }
            results.append(metric_info)
        
        return results
    
    def get_docker_stats(self) -> Dict[str, Any]:
        """Get Docker container statistics"""
        try:
            # Get container stats using docker stats
            cmd = ['docker', 'stats', '--no-stream', '--format', 'table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                return {'error': f"Docker stats failed: {result.stderr}"}
            
            # Parse docker stats output
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            stats = []
            
            for line in lines:
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 5:
                        stats.append({
                            'container': parts[0],
                            'cpu_percent': parts[1],
                            'memory_usage': parts[2],
                            'network_io': parts[3],
                            'block_io': parts[4]
                        })
            
            return {'stats': stats}
            
        except subprocess.TimeoutExpired:
            return {'error': 'Docker stats command timed out'}
        except FileNotFoundError:
            return {'error': 'Docker command not found'}
    
    def analyze_performance(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance metrics and identify issues"""
        analysis = {
            'timestamp': datetime.now().isoformat(),
            'issues': [],
            'recommendations': [],
            'summary': {}
        }
        
        # Analyze CPU usage
        cpu_metrics = metrics.get('cpu_usage', [])
        high_cpu_containers = [m for m in cpu_metrics if m['value'] > 80]
        if high_cpu_containers:
            analysis['issues'].append({
                'type': 'high_cpu_usage',
                'severity': 'warning',
                'containers': [c['labels'].get('name', 'unknown') for c in high_cpu_containers],
                'description': 'High CPU usage detected'
            })
            analysis['recommendations'].append('Consider scaling up CPU resources or optimizing application code')
        
        # Analyze memory usage
        memory_metrics = metrics.get('memory_usage', [])
        high_memory_containers = [m for m in memory_metrics if m['value'] > 85]
        if high_memory_containers:
            analysis['issues'].append({
                'type': 'high_memory_usage',
                'severity': 'warning',
                'containers': [c['labels'].get('name', 'unknown') for c in high_memory_containers],
                'description': 'High memory usage detected'
            })
            analysis['recommendations'].append('Consider increasing memory limits or optimizing memory usage')
        
        # Analyze application metrics
        app_metrics = metrics.get('application', {})
        error_rates = app_metrics.get('error_rate', [])
        high_error_services = [m for m in error_rates if m['value'] > 0.05]  # 5% error rate
        if high_error_services:
            analysis['issues'].append({
                'type': 'high_error_rate',
                'severity': 'critical',
                'services': [s['labels'].get('job', 'unknown') for s in high_error_services],
                'description': 'High error rate detected'
            })
            analysis['recommendations'].append('Investigate application errors and fix underlying issues')
        
        # Generate summary
        analysis['summary'] = {
            'total_issues': len(analysis['issues']),
            'critical_issues': len([i for i in analysis['issues'] if i['severity'] == 'critical']),
            'warning_issues': len([i for i in analysis['issues'] if i['severity'] == 'warning']),
            'containers_monitored': len(set(
                [c['labels'].get('name', 'unknown') for c in cpu_metrics] +
                [c['labels'].get('name', 'unknown') for c in memory_metrics]
            ))
        }
        
        return analysis
    
    def generate_report(self, metrics: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate performance monitoring report"""
        report_lines = [
            "CulicidaeLab Performance Monitoring Report",
            "=" * 45,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            ""
        ]
        
        # Summary section
        summary = analysis.get('summary', {})
        report_lines.extend([
            "Summary",
            "-" * 20,
            f"Containers Monitored: {summary.get('containers_monitored', 0)}",
            f"Total Issues: {summary.get('total_issues', 0)}",
            f"Critical Issues: {summary.get('critical_issues', 0)}",
            f"Warning Issues: {summary.get('warning_issues', 0)}",
            ""
        ])
        
        # Issues section
        issues = analysis.get('issues', [])
        if issues:
            report_lines.append("Issues Detected")
            report_lines.append("-" * 20)
            for issue in issues:
                severity_symbol = "🔴" if issue['severity'] == 'critical' else "🟡"
                report_lines.append(f"{severity_symbol} {issue['type'].upper()}: {issue['description']}")
                if 'containers' in issue:
                    report_lines.append(f"   Affected containers: {', '.join(issue['containers'])}")
                if 'services' in issue:
                    report_lines.append(f"   Affected services: {', '.join(issue['services'])}")
            report_lines.append("")
        
        # Recommendations section
        recommendations = analysis.get('recommendations', [])
        if recommendations:
            report_lines.append("Recommendations")
            report_lines.append("-" * 20)
            for i, rec in enumerate(recommendations, 1):
                report_lines.append(f"{i}. {rec}")
            report_lines.append("")
        
        # Metrics section
        report_lines.extend([
            "Current Metrics",
            "-" * 20,
        ])
        
        # CPU metrics
        cpu_metrics = metrics.get('cpu_usage', [])
        if cpu_metrics:
            report_lines.append("CPU Usage:")
            for metric in cpu_metrics[:5]:  # Show top 5
                container = metric['labels'].get('name', 'unknown')
                value = metric['value']
                report_lines.append(f"  {container}: {value:.2f}%")
        
        # Memory metrics
        memory_metrics = metrics.get('memory_usage', [])
        if memory_metrics:
            report_lines.append("\nMemory Usage:")
            for metric in memory_metrics[:5]:  # Show top 5
                container = metric['labels'].get('name', 'unknown')
                value = metric['value']
                report_lines.append(f"  {container}: {value:.2f}%")
        
        return "\n".join(report_lines)
    
    def save_report(self, report: str, filename: str = None) -> Path:
        """Save performance report to file"""
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"performance_report_{timestamp}.txt"
        
        report_path = self.reports_dir / filename
        report_path.write_text(report)
        return report_path
    
    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run a complete monitoring cycle"""
        print("Starting performance monitoring cycle...")
        
        # Collect metrics
        print("Collecting container metrics...")
        container_metrics = self.get_container_metrics()
        
        print("Collecting application metrics...")
        app_metrics = self.get_application_metrics()
        
        print("Collecting Docker stats...")
        docker_stats = self.get_docker_stats()
        
        # Combine all metrics
        all_metrics = {
            **container_metrics,
            'application': app_metrics,
            'docker_stats': docker_stats
        }
        
        # Analyze performance
        print("Analyzing performance...")
        analysis = self.analyze_performance(all_metrics)
        
        # Generate report
        print("Generating report...")
        report = self.generate_report(all_metrics, analysis)
        
        return {
            'metrics': all_metrics,
            'analysis': analysis,
            'report': report
        }


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Monitor CulicidaeLab performance')
    parser.add_argument('--prometheus-url', default='http://localhost:9090',
                       help='Prometheus server URL')
    parser.add_argument('--output', help='Output report file')
    parser.add_argument('--continuous', action='store_true',
                       help='Run continuous monitoring')
    parser.add_argument('--interval', type=int, default=300,
                       help='Monitoring interval in seconds (for continuous mode)')
    
    args = parser.parse_args()
    
    monitor = PerformanceMonitor(args.prometheus_url)
    
    if args.continuous:
        print(f"Starting continuous monitoring (interval: {args.interval}s)")
        try:
            while True:
                result = monitor.run_monitoring_cycle()
                
                # Save report
                report_path = monitor.save_report(result['report'], args.output)
                print(f"Report saved to: {report_path}")
                
                # Print summary
                summary = result['analysis'].get('summary', {})
                print(f"Issues found: {summary.get('total_issues', 0)} "
                      f"(Critical: {summary.get('critical_issues', 0)}, "
                      f"Warning: {summary.get('warning_issues', 0)})")
                
                print(f"Sleeping for {args.interval} seconds...")
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    else:
        # Single monitoring cycle
        result = monitor.run_monitoring_cycle()
        
        if args.output:
            report_path = monitor.save_report(result['report'], args.output)
            print(f"Performance report saved to: {report_path}")
        else:
            print(result['report'])
        
        # Exit with error code if critical issues found
        critical_issues = result['analysis'].get('summary', {}).get('critical_issues', 0)
        sys.exit(1 if critical_issues > 0 else 0)


if __name__ == '__main__':
    main()