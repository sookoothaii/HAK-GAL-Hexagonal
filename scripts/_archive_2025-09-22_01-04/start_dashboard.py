#!/usr/bin/env python3
"""
HAK/GAL Performance Dashboard Starter
"""

import os
import sys
import time
import threading
import random
from hakgal_performance_monitor import HAKGALPerformanceMonitor

def create_directories():
    """Create necessary directories"""
    dirs = ['data', 'logs', 'reports']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created directory: {dir_name}")

def simulate_realistic_activity(monitor):
    """Simulate realistic HAK/GAL activity"""
    print("🎭 Starting realistic activity simulation...")
    
    while True:
        try:
            # Simulate different types of queries
            query_types = [
                ('search_knowledge', 0.05, 0.15),
                ('add_fact', 0.02, 0.08),
                ('get_system_status', 0.01, 0.03),
                ('health_check', 0.01, 0.02),
                ('consistency_check', 0.1, 0.3)
            ]
            
            query_type, min_time, max_time = random.choice(query_types)
            query_time = random.uniform(min_time, max_time)
            
            # Record query time
            monitor.record_query_time(query_time)
            
            # Simulate cache behavior (70% hit rate for realistic scenario)
            if random.random() > 0.3:
                monitor.record_cache_event(hit=True)
            else:
                monitor.record_cache_event(hit=False)
            
            # Simulate occasional high-load scenarios
            if random.random() < 0.05:  # 5% chance
                for _ in range(5):
                    monitor.record_query_time(random.uniform(0.2, 0.5))
                    monitor.record_cache_event(hit=False)
            
            time.sleep(random.uniform(0.5, 2.0))
            
        except Exception as e:
            print(f"⚠️ Simulation error: {e}")
            time.sleep(1)

def main():
    """Main dashboard starter"""
    print("🚀 HAK/GAL Performance Dashboard Starter")
    print("=" * 50)
    
    # Create directories
    create_directories()
    
    # Configuration
    config = {
        'database_path': 'data/hakgal_performance.db',
        'monitoring_interval': 1.0,
        'max_history_size': 1000,
        'max_query_samples': 1000,
        'alert_thresholds': {
            'query_latency_ms': 100,
            'cache_hit_rate_percent': 80,
            'cpu_percent': 80,
            'memory_percent': 85
        }
    }
    
    try:
        # Initialize monitor
        print("🔧 Initializing performance monitor...")
        monitor = HAKGALPerformanceMonitor(config)
        monitor.start_monitoring()
        print("✅ Monitor started successfully")
        
        # Start activity simulation
        simulation_thread = threading.Thread(
            target=simulate_realistic_activity, 
            args=(monitor,), 
            daemon=True
        )
        simulation_thread.start()
        print("✅ Activity simulation started")
        
        # Wait a moment for initial data
        time.sleep(3)
        
        # Show initial metrics
        print("\n📊 Initial Metrics:")
        print("-" * 30)
        metrics = monitor._collect_metrics()
        print(f"CPU Usage: {metrics.system_cpu_percent:.1f}%")
        print(f"Memory Usage: {metrics.system_memory_percent:.1f}%")
        print(f"Query Times: {len(monitor.query_times)} recorded")
        print(f"Cache Stats: {monitor.cache_stats}")
        
        # Start Flask dashboard
        print("\n🌐 Starting Flask Dashboard...")
        print("📊 Dashboard: http://localhost:5000")
        print("📈 API Metrics: http://localhost:5000/api/metrics")
        print("🔍 Health Check: http://localhost:5000/api/health")
        print("📊 Prometheus: http://localhost:8000/metrics")
        print("⏹️  Press Ctrl+C to stop")
        print("=" * 50)
        
        # Run Flask app
        monitor.run_flask_app(host='0.0.0.0', port=5000, debug=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        monitor.stop_monitoring()
        print("✅ Dashboard stopped")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()