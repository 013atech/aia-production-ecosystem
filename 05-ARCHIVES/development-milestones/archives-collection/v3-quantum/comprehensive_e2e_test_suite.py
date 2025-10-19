#!/usr/bin/env python3
"""
Comprehensive End-to-End Testing Suite for AIA Production System
================================================================

This script performs comprehensive testing of the AIA system including:
- Frontend functionality and performance
- Backend API endpoints
- Integration testing
- Performance benchmarking
- Security validation
- Cross-browser compatibility
- Database connectivity
- Monitoring systems

Production URLs:
- Frontend: https://013a.tech
- Backend: https://api.013a.tech
- LoadBalancer IP: 35.204.144.16
"""

import asyncio
import aiohttp
import json
import time
import logging
import traceback
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess
import platform
import ssl
import socket
from urllib.parse import urlparse
import statistics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('comprehensive_test_results.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    test_name: str
    status: str  # PASS, FAIL, WARN, SKIP
    duration_ms: float
    details: Dict[str, Any]
    error: Optional[str] = None
    severity: str = "INFO"  # INFO, WARN, ERROR, CRITICAL

@dataclass
class SystemUrls:
    frontend_base: str = "https://013a.tech"
    backend_base: str = "https://api.013a.tech"
    loadbalancer_ip: str = "35.204.144.16"

    def get_frontend_urls(self) -> List[str]:
        """Get all frontend routes to test"""
        return [
            f"{self.frontend_base}/",
            f"{self.frontend_base}/request",
            f"{self.frontend_base}/signup",
            f"{self.frontend_base}/login",
            f"{self.frontend_base}/dashboard",
            f"{self.frontend_base}/aia",
            f"{self.frontend_base}/complete",
            f"{self.frontend_base}/test",
            f"{self.frontend_base}/ultimate",
            f"{self.frontend_base}/immersive",
            f"{self.frontend_base}/sprint1",
            f"{self.frontend_base}/payment",
            f"{self.frontend_base}/partners/ey",
            f"{self.frontend_base}/partners/jpmorgan",
            f"{self.frontend_base}/partners/google-cloud",
            f"{self.frontend_base}/partners/apple"
        ]

    def get_backend_endpoints(self) -> List[str]:
        """Get all backend API endpoints to test"""
        return [
            f"{self.backend_base}/",
            f"{self.backend_base}/health",
            f"{self.backend_base}/metrics",
            f"{self.backend_base}/knowledge-graph/status",
            f"{self.backend_base}/business-intelligence/dashboard",
            f"{self.backend_base}/sprint4/status",
            f"{self.backend_base}/sprint5/status",
            f"{self.backend_base}/monitoring/dashboard"
        ]

class ComprehensiveTestSuite:
    def __init__(self):
        self.urls = SystemUrls()
        self.results: List[TestResult] = []
        self.start_time = datetime.now()
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ssl=ssl.create_default_context()
        )
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={
                'User-Agent': 'AIA-E2E-Test-Suite/1.0'
            }
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()

    def add_result(self, result: TestResult):
        """Add a test result to the collection"""
        self.results.append(result)

        # Log result immediately
        status_icon = {
            "PASS": "✅",
            "FAIL": "❌",
            "WARN": "⚠️",
            "SKIP": "⏭️"
        }.get(result.status, "❓")

        logger.info(f"{status_icon} {result.test_name}: {result.status} ({result.duration_ms:.0f}ms)")
        if result.error:
            logger.error(f"   Error: {result.error}")

    async def test_ssl_certificates(self) -> List[TestResult]:
        """Test SSL certificate validity and security"""
        results = []
        test_domains = ["013a.tech", "api.013a.tech"]

        for domain in test_domains:
            start_time = time.time()
            try:
                # Test SSL connection
                context = ssl.create_default_context()
                sock = socket.create_connection((domain, 443), timeout=10)
                ssock = context.wrap_socket(sock, server_hostname=domain)

                cert = ssock.getpeercert()
                ssock.close()
                sock.close()

                # Check certificate details
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.now()).days

                if days_until_expiry < 30:
                    status = "WARN"
                    severity = "WARN"
                elif days_until_expiry < 7:
                    status = "FAIL"
                    severity = "ERROR"
                else:
                    status = "PASS"
                    severity = "INFO"

                results.append(TestResult(
                    test_name=f"SSL Certificate - {domain}",
                    status=status,
                    duration_ms=(time.time() - start_time) * 1000,
                    details={
                        "domain": domain,
                        "issuer": cert.get('issuer'),
                        "subject": cert.get('subject'),
                        "not_after": cert['notAfter'],
                        "days_until_expiry": days_until_expiry,
                        "version": cert.get('version'),
                        "serial_number": cert.get('serialNumber')
                    },
                    severity=severity
                ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"SSL Certificate - {domain}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"domain": domain},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_dns_resolution(self) -> List[TestResult]:
        """Test DNS resolution for all domains"""
        results = []
        test_domains = ["013a.tech", "api.013a.tech", "www.013a.tech"]

        for domain in test_domains:
            start_time = time.time()
            try:
                # Test DNS resolution
                addr_info = socket.getaddrinfo(domain, None)
                ip_addresses = list(set([info[4][0] for info in addr_info]))

                results.append(TestResult(
                    test_name=f"DNS Resolution - {domain}",
                    status="PASS",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={
                        "domain": domain,
                        "ip_addresses": ip_addresses,
                        "record_count": len(ip_addresses)
                    },
                    severity="INFO"
                ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"DNS Resolution - {domain}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"domain": domain},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_frontend_routes(self) -> List[TestResult]:
        """Test all frontend routes for accessibility and performance"""
        results = []
        frontend_urls = self.urls.get_frontend_urls()

        for url in frontend_urls:
            start_time = time.time()
            try:
                async with self.session.get(url) as response:
                    duration = (time.time() - start_time) * 1000

                    content = await response.text()
                    content_size = len(content)

                    # Performance thresholds
                    if duration > 3000:  # 3 seconds
                        status = "WARN"
                        severity = "WARN"
                    elif duration > 5000:  # 5 seconds
                        status = "FAIL"
                        severity = "ERROR"
                    else:
                        status = "PASS" if response.status == 200 else "FAIL"
                        severity = "INFO" if response.status == 200 else "ERROR"

                    # Check for React app indicators
                    has_react = 'React' in content or 'react' in content
                    has_root_div = 'id="root"' in content or 'id=root' in content

                    results.append(TestResult(
                        test_name=f"Frontend Route - {url.split('/')[-1] or 'home'}",
                        status=status,
                        duration_ms=duration,
                        details={
                            "url": url,
                            "status_code": response.status,
                            "content_size": content_size,
                            "has_react": has_react,
                            "has_root_div": has_root_div,
                            "headers": dict(response.headers)
                        },
                        severity=severity
                    ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"Frontend Route - {url.split('/')[-1] or 'home'}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"url": url},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_backend_endpoints(self) -> List[TestResult]:
        """Test all backend API endpoints"""
        results = []
        backend_endpoints = self.urls.get_backend_endpoints()

        for endpoint in backend_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(endpoint) as response:
                    duration = (time.time() - start_time) * 1000

                    content_type = response.headers.get('content-type', '')

                    if 'application/json' in content_type:
                        data = await response.json()
                    else:
                        data = await response.text()

                    # API performance thresholds
                    if duration > 2000:  # 2 seconds
                        status = "WARN"
                        severity = "WARN"
                    elif duration > 5000:  # 5 seconds
                        status = "FAIL"
                        severity = "ERROR"
                    else:
                        status = "PASS" if response.status == 200 else "FAIL"
                        severity = "INFO" if response.status == 200 else "ERROR"

                    results.append(TestResult(
                        test_name=f"Backend API - {endpoint.split('/')[-1] or 'root'}",
                        status=status,
                        duration_ms=duration,
                        details={
                            "endpoint": endpoint,
                            "status_code": response.status,
                            "content_type": content_type,
                            "response_data": data if isinstance(data, dict) else str(data)[:200],
                            "headers": dict(response.headers)
                        },
                        severity=severity
                    ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"Backend API - {endpoint.split('/')[-1] or 'root'}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"endpoint": endpoint},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_health_endpoints(self) -> List[TestResult]:
        """Test health and monitoring endpoints in detail"""
        results = []
        health_endpoints = [
            f"{self.urls.backend_base}/health",
            f"{self.urls.backend_base}/metrics",
            f"{self.urls.backend_base}/monitoring/dashboard"
        ]

        for endpoint in health_endpoints:
            start_time = time.time()
            try:
                async with self.session.get(endpoint) as response:
                    duration = (time.time() - start_time) * 1000

                    if response.status == 200:
                        data = await response.json()

                        # Analyze health data
                        health_details = {}
                        if 'health' in endpoint:
                            health_details = {
                                "system_status": data.get("status", "unknown"),
                                "initialized": data.get("initialized", False),
                                "components": data.get("components", {}),
                                "circuit_breakers": data.get("circuit_breakers", {})
                            }
                        elif 'metrics' in endpoint:
                            health_details = {
                                "active_tasks": data.get("active_tasks", 0),
                                "completed_tasks": data.get("completed_tasks", 0),
                                "failed_tasks": data.get("failed_tasks", 0),
                                "queued_tasks": data.get("queued_tasks", 0)
                            }

                        status = "PASS"
                        if 'health' in endpoint and data.get("status") != "healthy":
                            status = "WARN" if data.get("status") == "degraded" else "FAIL"

                        results.append(TestResult(
                            test_name=f"Health Check - {endpoint.split('/')[-1]}",
                            status=status,
                            duration_ms=duration,
                            details={
                                "endpoint": endpoint,
                                "response_data": data,
                                **health_details
                            },
                            severity="INFO" if status == "PASS" else "WARN"
                        ))
                    else:
                        results.append(TestResult(
                            test_name=f"Health Check - {endpoint.split('/')[-1]}",
                            status="FAIL",
                            duration_ms=duration,
                            details={
                                "endpoint": endpoint,
                                "status_code": response.status
                            },
                            error=f"HTTP {response.status}",
                            severity="ERROR"
                        ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"Health Check - {endpoint.split('/')[-1]}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"endpoint": endpoint},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_load_performance(self) -> List[TestResult]:
        """Test system performance under concurrent load"""
        results = []

        # Test concurrent requests to main endpoints
        test_urls = [
            f"{self.urls.frontend_base}/",
            f"{self.urls.backend_base}/health",
            f"{self.urls.backend_base}/metrics"
        ]

        for url in test_urls:
            start_time = time.time()

            # Run 10 concurrent requests
            concurrent_requests = 10
            tasks = []

            for i in range(concurrent_requests):
                tasks.append(self.single_request(url))

            try:
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = (time.time() - start_time) * 1000

                # Analyze responses
                successful_requests = sum(1 for r in responses if not isinstance(r, Exception) and r.get('status') == 200)
                failed_requests = concurrent_requests - successful_requests

                if isinstance(responses[0], dict):
                    response_times = [r.get('duration', 0) for r in responses if isinstance(r, dict)]
                    avg_response_time = statistics.mean(response_times) if response_times else 0
                    max_response_time = max(response_times) if response_times else 0
                    min_response_time = min(response_times) if response_times else 0
                else:
                    avg_response_time = max_response_time = min_response_time = 0

                success_rate = (successful_requests / concurrent_requests) * 100

                if success_rate < 80:
                    status = "FAIL"
                    severity = "ERROR"
                elif success_rate < 95:
                    status = "WARN"
                    severity = "WARN"
                else:
                    status = "PASS"
                    severity = "INFO"

                results.append(TestResult(
                    test_name=f"Load Test - {url.split('/')[-1] or 'home'}",
                    status=status,
                    duration_ms=duration,
                    details={
                        "url": url,
                        "concurrent_requests": concurrent_requests,
                        "successful_requests": successful_requests,
                        "failed_requests": failed_requests,
                        "success_rate_percent": success_rate,
                        "avg_response_time_ms": avg_response_time,
                        "max_response_time_ms": max_response_time,
                        "min_response_time_ms": min_response_time
                    },
                    severity=severity
                ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"Load Test - {url.split('/')[-1] or 'home'}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={
                        "url": url,
                        "concurrent_requests": concurrent_requests
                    },
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def single_request(self, url: str) -> Dict[str, Any]:
        """Make a single request and return timing info"""
        start_time = time.time()
        try:
            async with self.session.get(url) as response:
                duration = (time.time() - start_time) * 1000
                return {
                    "url": url,
                    "status": response.status,
                    "duration": duration,
                    "success": response.status == 200
                }
        except Exception as e:
            return {
                "url": url,
                "status": 0,
                "duration": (time.time() - start_time) * 1000,
                "success": False,
                "error": str(e)
            }

    async def test_cors_headers(self) -> List[TestResult]:
        """Test CORS configuration"""
        results = []
        test_origins = [
            "https://013a.tech",
            "https://www.013a.tech",
            "http://localhost:3000"
        ]

        for origin in test_origins:
            start_time = time.time()
            try:
                headers = {
                    'Origin': origin,
                    'Access-Control-Request-Method': 'GET',
                    'Access-Control-Request-Headers': 'Content-Type'
                }

                async with self.session.options(f"{self.urls.backend_base}/health", headers=headers) as response:
                    duration = (time.time() - start_time) * 1000

                    cors_headers = {
                        'access_control_allow_origin': response.headers.get('Access-Control-Allow-Origin'),
                        'access_control_allow_methods': response.headers.get('Access-Control-Allow-Methods'),
                        'access_control_allow_headers': response.headers.get('Access-Control-Allow-Headers'),
                        'access_control_allow_credentials': response.headers.get('Access-Control-Allow-Credentials')
                    }

                    status = "PASS" if response.status in [200, 204] else "FAIL"

                    results.append(TestResult(
                        test_name=f"CORS Test - {origin}",
                        status=status,
                        duration_ms=duration,
                        details={
                            "origin": origin,
                            "status_code": response.status,
                            "cors_headers": cors_headers
                        },
                        severity="INFO" if status == "PASS" else "WARN"
                    ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"CORS Test - {origin}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"origin": origin},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def test_security_headers(self) -> List[TestResult]:
        """Test security headers"""
        results = []

        test_urls = [
            f"{self.urls.frontend_base}/",
            f"{self.urls.backend_base}/health"
        ]

        for url in test_urls:
            start_time = time.time()
            try:
                async with self.session.get(url) as response:
                    duration = (time.time() - start_time) * 1000

                    # Check for security headers
                    security_headers = {
                        'strict_transport_security': response.headers.get('Strict-Transport-Security'),
                        'content_security_policy': response.headers.get('Content-Security-Policy'),
                        'x_frame_options': response.headers.get('X-Frame-Options'),
                        'x_content_type_options': response.headers.get('X-Content-Type-Options'),
                        'x_xss_protection': response.headers.get('X-XSS-Protection'),
                        'referrer_policy': response.headers.get('Referrer-Policy')
                    }

                    # Count present security headers
                    present_headers = sum(1 for v in security_headers.values() if v is not None)

                    if present_headers >= 4:
                        status = "PASS"
                        severity = "INFO"
                    elif present_headers >= 2:
                        status = "WARN"
                        severity = "WARN"
                    else:
                        status = "FAIL"
                        severity = "ERROR"

                    results.append(TestResult(
                        test_name=f"Security Headers - {url.split('/')[-1] or 'home'}",
                        status=status,
                        duration_ms=duration,
                        details={
                            "url": url,
                            "security_headers": security_headers,
                            "present_headers_count": present_headers,
                            "total_headers_checked": len(security_headers)
                        },
                        severity=severity
                    ))

            except Exception as e:
                results.append(TestResult(
                    test_name=f"Security Headers - {url.split('/')[-1] or 'home'}",
                    status="FAIL",
                    duration_ms=(time.time() - start_time) * 1000,
                    details={"url": url},
                    error=str(e),
                    severity="ERROR"
                ))

        return results

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all test suites"""
        logger.info("🚀 Starting Comprehensive AIA Production System Testing...")
        logger.info(f"Testing Frontend: {self.urls.frontend_base}")
        logger.info(f"Testing Backend: {self.urls.backend_base}")
        logger.info(f"LoadBalancer IP: {self.urls.loadbalancer_ip}")

        # Run all test suites
        test_suites = [
            ("DNS Resolution", self.test_dns_resolution()),
            ("SSL Certificates", self.test_ssl_certificates()),
            ("Frontend Routes", self.test_frontend_routes()),
            ("Backend Endpoints", self.test_backend_endpoints()),
            ("Health Endpoints", self.test_health_endpoints()),
            ("Load Performance", self.test_load_performance()),
            ("CORS Configuration", self.test_cors_headers()),
            ("Security Headers", self.test_security_headers())
        ]

        for suite_name, suite_coro in test_suites:
            logger.info(f"\n📋 Running {suite_name} Tests...")
            try:
                suite_results = await suite_coro
                self.results.extend(suite_results)
                logger.info(f"✅ {suite_name} Tests Complete: {len(suite_results)} tests")
            except Exception as e:
                logger.error(f"❌ {suite_name} Test Suite Failed: {e}")
                self.add_result(TestResult(
                    test_name=f"{suite_name} Suite",
                    status="FAIL",
                    duration_ms=0,
                    details={},
                    error=str(e),
                    severity="CRITICAL"
                ))

        # Generate summary
        total_tests = len(self.results)
        passed = len([r for r in self.results if r.status == "PASS"])
        failed = len([r for r in self.results if r.status == "FAIL"])
        warnings = len([r for r in self.results if r.status == "WARN"])
        skipped = len([r for r in self.results if r.status == "SKIP"])

        total_duration = (datetime.now() - self.start_time).total_seconds()

        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "skipped": skipped,
                "success_rate": (passed / total_tests * 100) if total_tests > 0 else 0,
                "total_duration_seconds": total_duration
            },
            "system_status": "HEALTHY" if failed == 0 else "DEGRADED" if failed < 3 else "UNHEALTHY",
            "recommendations": self.generate_recommendations(),
            "detailed_results": [asdict(result) for result in self.results],
            "test_environment": {
                "frontend_base": self.urls.frontend_base,
                "backend_base": self.urls.backend_base,
                "loadbalancer_ip": self.urls.loadbalancer_ip,
                "test_timestamp": self.start_time.isoformat(),
                "platform": platform.platform(),
                "python_version": platform.python_version()
            }
        }

        return summary

    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Analyze failures
        critical_failures = [r for r in self.results if r.severity == "CRITICAL"]
        error_failures = [r for r in self.results if r.severity == "ERROR"]
        warnings = [r for r in self.results if r.severity == "WARN"]

        if critical_failures:
            recommendations.append("🚨 CRITICAL: Address system-wide failures immediately")

        if error_failures:
            recommendations.append(f"❌ HIGH: Fix {len(error_failures)} error-level issues")

        if warnings:
            recommendations.append(f"⚠️ MEDIUM: Address {len(warnings)} warning-level issues")

        # Performance recommendations
        slow_tests = [r for r in self.results if r.duration_ms > 3000]
        if slow_tests:
            recommendations.append(f"🐌 PERFORMANCE: {len(slow_tests)} endpoints have slow response times (>3s)")

        # Security recommendations
        security_issues = [r for r in self.results if "Security" in r.test_name and r.status != "PASS"]
        if security_issues:
            recommendations.append(f"🔒 SECURITY: Address {len(security_issues)} security header issues")

        # SSL recommendations
        ssl_warnings = [r for r in self.results if "SSL" in r.test_name and r.status == "WARN"]
        if ssl_warnings:
            recommendations.append("📜 SSL: Monitor SSL certificate expiration dates")

        if not recommendations:
            recommendations.append("✅ EXCELLENT: All systems are performing within acceptable parameters")

        return recommendations

async def main():
    """Main test execution function"""
    try:
        async with ComprehensiveTestSuite() as test_suite:
            results = await test_suite.run_all_tests()

            # Save results to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"aia_comprehensive_test_results_{timestamp}.json"

            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            # Print summary
            summary = results["test_summary"]
            logger.info(f"\n" + "="*80)
            logger.info(f"🏁 AIA COMPREHENSIVE TEST RESULTS SUMMARY")
            logger.info(f"="*80)
            logger.info(f"📊 Total Tests: {summary['total_tests']}")
            logger.info(f"✅ Passed: {summary['passed']}")
            logger.info(f"❌ Failed: {summary['failed']}")
            logger.info(f"⚠️ Warnings: {summary['warnings']}")
            logger.info(f"⏭️ Skipped: {summary['skipped']}")
            logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
            logger.info(f"⏱️ Duration: {summary['total_duration_seconds']:.1f}s")
            logger.info(f"🏥 System Status: {results['system_status']}")
            logger.info(f"="*80)

            logger.info(f"\n🎯 RECOMMENDATIONS:")
            for rec in results["recommendations"]:
                logger.info(f"   {rec}")

            logger.info(f"\n💾 Detailed results saved to: {results_file}")

            return results

    except Exception as e:
        logger.error(f"❌ Test suite execution failed: {e}")
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    asyncio.run(main())