#!/usr/bin/env python3
"""
Quick test script for HAK/GAL Performance Monitor
"""

from hakgal_performance_monitor import HAKGALPerformanceMonitor
import tempfile
import os
import time

def test_monitor():
    """Test the performance monitor"""
    print("🚀 Testing HAK/GAL Performance Monitor...")
    
    # Test basic functionality
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, 'test.db')
    
    config = {
        'database_path': db_path,
        'monitoring_interval': 1.0,
        'max_history_size': 100,
        'max_query_samples': 100
    }
    
    try:
        monitor = HAKGALPerformanceMonitor(config)
        print('✅ Monitor created successfully')
        
        # Test metrics collection
        metrics = monitor._collect_metrics()
        print(f'✅ Metrics collected: CPU={metrics.system_cpu_percent:.1f}%, Memory={metrics.system_memory_percent:.1f}%')
        
        # Test query time recording
        monitor.record_query_time(0.1)
        monitor.record_query_time(0.2)
        print(f'✅ Query times recorded: {len(monitor.query_times)} entries')
        
        # Test cache events
        monitor.record_cache_event(hit=True)
        monitor.record_cache_event(hit=False)
        hits = monitor.cache_stats['hits']
        misses = monitor.cache_stats['misses']
        print(f'✅ Cache events recorded: Hits={hits}, Misses={misses}')
        
        # Test report generation
        report = monitor.generate_report(timeframe_minutes=1)
        print(f'✅ Report generated: {len(report)} keys')
        
        # Test monitoring loop (short)
        monitor.start_monitoring()
        time.sleep(2)
        monitor.stop_monitoring()
        print(f'✅ Monitoring loop tested: {len(monitor.metrics_history)} metrics collected')
        
        print('🎉 All tests passed!')
        return True
        
    except Exception as e:
        print(f'❌ Test failed: {e}')
        return False
    finally:
        monitor.stop_monitoring()
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)

if __name__ == "__main__":
    test_monitor()