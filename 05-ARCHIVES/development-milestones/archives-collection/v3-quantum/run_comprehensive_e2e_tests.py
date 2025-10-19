#!/usr/bin/env python3
"""
Master Test Execution Script for AIA Production System
======================================================

This script orchestrates and executes all test suites:
1. Comprehensive API and Frontend Testing
2. Browser Automation Testing
3. Performance and Load Testing
4. Security and Penetration Testing

Generates unified reports and recommendations.
"""

import asyncio
import subprocess
import sys
import json
import logging
import time
import os
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('master_test_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MasterTestExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.results: Dict[str, Any] = {}
        self.test_scripts = [
            {
                "name": "Comprehensive E2E Tests",
                "script": "comprehensive_e2e_test_suite.py",
                "description": "API endpoints, frontend routes, health checks, CORS, SSL",
                "timeout": 300  # 5 minutes
            },
            {
                "name": "Performance Load Tests",
                "script": "performance_load_tests.py",
                "description": "Load testing, stress testing, breaking point analysis",
                "timeout": 600  # 10 minutes
            },
            {
                "name": "Security Penetration Tests",
                "script": "security_penetration_tests.py",
                "description": "Security headers, SSL, input validation, authentication",
                "timeout": 400  # 6.5 minutes
            },
            {
                "name": "Frontend Browser Tests",
                "script": "frontend_browser_tests.py",
                "description": "Cross-browser testing, 3D rendering, responsive design",
                "timeout": 500,  # 8 minutes
                "optional": True  # Skip if selenium not available
            }
        ]

    def check_dependencies(self) -> Dict[str, bool]:
        """Check if required dependencies are available"""
        dependencies = {
            "aiohttp": False,
            "psutil": False,
            "selenium": False
        }

        for dep in dependencies:
            try:
                __import__(dep)
                dependencies[dep] = True
                logger.info(f"✅ {dep} is available")
            except ImportError:
                logger.warning(f"⚠️ {dep} is not available")

        return dependencies

    async def execute_test_script(self, test_info: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test script"""
        script_name = test_info["script"]
        test_name = test_info["name"]
        timeout = test_info.get("timeout", 300)

        logger.info(f"\n🚀 Executing {test_name}...")
        logger.info(f"   Script: {script_name}")
        logger.info(f"   Description: {test_info['description']}")
        logger.info(f"   Timeout: {timeout}s")

        start_time = time.time()

        try:
            # Check if script exists
            script_path = Path(script_name)
            if not script_path.exists():
                logger.error(f"❌ Script not found: {script_name}")
                return {
                    "test_name": test_name,
                    "status": "FAILED",
                    "error": f"Script not found: {script_name}",
                    "duration": 0
                }

            # Execute the script
            process = await asyncio.create_subprocess_exec(
                sys.executable, script_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout
                )

                duration = time.time() - start_time

                if process.returncode == 0:
                    logger.info(f"✅ {test_name} completed successfully ({duration:.1f}s)")

                    # Try to find and load the results file
                    results_pattern = test_name.lower().replace(" ", "_").replace("&", "")
                    result_files = list(Path(".").glob(f"*{results_pattern}*results*.json"))

                    results_data = {}
                    if result_files:
                        try:
                            with open(result_files[-1]) as f:  # Use most recent
                                results_data = json.load(f)
                        except Exception as e:
                            logger.warning(f"Could not load results file: {e}")

                    return {
                        "test_name": test_name,
                        "script": script_name,
                        "status": "COMPLETED",
                        "duration": duration,
                        "results_data": results_data,
                        "stdout": stdout.decode('utf-8')[-1000:],  # Last 1000 chars
                        "stderr": stderr.decode('utf-8') if stderr else ""
                    }
                else:
                    logger.error(f"❌ {test_name} failed with return code {process.returncode}")
                    return {
                        "test_name": test_name,
                        "script": script_name,
                        "status": "FAILED",
                        "duration": duration,
                        "return_code": process.returncode,
                        "stdout": stdout.decode('utf-8')[-1000:],
                        "stderr": stderr.decode('utf-8') if stderr else ""
                    }

            except asyncio.TimeoutError:
                logger.error(f"❌ {test_name} timed out after {timeout}s")
                process.kill()
                await process.wait()

                return {
                    "test_name": test_name,
                    "script": script_name,
                    "status": "TIMEOUT",
                    "duration": timeout,
                    "error": f"Test timed out after {timeout}s"
                }

        except Exception as e:
            logger.error(f"❌ {test_name} execution failed: {e}")
            return {
                "test_name": test_name,
                "script": script_name,
                "status": "ERROR",
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute all test suites"""
        logger.info("🎯 Starting Master Test Execution for AIA Production System")
        logger.info("="*80)

        # Check dependencies
        dependencies = self.check_dependencies()

        test_results = []

        for test_info in self.test_scripts:
            # Skip optional tests if dependencies not available
            if test_info.get("optional") and not dependencies.get("selenium", False):
                logger.info(f"⏭️ Skipping {test_info['name']} (optional dependency missing)")
                continue

            result = await self.execute_test_script(test_info)
            test_results.append(result)

        # Generate unified summary
        total_duration = (datetime.now() - self.start_time).total_seconds()

        completed_tests = len([r for r in test_results if r["status"] == "COMPLETED"])
        failed_tests = len([r for r in test_results if r["status"] in ["FAILED", "ERROR", "TIMEOUT"]])

        # Extract key metrics from individual test results
        performance_metrics = {}
        security_metrics = {}
        frontend_metrics = {}
        api_metrics = {}

        for result in test_results:
            if result["status"] == "COMPLETED" and result.get("results_data"):
                data = result["results_data"]

                # Extract performance metrics
                if "performance_summary" in data:
                    performance_metrics = data["performance_summary"]

                # Extract security metrics
                if "security_summary" in data:
                    security_metrics = data["security_summary"]

                # Extract frontend metrics
                if "frontend_test_summary" in data:
                    frontend_metrics = data["frontend_test_summary"]

                # Extract API test metrics
                if "test_summary" in data:
                    api_metrics = data["test_summary"]

        # Calculate overall system health score
        health_score = 100

        # Deduct for failed tests
        health_score -= (failed_tests * 15)

        # Deduct for performance issues
        if performance_metrics.get("overall_avg_response_time_ms", 0) > 2000:
            health_score -= 10

        # Deduct for security issues
        critical_vulns = security_metrics.get("critical_vulnerabilities", 0)
        high_vulns = security_metrics.get("high_vulnerabilities", 0)
        health_score -= (critical_vulns * 20) + (high_vulns * 10)

        health_score = max(0, health_score)

        # Determine overall system status
        if health_score >= 90:
            system_status = "EXCELLENT"
            status_icon = "🟢"
        elif health_score >= 80:
            system_status = "GOOD"
            status_icon = "🟡"
        elif health_score >= 70:
            system_status = "ACCEPTABLE"
            status_icon = "🟠"
        else:
            system_status = "NEEDS_ATTENTION"
            status_icon = "🔴"

        unified_results = {
            "master_test_summary": {
                "total_test_suites": len(self.test_scripts),
                "executed_test_suites": len(test_results),
                "completed_successfully": completed_tests,
                "failed_or_timeout": failed_tests,
                "total_duration_seconds": total_duration,
                "overall_health_score": health_score,
                "system_status": system_status,
                "status_icon": status_icon,
                "test_timestamp": self.start_time.isoformat(),
                "dependencies_available": dependencies
            },
            "performance_summary": performance_metrics,
            "security_summary": security_metrics,
            "frontend_summary": frontend_metrics,
            "api_summary": api_metrics,
            "individual_test_results": test_results,
            "system_recommendations": self.generate_recommendations(
                test_results, performance_metrics, security_metrics, health_score
            ),
            "production_readiness": self.assess_production_readiness(
                health_score, security_metrics, performance_metrics
            )
        }

        return unified_results

    def generate_recommendations(
        self,
        test_results: List[Dict],
        performance_metrics: Dict,
        security_metrics: Dict,
        health_score: float
    ) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        # Failed test recommendations
        failed_tests = [r for r in test_results if r["status"] != "COMPLETED"]
        if failed_tests:
            recommendations.append(
                f"🚨 CRITICAL: {len(failed_tests)} test suite(s) failed - investigate immediately"
            )

        # Performance recommendations
        if performance_metrics:
            avg_response = performance_metrics.get("overall_avg_response_time_ms", 0)
            if avg_response > 3000:
                recommendations.append("🐌 HIGH: Optimize response times (currently >3s average)")
            elif avg_response > 1500:
                recommendations.append("⚡ MEDIUM: Consider response time optimization")

            error_rate = performance_metrics.get("overall_avg_error_rate_percent", 0)
            if error_rate > 5:
                recommendations.append("❌ HIGH: Reduce error rate (currently >5%)")

        # Security recommendations
        if security_metrics:
            critical_vulns = security_metrics.get("critical_vulnerabilities", 0)
            high_vulns = security_metrics.get("high_vulnerabilities", 0)

            if critical_vulns > 0:
                recommendations.append(f"🚨 CRITICAL: Fix {critical_vulns} critical security vulnerabilities immediately")

            if high_vulns > 0:
                recommendations.append(f"🔒 HIGH: Address {high_vulns} high-severity security issues")

        # Overall health recommendations
        if health_score < 70:
            recommendations.append("🏥 CRITICAL: Overall system health needs immediate attention")
        elif health_score < 85:
            recommendations.append("💊 MEDIUM: Monitor system health and address issues")

        if not recommendations:
            recommendations.append("✅ EXCELLENT: System is performing well across all test categories")

        return recommendations

    def assess_production_readiness(
        self,
        health_score: float,
        security_metrics: Dict,
        performance_metrics: Dict
    ) -> Dict[str, Any]:
        """Assess production readiness"""

        readiness_score = health_score
        blockers = []

        # Security blockers
        critical_vulns = security_metrics.get("critical_vulnerabilities", 0)
        if critical_vulns > 0:
            blockers.append(f"{critical_vulns} critical security vulnerabilities")
            readiness_score -= 30

        # Performance blockers
        avg_response = performance_metrics.get("overall_avg_response_time_ms", 0)
        if avg_response > 5000:
            blockers.append("Response times exceed 5 seconds")
            readiness_score -= 20

        error_rate = performance_metrics.get("overall_avg_error_rate_percent", 0)
        if error_rate > 10:
            blockers.append("Error rate exceeds 10%")
            readiness_score -= 20

        readiness_score = max(0, readiness_score)

        # Determine readiness status
        if readiness_score >= 85 and not blockers:
            status = "READY"
            recommendation = "✅ System is ready for production"
        elif readiness_score >= 70:
            status = "READY_WITH_MONITORING"
            recommendation = "⚠️ Ready for production with enhanced monitoring"
        elif readiness_score >= 50:
            status = "NEEDS_IMPROVEMENTS"
            recommendation = "🔧 Address issues before production deployment"
        else:
            status = "NOT_READY"
            recommendation = "🚨 Critical issues must be resolved before production"

        return {
            "readiness_score": readiness_score,
            "status": status,
            "blockers": blockers,
            "recommendation": recommendation,
            "assessment_timestamp": datetime.now().isoformat()
        }

async def main():
    """Main execution function"""
    try:
        executor = MasterTestExecutor()
        results = await executor.run_all_tests()

        # Save unified results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"aia_comprehensive_test_report_{timestamp}.json"

        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        # Print executive summary
        summary = results["master_test_summary"]
        logger.info(f"\n" + "="*80)
        logger.info(f"🎯 AIA PRODUCTION SYSTEM - COMPREHENSIVE TEST REPORT")
        logger.info(f"="*80)
        logger.info(f"{summary['status_icon']} System Status: {summary['system_status']}")
        logger.info(f"🏥 Health Score: {summary['overall_health_score']}/100")
        logger.info(f"📊 Test Suites: {summary['executed_test_suites']}/{summary['total_test_suites']}")
        logger.info(f"✅ Completed: {summary['completed_successfully']}")
        logger.info(f"❌ Failed: {summary['failed_or_timeout']}")
        logger.info(f"⏱️ Total Duration: {summary['total_duration_seconds']:.1f}s")
        logger.info(f"="*80)

        # Show production readiness
        readiness = results["production_readiness"]
        logger.info(f"\n🚀 PRODUCTION READINESS ASSESSMENT:")
        logger.info(f"📈 Readiness Score: {readiness['readiness_score']}/100")
        logger.info(f"🎯 Status: {readiness['status']}")
        logger.info(f"💡 {readiness['recommendation']}")

        if readiness["blockers"]:
            logger.warning(f"\n🚨 PRODUCTION BLOCKERS:")
            for blocker in readiness["blockers"]:
                logger.warning(f"  • {blocker}")

        # Show recommendations
        logger.info(f"\n💡 SYSTEM RECOMMENDATIONS:")
        for rec in results["system_recommendations"]:
            logger.info(f"  {rec}")

        logger.info(f"\n💾 Complete report saved to: {results_file}")

        return results

    except Exception as e:
        logger.error(f"❌ Master test execution failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

if __name__ == "__main__":
    asyncio.run(main())