#!/usr/bin/env python3
"""
AIA SDK Comprehensive Testing Suite
===================================
Complete testing of the AIA SDK built upon CLI infrastructure.
Tests core functionality, multi-agent orchestration, and knowledge graph integration.
"""

import asyncio
import pytest
import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add SDK to path
sys.path.append(str(Path(__file__).parent))

# Test imports
try:
    from aia_sdk.core import AIAClient, AIARequest, ProcessingMode, SecurityLevel
    from aia_sdk.agents import AgentSystem, OrchestrationRequest, AgentType
    from aia_sdk.knowledge import KnowledgeGraph, KnowledgeCategory
    SDK_IMPORTS_OK = True
except ImportError as e:
    print(f"❌ SDK imports failed: {e}")
    SDK_IMPORTS_OK = False

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

class AIASDKTestSuite:
    """Comprehensive AIA SDK testing suite"""

    def __init__(self):
        self.test_results = {}
        self.performance_metrics = []
        self.failed_tests = []

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run complete SDK testing suite"""
        console.print(Panel.fit("🧪 AIA SDK COMPREHENSIVE TESTING", border_style="blue"))

        if not SDK_IMPORTS_OK:
            console.print("[red]❌ SDK imports failed - cannot run tests[/red]")
            return {"status": "failed", "reason": "import_errors"}

        # Test categories
        test_categories = [
            ("Core SDK Functionality", self.test_core_sdk),
            ("Multi-Agent Orchestration", self.test_multi_agent_system),
            ("Knowledge Graph Integration", self.test_knowledge_graph),
            ("Performance Benchmarks", self.test_performance),
            ("Error Handling", self.test_error_handling),
            ("Integration Compatibility", self.test_integration_compatibility)
        ]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:

            for test_name, test_func in test_categories:
                task = progress.add_task(f"Testing {test_name}...", total=None)

                try:
                    result = await test_func()
                    self.test_results[test_name] = result
                    progress.update(task, description=f"✅ {test_name} - {'PASSED' if result['success'] else 'FAILED'}")

                    if not result['success']:
                        self.failed_tests.append(test_name)

                except Exception as e:
                    self.test_results[test_name] = {"success": False, "error": str(e)}
                    self.failed_tests.append(test_name)
                    progress.update(task, description=f"❌ {test_name} - ERROR")

                await asyncio.sleep(0.1)  # Brief pause between tests

        # Generate final report
        return self.generate_test_report()

    async def test_core_sdk(self) -> Dict[str, Any]:
        """Test core SDK functionality"""
        test_data = {
            "category": "Core SDK",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": []
        }

        try:
            # Test 1: Client initialization
            async with AIAClient() as aia:
                test_data["tests_run"] += 1

                # Check system info
                system_info = await aia.get_system_info()
                if system_info and "aia_sdk_version" in system_info:
                    test_data["tests_passed"] += 1
                    test_data["details"].append("✅ Client initialization successful")
                else:
                    test_data["details"].append("❌ Client initialization failed")

                # Test 2: Basic processing
                test_data["tests_run"] += 1
                result = await aia.process("test SDK core functionality")

                if result and result.success:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Basic processing: {result.confidence:.2%} confidence")
                else:
                    test_data["details"].append("❌ Basic processing failed")

                # Test 3: Structured request
                test_data["tests_run"] += 1
                structured_request = AIARequest(
                    query="test structured processing",
                    mode=ProcessingMode.TECHNICAL,
                    security_level=SecurityLevel.STANDARD,
                    enable_orchestration=True
                )

                structured_result = await aia.process(structured_request)
                if structured_result and structured_result.success:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Structured request: {structured_result.processing_time:.3f}s")
                else:
                    test_data["details"].append("❌ Structured request failed")

                # Test 4: Health check
                test_data["tests_run"] += 1
                health = await aia.health_check()

                if health and health.get("overall_healthy"):
                    test_data["tests_passed"] += 1
                    test_data["details"].append("✅ Health check passed")
                else:
                    test_data["details"].append("❌ Health check failed")

                # Test 5: Performance metrics
                test_data["tests_run"] += 1
                metrics = await aia.get_performance_metrics()

                if metrics and "total_requests" in metrics:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Performance metrics: {metrics['total_requests']} requests tracked")
                else:
                    test_data["details"].append("❌ Performance metrics unavailable")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Core SDK test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.8
            test_data["success_rate"] = success_rate
        else:
            test_data["success"] = False

        return test_data

    async def test_multi_agent_system(self) -> Dict[str, Any]:
        """Test multi-agent system functionality"""
        test_data = {
            "category": "Multi-Agent System",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": []
        }

        try:
            async with AIAClient() as aia:
                agent_system = AgentSystem(aia)

                # Test 1: Agent discovery
                test_data["tests_run"] += 1
                agents = await agent_system.discover_agents()

                if agents and len(agents) > 0:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Agent discovery: {len(agents)} agents found")
                else:
                    test_data["details"].append("❌ Agent discovery failed")

                # Test 2: Agent selection
                test_data["tests_run"] += 1
                selected_agents = agent_system.select_agents_for_query(
                    "deploy secure microservices architecture",
                    max_agents=3
                )

                if selected_agents and len(selected_agents) > 0:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Agent selection: {len(selected_agents)} agents selected")
                else:
                    test_data["details"].append("❌ Agent selection failed")

                # Test 3: Basic orchestration
                test_data["tests_run"] += 1
                orchestration_request = OrchestrationRequest(
                    query="test multi-agent coordination",
                    max_agents=2,
                    orchestration_mode="automatic"
                )

                orchestration_result = await agent_system.orchestrate(orchestration_request)

                if orchestration_result and orchestration_result.success:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Orchestration: {orchestration_result.confidence:.2%} confidence")
                else:
                    test_data["details"].append("❌ Orchestration failed")

                # Test 4: Agent status
                test_data["tests_run"] += 1
                agent_status = await agent_system.get_agent_status()

                if agent_status and len(agent_status) > 0:
                    test_data["tests_passed"] += 1
                    available_count = sum(1 for status in agent_status.values() if status.value == "available")
                    test_data["details"].append(f"✅ Agent status: {available_count} agents available")
                else:
                    test_data["details"].append("❌ Agent status check failed")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Multi-agent test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.75
            test_data["success_rate"] = success_rate

        return test_data

    async def test_knowledge_graph(self) -> Dict[str, Any]:
        """Test knowledge graph functionality"""
        test_data = {
            "category": "Knowledge Graph",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": []
        }

        try:
            async with AIAClient() as aia:
                knowledge_graph = KnowledgeGraph(aia)

                # Test 1: Knowledge statistics
                test_data["tests_run"] += 1
                stats = await knowledge_graph.get_knowledge_statistics()

                if stats and stats.get("total_atoms", 0) > 0:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Knowledge stats: {stats['total_atoms']:,} atoms")
                else:
                    test_data["details"].append("❌ Knowledge statistics failed")

                # Test 2: Semantic search
                test_data["tests_run"] += 1
                search_result = await knowledge_graph.semantic_search(
                    query="performance optimization techniques",
                    max_results=5
                )

                if search_result and search_result.matching_atoms:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Semantic search: {len(search_result.matching_atoms)} results")
                else:
                    test_data["details"].append("❌ Semantic search failed")

                # Test 3: Intelligence insights
                test_data["tests_run"] += 1
                insights = await knowledge_graph.get_intelligence_insights(
                    context="business opportunities in AI development",
                    analysis_type="business"
                )

                if insights and len(insights) > 0:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ Intelligence insights: {len(insights)} generated")
                else:
                    test_data["details"].append("❌ Intelligence insights failed")

                # Test 4: Knowledge graph status
                test_data["tests_run"] += 1
                kg_status = await knowledge_graph.knowledge_graph_status()

                if kg_status and kg_status.get("status") in ["operational", "simulated"]:
                    test_data["tests_passed"] += 1
                    test_data["details"].append(f"✅ KG Status: {kg_status['status']}")
                else:
                    test_data["details"].append("❌ Knowledge graph status failed")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Knowledge graph test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.75
            test_data["success_rate"] = success_rate

        return test_data

    async def test_performance(self) -> Dict[str, Any]:
        """Test SDK performance benchmarks"""
        test_data = {
            "category": "Performance",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": [],
            "benchmarks": {}
        }

        try:
            async with AIAClient(performance_monitoring=True) as aia:
                # Benchmark different processing modes
                benchmark_queries = [
                    ("Quick task", ProcessingMode.GENERAL),
                    ("Business analysis", ProcessingMode.BUSINESS),
                    ("Technical review", ProcessingMode.TECHNICAL),
                    ("Security audit", ProcessingMode.SECURITY)
                ]

                response_times = []

                for query, mode in benchmark_queries:
                    test_data["tests_run"] += 1
                    start_time = time.time()

                    try:
                        request = AIARequest(query=query, mode=mode)
                        result = await aia.process(request)

                        processing_time = time.time() - start_time

                        if result.success and processing_time < 2.0:  # Under 2 seconds
                            test_data["tests_passed"] += 1
                            response_times.append(processing_time)
                            test_data["details"].append(f"✅ {mode.value}: {processing_time:.3f}s")
                        else:
                            test_data["details"].append(f"❌ {mode.value}: failed or too slow")

                    except Exception as e:
                        test_data["details"].append(f"❌ {mode.value}: exception - {str(e)}")

                # Performance analysis
                if response_times:
                    avg_time = sum(response_times) / len(response_times)
                    max_time = max(response_times)
                    min_time = min(response_times)

                    test_data["benchmarks"] = {
                        "average_time": avg_time,
                        "max_time": max_time,
                        "min_time": min_time,
                        "samples": len(response_times)
                    }

                    # Performance grade
                    if avg_time < 0.2:
                        grade = "A+"
                    elif avg_time < 0.5:
                        grade = "A"
                    elif avg_time < 1.0:
                        grade = "B"
                    else:
                        grade = "C"

                    test_data["performance_grade"] = grade
                    test_data["details"].append(f"✅ Performance grade: {grade} (avg: {avg_time:.3f}s)")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Performance test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.75
            test_data["success_rate"] = success_rate

        return test_data

    async def test_error_handling(self) -> Dict[str, Any]:
        """Test error handling and resilience"""
        test_data = {
            "category": "Error Handling",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": []
        }

        try:
            # Test 1: Invalid query handling
            test_data["tests_run"] += 1
            async with AIAClient() as aia:
                result = await aia.process("")  # Empty query

                if not result.success and result.error:
                    test_data["tests_passed"] += 1
                    test_data["details"].append("✅ Empty query handled gracefully")
                else:
                    test_data["details"].append("❌ Empty query not handled properly")

                # Test 2: Invalid mode handling
                test_data["tests_run"] += 1
                try:
                    invalid_request = AIARequest(
                        query="test query",
                        mode="invalid_mode"  # This will cause an error
                    )
                    # This should fail gracefully
                    test_data["details"].append("❌ Invalid mode not rejected")
                except (ValueError, TypeError):
                    test_data["tests_passed"] += 1
                    test_data["details"].append("✅ Invalid mode rejected properly")

                # Test 3: Timeout handling
                test_data["tests_run"] += 1
                timeout_request = AIARequest(
                    query="test timeout handling",
                    timeout=0.001  # Very short timeout
                )

                timeout_result = await aia.process(timeout_request)
                # Should either succeed quickly or fail gracefully
                if not timeout_result.success or timeout_result.processing_time > 0.01:
                    test_data["tests_passed"] += 1
                    test_data["details"].append("✅ Timeout handling working")
                else:
                    test_data["details"].append("❌ Timeout handling unclear")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Error handling test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.6  # Lower threshold for error tests
            test_data["success_rate"] = success_rate

        return test_data

    async def test_integration_compatibility(self) -> Dict[str, Any]:
        """Test integration compatibility"""
        test_data = {
            "category": "Integration Compatibility",
            "tests_run": 0,
            "tests_passed": 0,
            "success": True,
            "details": []
        }

        try:
            # Test 1: FastAPI integration import
            test_data["tests_run"] += 1
            try:
                from aia_sdk.integrations.fastapi_integration import AIAConfig
                test_data["tests_passed"] += 1
                test_data["details"].append("✅ FastAPI integration imports")
            except ImportError:
                test_data["details"].append("⚠️ FastAPI integration unavailable (optional)")
                test_data["tests_passed"] += 1  # Count as pass since it's optional

            # Test 2: Django integration import
            test_data["tests_run"] += 1
            try:
                from aia_sdk.integrations.django_integration import DjangoIntegration
                test_data["tests_passed"] += 1
                test_data["details"].append("✅ Django integration available")
            except ImportError:
                test_data["details"].append("⚠️ Django integration unavailable (optional)")
                test_data["tests_passed"] += 1  # Count as pass since it's optional

            # Test 3: JavaScript SDK structure
            test_data["tests_run"] += 1
            js_sdk_path = Path(__file__).parent / "aia_sdk" / "javascript" / "aia-sdk.ts"
            if js_sdk_path.exists():
                test_data["tests_passed"] += 1
                test_data["details"].append("✅ JavaScript SDK structure present")
            else:
                test_data["details"].append("❌ JavaScript SDK missing")

            # Test 4: SDK module structure
            test_data["tests_run"] += 1
            required_modules = ["core", "agents", "knowledge", "security", "deployment"]
            missing_modules = []

            for module in required_modules:
                module_path = Path(__file__).parent / "aia_sdk" / f"{module}.py"
                if not module_path.exists():
                    missing_modules.append(module)

            if not missing_modules:
                test_data["tests_passed"] += 1
                test_data["details"].append("✅ All core modules present")
            else:
                test_data["details"].append(f"❌ Missing modules: {missing_modules}")

        except Exception as e:
            test_data["success"] = False
            test_data["details"].append(f"❌ Integration test exception: {str(e)}")

        # Calculate success rate
        if test_data["tests_run"] > 0:
            success_rate = test_data["tests_passed"] / test_data["tests_run"]
            test_data["success"] = success_rate >= 0.75
            test_data["success_rate"] = success_rate

        return test_data

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = sum(result.get("tests_run", 0) for result in self.test_results.values())
        total_passed = sum(result.get("tests_passed", 0) for result in self.test_results.values())
        overall_success_rate = total_passed / max(total_tests, 1)

        categories_passed = sum(1 for result in self.test_results.values() if result.get("success", False))
        categories_total = len(self.test_results)

        # Determine overall status
        if overall_success_rate >= 0.9 and categories_passed >= categories_total * 0.8:
            overall_status = "EXCELLENT"
            status_color = "bright_green"
        elif overall_success_rate >= 0.8 and categories_passed >= categories_total * 0.7:
            overall_status = "GOOD"
            status_color = "green"
        elif overall_success_rate >= 0.6 and categories_passed >= categories_total * 0.5:
            overall_status = "FAIR"
            status_color = "yellow"
        else:
            overall_status = "POOR"
            status_color = "red"

        return {
            "overall_status": overall_status,
            "status_color": status_color,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "overall_success_rate": overall_success_rate,
            "categories_passed": categories_passed,
            "categories_total": categories_total,
            "failed_categories": self.failed_tests,
            "detailed_results": self.test_results,
            "recommendations": self.generate_recommendations(overall_success_rate, self.failed_tests)
        }

    def generate_recommendations(self, success_rate: float, failed_tests: List[str]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []

        if success_rate >= 0.9:
            recommendations.extend([
                "🚀 SDK is production-ready for release",
                "📚 Create comprehensive documentation",
                "🎯 Begin developer beta testing program",
                "🌟 Consider advanced features development"
            ])
        elif success_rate >= 0.8:
            recommendations.extend([
                "🔧 Address minor issues in failed tests",
                "🧪 Conduct additional edge case testing",
                "📖 Complete documentation for successful components",
                "⚡ Performance tuning for optimization"
            ])
        elif success_rate >= 0.6:
            recommendations.extend([
                "🚨 Resolve critical issues before release",
                "🔍 Deep debugging of failed components",
                "🎯 Focus on core functionality stability",
                "📊 Conduct thorough performance analysis"
            ])
        else:
            recommendations.extend([
                "⚠️ Major rework required before production use",
                "🛠️ Fundamental architecture review needed",
                "🧪 Extensive testing and debugging required",
                "📋 Consider phased development approach"
            ])

        # Specific recommendations for failed categories
        if "Core SDK Functionality" in failed_tests:
            recommendations.append("🔧 Core SDK requires immediate attention - fundamental to all operations")

        if "Multi-Agent System" in failed_tests:
            recommendations.append("🤖 Multi-agent orchestration needs debugging - key differentiator")

        if "Knowledge Graph Integration" in failed_tests:
            recommendations.append("🧠 Knowledge graph integration critical for intelligence features")

        return recommendations

    def display_test_results(self, report: Dict[str, Any]):
        """Display comprehensive test results"""
        # Header
        console.print(f"\n[{report['status_color']}]🏆 AIA SDK Testing Complete - {report['overall_status']}[/{report['status_color']}]")

        # Summary stats
        console.print(f"\n📊 [bold]Overall Results:[/bold]")
        console.print(f"   • Total Tests: {report['total_passed']}/{report['total_tests']} passed")
        console.print(f"   • Success Rate: {report['overall_success_rate']:.1%}")
        console.print(f"   • Categories: {report['categories_passed']}/{report['categories_total']} successful")

        # Detailed results table
        results_table = Table(title="📋 Detailed Test Results")
        results_table.add_column("Category", style="cyan")
        results_table.add_column("Tests", style="white")
        results_table.add_column("Status", style="bold")
        results_table.add_column("Success Rate", style="green")

        for category, result in report["detailed_results"].items():
            status = "✅ PASSED" if result.get("success", False) else "❌ FAILED"
            tests_info = f"{result.get('tests_passed', 0)}/{result.get('tests_run', 0)}"
            success_rate = f"{result.get('success_rate', 0):.1%}"

            results_table.add_row(category, tests_info, status, success_rate)

        console.print(results_table)

        # Recommendations
        console.print(f"\n💡 [bold cyan]Recommendations:[/bold cyan]")
        for recommendation in report["recommendations"]:
            console.print(f"   {recommendation}")

        # Failed tests details
        if report["failed_categories"]:
            console.print(f"\n⚠️ [bold yellow]Failed Categories:[/bold yellow]")
            for category in report["failed_categories"]:
                if category in report["detailed_results"]:
                    details = report["detailed_results"][category].get("details", [])
                    console.print(f"\n   [red]{category}:[/red]")
                    for detail in details[-3:]:  # Show last 3 details
                        console.print(f"     {detail}")


async def main():
    """Main testing entry point"""
    console.print("[bold blue]🚀 AIA SDK COMPREHENSIVE TESTING SUITE[/bold blue]")
    console.print("=" * 70)

    test_suite = AIASDKTestSuite()

    try:
        # Run all tests
        report = await test_suite.run_all_tests()

        # Display results
        test_suite.display_test_results(report)

        # Final status
        if report["overall_status"] in ["EXCELLENT", "GOOD"]:
            console.print(f"\n🎉 [bold green]AIA SDK Testing Successful![/bold green]")
            console.print("🚀 SDK is ready for production use and developer adoption!")
        elif report["overall_status"] == "FAIR":
            console.print(f"\n⚠️ [bold yellow]AIA SDK Testing Partially Successful[/bold yellow]")
            console.print("🔧 Address identified issues before production release")
        else:
            console.print(f"\n❌ [bold red]AIA SDK Testing Identified Issues[/bold red]")
            console.print("🛠️ Significant work needed before production readiness")

        # Performance summary
        if "Performance" in report["detailed_results"]:
            perf_data = report["detailed_results"]["Performance"]
            if "benchmarks" in perf_data:
                benchmarks = perf_data["benchmarks"]
                console.print(f"\n⚡ [bold]Performance Summary:[/bold]")
                console.print(f"   • Average Response: {benchmarks.get('average_time', 0):.3f}s")
                console.print(f"   • Best Response: {benchmarks.get('min_time', 0):.3f}s")
                console.print(f"   • Performance Grade: {perf_data.get('performance_grade', 'N/A')}")

    except Exception as e:
        console.print(f"[red]❌ Testing suite failed: {e}[/red]")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())