#!/usr/bin/env python3
"""
HAK/GAL Performance Optimizer Load Tests
Locust-based load testing for the monitoring system
"""

from locust import HttpUser, task, between
import random
import json

class HAKGALPerformanceUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when a user starts"""
        self.client.verify = False  # Disable SSL verification for testing
    
    @task(3)
    def get_metrics(self):
        """Get current metrics (most common operation)"""
        with self.client.get("/api/metrics", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'timestamp' in data:
                        response.success()
                    else:
                        response.failure("Invalid metrics response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(2)
    def get_health(self):
        """Get health status"""
        with self.client.get("/api/health", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('status') == 'healthy':
                        response.success()
                    else:
                        response.failure("Unhealthy status")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_metrics_history(self):
        """Get metrics history"""
        limit = random.randint(10, 100)
        with self.client.get(f"/api/metrics/history?limit={limit}", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Invalid history response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON response")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_dashboard(self):
        """Get dashboard page"""
        with self.client.get("/", catch_response=True) as response:
            if response.status_code == 200:
                if "HAK/GAL Performance Monitor" in response.text:
                    response.success()
                else:
                    response.failure("Invalid dashboard content")
            else:
                response.failure(f"HTTP {response.status_code}")
    
    @task(1)
    def get_prometheus_metrics(self):
        """Get Prometheus metrics"""
        with self.client.get("/metrics", catch_response=True) as response:
            if response.status_code == 200:
                if "mcp_cache_hits" in response.text:
                    response.success()
                else:
                    response.failure("Invalid Prometheus metrics")
            else:
                response.failure(f"HTTP {response.status_code}")

class HAKGALStressUser(HttpUser):
    wait_time = between(0.1, 0.5)
    weight = 1  # Lower weight for stress testing
    
    def on_start(self):
        """Called when a user starts"""
        self.client.verify = False
    
    @task(10)
    def rapid_metrics_requests(self):
        """Rapid fire metrics requests"""
        self.client.get("/api/metrics")
    
    @task(5)
    def rapid_health_requests(self):
        """Rapid fire health requests"""
        self.client.get("/api/health")
    
    @task(2)
    def large_history_requests(self):
        """Request large amounts of history data"""
        self.client.get("/api/metrics/history?limit=1000")