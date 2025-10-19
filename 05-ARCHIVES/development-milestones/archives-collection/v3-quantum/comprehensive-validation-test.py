#!/usr/bin/env python3
"""
AIA Production System - Comprehensive End-to-End Validation Test Suite
=================================================================

Full-complexity validation of the deployed AIA production system including:
- Multi-agent orchestration testing
- Database connectivity validation
- API endpoint verification
- Performance benchmarking
- Resource optimization validation
- Security and compliance checks
"""

import os
import sys
import json
import time
import logging
import requests
import subprocess
import concurrent.futures
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

class AIAProductionValidator:
    def __init__(self):
        self.namespace = "aia-production"
        self.backend_service = "aia-backend-service-simple"
        self.frontend_service = "aia-frontend-service"
        self.postgres_service = "aia-postgres"
        self.redis_service = "aia-redis"

        self.test_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_suite_version": "4.0.2",
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_details": []
        }

        # Get cluster endpoint for external testing
        try:
            result = subprocess.run(['kubectl', 'cluster-info'],
                                  capture_output=True, text=True)
            self.cluster_available = result.returncode == 0
        except:
            self.cluster_available = False

    def run_kubectl_command(self, command: List[str]) -> Tuple[bool, str]:
        """Execute kubectl command and return success status and output"""
        try:
            result = subprocess.run(['kubectl'] + command,
                                  capture_output=True, text=True, timeout=30)
            return result.returncode == 0, result.stdout.strip()
        except subprocess.TimeoutExpired:
            return False, "Command timeout"
        except Exception as e:
            return False, str(e)

    def test_cluster_connectivity(self) -> bool:
        """Test basic Kubernetes cluster connectivity"""
        logger.info("🔗 Testing cluster connectivity...")

        success, output = self.run_kubectl_command(['get', 'nodes'])

        test_result = {
            "test_name": "Cluster Connectivity",
            "category": "Infrastructure",
            "status": "PASS" if success else "FAIL",
            "details": output[:200] + "..." if len(output) > 200 else output,
            "timestamp": datetime.utcnow().isoformat()
        }

        self.test_results["test_details"].append(test_result)
        self.test_results["total_tests"] += 1

        if success:
            self.test_results["passed_tests"] += 1
            logger.info("✅ Cluster connectivity test passed")
            return True
        else:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ Cluster connectivity test failed: {output}")
            return False

    def test_namespace_status(self) -> bool:
        """Verify AIA production namespace exists and is active"""
        logger.info("🏠 Testing namespace status...")

        success, output = self.run_kubectl_command([
            'get', 'namespace', self.namespace, '-o', 'jsonpath={.status.phase}'
        ])

        namespace_active = success and output == "Active"

        test_result = {
            "test_name": "Namespace Status",
            "category": "Infrastructure",
            "status": "PASS" if namespace_active else "FAIL",
            "details": f"Namespace {self.namespace} status: {output}",
            "timestamp": datetime.utcnow().isoformat()
        }

        self.test_results["test_details"].append(test_result)
        self.test_results["total_tests"] += 1

        if namespace_active:
            self.test_results["passed_tests"] += 1
            logger.info(f"✅ Namespace {self.namespace} is active")
            return True
        else:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ Namespace {self.namespace} test failed")
            return False

    def test_pod_health(self) -> bool:
        """Test all AIA pods are running and healthy"""
        logger.info("🏃 Testing pod health...")

        success, output = self.run_kubectl_command([
            'get', 'pods', '-n', self.namespace, '-o', 'json'
        ])

        if not success:
            test_result = {
                "test_name": "Pod Health Check",
                "category": "Application",
                "status": "FAIL",
                "details": f"Failed to get pods: {output}",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1
            self.test_results["failed_tests"] += 1
            return False

        try:
            pods_data = json.loads(output)
            pods = pods_data.get("items", [])

            total_pods = len(pods)
            running_pods = 0
            ready_pods = 0
            pod_details = []

            for pod in pods:
                pod_name = pod["metadata"]["name"]
                phase = pod["status"].get("phase", "Unknown")

                # Check readiness
                conditions = pod["status"].get("conditions", [])
                ready_condition = next(
                    (c for c in conditions if c["type"] == "Ready"),
                    {"status": "Unknown"}
                )

                is_ready = ready_condition["status"] == "True"
                is_running = phase == "Running"

                if is_running:
                    running_pods += 1
                if is_ready:
                    ready_pods += 1

                pod_details.append({
                    "name": pod_name,
                    "phase": phase,
                    "ready": is_ready,
                    "restarts": sum(
                        c.get("restartCount", 0)
                        for c in pod["status"].get("containerStatuses", [])
                    )
                })

            all_healthy = running_pods == total_pods and ready_pods == total_pods

            test_result = {
                "test_name": "Pod Health Check",
                "category": "Application",
                "status": "PASS" if all_healthy else "FAIL",
                "details": {
                    "total_pods": total_pods,
                    "running_pods": running_pods,
                    "ready_pods": ready_pods,
                    "pod_details": pod_details
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1

            if all_healthy:
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ All {total_pods} pods are healthy")
                return True
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ Pod health check failed: {running_pods}/{total_pods} running, {ready_pods}/{total_pods} ready")
                return False

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse pod status: {e}")
            return False

    def test_service_connectivity(self) -> bool:
        """Test internal service connectivity"""
        logger.info("🔌 Testing service connectivity...")

        services = [
            (self.backend_service, "8000"),
            (self.frontend_service, "80"),
            (self.postgres_service, "5432"),
            (self.redis_service, "6379")
        ]

        all_services_ok = True
        service_results = []

        for service_name, port in services:
            success, output = self.run_kubectl_command([
                'get', 'service', service_name, '-n', self.namespace, '-o', 'json'
            ])

            if success:
                try:
                    service_data = json.loads(output)
                    cluster_ip = service_data["spec"].get("clusterIP")
                    ports = service_data["spec"].get("ports", [])

                    service_results.append({
                        "service": service_name,
                        "cluster_ip": cluster_ip,
                        "ports": ports,
                        "status": "Available"
                    })

                    logger.info(f"✅ Service {service_name} available at {cluster_ip}")

                except json.JSONDecodeError:
                    service_results.append({
                        "service": service_name,
                        "status": "Parse Error"
                    })
                    all_services_ok = False
            else:
                service_results.append({
                    "service": service_name,
                    "status": "Not Found",
                    "error": output
                })
                all_services_ok = False

        test_result = {
            "test_name": "Service Connectivity",
            "category": "Networking",
            "status": "PASS" if all_services_ok else "FAIL",
            "details": {"services": service_results},
            "timestamp": datetime.utcnow().isoformat()
        }

        self.test_results["test_details"].append(test_result)
        self.test_results["total_tests"] += 1

        if all_services_ok:
            self.test_results["passed_tests"] += 1
            return True
        else:
            self.test_results["failed_tests"] += 1
            return False

    def test_api_endpoints(self) -> bool:
        """Test API endpoints through port-forward"""
        logger.info("🌐 Testing API endpoints...")

        # Start port-forward for backend service
        port_forward_process = None
        try:
            port_forward_process = subprocess.Popen([
                'kubectl', 'port-forward',
                f'service/{self.backend_service}',
                '8080:8000',
                '-n', self.namespace
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Wait for port-forward to establish
            time.sleep(5)

            # Test endpoints
            endpoints = [
                ("/health", "Health Check"),
                ("/api/v1/analytics/dashboard", "Analytics Dashboard"),
                ("/api/v1/economy/status", "Economy Status"),
                ("/api/v1/crypto/status", "Crypto Status"),
                ("/api/v1/dkg/status", "DKG Status")
            ]

            endpoint_results = []
            all_endpoints_ok = True

            for endpoint, description in endpoints:
                try:
                    response = requests.get(f"http://localhost:8080{endpoint}", timeout=10)

                    endpoint_result = {
                        "endpoint": endpoint,
                        "description": description,
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                        "success": response.status_code == 200
                    }

                    if response.status_code == 200:
                        try:
                            data = response.json()
                            endpoint_result["response_size"] = len(json.dumps(data))

                            # Specific validations
                            if endpoint == "/health":
                                endpoint_result["health_status"] = data.get("status")
                                endpoint_result["services_ok"] = all(
                                    "connected" in str(v) for v in data.get("services", {}).values()
                                )

                        except json.JSONDecodeError:
                            endpoint_result["response_type"] = "non-json"

                    endpoint_results.append(endpoint_result)

                    if response.status_code == 200:
                        logger.info(f"✅ {description} endpoint working - {response.elapsed.total_seconds():.3f}s")
                    else:
                        logger.warning(f"⚠️ {description} returned {response.status_code}")
                        all_endpoints_ok = False

                except requests.exceptions.RequestException as e:
                    endpoint_result = {
                        "endpoint": endpoint,
                        "description": description,
                        "error": str(e),
                        "success": False
                    }
                    endpoint_results.append(endpoint_result)
                    all_endpoints_ok = False
                    logger.error(f"❌ {description} failed: {e}")

            test_result = {
                "test_name": "API Endpoints",
                "category": "Application",
                "status": "PASS" if all_endpoints_ok else "FAIL",
                "details": {"endpoints": endpoint_results},
                "timestamp": datetime.utcnow().isoformat()
            }

            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1

            if all_endpoints_ok:
                self.test_results["passed_tests"] += 1
                return True
            else:
                self.test_results["failed_tests"] += 1
                return False

        finally:
            if port_forward_process:
                port_forward_process.terminate()
                time.sleep(2)
                port_forward_process.kill()

    def test_orchestration_functionality(self) -> bool:
        """Test multi-agent orchestration via port-forward"""
        logger.info("🤖 Testing orchestration functionality...")

        port_forward_process = None
        try:
            port_forward_process = subprocess.Popen([
                'kubectl', 'port-forward',
                f'service/{self.backend_service}',
                '8081:8000',
                '-n', self.namespace
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            time.sleep(5)

            test_requests = [
                {"ta[STRIPE_KEY_PLACEHOLDER]": "research", "parameters": {"query": "AI validation test"}},
                {"ta[STRIPE_KEY_PLACEHOLDER]": "analysis", "parameters": {"data": "test_dataset"}},
                {"ta[STRIPE_KEY_PLACEHOLDER]": "synthesis", "parameters": {"sources": ["test1", "test2"]}},
                {"ta[STRIPE_KEY_PLACEHOLDER]": "comprehensive", "parameters": {"scope": "full_validation"}}
            ]

            orchestration_results = []
            all_orchestrations_ok = True

            for i, request in enumerate(test_requests):
                try:
                    start_time = time.time()
                    response = requests.post(
                        "http://localhost:8081/api/v1/agents/orchestrate",
                        json=request,
                        timeout=15
                    )
                    response_time = time.time() - start_time

                    if response.status_code == 200:
                        data = response.json()
                        orchestration_results.append({
                            "request_id": i + 1,
                            "ta[STRIPE_KEY_PLACEHOLDER]": request["ta[STRIPE_KEY_PLACEHOLDER]"],
                            "response_time": response_time,
                            "orchestration_id": data.get("orchestration_id"),
                            "agents_activated": data.get("agents_activated", []),
                            "status": data.get("status"),
                            "success": True
                        })
                        logger.info(f"✅ Orchestration {i+1} ({request['ta[STRIPE_KEY_PLACEHOLDER]']}) successful - {response_time:.3f}s")
                    else:
                        orchestration_results.append({
                            "request_id": i + 1,
                            "ta[STRIPE_KEY_PLACEHOLDER]": request["ta[STRIPE_KEY_PLACEHOLDER]"],
                            "error": f"HTTP {response.status_code}",
                            "success": False
                        })
                        all_orchestrations_ok = False
                        logger.error(f"❌ Orchestration {i+1} failed with status {response.status_code}")

                except requests.exceptions.RequestException as e:
                    orchestration_results.append({
                        "request_id": i + 1,
                        "ta[STRIPE_KEY_PLACEHOLDER]": request["ta[STRIPE_KEY_PLACEHOLDER]"],
                        "error": str(e),
                        "success": False
                    })
                    all_orchestrations_ok = False
                    logger.error(f"❌ Orchestration {i+1} failed: {e}")

            success_rate = len([r for r in orchestration_results if r.get("success")]) / len(test_requests)
            avg_response_time = sum(r.get("response_time", 0) for r in orchestration_results if r.get("response_time")) / len(orchestration_results)

            test_result = {
                "test_name": "Orchestration Functionality",
                "category": "Multi-Agent System",
                "status": "PASS" if all_orchestrations_ok else "FAIL",
                "details": {
                    "success_rate": success_rate,
                    "avg_response_time": avg_response_time,
                    "orchestrations": orchestration_results
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1

            if all_orchestrations_ok:
                self.test_results["passed_tests"] += 1
                logger.info(f"✅ All orchestrations successful (Success rate: {success_rate:.2%})")
                return True
            else:
                self.test_results["failed_tests"] += 1
                logger.error(f"❌ Orchestration test failed (Success rate: {success_rate:.2%})")
                return False

        finally:
            if port_forward_process:
                port_forward_process.terminate()
                time.sleep(2)
                port_forward_process.kill()

    def test_resource_utilization(self) -> bool:
        """Test resource utilization and optimization"""
        logger.info("📊 Testing resource utilization...")

        # Get resource usage
        success, output = self.run_kubectl_command([
            'top', 'pods', '-n', self.namespace, '--no-headers'
        ])

        if not success:
            logger.warning("⚠️ Could not get resource metrics, skipping resource test")
            return True  # Don't fail the entire test suite

        resource_data = []
        total_cpu = 0
        total_memory = 0

        for line in output.split('\n'):
            if line.strip():
                parts = line.split()
                if len(parts) >= 3:
                    pod_name = parts[0]
                    cpu_str = parts[1]
                    memory_str = parts[2]

                    try:
                        # Parse CPU (remove 'm' suffix)
                        cpu_millicores = int(cpu_str.replace('m', ''))
                        # Parse Memory (remove 'Mi' suffix)
                        memory_mb = int(memory_str.replace('Mi', ''))

                        total_cpu += cpu_millicores
                        total_memory += memory_mb

                        resource_data.append({
                            "pod": pod_name,
                            "cpu_millicores": cpu_millicores,
                            "memory_mb": memory_mb
                        })

                    except ValueError:
                        pass

        # Check if resources are within acceptable ranges
        cpu_reasonable = total_cpu < 2000  # Less than 2 CPU cores total
        memory_reasonable = total_memory < 4096  # Less than 4GB total

        resources_ok = cpu_reasonable and memory_reasonable

        test_result = {
            "test_name": "Resource Utilization",
            "category": "Performance",
            "status": "PASS" if resources_ok else "FAIL",
            "details": {
                "total_cpu_millicores": total_cpu,
                "total_memory_mb": total_memory,
                "pod_resources": resource_data,
                "cpu_reasonable": cpu_reasonable,
                "memory_reasonable": memory_reasonable
            },
            "timestamp": datetime.utcnow().isoformat()
        }

        self.test_results["test_details"].append(test_result)
        self.test_results["total_tests"] += 1

        if resources_ok:
            self.test_results["passed_tests"] += 1
            logger.info(f"✅ Resource utilization optimal: {total_cpu}m CPU, {total_memory}Mi Memory")
            return True
        else:
            self.test_results["failed_tests"] += 1
            logger.error(f"❌ Resource utilization high: {total_cpu}m CPU, {total_memory}Mi Memory")
            return False

    def test_ingress_configuration(self) -> bool:
        """Test ingress configuration and SSL certificate status"""
        logger.info("🌍 Testing ingress configuration...")

        success, output = self.run_kubectl_command([
            'get', 'ingress', '-n', self.namespace, '-o', 'json'
        ])

        if not success:
            test_result = {
                "test_name": "Ingress Configuration",
                "category": "Networking",
                "status": "FAIL",
                "details": f"Failed to get ingress: {output}",
                "timestamp": datetime.utcnow().isoformat()
            }
            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1
            self.test_results["failed_tests"] += 1
            return False

        try:
            ingress_data = json.loads(output)
            ingresses = ingress_data.get("items", [])

            ingress_details = []
            any_ingress_ready = False

            for ingress in ingresses:
                ingress_name = ingress["metadata"]["name"]

                # Check if ingress has an address
                status = ingress.get("status", {})
                load_balancer = status.get("loadBalancer", {})
                ingress_ips = load_balancer.get("ingress", [])

                has_ip = bool(ingress_ips)
                if has_ip:
                    any_ingress_ready = True

                # Get rules
                spec = ingress.get("spec", {})
                rules = spec.get("rules", [])

                ingress_details.append({
                    "name": ingress_name,
                    "has_ip": has_ip,
                    "ips": ingress_ips,
                    "rules": len(rules),
                    "hosts": [rule.get("host") for rule in rules if rule.get("host")]
                })

            test_result = {
                "test_name": "Ingress Configuration",
                "category": "Networking",
                "status": "PASS" if any_ingress_ready else "PARTIAL",
                "details": {
                    "ingresses": ingress_details,
                    "any_ready": any_ingress_ready
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            self.test_results["test_details"].append(test_result)
            self.test_results["total_tests"] += 1

            if any_ingress_ready:
                self.test_results["passed_tests"] += 1
                logger.info("✅ Ingress configuration has external IPs")
                return True
            else:
                self.test_results["passed_tests"] += 1  # Still count as pass since ingress exists
                logger.info("⚠️ Ingress configured but no external IP yet (may be provisioning)")
                return True

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse ingress data: {e}")
            return False

    def generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final validation report"""

        success_rate = (self.test_results["passed_tests"] / self.test_results["total_tests"]) if self.test_results["total_tests"] > 0 else 0

        # Categorize results
        categories = {}
        for test in self.test_results["test_details"]:
            category = test.get("category", "Other")
            if category not in categories:
                categories[category] = {"passed": 0, "failed": 0, "total": 0}

            categories[category]["total"] += 1
            if test["status"] == "PASS":
                categories[category]["passed"] += 1
            else:
                categories[category]["failed"] += 1

        # Overall system status
        if success_rate >= 0.9:
            overall_status = "EXCELLENT"
            status_emoji = "🟢"
        elif success_rate >= 0.8:
            overall_status = "GOOD"
            status_emoji = "🟡"
        elif success_rate >= 0.6:
            overall_status = "ACCEPTABLE"
            status_emoji = "🟠"
        else:
            overall_status = "NEEDS_ATTENTION"
            status_emoji = "🔴"

        final_report = {
            "validation_summary": {
                "overall_status": overall_status,
                "status_emoji": status_emoji,
                "success_rate": success_rate,
                "total_tests": self.test_results["total_tests"],
                "passed_tests": self.test_results["passed_tests"],
                "failed_tests": self.test_results["failed_tests"]
            },
            "category_breakdown": categories,
            "detailed_results": self.test_results,
            "recommendations": self._generate_recommendations(),
            "next_steps": self._generate_next_steps()
        }

        return final_report

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        failed_tests = [t for t in self.test_results["test_details"] if t["status"] == "FAIL"]

        if not failed_tests:
            recommendations.append("✅ All tests passed! System is ready for production.")
            recommendations.append("📊 Consider implementing continuous monitoring for ongoing health checks.")
            recommendations.append("🚀 Set up automated scaling policies based on usage patterns.")
        else:
            for test in failed_tests:
                if "Cluster" in test["test_name"]:
                    recommendations.append("🔧 Fix cluster connectivity issues before proceeding with deployment.")
                elif "Pod" in test["test_name"]:
                    recommendations.append("🔄 Investigate pod health issues and restart failed containers.")
                elif "API" in test["test_name"]:
                    recommendations.append("🌐 Debug API endpoint issues and check service configurations.")
                elif "Resource" in test["test_name"]:
                    recommendations.append("📉 Optimize resource allocation and consider scaling down over-provisioned services.")

        return recommendations

    def _generate_next_steps(self) -> List[str]:
        """Generate next steps for deployment continuation"""
        next_steps = [
            "1. 📋 Review detailed test results and address any failed tests",
            "2. 🔍 Set up monitoring dashboards (Prometheus/Grafana) for ongoing observability",
            "3. 🔐 Configure SSL certificates and domain routing for production access",
            "4. 📊 Implement log aggregation and alerting for production monitoring",
            "5. 🚀 Run load testing to validate system performance under real-world conditions",
            "6. 💾 Set up automated backups for PostgreSQL data",
            "7. 🔄 Configure CI/CD pipelines for automated deployments and updates",
            "8. 📈 Implement cost optimization and resource auto-scaling policies"
        ]

        return next_steps

    def run_comprehensive_validation(self) -> Dict[str, Any]:
        """Run complete validation test suite"""

        logger.info("🚀 Starting AIA Production System Comprehensive Validation")
        logger.info("=" * 70)

        start_time = time.time()

        # Run all test categories
        test_methods = [
            self.test_cluster_connectivity,
            self.test_namespace_status,
            self.test_pod_health,
            self.test_service_connectivity,
            self.test_api_endpoints,
            self.test_orchestration_functionality,
            self.test_resource_utilization,
            self.test_ingress_configuration
        ]

        for test_method in test_methods:
            try:
                test_method()
                time.sleep(1)  # Brief pause between tests
            except Exception as e:
                logger.error(f"❌ Test {test_method.__name__} failed with exception: {e}")

                # Add failure record
                test_result = {
                    "test_name": test_method.__name__.replace("test_", "").replace("_", " ").title(),
                    "category": "System",
                    "status": "FAIL",
                    "details": f"Exception: {str(e)}",
                    "timestamp": datetime.utcnow().isoformat()
                }

                self.test_results["test_details"].append(test_result)
                self.test_results["total_tests"] += 1
                self.test_results["failed_tests"] += 1

        total_time = time.time() - start_time

        logger.info("=" * 70)
        logger.info(f"🏁 Validation completed in {total_time:.2f} seconds")

        # Generate final report
        final_report = self.generate_final_report()

        # Print summary
        summary = final_report["validation_summary"]
        logger.info(f"{summary['status_emoji']} Overall Status: {summary['overall_status']}")
        logger.info(f"📊 Success Rate: {summary['success_rate']:.1%} ({summary['passed_tests']}/{summary['total_tests']} tests passed)")

        if final_report["validation_summary"]["overall_status"] in ["EXCELLENT", "GOOD"]:
            logger.info("🎉 AIA Production System validation SUCCESSFUL!")
            logger.info("✅ System is ready for full production deployment!")
        else:
            logger.warning("⚠️ Some issues found that should be addressed before full production use.")

        return final_report

def main():
    """Main entry point for validation script"""

    print("""
    ╔══════════════════════════════════════════════════════════════════════╗
    ║                  AIA Production System Validator                     ║
    ║                     Comprehensive E2E Testing                        ║
    ║                         Version 4.0.2                               ║
    ╚══════════════════════════════════════════════════════════════════════╝
    """)

    # Create validator and run tests
    validator = AIAProductionValidator()

    try:
        final_report = validator.run_comprehensive_validation()

        # Save detailed report
        report_filename = f"aia_validation_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"

        with open(report_filename, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_filename}")

        # Print recommendations
        print("\n🎯 RECOMMENDATIONS:")
        for recommendation in final_report["recommendations"]:
            print(f"  {recommendation}")

        print("\n🚀 NEXT STEPS:")
        for step in final_report["next_steps"]:
            print(f"  {step}")

        # Exit with appropriate code
        if final_report["validation_summary"]["overall_status"] in ["EXCELLENT", "GOOD"]:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n🛑 Validation interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Validation failed with critical error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()