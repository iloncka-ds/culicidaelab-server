#!/usr/bin/env python3
"""Health monitoring script for CulicidaeLab services.

This script checks the health of all services and provides monitoring
capabilities for the Docker deployment.
"""

import asyncio
import json
import logging
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
import argparse


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HealthMonitor:
    """Health monitoring class for checking service status."""
    
    def __init__(self, base_url: str = "http://localhost"):
        """Initialize health monitor.
        
        Args:
            base_url: Base URL for the services.
        """
        self.base_url = base_url.rstrip('/')
        self.services = {
            "nginx": f"{self.base_url}/health",
            "backend": f"{self.base_url}/api/health", 
            "frontend": f"{self.base_url}/health"
        }
        
    async def check_service_health(self, session: aiohttp.ClientSession, 
                                 service_name: str, url: str) -> Dict:
        """Check health of a single service.
        
        Args:
            session: HTTP session for making requests.
            service_name: Name of the service.
            url: Health check URL.
            
        Returns:
            Dictionary containing health check results.
        """
        start_time = time.time()
        
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    try:
                        data = await response.json()
                        return {
                            "service": service_name,
                            "status": "healthy",
                            "response_time": round(response_time * 1000, 2),
                            "http_status": response.status,
                            "details": data,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                    except json.JSONDecodeError:
                        # Handle plain text responses
                        text = await response.text()
                        return {
                            "service": service_name,
                            "status": "healthy",
                            "response_time": round(response_time * 1000, 2),
                            "http_status": response.status,
                            "details": {"message": text.strip()},
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                else:
                    return {
                        "service": service_name,
                        "status": "unhealthy",
                        "response_time": round(response_time * 1000, 2),
                        "http_status": response.status,
                        "error": f"HTTP {response.status}",
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    }
                    
        except asyncio.TimeoutError:
            return {
                "service": service_name,
                "status": "timeout",
                "response_time": round((time.time() - start_time) * 1000, 2),
                "error": "Request timeout",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        except Exception as e:
            return {
                "service": service_name,
                "status": "error",
                "response_time": round((time.time() - start_time) * 1000, 2),
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
    
    async def check_all_services(self) -> List[Dict]:
        """Check health of all services.
        
        Returns:
            List of health check results for all services.
        """
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.check_service_health(session, service_name, url)
                for service_name, url in self.services.items()
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions that occurred
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    service_name = list(self.services.keys())[i]
                    processed_results.append({
                        "service": service_name,
                        "status": "error",
                        "error": str(result),
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def monitor_continuously(self, interval: int = 30, max_checks: Optional[int] = None):
        """Monitor services continuously.
        
        Args:
            interval: Check interval in seconds.
            max_checks: Maximum number of checks (None for infinite).
        """
        check_count = 0
        
        logger.info(f"Starting continuous monitoring (interval: {interval}s)")
        
        try:
            while max_checks is None or check_count < max_checks:
                results = await self.check_all_services()
                
                # Log results
                overall_status = "healthy" if all(r.get("status") == "healthy" for r in results) else "degraded"
                
                summary = {
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                    "overall_status": overall_status,
                    "services": results,
                    "check_number": check_count + 1
                }
                
                print(json.dumps(summary, indent=2))
                
                # Log individual service issues
                for result in results:
                    if result.get("status") != "healthy":
                        logger.warning(f"Service {result['service']} is {result.get('status')}: {result.get('error', 'Unknown error')}")
                
                check_count += 1
                
                if max_checks is None or check_count < max_checks:
                    await asyncio.sleep(interval)
                    
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            raise


async def main():
    """Main function for the health monitor."""
    parser = argparse.ArgumentParser(description="Health monitor for CulicidaeLab services")
    parser.add_argument("--base-url", default="http://localhost", 
                       help="Base URL for services (default: http://localhost)")
    parser.add_argument("--interval", type=int, default=30,
                       help="Check interval in seconds (default: 30)")
    parser.add_argument("--max-checks", type=int, default=None,
                       help="Maximum number of checks (default: infinite)")
    parser.add_argument("--single", action="store_true",
                       help="Run a single health check instead of continuous monitoring")
    
    args = parser.parse_args()
    
    monitor = HealthMonitor(base_url=args.base_url)
    
    if args.single:
        # Single health check
        results = await monitor.check_all_services()
        
        summary = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "overall_status": "healthy" if all(r.get("status") == "healthy" for r in results) else "degraded",
            "services": results
        }
        
        print(json.dumps(summary, indent=2))
        
        # Exit with error code if any service is unhealthy
        if summary["overall_status"] != "healthy":
            sys.exit(1)
    else:
        # Continuous monitoring
        await monitor.monitor_continuously(
            interval=args.interval,
            max_checks=args.max_checks
        )


if __name__ == "__main__":
    asyncio.run(main())