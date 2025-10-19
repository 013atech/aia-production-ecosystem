#!/usr/bin/env python3
"""
🎼 ANALYTICS ORCHESTRATOR
========================
Main orchestration system for institutional-grade analytics deployment

This system coordinates all analytics components to deliver comprehensive
business intelligence for Fortune 500 enterprises and institutional investors.

Features:
- Orchestrates institutional analytics system
- Manages real-time business intelligence
- Controls executive presentation generation
- Coordinates multi-agent analytics deployment
- Provides unified API for all analytics services
- Handles data pipeline orchestration
- Manages performance monitoring and optimization
- Provides comprehensive logging and error handling

Enterprise-grade reliability with institutional investor presentation quality.
"""

import asyncio
import concurrent.futures
import json
import logging
import multiprocessing
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
import signal

# Import our analytics systems
from institutional_analytics_system import InstitutionalAnalyticsSystem
from real_time_business_intelligence import RealTimeBusinessIntelligence
from executive_presentation_system import PresentationGenerator, PresentationViewer

# Web framework for unified API
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import waitress

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/Users/wXy/dev/Projects/aia/analytics/analytics_orchestrator.log')
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemHealth:
    """System health monitoring"""
    component: str
    status: str  # 'healthy', 'degraded', 'unhealthy'
    last_check: datetime
    response_time_ms: float
    error_count: int = 0
    uptime_percent: float = 100.0

@dataclass
class AnalyticsJob:
    """Analytics job definition"""
    job_id: str
    job_type: str  # 'full_analysis', 'real_time_monitoring', 'presentation_generation'
    parameters: Dict[str, Any]
    status: str  # 'pending', 'running', 'completed', 'failed'
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None

class SystemMonitor:
    """Advanced system monitoring and health checks"""

    def __init__(self):
        self.logger = logger.getChild('SystemMonitor')
        self.health_status = {}
        self.monitoring_active = False
        self.performance_metrics = {}

    def register_component(self, component_name: str, health_check: Callable):
        """Register a component for health monitoring"""
        self.health_status[component_name] = {
            'health_check': health_check,
            'status': SystemHealth(
                component=component_name,
                status='unknown',
                last_check=datetime.now(),
                response_time_ms=0
            )
        }
        self.logger.info(f"Registered component for monitoring: {component_name}")

    def start_monitoring(self, interval_seconds: int = 30):
        """Start continuous health monitoring"""
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, args=(interval_seconds,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
        self.logger.info(f"Started system monitoring with {interval_seconds}s interval")

    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        if hasattr(self, 'monitoring_thread'):
            self.monitoring_thread.join()
        self.logger.info("Stopped system monitoring")

    def _monitoring_loop(self, interval_seconds: int):
        """Main monitoring loop"""
        while self.monitoring_active:
            for component_name, component_info in self.health_status.items():
                try:
                    start_time = time.time()
                    health_check = component_info['health_check']

                    # Execute health check
                    is_healthy = health_check()
                    response_time = (time.time() - start_time) * 1000

                    # Update status
                    status = component_info['status']
                    status.last_check = datetime.now()
                    status.response_time_ms = response_time

                    if is_healthy:
                        status.status = 'healthy'
                        status.error_count = max(0, status.error_count - 1)
                    else:
                        status.status = 'unhealthy'
                        status.error_count += 1

                    # Calculate uptime
                    if status.error_count > 0:
                        status.uptime_percent = max(0, 100 - (status.error_count * 5))

                except Exception as e:
                    self.logger.error(f"Health check failed for {component_name}: {e}")
                    status = component_info['status']
                    status.status = 'unhealthy'
                    status.error_count += 1
                    status.last_check = datetime.now()

            time.sleep(interval_seconds)

    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health status"""
        overall_status = 'healthy'
        component_statuses = {}

        for component_name, component_info in self.health_status.items():
            status = component_info['status']
            component_statuses[component_name] = {
                'status': status.status,
                'last_check': status.last_check.isoformat(),
                'response_time_ms': status.response_time_ms,
                'error_count': status.error_count,
                'uptime_percent': status.uptime_percent
            }

            if status.status == 'unhealthy':
                overall_status = 'unhealthy'
            elif status.status == 'degraded' and overall_status == 'healthy':
                overall_status = 'degraded'

        return {
            'overall_status': overall_status,
            'components': component_statuses,
            'last_updated': datetime.now().isoformat()
        }

class JobManager:
    """Advanced job management for analytics tasks"""

    def __init__(self, max_concurrent_jobs: int = 4):
        self.logger = logger.getChild('JobManager')
        self.jobs = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent_jobs)
        self.job_queue = []
        self.max_concurrent_jobs = max_concurrent_jobs

    def submit_job(self, job: AnalyticsJob) -> str:
        """Submit an analytics job for execution"""
        self.jobs[job.job_id] = job
        job.status = 'pending'

        future = self.executor.submit(self._execute_job, job)
        self.job_queue.append({'job': job, 'future': future})

        self.logger.info(f"Submitted job: {job.job_id} ({job.job_type})")
        return job.job_id

    def _execute_job(self, job: AnalyticsJob):
        """Execute an analytics job"""
        try:
            job.status = 'running'
            job.started_at = datetime.now()

            self.logger.info(f"Executing job: {job.job_id}")

            if job.job_type == 'full_analysis':
                results = self._run_full_analysis(job.parameters)
            elif job.job_type == 'presentation_generation':
                results = self._run_presentation_generation(job.parameters)
            else:
                raise ValueError(f"Unknown job type: {job.job_type}")

            job.results = results
            job.status = 'completed'
            job.completed_at = datetime.now()

            self.logger.info(f"Completed job: {job.job_id}")

        except Exception as e:
            job.status = 'failed'
            job.error_message = str(e)
            job.completed_at = datetime.now()
            self.logger.error(f"Job failed: {job.job_id} - {e}")

    def _run_full_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute full institutional analysis"""
        system = InstitutionalAnalyticsSystem()
        return system.run_comprehensive_analysis()

    def _run_presentation_generation(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute presentation generation"""
        analysis_results = parameters.get('analysis_results', {})
        generator = PresentationGenerator()
        slides = generator.create_executive_presentation(analysis_results)

        return {
            'slides_generated': len(slides),
            'slides': [
                {
                    'title': slide.title,
                    'content_type': slide.content_type,
                    'slide_number': slide.slide_number
                }
                for slide in slides
            ]
        }

    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific job"""
        if job_id not in self.jobs:
            return None

        job = self.jobs[job_id]
        return {
            'job_id': job.job_id,
            'job_type': job.job_type,
            'status': job.status,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None,
            'error_message': job.error_message,
            'has_results': job.results is not None
        }

    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """Get status of all jobs"""
        return [self.get_job_status(job_id) for job_id in self.jobs.keys()]

    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Clean up old completed jobs"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        jobs_to_remove = []

        for job_id, job in self.jobs.items():
            if job.status in ['completed', 'failed'] and job.completed_at and job.completed_at < cutoff_time:
                jobs_to_remove.append(job_id)

        for job_id in jobs_to_remove:
            del self.jobs[job_id]

        if jobs_to_remove:
            self.logger.info(f"Cleaned up {len(jobs_to_remove)} old jobs")

class AnalyticsOrchestrator:
    """Main orchestrator for all analytics systems"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logger.getChild('AnalyticsOrchestrator')

        # Initialize components
        self.system_monitor = SystemMonitor()
        self.job_manager = JobManager(max_concurrent_jobs=self.config.get('max_concurrent_jobs', 4))

        # Analytics systems
        self.institutional_system = None
        self.realtime_system = None

        # Web API
        self.app = Flask(__name__)
        CORS(self.app)
        self.setup_api_routes()

        # System state
        self.is_running = False
        self.startup_time = None

        self.logger.info("🎼 Analytics Orchestrator initialized")

    def initialize_systems(self):
        """Initialize all analytics systems"""
        try:
            self.logger.info("🚀 Initializing analytics systems...")

            # Initialize institutional analytics
            self.institutional_system = InstitutionalAnalyticsSystem()

            # Initialize real-time system
            self.realtime_system = RealTimeBusinessIntelligence()

            # Register health checks
            self.system_monitor.register_component('institutional_analytics', self._check_institutional_health)
            self.system_monitor.register_component('realtime_analytics', self._check_realtime_health)
            self.system_monitor.register_component('job_manager', self._check_job_manager_health)

            self.logger.info("✅ All analytics systems initialized successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to initialize systems: {e}")
            raise

    def _check_institutional_health(self) -> bool:
        """Health check for institutional analytics system"""
        return self.institutional_system is not None

    def _check_realtime_health(self) -> bool:
        """Health check for real-time system"""
        return self.realtime_system is not None

    def _check_job_manager_health(self) -> bool:
        """Health check for job manager"""
        return len([j for j in self.job_manager.jobs.values() if j.status == 'failed']) < 5

    def setup_api_routes(self):
        """Setup REST API routes"""

        @self.app.route('/health', methods=['GET'])
        def health_check():
            """System health endpoint"""
            health = self.system_monitor.get_system_health()
            return jsonify(health)

        @self.app.route('/api/v1/analytics/full', methods=['POST'])
        def run_full_analysis():
            """Trigger full institutional analysis"""
            try:
                job_id = f"full_analysis_{int(time.time())}"
                parameters = request.get_json() or {}

                job = AnalyticsJob(
                    job_id=job_id,
                    job_type='full_analysis',
                    parameters=parameters,
                    status='pending',
                    created_at=datetime.now()
                )

                self.job_manager.submit_job(job)

                return jsonify({
                    'job_id': job_id,
                    'status': 'submitted',
                    'message': 'Full analysis job submitted successfully'
                })

            except Exception as e:
                self.logger.error(f"Failed to submit full analysis job: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v1/presentation/generate', methods=['POST'])
        def generate_presentation():
            """Generate executive presentation"""
            try:
                data = request.get_json() or {}
                job_id = f"presentation_{int(time.time())}"

                job = AnalyticsJob(
                    job_id=job_id,
                    job_type='presentation_generation',
                    parameters=data,
                    status='pending',
                    created_at=datetime.now()
                )

                self.job_manager.submit_job(job)

                return jsonify({
                    'job_id': job_id,
                    'status': 'submitted',
                    'message': 'Presentation generation job submitted successfully'
                })

            except Exception as e:
                self.logger.error(f"Failed to submit presentation job: {e}")
                return jsonify({'error': str(e)}), 500

        @self.app.route('/api/v1/jobs/<job_id>', methods=['GET'])
        def get_job_status(job_id):
            """Get job status"""
            status = self.job_manager.get_job_status(job_id)
            if status:
                return jsonify(status)
            return jsonify({'error': 'Job not found'}), 404

        @self.app.route('/api/v1/jobs/<job_id>/results', methods=['GET'])
        def get_job_results(job_id):
            """Get job results"""
            if job_id not in self.job_manager.jobs:
                return jsonify({'error': 'Job not found'}), 404

            job = self.job_manager.jobs[job_id]
            if job.status != 'completed':
                return jsonify({'error': 'Job not completed'}), 400

            return jsonify(job.results)

        @self.app.route('/api/v1/jobs', methods=['GET'])
        def list_jobs():
            """List all jobs"""
            jobs = self.job_manager.get_all_jobs()
            return jsonify(jobs)

        @self.app.route('/api/v1/system/info', methods=['GET'])
        def system_info():
            """Get system information"""
            return jsonify({
                'system': 'AIA Analytics Orchestrator',
                'version': '1.0.0',
                'startup_time': self.startup_time.isoformat() if self.startup_time else None,
                'uptime_seconds': (datetime.now() - self.startup_time).total_seconds() if self.startup_time else 0,
                'components': {
                    'institutional_analytics': self.institutional_system is not None,
                    'realtime_analytics': self.realtime_system is not None,
                    'job_manager': True,
                    'system_monitor': self.system_monitor.monitoring_active
                }
            })

    def start_orchestrator(self):
        """Start the analytics orchestrator"""
        try:
            self.logger.info("🎼 Starting Analytics Orchestrator...")
            self.startup_time = datetime.now()

            # Initialize systems
            self.initialize_systems()

            # Start monitoring
            self.system_monitor.start_monitoring(interval_seconds=30)

            # Start real-time system in background
            if self.realtime_system:
                realtime_thread = threading.Thread(target=self.realtime_system.start_system)
                realtime_thread.daemon = True
                realtime_thread.start()

            self.is_running = True
            self.logger.info("✅ Analytics Orchestrator started successfully")

        except Exception as e:
            self.logger.error(f"❌ Failed to start orchestrator: {e}")
            raise

    def stop_orchestrator(self):
        """Stop the analytics orchestrator"""
        self.logger.info("🛑 Stopping Analytics Orchestrator...")

        self.is_running = False

        # Stop monitoring
        self.system_monitor.stop_monitoring()

        # Stop real-time system
        if self.realtime_system:
            self.realtime_system.stop_system()

        # Shutdown job manager
        self.job_manager.executor.shutdown(wait=True)

        self.logger.info("👋 Analytics Orchestrator stopped")

    def run_api_server(self, host='0.0.0.0', port=8053, debug=False):
        """Run the API server"""
        self.logger.info(f"🌐 Starting API server on http://{host}:{port}")

        if debug:
            self.app.run(host=host, port=port, debug=debug)
        else:
            waitress.serve(self.app, host=host, port=port)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, shutting down gracefully...")
    if 'orchestrator' in globals():
        orchestrator.stop_orchestrator()
    sys.exit(0)

def main():
    """Main execution function"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║               🎼 ANALYTICS ORCHESTRATOR                                        ║
║                                                                               ║
║    Enterprise-Grade Analytics Deployment for Fortune 500 Organizations        ║
║                                                                               ║
║  🏢 Institutional Analytics System                                            ║
║  🔄 Real-Time Business Intelligence                                            ║
║  🎯 Executive Presentation Generation                                          ║
║  📊 Unified API for All Analytics Services                                    ║
║  🔍 Advanced System Monitoring & Health Checks                                ║
║  ⚡ High-Performance Job Management                                            ║
║                                                                               ║
║  🌐 REST API: http://localhost:8053                                           ║
║  📊 Real-Time Dashboard: http://localhost:8051                                ║
║  🎯 Presentations: http://localhost:8052                                      ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Configuration
    config = {
        'max_concurrent_jobs': 4,
        'monitoring_interval': 30,
        'api_port': 8053,
        'debug': False
    }

    global orchestrator
    orchestrator = AnalyticsOrchestrator(config)

    try:
        # Start orchestrator
        orchestrator.start_orchestrator()

        print("✅ Analytics Orchestrator started successfully!")
        print("\n📋 Available Services:")
        print("  • REST API: http://localhost:8053")
        print("  • Health Check: http://localhost:8053/health")
        print("  • System Info: http://localhost:8053/api/v1/system/info")
        print("\n🔄 Background Services:")
        print("  • Real-time data ingestion and monitoring")
        print("  • System health monitoring")
        print("  • Job queue management")
        print("\n💡 API Endpoints:")
        print("  • POST /api/v1/analytics/full - Run full analysis")
        print("  • POST /api/v1/presentation/generate - Generate presentation")
        print("  • GET /api/v1/jobs - List all jobs")
        print("  • GET /api/v1/jobs/<job_id> - Get job status")

        print("\nPress Ctrl+C to stop the orchestrator\n")

        # Run API server
        orchestrator.run_api_server(port=config['api_port'], debug=config['debug'])

    except KeyboardInterrupt:
        print("\n🛑 Shutting down Analytics Orchestrator...")
        orchestrator.stop_orchestrator()
    except Exception as e:
        print(f"\n❌ Orchestrator error: {e}")
        logger.error(f"Orchestrator error: {e}")
        orchestrator.stop_orchestrator()

if __name__ == "__main__":
    main()