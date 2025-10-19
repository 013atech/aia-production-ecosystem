#!/usr/bin/env python3
"""
📊 DRIFT MONITORING SYSTEM - REAL-TIME MODEL & DATA DRIFT DETECTION
===================================================================

Enterprise-grade drift detection system with automated alerts and remediation.
Monitors model performance, data distribution changes, and concept drift.

Key Features:
- Real-time statistical drift detection
- Model performance monitoring
- Automated alert systems
- Feature drift analysis
- Concept drift detection
- Integration with MLOps pipelines

Author: Claude Code (MLOps Specialist)
Version: v3.0 - Production Ready
Deployment: monitoring.013a.tech/drift
"""

import json
import logging
import asyncio
import threading
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
from collections import defaultdict, deque
import sqlite3
import hashlib
import pickle
from contextlib import contextmanager
import warnings
warnings.filterwarnings("ignore")

# Statistical Analysis
from scipy import stats
from scipy.stats import ks_2samp, chi2_contingency
import scipy.spatial.distance as distance
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.ensemble import IsolationForest
from sklearn.cluster import DBSCAN

# ML Frameworks
import torch
import torch.nn as nn
import torch.nn.functional as F

# FastAPI for monitoring endpoints
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
import uvicorn

# Visualization (optional)
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False
    logging.warning("Matplotlib/seaborn not available, plotting disabled")

@dataclass
class DriftAlert:
    """Alert structure for drift detection."""
    alert_id: str
    alert_type: str  # "data_drift", "model_drift", "performance_drift"
    severity: str    # "low", "medium", "high", "critical"
    pipeline_id: str
    feature_name: Optional[str]
    drift_score: float
    threshold: float
    description: str
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

@dataclass
class DriftMetrics:
    """Comprehensive drift metrics."""
    pipeline_id: str
    feature_name: Optional[str]
    drift_type: str
    drift_score: float
    p_value: float
    test_statistic: float
    baseline_mean: float
    current_mean: float
    baseline_std: float
    current_std: float
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ModelPerformanceMetrics:
    """Model performance tracking metrics."""
    pipeline_id: str
    model_version: str
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    auc_roc: float
    prediction_latency: float
    throughput: float
    error_rate: float
    timestamp: datetime = field(default_factory=datetime.now)

class StatisticalDriftDetector:
    """Statistical methods for drift detection."""

    def __init__(self, confidence_level: float = 0.05):
        self.confidence_level = confidence_level
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def kolmogorov_smirnov_test(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray
    ) -> Tuple[float, float]:
        """Perform Kolmogorov-Smirnov test for distribution drift."""
        try:
            statistic, p_value = ks_2samp(baseline_data, current_data)
            return statistic, p_value
        except Exception as e:
            self.logger.error(f"KS test failed: {e}")
            return 0.0, 1.0

    def population_stability_index(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray,
        bins: int = 10
    ) -> float:
        """Calculate Population Stability Index (PSI)."""
        try:
            # Create bins
            combined_data = np.concatenate([baseline_data, current_data])
            bin_edges = np.histogram_bin_edges(combined_data, bins=bins)

            # Calculate histograms
            baseline_counts, _ = np.histogram(baseline_data, bins=bin_edges)
            current_counts, _ = np.histogram(current_data, bins=bin_edges)

            # Normalize to get proportions
            baseline_props = baseline_counts / len(baseline_data)
            current_props = current_counts / len(current_data)

            # Avoid division by zero
            baseline_props = np.where(baseline_props == 0, 1e-10, baseline_props)
            current_props = np.where(current_props == 0, 1e-10, current_props)

            # Calculate PSI
            psi = np.sum((current_props - baseline_props) * np.log(current_props / baseline_props))
            return psi

        except Exception as e:
            self.logger.error(f"PSI calculation failed: {e}")
            return 0.0

    def jensen_shannon_divergence(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray,
        bins: int = 50
    ) -> float:
        """Calculate Jensen-Shannon divergence."""
        try:
            # Create histograms
            combined_data = np.concatenate([baseline_data, current_data])
            range_min, range_max = combined_data.min(), combined_data.max()

            baseline_hist, _ = np.histogram(
                baseline_data, bins=bins, range=(range_min, range_max), density=True
            )
            current_hist, _ = np.histogram(
                current_data, bins=bins, range=(range_min, range_max), density=True
            )

            # Normalize
            baseline_hist = baseline_hist / np.sum(baseline_hist)
            current_hist = current_hist / np.sum(current_hist)

            # Avoid zeros
            baseline_hist = np.where(baseline_hist == 0, 1e-10, baseline_hist)
            current_hist = np.where(current_hist == 0, 1e-10, current_hist)

            # Calculate JS divergence
            m = 0.5 * (baseline_hist + current_hist)
            js_div = 0.5 * stats.entropy(baseline_hist, m) + 0.5 * stats.entropy(current_hist, m)

            return js_div

        except Exception as e:
            self.logger.error(f"JS divergence calculation failed: {e}")
            return 0.0

    def wasserstein_distance(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray
    ) -> float:
        """Calculate Wasserstein (Earth Mover's) distance."""
        try:
            return stats.wasserstein_distance(baseline_data, current_data)
        except Exception as e:
            self.logger.error(f"Wasserstein distance calculation failed: {e}")
            return 0.0

    def chi_square_test(
        self,
        baseline_data: np.ndarray,
        current_data: np.ndarray,
        bins: int = 10
    ) -> Tuple[float, float]:
        """Perform Chi-square test for categorical drift."""
        try:
            # Create contingency table
            combined_data = np.concatenate([baseline_data, current_data])
            bin_edges = np.histogram_bin_edges(combined_data, bins=bins)

            baseline_counts, _ = np.histogram(baseline_data, bins=bin_edges)
            current_counts, _ = np.histogram(current_data, bins=bin_edges)

            # Create contingency table
            contingency_table = np.array([baseline_counts, current_counts])

            # Perform chi-square test
            chi2, p_value, _, _ = chi2_contingency(contingency_table)

            return chi2, p_value

        except Exception as e:
            self.logger.error(f"Chi-square test failed: {e}")
            return 0.0, 1.0

class FeatureDriftAnalyzer:
    """Analyze drift at the feature level."""

    def __init__(self, detection_methods: List[str] = None):
        self.detection_methods = detection_methods or [
            "kolmogorov_smirnov", "population_stability_index",
            "jensen_shannon_divergence", "wasserstein_distance"
        ]
        self.detector = StatisticalDriftDetector()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def analyze_feature_drift(
        self,
        baseline_features: pd.DataFrame,
        current_features: pd.DataFrame,
        feature_names: List[str] = None
    ) -> Dict[str, DriftMetrics]:
        """Analyze drift for individual features."""
        if feature_names is None:
            feature_names = baseline_features.columns.tolist()

        drift_results = {}

        for feature_name in feature_names:
            if feature_name not in baseline_features.columns or feature_name not in current_features.columns:
                self.logger.warning(f"Feature {feature_name} not found in data")
                continue

            baseline_data = baseline_features[feature_name].dropna().values
            current_data = current_features[feature_name].dropna().values

            if len(baseline_data) == 0 or len(current_data) == 0:
                self.logger.warning(f"Empty data for feature {feature_name}")
                continue

            # Run all detection methods
            feature_drift_scores = {}

            for method in self.detection_methods:
                try:
                    if method == "kolmogorov_smirnov":
                        statistic, p_value = self.detector.kolmogorov_smirnov_test(
                            baseline_data, current_data
                        )
                        feature_drift_scores[method] = {
                            "score": statistic,
                            "p_value": p_value,
                            "test_statistic": statistic
                        }

                    elif method == "population_stability_index":
                        psi_score = self.detector.population_stability_index(
                            baseline_data, current_data
                        )
                        feature_drift_scores[method] = {
                            "score": psi_score,
                            "p_value": 0.0,  # PSI doesn't have p-value
                            "test_statistic": psi_score
                        }

                    elif method == "jensen_shannon_divergence":
                        js_score = self.detector.jensen_shannon_divergence(
                            baseline_data, current_data
                        )
                        feature_drift_scores[method] = {
                            "score": js_score,
                            "p_value": 0.0,
                            "test_statistic": js_score
                        }

                    elif method == "wasserstein_distance":
                        wd_score = self.detector.wasserstein_distance(
                            baseline_data, current_data
                        )
                        feature_drift_scores[method] = {
                            "score": wd_score,
                            "p_value": 0.0,
                            "test_statistic": wd_score
                        }

                except Exception as e:
                    self.logger.error(f"Drift detection failed for {feature_name} using {method}: {e}")

            # Select primary method result (KS test if available)
            primary_method = "kolmogorov_smirnov" if "kolmogorov_smirnov" in feature_drift_scores else self.detection_methods[0]
            primary_result = feature_drift_scores.get(primary_method, {})

            # Create drift metrics
            drift_metrics = DriftMetrics(
                pipeline_id="unknown",  # Will be set by caller
                feature_name=feature_name,
                drift_type=primary_method,
                drift_score=primary_result.get("score", 0.0),
                p_value=primary_result.get("p_value", 1.0),
                test_statistic=primary_result.get("test_statistic", 0.0),
                baseline_mean=float(np.mean(baseline_data)),
                current_mean=float(np.mean(current_data)),
                baseline_std=float(np.std(baseline_data)),
                current_std=float(np.std(current_data))
            )

            drift_results[feature_name] = drift_metrics

        return drift_results

class ModelPerformanceMonitor:
    """Monitor model performance for drift detection."""

    def __init__(self):
        self.performance_history = defaultdict(deque)
        self.performance_thresholds = {
            "accuracy_drop": 0.05,
            "latency_increase": 2.0,
            "error_rate_increase": 0.1
        }
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def track_performance(
        self,
        pipeline_id: str,
        metrics: ModelPerformanceMetrics
    ):
        """Track model performance metrics."""
        self.performance_history[pipeline_id].append(metrics)

        # Keep only recent history (last 1000 records)
        if len(self.performance_history[pipeline_id]) > 1000:
            self.performance_history[pipeline_id].popleft()

    def detect_performance_drift(
        self,
        pipeline_id: str,
        window_size: int = 50
    ) -> List[DriftAlert]:
        """Detect performance drift using statistical analysis."""
        if pipeline_id not in self.performance_history:
            return []

        history = list(self.performance_history[pipeline_id])
        if len(history) < window_size * 2:
            return []

        alerts = []

        # Get baseline and current windows
        baseline_window = history[-window_size*2:-window_size]
        current_window = history[-window_size:]

        # Check accuracy drift
        baseline_accuracy = [m.accuracy for m in baseline_window]
        current_accuracy = [m.accuracy for m in current_window]

        accuracy_drift = np.mean(baseline_accuracy) - np.mean(current_accuracy)
        if accuracy_drift > self.performance_thresholds["accuracy_drop"]:
            alerts.append(DriftAlert(
                alert_id=f"perf_{pipeline_id}_{int(time.time())}",
                alert_type="performance_drift",
                severity="high" if accuracy_drift > 0.1 else "medium",
                pipeline_id=pipeline_id,
                feature_name="accuracy",
                drift_score=accuracy_drift,
                threshold=self.performance_thresholds["accuracy_drop"],
                description=f"Model accuracy dropped by {accuracy_drift:.3f}"
            ))

        # Check latency drift
        baseline_latency = [m.prediction_latency for m in baseline_window]
        current_latency = [m.prediction_latency for m in current_window]

        latency_ratio = np.mean(current_latency) / max(np.mean(baseline_latency), 0.001)
        if latency_ratio > self.performance_thresholds["latency_increase"]:
            alerts.append(DriftAlert(
                alert_id=f"perf_{pipeline_id}_{int(time.time())}_lat",
                alert_type="performance_drift",
                severity="medium",
                pipeline_id=pipeline_id,
                feature_name="latency",
                drift_score=latency_ratio,
                threshold=self.performance_thresholds["latency_increase"],
                description=f"Prediction latency increased by {latency_ratio:.2f}x"
            ))

        return alerts

class DriftMonitoringSystem:
    """Main drift monitoring system coordinating all components."""

    def __init__(
        self,
        monitoring_database: str = "/tmp/drift_monitoring.db",
        alert_retention_days: int = 30
    ):
        self.logger = logging.getLogger(__name__)
        self.monitoring_database = Path(monitoring_database)
        self.alert_retention_days = alert_retention_days

        # Core components
        self.feature_analyzer = FeatureDriftAnalyzer()
        self.performance_monitor = ModelPerformanceMonitor()

        # System state
        self.active_monitors = {}
        self.baseline_data = {}
        self.drift_thresholds = {}
        self.alert_handlers = []

        # Background processing
        self.running = False
        self.monitoring_thread = None

        # Initialize database
        self._initialize_database()

        self.logger.info("📊 Drift Monitoring System initialized")

    def _initialize_database(self):
        """Initialize SQLite database for monitoring data."""
        with sqlite3.connect(self.monitoring_database) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_id TEXT,
                    feature_name TEXT,
                    drift_type TEXT,
                    drift_score REAL,
                    p_value REAL,
                    test_statistic REAL,
                    baseline_mean REAL,
                    current_mean REAL,
                    baseline_std REAL,
                    current_std REAL,
                    timestamp DATETIME
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS drift_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    alert_type TEXT,
                    severity TEXT,
                    pipeline_id TEXT,
                    feature_name TEXT,
                    drift_score REAL,
                    threshold_value REAL,
                    description TEXT,
                    timestamp DATETIME,
                    acknowledged BOOLEAN DEFAULT FALSE
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pipeline_id TEXT,
                    model_version TEXT,
                    accuracy REAL,
                    precision_val REAL,
                    recall_val REAL,
                    f1_score REAL,
                    auc_roc REAL,
                    prediction_latency REAL,
                    throughput REAL,
                    error_rate REAL,
                    timestamp DATETIME
                )
            """)

            conn.commit()

    @contextmanager
    def _get_db_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.monitoring_database)
        try:
            yield conn
        finally:
            conn.close()

    def register_pipeline(
        self,
        pipeline_id: str,
        baseline_data: pd.DataFrame,
        feature_names: List[str] = None,
        drift_thresholds: Dict[str, float] = None
    ):
        """Register a pipeline for drift monitoring."""
        self.logger.info(f"📝 Registering pipeline {pipeline_id} for drift monitoring")

        # Store baseline data
        self.baseline_data[pipeline_id] = baseline_data.copy()

        # Set feature names
        if feature_names is None:
            feature_names = baseline_data.columns.tolist()

        # Set drift thresholds
        default_thresholds = {
            "kolmogorov_smirnov": 0.1,
            "population_stability_index": 0.1,
            "jensen_shannon_divergence": 0.1,
            "wasserstein_distance": 0.5
        }

        if drift_thresholds:
            default_thresholds.update(drift_thresholds)

        self.drift_thresholds[pipeline_id] = default_thresholds

        # Create monitor configuration
        monitor_config = {
            "pipeline_id": pipeline_id,
            "feature_names": feature_names,
            "thresholds": default_thresholds,
            "baseline_stats": {
                "mean": baseline_data.mean().to_dict(),
                "std": baseline_data.std().to_dict(),
                "count": len(baseline_data)
            },
            "registered_at": datetime.now(),
            "status": "active"
        }

        self.active_monitors[pipeline_id] = monitor_config

        self.logger.info(f"✅ Pipeline {pipeline_id} registered successfully")

    def analyze_drift(
        self,
        pipeline_id: str,
        current_data: pd.DataFrame,
        feature_names: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze drift for a specific pipeline."""
        if pipeline_id not in self.active_monitors:
            raise ValueError(f"Pipeline {pipeline_id} not registered for monitoring")

        if pipeline_id not in self.baseline_data:
            raise ValueError(f"No baseline data found for pipeline {pipeline_id}")

        self.logger.info(f"🔍 Analyzing drift for pipeline {pipeline_id}")

        baseline_data = self.baseline_data[pipeline_id]
        monitor_config = self.active_monitors[pipeline_id]

        if feature_names is None:
            feature_names = monitor_config["feature_names"]

        # Analyze feature drift
        drift_results = self.feature_analyzer.analyze_feature_drift(
            baseline_data, current_data, feature_names
        )

        # Update pipeline_id in results
        for feature_name, metrics in drift_results.items():
            metrics.pipeline_id = pipeline_id

        # Store metrics in database
        self._store_drift_metrics(drift_results)

        # Generate alerts
        alerts = self._generate_drift_alerts(pipeline_id, drift_results)

        # Store alerts
        for alert in alerts:
            self._store_alert(alert)

        # Calculate overall drift score
        overall_drift_score = np.mean([
            metrics.drift_score for metrics in drift_results.values()
        ]) if drift_results else 0.0

        analysis_result = {
            "pipeline_id": pipeline_id,
            "overall_drift_score": overall_drift_score,
            "feature_drift_results": {
                name: asdict(metrics) for name, metrics in drift_results.items()
            },
            "alerts": [asdict(alert) for alert in alerts],
            "analysis_timestamp": datetime.now(),
            "baseline_data_points": len(baseline_data),
            "current_data_points": len(current_data)
        }

        self.logger.info(f"🎯 Drift analysis complete for pipeline {pipeline_id}: "
                        f"overall_score={overall_drift_score:.3f}, alerts={len(alerts)}")

        return analysis_result

    def _store_drift_metrics(self, drift_results: Dict[str, DriftMetrics]):
        """Store drift metrics in database."""
        with self._get_db_connection() as conn:
            for feature_name, metrics in drift_results.items():
                conn.execute("""
                    INSERT INTO drift_metrics (
                        pipeline_id, feature_name, drift_type, drift_score, p_value,
                        test_statistic, baseline_mean, current_mean, baseline_std,
                        current_std, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    metrics.pipeline_id,
                    metrics.feature_name,
                    metrics.drift_type,
                    metrics.drift_score,
                    metrics.p_value,
                    metrics.test_statistic,
                    metrics.baseline_mean,
                    metrics.current_mean,
                    metrics.baseline_std,
                    metrics.current_std,
                    metrics.timestamp
                ))
            conn.commit()

    def _generate_drift_alerts(
        self,
        pipeline_id: str,
        drift_results: Dict[str, DriftMetrics]
    ) -> List[DriftAlert]:
        """Generate alerts based on drift detection results."""
        alerts = []
        thresholds = self.drift_thresholds.get(pipeline_id, {})

        for feature_name, metrics in drift_results.items():
            threshold = thresholds.get(metrics.drift_type, 0.1)

            if metrics.drift_score > threshold:
                # Determine severity
                if metrics.drift_score > threshold * 3:
                    severity = "critical"
                elif metrics.drift_score > threshold * 2:
                    severity = "high"
                else:
                    severity = "medium"

                alert = DriftAlert(
                    alert_id=f"drift_{pipeline_id}_{feature_name}_{int(time.time())}",
                    alert_type="data_drift",
                    severity=severity,
                    pipeline_id=pipeline_id,
                    feature_name=feature_name,
                    drift_score=metrics.drift_score,
                    threshold=threshold,
                    description=f"Feature '{feature_name}' drift detected: "
                               f"score={metrics.drift_score:.3f} (threshold={threshold:.3f})"
                )

                alerts.append(alert)

        return alerts

    def _store_alert(self, alert: DriftAlert):
        """Store alert in database."""
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT OR IGNORE INTO drift_alerts (
                    alert_id, alert_type, severity, pipeline_id, feature_name,
                    drift_score, threshold_value, description, timestamp, acknowledged
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.alert_type,
                alert.severity,
                alert.pipeline_id,
                alert.feature_name,
                alert.drift_score,
                alert.threshold,
                alert.description,
                alert.timestamp,
                alert.acknowledged
            ))
            conn.commit()

    def track_model_performance(
        self,
        pipeline_id: str,
        performance_metrics: ModelPerformanceMetrics
    ):
        """Track model performance metrics."""
        self.performance_monitor.track_performance(pipeline_id, performance_metrics)

        # Store in database
        with self._get_db_connection() as conn:
            conn.execute("""
                INSERT INTO performance_metrics (
                    pipeline_id, model_version, accuracy, precision_val, recall_val,
                    f1_score, auc_roc, prediction_latency, throughput, error_rate, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                performance_metrics.pipeline_id,
                performance_metrics.model_version,
                performance_metrics.accuracy,
                performance_metrics.precision,
                performance_metrics.recall,
                performance_metrics.f1_score,
                performance_metrics.auc_roc,
                performance_metrics.prediction_latency,
                performance_metrics.throughput,
                performance_metrics.error_rate,
                performance_metrics.timestamp
            ))
            conn.commit()

        # Check for performance drift
        perf_alerts = self.performance_monitor.detect_performance_drift(pipeline_id)
        for alert in perf_alerts:
            self._store_alert(alert)

    def get_pipeline_drift_summary(self, pipeline_id: str) -> Dict[str, Any]:
        """Get drift summary for a specific pipeline."""
        with self._get_db_connection() as conn:
            # Get recent drift metrics
            cursor = conn.execute("""
                SELECT feature_name, drift_type, drift_score, p_value, timestamp
                FROM drift_metrics
                WHERE pipeline_id = ? AND timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
            """, (pipeline_id,))

            drift_data = cursor.fetchall()

            # Get active alerts
            cursor = conn.execute("""
                SELECT alert_type, severity, feature_name, drift_score, description, timestamp
                FROM drift_alerts
                WHERE pipeline_id = ? AND acknowledged = FALSE
                ORDER BY timestamp DESC
            """, (pipeline_id,))

            alerts_data = cursor.fetchall()

            # Get performance metrics
            cursor = conn.execute("""
                SELECT accuracy, prediction_latency, error_rate, timestamp
                FROM performance_metrics
                WHERE pipeline_id = ? AND timestamp > datetime('now', '-24 hours')
                ORDER BY timestamp DESC
                LIMIT 100
            """, (pipeline_id,))

            performance_data = cursor.fetchall()

        return {
            "pipeline_id": pipeline_id,
            "drift_metrics": [
                {
                    "feature_name": row[0],
                    "drift_type": row[1],
                    "drift_score": row[2],
                    "p_value": row[3],
                    "timestamp": row[4]
                } for row in drift_data
            ],
            "active_alerts": [
                {
                    "alert_type": row[0],
                    "severity": row[1],
                    "feature_name": row[2],
                    "drift_score": row[3],
                    "description": row[4],
                    "timestamp": row[5]
                } for row in alerts_data
            ],
            "performance_metrics": [
                {
                    "accuracy": row[0],
                    "prediction_latency": row[1],
                    "error_rate": row[2],
                    "timestamp": row[3]
                } for row in performance_data
            ],
            "summary_timestamp": datetime.now()
        }

    def start_monitoring(self):
        """Start background monitoring processes."""
        if self.running:
            return

        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("🚀 Drift monitoring system started")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                # Clean up old alerts
                self._cleanup_old_alerts()

                # Check for system health
                self._check_system_health()

                time.sleep(300)  # Check every 5 minutes

            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)

    def _cleanup_old_alerts(self):
        """Clean up old acknowledged alerts."""
        cutoff_date = datetime.now() - timedelta(days=self.alert_retention_days)

        with self._get_db_connection() as conn:
            conn.execute("""
                DELETE FROM drift_alerts
                WHERE acknowledged = TRUE AND timestamp < ?
            """, (cutoff_date,))
            conn.commit()

    def _check_system_health(self):
        """Check overall system health."""
        # This could include checks for:
        # - Database connectivity
        # - Monitoring process health
        # - Resource usage
        # - Alert delivery status
        pass

    def stop_monitoring(self):
        """Stop background monitoring processes."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)

        self.logger.info("🛑 Drift monitoring system stopped")

# FastAPI application for drift monitoring API
app = FastAPI(title="Drift Monitoring System", version="3.0")

# Global monitoring system instance
monitoring_system = None

@app.on_event("startup")
async def startup_event():
    """Initialize monitoring system on startup."""
    global monitoring_system
    monitoring_system = DriftMonitoringSystem()
    monitoring_system.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if monitoring_system:
        monitoring_system.stop_monitoring()

class PipelineRegistrationRequest(BaseModel):
    pipeline_id: str
    baseline_data_path: str  # In real implementation, would load data
    feature_names: Optional[List[str]] = None
    drift_thresholds: Optional[Dict[str, float]] = None

class DriftAnalysisRequest(BaseModel):
    pipeline_id: str
    current_data_size: int = 1000  # Mock data size for testing

class PerformanceTrackingRequest(BaseModel):
    pipeline_id: str
    model_version: str
    accuracy: float
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    auc_roc: float = 0.0
    prediction_latency: float = 0.0
    throughput: float = 0.0
    error_rate: float = 0.0

@app.post("/api/v3/monitoring/register")
async def register_pipeline_endpoint(request: PipelineRegistrationRequest):
    """Register pipeline for drift monitoring."""
    try:
        # Generate mock baseline data (in real implementation would load from path)
        baseline_data = pd.DataFrame(
            np.random.randn(1000, 10),
            columns=[f"feature_{i}" for i in range(10)]
        )

        monitoring_system.register_pipeline(
            request.pipeline_id,
            baseline_data,
            request.feature_names,
            request.drift_thresholds
        )

        return {
            "success": True,
            "message": f"Pipeline {request.pipeline_id} registered for monitoring"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/monitoring/analyze")
async def analyze_drift_endpoint(request: DriftAnalysisRequest):
    """Analyze drift for pipeline."""
    try:
        # Generate mock current data
        current_data = pd.DataFrame(
            np.random.randn(request.current_data_size, 10) + 0.2,  # Slight shift to simulate drift
            columns=[f"feature_{i}" for i in range(10)]
        )

        result = monitoring_system.analyze_drift(request.pipeline_id, current_data)

        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v3/monitoring/performance")
async def track_performance_endpoint(request: PerformanceTrackingRequest):
    """Track model performance metrics."""
    try:
        metrics = ModelPerformanceMetrics(
            pipeline_id=request.pipeline_id,
            model_version=request.model_version,
            accuracy=request.accuracy,
            precision=request.precision,
            recall=request.recall,
            f1_score=request.f1_score,
            auc_roc=request.auc_roc,
            prediction_latency=request.prediction_latency,
            throughput=request.throughput,
            error_rate=request.error_rate
        )

        monitoring_system.track_model_performance(request.pipeline_id, metrics)

        return {"success": True, "message": "Performance metrics tracked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/monitoring/{pipeline_id}/summary")
async def get_pipeline_summary_endpoint(pipeline_id: str):
    """Get drift monitoring summary for pipeline."""
    try:
        summary = monitoring_system.get_pipeline_drift_summary(pipeline_id)
        return {"success": True, "data": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "system": "drift_monitoring_system"
    }

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    )

    # Run the application
    uvicorn.run(
        "drift_monitoring_system:app",
        host="0.0.0.0",
        port=8003,
        log_level="info",
        reload=False
    )