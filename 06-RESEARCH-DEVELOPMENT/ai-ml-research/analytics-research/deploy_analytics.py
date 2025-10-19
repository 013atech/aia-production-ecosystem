#!/usr/bin/env python3
"""
🚀 ANALYTICS DEPLOYMENT SCRIPT
=============================
Comprehensive deployment system for institutional-grade analytics

This script handles the complete deployment of the AIA Analytics Platform
including all dependencies, system checks, and service startup.

Features:
- Automated dependency installation
- System compatibility checks
- Service health verification
- Multi-service orchestration
- Production deployment configuration
- Comprehensive logging and error handling
"""

import os
import sys
import subprocess
import json
import time
import logging
import argparse
import multiprocessing
from pathlib import Path
from typing import Dict, List, Any, Optional
import concurrent.futures

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
)
logger = logging.getLogger('AnalyticsDeployer')

class SystemChecker:
    """System compatibility and requirements checker"""

    def __init__(self):
        self.logger = logger.getChild('SystemChecker')

    def check_python_version(self) -> bool:
        """Check Python version compatibility"""
        min_version = (3, 8)
        current_version = sys.version_info[:2]

        if current_version >= min_version:
            self.logger.info(f"✅ Python {current_version[0]}.{current_version[1]} is compatible")
            return True
        else:
            self.logger.error(f"❌ Python {current_version[0]}.{current_version[1]} is not supported. Minimum: {min_version[0]}.{min_version[1]}")
            return False

    def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources"""
        try:
            import psutil

            cpu_count = multiprocessing.cpu_count()
            memory_gb = psutil.virtual_memory().total / (1024**3)
            disk_gb = psutil.disk_usage('.').free / (1024**3)

            resources = {
                'cpu_cores': cpu_count,
                'memory_gb': memory_gb,
                'disk_free_gb': disk_gb,
                'sufficient': True
            }

            # Check minimum requirements
            if cpu_count < 2:
                resources['sufficient'] = False
                self.logger.warning(f"⚠️ Only {cpu_count} CPU cores available (recommended: 4+)")

            if memory_gb < 4:
                resources['sufficient'] = False
                self.logger.warning(f"⚠️ Only {memory_gb:.1f}GB RAM available (recommended: 8GB+)")

            if disk_gb < 2:
                resources['sufficient'] = False
                self.logger.warning(f"⚠️ Only {disk_gb:.1f}GB disk space available (recommended: 5GB+)")

            if resources['sufficient']:
                self.logger.info(f"✅ System resources adequate: {cpu_count} cores, {memory_gb:.1f}GB RAM, {disk_gb:.1f}GB free")

            return resources

        except ImportError:
            self.logger.warning("⚠️ psutil not available, skipping detailed resource check")
            return {'sufficient': True}

    def check_port_availability(self, ports: List[int]) -> Dict[int, bool]:
        """Check if required ports are available"""
        import socket

        port_status = {}

        for port in ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(('localhost', port))
                    port_status[port] = True
                    self.logger.info(f"✅ Port {port} is available")
            except OSError:
                port_status[port] = False
                self.logger.warning(f"⚠️ Port {port} is already in use")

        return port_status

class DependencyManager:
    """Manages Python dependencies and system requirements"""

    def __init__(self):
        self.logger = logger.getChild('DependencyManager')

    def install_requirements(self, requirements_file: str) -> bool:
        """Install Python requirements"""
        try:
            self.logger.info(f"📦 Installing requirements from {requirements_file}")

            cmd = [sys.executable, '-m', 'pip', 'install', '-r', requirements_file]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                self.logger.info("✅ Requirements installed successfully")
                return True
            else:
                self.logger.error(f"❌ Failed to install requirements: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            self.logger.error("❌ Requirements installation timed out")
            return False
        except Exception as e:
            self.logger.error(f"❌ Requirements installation failed: {e}")
            return False

    def check_critical_imports(self) -> Dict[str, bool]:
        """Check if critical packages can be imported"""
        critical_packages = [
            'numpy', 'pandas', 'scipy', 'sklearn', 'plotly',
            'dash', 'flask', 'redis', 'requests'
        ]

        import_status = {}

        for package in critical_packages:
            try:
                __import__(package)
                import_status[package] = True
                self.logger.info(f"✅ {package} imported successfully")
            except ImportError as e:
                import_status[package] = False
                self.logger.error(f"❌ Failed to import {package}: {e}")

        return import_status

class ServiceManager:
    """Manages analytics services startup and health checking"""

    def __init__(self):
        self.logger = logger.getChild('ServiceManager')
        self.services = {}

    def start_service(self, service_name: str, command: List[str], cwd: Optional[str] = None) -> bool:
        """Start a service process"""
        try:
            self.logger.info(f"🚀 Starting service: {service_name}")

            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            self.services[service_name] = {
                'process': process,
                'command': command,
                'started_at': time.time()
            }

            # Give service time to start
            time.sleep(2)

            if process.poll() is None:
                self.logger.info(f"✅ Service {service_name} started successfully (PID: {process.pid})")
                return True
            else:
                stdout, stderr = process.communicate()
                self.logger.error(f"❌ Service {service_name} failed to start: {stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Failed to start service {service_name}: {e}")
            return False

    def check_service_health(self, service_name: str, health_url: str) -> bool:
        """Check service health via HTTP endpoint"""
        try:
            import requests
            response = requests.get(health_url, timeout=10)
            if response.status_code == 200:
                self.logger.info(f"✅ Service {service_name} health check passed")
                return True
            else:
                self.logger.warning(f"⚠️ Service {service_name} health check failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.warning(f"⚠️ Service {service_name} health check failed: {e}")
            return False

    def stop_all_services(self):
        """Stop all managed services"""
        for service_name, service_info in self.services.items():
            try:
                process = service_info['process']
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=10)
                    self.logger.info(f"🛑 Stopped service: {service_name}")
            except Exception as e:
                self.logger.error(f"❌ Failed to stop service {service_name}: {e}")

class AnalyticsDeployer:
    """Main deployment orchestrator"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger.getChild('AnalyticsDeployer')

        self.system_checker = SystemChecker()
        self.dependency_manager = DependencyManager()
        self.service_manager = ServiceManager()

    def validate_environment(self) -> bool:
        """Comprehensive environment validation"""
        self.logger.info("🔍 Validating deployment environment...")

        # Check Python version
        if not self.system_checker.check_python_version():
            return False

        # Check system resources
        resources = self.system_checker.check_system_resources()
        if not resources['sufficient']:
            if not self.config.get('force_deploy', False):
                self.logger.error("❌ Insufficient system resources. Use --force to override.")
                return False

        # Check port availability
        required_ports = [8051, 8052, 8053]  # Real-time, Presentation, Orchestrator
        port_status = self.system_checker.check_port_availability(required_ports)

        unavailable_ports = [port for port, available in port_status.items() if not available]
        if unavailable_ports and not self.config.get('force_deploy', False):
            self.logger.error(f"❌ Ports {unavailable_ports} are not available. Use --force to override.")
            return False

        self.logger.info("✅ Environment validation passed")
        return True

    def install_dependencies(self) -> bool:
        """Install all required dependencies"""
        self.logger.info("📦 Installing dependencies...")

        # Find requirements file
        current_dir = Path(__file__).parent
        requirements_file = current_dir / 'requirements.txt'

        if not requirements_file.exists():
            self.logger.error(f"❌ Requirements file not found: {requirements_file}")
            return False

        # Install requirements
        if not self.dependency_manager.install_requirements(str(requirements_file)):
            return False

        # Verify critical imports
        import_status = self.dependency_manager.check_critical_imports()
        failed_imports = [pkg for pkg, status in import_status.items() if not status]

        if failed_imports:
            self.logger.error(f"❌ Critical packages failed to import: {failed_imports}")
            return False

        self.logger.info("✅ Dependencies installed and verified")
        return True

    def deploy_services(self) -> bool:
        """Deploy all analytics services"""
        self.logger.info("🚀 Deploying analytics services...")

        current_dir = Path(__file__).parent
        services_to_deploy = []

        # Define services
        if self.config.get('deploy_orchestrator', True):
            services_to_deploy.append({
                'name': 'orchestrator',
                'command': [sys.executable, 'analytics_orchestrator.py'],
                'health_url': 'http://localhost:8053/health',
                'cwd': str(current_dir)
            })

        if self.config.get('deploy_realtime', True):
            services_to_deploy.append({
                'name': 'realtime',
                'command': [sys.executable, 'real_time_business_intelligence.py'],
                'health_url': 'http://localhost:8051',
                'cwd': str(current_dir)
            })

        # Start services
        success_count = 0
        for service in services_to_deploy:
            if self.service_manager.start_service(
                service['name'],
                service['command'],
                service.get('cwd')
            ):
                success_count += 1

        # Wait for services to fully start
        self.logger.info("⏳ Waiting for services to initialize...")
        time.sleep(10)

        # Health checks
        healthy_services = 0
        for service in services_to_deploy:
            if self.service_manager.check_service_health(service['name'], service['health_url']):
                healthy_services += 1

        deployment_success = healthy_services == len(services_to_deploy)

        if deployment_success:
            self.logger.info("✅ All services deployed and healthy")
        else:
            self.logger.warning(f"⚠️ {healthy_services}/{len(services_to_deploy)} services are healthy")

        return deployment_success

    def run_deployment_tests(self) -> bool:
        """Run comprehensive deployment verification tests"""
        self.logger.info("🧪 Running deployment tests...")

        tests = [
            self._test_orchestrator_api,
            self._test_analytics_job_submission,
            self._test_system_health_monitoring
        ]

        passed_tests = 0
        for test in tests:
            try:
                if test():
                    passed_tests += 1
            except Exception as e:
                self.logger.error(f"❌ Test failed: {e}")

        test_success = passed_tests == len(tests)

        if test_success:
            self.logger.info("✅ All deployment tests passed")
        else:
            self.logger.warning(f"⚠️ {passed_tests}/{len(tests)} tests passed")

        return test_success

    def _test_orchestrator_api(self) -> bool:
        """Test orchestrator API endpoints"""
        import requests

        try:
            # Test system info endpoint
            response = requests.get('http://localhost:8053/api/v1/system/info', timeout=10)
            if response.status_code == 200:
                info = response.json()
                self.logger.info(f"✅ Orchestrator API test passed: {info.get('system', 'Unknown')}")
                return True
            else:
                self.logger.error(f"❌ Orchestrator API test failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Orchestrator API test failed: {e}")
            return False

    def _test_analytics_job_submission(self) -> bool:
        """Test analytics job submission"""
        import requests

        try:
            # Submit a test analysis job
            response = requests.post(
                'http://localhost:8053/api/v1/analytics/full',
                json={'test_mode': True},
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                job_id = result.get('job_id')
                self.logger.info(f"✅ Job submission test passed: {job_id}")
                return True
            else:
                self.logger.error(f"❌ Job submission test failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Job submission test failed: {e}")
            return False

    def _test_system_health_monitoring(self) -> bool:
        """Test system health monitoring"""
        import requests

        try:
            # Check health endpoint
            response = requests.get('http://localhost:8053/health', timeout=10)
            if response.status_code == 200:
                health = response.json()
                overall_status = health.get('overall_status', 'unknown')
                self.logger.info(f"✅ Health monitoring test passed: {overall_status}")
                return overall_status in ['healthy', 'degraded']
            else:
                self.logger.error(f"❌ Health monitoring test failed: HTTP {response.status_code}")
                return False
        except Exception as e:
            self.logger.error(f"❌ Health monitoring test failed: {e}")
            return False

    def generate_deployment_report(self) -> Dict[str, Any]:
        """Generate comprehensive deployment report"""
        return {
            'timestamp': time.time(),
            'deployment_config': self.config,
            'services': {
                name: {
                    'running': service['process'].poll() is None,
                    'pid': service['process'].pid if service['process'].poll() is None else None,
                    'started_at': service['started_at']
                }
                for name, service in self.service_manager.services.items()
            },
            'system_info': {
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}",
                'cpu_cores': multiprocessing.cpu_count(),
                'platform': sys.platform
            }
        }

    def run_full_deployment(self) -> bool:
        """Execute complete deployment process"""
        try:
            self.logger.info("🎼 Starting AIA Analytics Platform Deployment")

            # Step 1: Validate environment
            if not self.validate_environment():
                self.logger.error("❌ Environment validation failed")
                return False

            # Step 2: Install dependencies
            if not self.install_dependencies():
                self.logger.error("❌ Dependency installation failed")
                return False

            # Step 3: Deploy services
            if not self.deploy_services():
                self.logger.error("❌ Service deployment failed")
                return False

            # Step 4: Run tests
            if not self.run_deployment_tests():
                self.logger.warning("⚠️ Some deployment tests failed")
                if not self.config.get('ignore_test_failures', False):
                    return False

            # Step 5: Generate report
            report = self.generate_deployment_report()
            report_file = f"deployment_report_{int(time.time())}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"📋 Deployment report saved: {report_file}")
            self.logger.info("✅ AIA Analytics Platform deployment completed successfully!")

            return True

        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            return False

        finally:
            if self.config.get('cleanup_on_exit', True):
                self.service_manager.stop_all_services()

def main():
    """Main deployment function"""
    parser = argparse.ArgumentParser(description='Deploy AIA Analytics Platform')
    parser.add_argument('--force', action='store_true', help='Force deployment despite warnings')
    parser.add_argument('--no-orchestrator', action='store_true', help='Skip orchestrator deployment')
    parser.add_argument('--no-realtime', action='store_true', help='Skip real-time system deployment')
    parser.add_argument('--ignore-test-failures', action='store_true', help='Ignore test failures')
    parser.add_argument('--no-cleanup', action='store_true', help='Keep services running after deployment')

    args = parser.parse_args()

    # Configuration
    config = {
        'force_deploy': args.force,
        'deploy_orchestrator': not args.no_orchestrator,
        'deploy_realtime': not args.no_realtime,
        'ignore_test_failures': args.ignore_test_failures,
        'cleanup_on_exit': not args.no_cleanup
    }

    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║               🚀 AIA ANALYTICS PLATFORM DEPLOYMENT                            ║
║                                                                               ║
║    Institutional-Grade Business Intelligence System                            ║
║                                                                               ║
║  📊 Comprehensive financial modeling and projections                          ║
║  🔄 Real-time business intelligence monitoring                                 ║
║  🎯 Executive presentation generation                                          ║
║  🏢 Fortune 500 enterprise integration                                        ║
║  ⚡ High-performance analytics orchestration                                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    deployer = AnalyticsDeployer(config)

    try:
        success = deployer.run_full_deployment()

        if success:
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("\n📋 Analytics Platform Services:")
            print("  • Orchestrator API: http://localhost:8053")
            print("  • Real-Time Dashboard: http://localhost:8051")
            print("  • System Health: http://localhost:8053/health")
            print("\n💡 Next Steps:")
            print("  1. Access the orchestrator API to submit analytics jobs")
            print("  2. Monitor real-time business intelligence dashboard")
            print("  3. Generate executive presentations via API")
            print("  4. Review system health and performance metrics")

            if not config['cleanup_on_exit']:
                print("\n⚠️ Services are running in background")
                print("Use Ctrl+C to stop or manually terminate processes")

        else:
            print("\n❌ DEPLOYMENT FAILED!")
            print("Check logs above for detailed error information")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n🛑 Deployment interrupted by user")
        deployer.service_manager.stop_all_services()
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment crashed: {e}")
        deployer.service_manager.stop_all_services()
        sys.exit(1)

if __name__ == "__main__":
    main()