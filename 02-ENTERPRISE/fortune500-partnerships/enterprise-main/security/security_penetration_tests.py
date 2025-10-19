#!/usr/bin/env python3
"""
Security and Penetration Testing Suite for AIA Production System
================================================================

This script performs comprehensive security testing including:
- SSL/TLS configuration analysis
- HTTP security headers validation
- Input validation and sanitization testing
- Authentication and authorization testing
- OWASP Top 10 vulnerability scanning
- API security testing
- Cross-site scripting (XSS) testing
- SQL injection testing
- CORS policy validation
"""

import asyncio
import aiohttp
import ssl
import socket
import json
import re
import logging
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from urllib.parse import urlparse, quote
import base64

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SecurityTestResult:
    test_name: str
    category: str  # SSL, Headers, Input, Authentication, etc.
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    status: str    # PASS, FAIL, WARN, SKIP
    vulnerability_found: bool
    details: Dict[str, Any]
    remediation: str
    cvss_score: Optional[float] = None

class SecurityPenetrationTester:
    def __init__(self, base_url: str = "https://013a.tech", api_url: str = "https://api.013a.tech"):
        self.base_url = base_url
        self.api_url = api_url
        self.results: List[SecurityTestResult] = []
        self.start_time = datetime.now()

        # Common payloads for testing
        self.xss_payloads = [
            "<script>alert('XSS')</script>",
            "';alert(String.fromCharCode(88,83,83));//",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg/onload=alert('XSS')>"
        ]

        self.sql_payloads = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL, NULL, NULL --",
            "1' OR '1'='1' --",
            "admin'--"
        ]

        self.command_injection_payloads = [
            "; ls -la",
            "| whoami",
            "`id`",
            "$(whoami)",
            "&& cat /etc/passwd"
        ]

    async def test_ssl_configuration(self) -> List[SecurityTestResult]:
        """Test SSL/TLS configuration and certificate security"""
        results = []
        test_domains = [
            urlparse(self.base_url).netloc,
            urlparse(self.api_url).netloc
        ]

        for domain in test_domains:
            # Test SSL connection and certificate
            try:
                context = ssl.create_default_context()
                sock = socket.create_connection((domain, 443), timeout=10)
                ssock = context.wrap_socket(sock, server_hostname=domain)

                cert = ssock.getpeercert()
                cipher = ssock.cipher()

                ssock.close()
                sock.close()

                # Analyze certificate
                not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                days_until_expiry = (not_after - datetime.now()).days

                # Check for weak ciphers
                weak_ciphers = ['RC4', 'DES', 'MD5', 'NULL']
                cipher_strength = "STRONG"
                if any(weak in cipher[0] for weak in weak_ciphers):
                    cipher_strength = "WEAK"

                # Certificate validation
                cert_issues = []
                if days_until_expiry < 30:
                    cert_issues.append("Certificate expires within 30 days")

                if cert.get('version', 0) < 3:
                    cert_issues.append("Certificate version is outdated")

                results.append(SecurityTestResult(
                    test_name=f"SSL Certificate - {domain}",
                    category="SSL/TLS",
                    severity="HIGH" if cert_issues else "LOW",
                    status="FAIL" if cert_issues else "PASS",
                    vulnerability_found=bool(cert_issues),
                    details={
                        "domain": domain,
                        "certificate_valid": True,
                        "days_until_expiry": days_until_expiry,
                        "cipher_suite": cipher[0] if cipher else "Unknown",
                        "cipher_strength": cipher_strength,
                        "certificate_version": cert.get('version'),
                        "issues": cert_issues
                    },
                    remediation="Renew certificate before expiration and ensure strong cipher suites are used",
                    cvss_score=7.5 if cert_issues else None
                ))

                # Test for weak SSL/TLS versions
                weak_versions = [ssl.PROTOCOL_SSLv2, ssl.PROTOCOL_SSLv3, ssl.PROTOCOL_TLSv1, ssl.PROTOCOL_TLSv1_1]
                weak_version_support = []

                for version in weak_versions:
                    try:
                        weak_context = ssl.SSLContext(version)
                        weak_sock = socket.create_connection((domain, 443), timeout=5)
                        weak_ssock = weak_context.wrap_socket(weak_sock, server_hostname=domain)
                        weak_ssock.close()
                        weak_sock.close()
                        weak_version_support.append(str(version))
                    except:
                        pass

                results.append(SecurityTestResult(
                    test_name=f"Weak SSL Versions - {domain}",
                    category="SSL/TLS",
                    severity="HIGH" if weak_version_support else "LOW",
                    status="FAIL" if weak_version_support else "PASS",
                    vulnerability_found=bool(weak_version_support),
                    details={
                        "domain": domain,
                        "weak_versions_supported": weak_version_support,
                        "secure": not bool(weak_version_support)
                    },
                    remediation="Disable support for SSL v2/v3 and TLS v1.0/v1.1. Use TLS v1.2+ only",
                    cvss_score=8.1 if weak_version_support else None
                ))

            except Exception as e:
                results.append(SecurityTestResult(
                    test_name=f"SSL Test - {domain}",
                    category="SSL/TLS",
                    severity="CRITICAL",
                    status="FAIL",
                    vulnerability_found=True,
                    details={"domain": domain, "error": str(e)},
                    remediation="Fix SSL/TLS configuration issues",
                    cvss_score=9.3
                ))

        return results

    async def test_security_headers(self, session: aiohttp.ClientSession) -> List[SecurityTestResult]:
        """Test HTTP security headers"""
        results = []

        test_urls = [
            self.base_url,
            f"{self.base_url}/aia",
            self.api_url,
            f"{self.api_url}/health"
        ]

        security_headers_tests = {
            "Strict-Transport-Security": {
                "required": True,
                "severity": "HIGH",
                "description": "HSTS header missing - site vulnerable to downgrade attacks"
            },
            "Content-Security-Policy": {
                "required": True,
                "severity": "MEDIUM",
                "description": "CSP header missing - site vulnerable to XSS attacks"
            },
            "X-Frame-Options": {
                "required": True,
                "severity": "MEDIUM",
                "description": "X-Frame-Options missing - site vulnerable to clickjacking"
            },
            "X-Content-Type-Options": {
                "required": True,
                "severity": "MEDIUM",
                "description": "X-Content-Type-Options missing - site vulnerable to MIME type confusion"
            },
            "X-XSS-Protection": {
                "required": False,
                "severity": "LOW",
                "description": "X-XSS-Protection missing - additional XSS protection disabled"
            },
            "Referrer-Policy": {
                "required": False,
                "severity": "LOW",
                "description": "Referrer-Policy missing - referrer information may leak"
            }
        }

        for url in test_urls:
            try:
                async with session.get(url) as response:
                    headers = response.headers

                    missing_headers = []
                    weak_headers = []

                    for header, config in security_headers_tests.items():
                        header_value = headers.get(header)

                        if not header_value and config["required"]:
                            missing_headers.append({
                                "header": header,
                                "severity": config["severity"],
                                "description": config["description"]
                            })
                        elif header_value:
                            # Check for weak configurations
                            if header == "X-Frame-Options" and header_value.upper() not in ["DENY", "SAMEORIGIN"]:
                                weak_headers.append(f"{header}: {header_value}")
                            elif header == "X-Content-Type-Options" and header_value.lower() != "nosniff":
                                weak_headers.append(f"{header}: {header_value}")

                    vulnerability_found = bool(missing_headers or weak_headers)
                    severity = "HIGH" if any(h["severity"] == "HIGH" for h in missing_headers) else "MEDIUM"

                    results.append(SecurityTestResult(
                        test_name=f"Security Headers - {urlparse(url).path or '/'}",
                        category="HTTP Headers",
                        severity=severity if vulnerability_found else "LOW",
                        status="FAIL" if vulnerability_found else "PASS",
                        vulnerability_found=vulnerability_found,
                        details={
                            "url": url,
                            "missing_headers": missing_headers,
                            "weak_headers": weak_headers,
                            "present_headers": {k: v for k, v in headers.items() if k in security_headers_tests}
                        },
                        remediation="Implement missing security headers and fix weak configurations",
                        cvss_score=6.1 if vulnerability_found else None
                    ))

            except Exception as e:
                results.append(SecurityTestResult(
                    test_name=f"Security Headers - {url}",
                    category="HTTP Headers",
                    severity="MEDIUM",
                    status="FAIL",
                    vulnerability_found=True,
                    details={"url": url, "error": str(e)},
                    remediation="Fix connectivity issues and implement security headers"
                ))

        return results

    async def test_input_validation(self, session: aiohttp.ClientSession) -> List[SecurityTestResult]:
        """Test input validation and sanitization"""
        results = []

        # Test XSS vulnerabilities
        xss_test_endpoints = [
            f"{self.api_url}/knowledge-graph/query",
            f"{self.api_url}/tasks/submit"
        ]

        for endpoint in xss_test_endpoints:
            for payload in self.xss_payloads:
                try:
                    # Test GET parameter injection
                    test_url = f"{endpoint}?search={quote(payload)}"
                    async with session.get(test_url) as response:
                        content = await response.text()

                        # Check if payload is reflected unescaped
                        payload_reflected = payload in content
                        payload_escaped = any(escaped in content for escaped in [
                            "&lt;script&gt;", "&amp;lt;", "\\u003c"
                        ])

                        if payload_reflected and not payload_escaped:
                            results.append(SecurityTestResult(
                                test_name=f"XSS Vulnerability - {endpoint}",
                                category="Input Validation",
                                severity="HIGH",
                                status="FAIL",
                                vulnerability_found=True,
                                details={
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "reflected": payload_reflected,
                                    "escaped": payload_escaped,
                                    "method": "GET"
                                },
                                remediation="Implement proper input validation and output encoding",
                                cvss_score=7.2
                            ))

                    # Test POST parameter injection
                    if endpoint.endswith('/query') or endpoint.endswith('/submit'):
                        test_data = {"search_term": payload, "query": payload}
                        async with session.post(endpoint, json=test_data) as response:
                            if response.status != 404:  # Skip if endpoint doesn't exist
                                content = await response.text()

                                payload_reflected = payload in content
                                if payload_reflected:
                                    results.append(SecurityTestResult(
                                        test_name=f"XSS Vulnerability POST - {endpoint}",
                                        category="Input Validation",
                                        severity="HIGH",
                                        status="FAIL",
                                        vulnerability_found=True,
                                        details={
                                            "endpoint": endpoint,
                                            "payload": payload,
                                            "method": "POST",
                                            "data": test_data
                                        },
                                        remediation="Implement proper input validation for POST requests",
                                        cvss_score=7.2
                                    ))

                except Exception as e:
                    # Expected for many test cases
                    pass

        # Test SQL Injection
        sql_test_endpoints = [
            f"{self.api_url}/knowledge-graph/query",
            f"{self.api_url}/metrics"
        ]

        for endpoint in sql_test_endpoints:
            for payload in self.sql_payloads:
                try:
                    test_data = {"search_term": payload, "id": payload}
                    async with session.post(endpoint, json=test_data) as response:
                        content = await response.text()

                        # Look for SQL error messages
                        sql_errors = [
                            "sql syntax", "mysql", "postgresql", "sqlite",
                            "ora-", "syntax error", "unclosed quotation mark",
                            "quoted string not properly terminated"
                        ]

                        if any(error in content.lower() for error in sql_errors):
                            results.append(SecurityTestResult(
                                test_name=f"SQL Injection - {endpoint}",
                                category="Input Validation",
                                severity="CRITICAL",
                                status="FAIL",
                                vulnerability_found=True,
                                details={
                                    "endpoint": endpoint,
                                    "payload": payload,
                                    "error_detected": True,
                                    "response_content": content[:500]
                                },
                                remediation="Use parameterized queries and input validation",
                                cvss_score=9.8
                            ))

                except Exception as e:
                    pass

        return results

    async def test_authentication_bypass(self, session: aiohttp.ClientSession) -> List[SecurityTestResult]:
        """Test for authentication and authorization bypass vulnerabilities"""
        results = []

        # Test endpoints that might require authentication
        protected_endpoints = [
            f"{self.api_url}/business-intelligence/dashboard",
            f"{self.api_url}/sprint4/status",
            f"{self.api_url}/monitoring/dashboard"
        ]

        for endpoint in protected_endpoints:
            try:
                # Test without authentication
                async with session.get(endpoint) as response:
                    # If we get 200 OK, might indicate missing authentication
                    if response.status == 200:
                        content = await response.text()

                        # Check if we're getting actual data or just public info
                        sensitive_indicators = [
                            "business_metrics", "revenue", "confidential",
                            "internal", "dashboard_data", "performance_metrics"
                        ]

                        has_sensitive_data = any(indicator in content.lower() for indicator in sensitive_indicators)

                        if has_sensitive_data:
                            results.append(SecurityTestResult(
                                test_name=f"Missing Authentication - {endpoint}",
                                category="Authentication",
                                severity="HIGH",
                                status="FAIL",
                                vulnerability_found=True,
                                details={
                                    "endpoint": endpoint,
                                    "status_code": response.status,
                                    "sensitive_data_exposed": has_sensitive_data,
                                    "content_sample": content[:200]
                                },
                                remediation="Implement proper authentication for sensitive endpoints",
                                cvss_score=8.2
                            ))

                # Test with invalid authentication
                fake_headers = {
                    "Authorization": "Bearer invalid_token_123",
                    "X-API-Key": "fake_api_key"
                }

                async with session.get(endpoint, headers=fake_headers) as response:
                    if response.status == 200:
                        results.append(SecurityTestResult(
                            test_name=f"Weak Authentication - {endpoint}",
                            category="Authentication",
                            severity="MEDIUM",
                            status="FAIL",
                            vulnerability_found=True,
                            details={
                                "endpoint": endpoint,
                                "fake_token_accepted": True,
                                "status_code": response.status
                            },
                            remediation="Implement proper token validation",
                            cvss_score=6.5
                        ))

            except Exception as e:
                pass

        return results

    async def test_information_disclosure(self, session: aiohttp.ClientSession) -> List[SecurityTestResult]:
        """Test for information disclosure vulnerabilities"""
        results = []

        # Test for exposed sensitive files
        sensitive_paths = [
            "/.env", "/.git/config", "/config.json", "/package.json",
            "/admin", "/debug", "/test", "/.DS_Store", "/backup"
        ]

        for path in sensitive_paths:
            try:
                test_url = f"{self.base_url}{path}"
                async with session.get(test_url) as response:
                    if response.status == 200:
                        content = await response.text()

                        # Check for sensitive information
                        sensitive_patterns = [
                            r"password\s*[:=]\s*['\"]([^'\"]+)['\"]",
                            r"api[_-]?key\s*[:=]\s*['\"]([^'\"]+)['\"]",
                            r"secret\s*[:=]\s*['\"]([^'\"]+)['\"]",
                            r"token\s*[:=]\s*['\"]([^'\"]+)['\"]"
                        ]

                        found_secrets = []
                        for pattern in sensitive_patterns:
                            matches = re.findall(pattern, content, re.IGNORECASE)
                            found_secrets.extend(matches)

                        if content and len(content) > 10:  # Non-empty response
                            results.append(SecurityTestResult(
                                test_name=f"Information Disclosure - {path}",
                                category="Information Disclosure",
                                severity="HIGH" if found_secrets else "MEDIUM",
                                status="FAIL",
                                vulnerability_found=True,
                                details={
                                    "path": path,
                                    "status_code": response.status,
                                    "content_length": len(content),
                                    "secrets_found": len(found_secrets),
                                    "content_preview": content[:200]
                                },
                                remediation="Remove or protect sensitive files from public access",
                                cvss_score=8.6 if found_secrets else 5.3
                            ))

            except Exception as e:
                pass

        return results

    async def test_cors_policy(self, session: aiohttp.ClientSession) -> List[SecurityTestResult]:
        """Test CORS policy configuration"""
        results = []

        # Test with malicious origins
        malicious_origins = [
            "https://evil.com",
            "http://attacker.local",
            "*",
            "null"
        ]

        test_endpoint = f"{self.api_url}/health"

        for origin in malicious_origins:
            try:
                headers = {
                    "Origin": origin,
                    "Access-Control-Request-Method": "GET"
                }

                async with session.options(test_endpoint, headers=headers) as response:
                    cors_origin = response.headers.get("Access-Control-Allow-Origin")

                    if cors_origin == origin or cors_origin == "*":
                        severity = "HIGH" if origin in ["*", "null"] else "MEDIUM"
                        results.append(SecurityTestResult(
                            test_name=f"Weak CORS Policy - {origin}",
                            category="CORS",
                            severity=severity,
                            status="FAIL",
                            vulnerability_found=True,
                            details={
                                "test_origin": origin,
                                "allowed_origin": cors_origin,
                                "status_code": response.status,
                                "allows_credentials": response.headers.get("Access-Control-Allow-Credentials")
                            },
                            remediation="Implement strict CORS policy with specific allowed origins",
                            cvss_score=7.5 if severity == "HIGH" else 5.3
                        ))

            except Exception as e:
                pass

        return results

    async def run_comprehensive_security_tests(self) -> Dict[str, Any]:
        """Run all security tests"""
        logger.info("🔒 Starting Comprehensive Security Testing...")
        logger.info(f"Testing Frontend: {self.base_url}")
        logger.info(f"Testing API: {self.api_url}")

        # Configure session with reasonable timeouts
        connector = aiohttp.TCPConnector(limit=30, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            # Run test suites
            test_suites = [
                ("SSL/TLS Configuration", self.test_ssl_configuration()),
                ("Security Headers", self.test_security_headers(session)),
                ("Input Validation", self.test_input_validation(session)),
                ("Authentication", self.test_authentication_bypass(session)),
                ("Information Disclosure", self.test_information_disclosure(session)),
                ("CORS Policy", self.test_cors_policy(session))
            ]

            all_results = []

            for suite_name, suite_coro in test_suites:
                logger.info(f"\n🔍 Running {suite_name} Tests...")
                try:
                    if asyncio.iscoroutine(suite_coro):
                        suite_results = await suite_coro
                    else:
                        suite_results = suite_coro

                    all_results.extend(suite_results)

                    # Count results
                    vulnerabilities = len([r for r in suite_results if r.vulnerability_found])
                    total = len(suite_results)

                    if vulnerabilities > 0:
                        logger.warning(f"  ⚠️ {suite_name}: {vulnerabilities}/{total} vulnerabilities found")
                    else:
                        logger.info(f"  ✅ {suite_name}: No vulnerabilities detected")

                except Exception as e:
                    logger.error(f"  ❌ {suite_name} failed: {e}")

        # Generate security report
        total_tests = len(all_results)
        vulnerabilities = [r for r in all_results if r.vulnerability_found]
        critical_vulns = len([r for r in vulnerabilities if r.severity == "CRITICAL"])
        high_vulns = len([r for r in vulnerabilities if r.severity == "HIGH"])
        medium_vulns = len([r for r in vulnerabilities if r.severity == "MEDIUM"])
        low_vulns = len([r for r in vulnerabilities if r.severity == "LOW"])

        # Calculate security score (0-100)
        max_possible_score = 100
        score_deductions = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3
        }

        security_score = max_possible_score
        for vuln in vulnerabilities:
            security_score -= score_deductions.get(vuln.severity, 0)

        security_score = max(0, security_score)

        # Determine security grade
        if security_score >= 90:
            security_grade = "A - Excellent Security"
        elif security_score >= 80:
            security_grade = "B - Good Security"
        elif security_score >= 70:
            security_grade = "C - Acceptable Security"
        elif security_score >= 60:
            security_grade = "D - Poor Security"
        else:
            security_grade = "F - Critical Security Issues"

        total_duration = (datetime.now() - self.start_time).total_seconds()

        return {
            "security_summary": {
                "total_tests": total_tests,
                "total_vulnerabilities": len(vulnerabilities),
                "critical_vulnerabilities": critical_vulns,
                "high_vulnerabilities": high_vulns,
                "medium_vulnerabilities": medium_vulns,
                "low_vulnerabilities": low_vulns,
                "security_score": security_score,
                "security_grade": security_grade,
                "test_duration_seconds": total_duration,
                "compliance_status": "NON-COMPLIANT" if critical_vulns > 0 else "COMPLIANT"
            },
            "vulnerability_breakdown": {
                "ssl_tls": len([r for r in vulnerabilities if r.category == "SSL/TLS"]),
                "headers": len([r for r in vulnerabilities if r.category == "HTTP Headers"]),
                "input_validation": len([r for r in vulnerabilities if r.category == "Input Validation"]),
                "authentication": len([r for r in vulnerabilities if r.category == "Authentication"]),
                "information_disclosure": len([r for r in vulnerabilities if r.category == "Information Disclosure"]),
                "cors": len([r for r in vulnerabilities if r.category == "CORS"])
            },
            "detailed_results": [asdict(result) for result in all_results],
            "remediation_priority": [
                asdict(vuln) for vuln in sorted(vulnerabilities,
                key=lambda x: {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}.get(x.severity, 0),
                reverse=True)[:10]  # Top 10 priority fixes
            ],
            "test_environment": {
                "base_url": self.base_url,
                "api_url": self.api_url,
                "test_timestamp": self.start_time.isoformat()
            }
        }

async def main():
    """Main execution function"""
    try:
        tester = SecurityPenetrationTester()
        results = await tester.run_comprehensive_security_tests()

        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"security_penetration_test_results_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Print summary
        summary = results["security_summary"]
        logger.info(f"\n" + "="*70)
        logger.info(f"🔒 SECURITY & PENETRATION TEST RESULTS")
        logger.info(f"="*70)
        logger.info(f"📊 Total Tests: {summary['total_tests']}")
        logger.info(f"🚨 Total Vulnerabilities: {summary['total_vulnerabilities']}")
        logger.info(f"💀 Critical: {summary['critical_vulnerabilities']}")
        logger.info(f"🔥 High: {summary['high_vulnerabilities']}")
        logger.info(f"⚠️ Medium: {summary['medium_vulnerabilities']}")
        logger.info(f"ℹ️ Low: {summary['low_vulnerabilities']}")
        logger.info(f"🎯 Security Score: {summary['security_score']}/100")
        logger.info(f"📈 Security Grade: {summary['security_grade']}")
        logger.info(f"✅ Compliance: {summary['compliance_status']}")
        logger.info(f"⏱️ Duration: {summary['test_duration_seconds']:.1f}s")
        logger.info(f"="*70)

        # Show top vulnerabilities
        if results.get("remediation_priority"):
            logger.info(f"\n🚨 TOP PRIORITY VULNERABILITIES:")
            for i, vuln in enumerate(results["remediation_priority"][:5], 1):
                logger.warning(f"  {i}. [{vuln['severity']}] {vuln['test_name']}")
                logger.info(f"     → {vuln['remediation']}")

        logger.info(f"\n💾 Detailed results saved to: {results_file}")

        return results

    except Exception as e:
        logger.error(f"❌ Security testing failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    asyncio.run(main())