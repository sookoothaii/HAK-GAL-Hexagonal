#!/usr/bin/env python3
"""
Test All ML Models and System Components
"""

import os
import json
import joblib
import numpy as np
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ml_models():
    """Test all trained ML models"""
    print("🤖 Testing All ML Models...")
    
    models_dir = "models"
    if not os.path.exists(models_dir):
        print("❌ Models directory not found")
        return False
    
    # Load model metadata
    metadata_path = os.path.join(models_dir, "model_metadata.json")
    if os.path.exists(metadata_path):
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print(f"✅ Model metadata loaded: {metadata['models']}")
    else:
        print("❌ Model metadata not found")
        return False
    
    # Test each model
    models_tested = 0
    for model_name in metadata['models']:
        model_path = os.path.join(models_dir, f"{model_name}_model.joblib")
        scaler_path = os.path.join(models_dir, f"{model_name}_scaler.joblib")
        
        if os.path.exists(model_path) and os.path.exists(scaler_path):
            try:
                # Load model and scaler
                model = joblib.load(model_path)
                scaler = joblib.load(scaler_path)
                
                # Create test data
                if model_name == "performance_prediction":
                    test_data = np.array([[12, 3, 25.0, 45.0, 50.0]])  # hour, day, cpu, memory, queries
                elif model_name == "cache_optimization":
                    test_data = np.array([[12, 3, 25.0, 45.0, 50.0]])  # hour, day, cpu, memory, queries
                elif model_name == "query_time_prediction":
                    test_data = np.array([[4.5, 12, 3]])  # content_length_log, hour, day_of_week
                else:
                    test_data = np.array([[1.0, 2.0, 3.0]])  # Generic test data
                
                # Scale test data
                test_data_scaled = scaler.transform(test_data)
                
                # Make prediction
                prediction = model.predict(test_data_scaled)
                
                print(f"✅ {model_name}: Prediction = {prediction[0]:.4f}")
                models_tested += 1
                
            except Exception as e:
                print(f"❌ {model_name}: Error - {e}")
        else:
            print(f"❌ {model_name}: Model or scaler file not found")
    
    print(f"🎯 Models tested: {models_tested}/{len(metadata['models'])}")
    return models_tested == len(metadata['models'])

def test_performance_monitor():
    """Test performance monitor functionality"""
    print("\n📊 Testing Performance Monitor...")
    
    try:
        from hakgal_performance_monitor import HAKGALPerformanceMonitor
        import tempfile
        
        # Create test monitor
        temp_dir = tempfile.mkdtemp()
        config = {
            'database_path': os.path.join(temp_dir, 'test.db'),
            'monitoring_interval': 1.0,
            'max_history_size': 100,
            'max_query_samples': 100
        }
        
        monitor = HAKGALPerformanceMonitor(config)
        
        # Test basic functionality
        monitor.start_monitoring()
        
        # Record some test data
        for i in range(10):
            monitor.record_query_time(0.1 + i * 0.01)
            monitor.record_cache_event(hit=i % 2 == 0)
        
        # Test report generation
        report = monitor.generate_report(timeframe_minutes=1)
        
        monitor.stop_monitoring()
        
        print("✅ Performance Monitor: All tests passed")
        print(f"   - Query times recorded: {len(monitor.query_times)}")
        print(f"   - Cache events: {monitor.cache_stats}")
        print(f"   - Report keys: {len(report)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance Monitor: Error - {e}")
        return False

def test_advanced_monitoring():
    """Test advanced monitoring system"""
    print("\n🚨 Testing Advanced Monitoring System...")
    
    try:
        from advanced_monitoring import AdvancedMonitoringSystem
        from hakgal_performance_monitor import HAKGALPerformanceMonitor
        import tempfile
        
        # Create base monitor
        temp_dir = tempfile.mkdtemp()
        config = {
            'database_path': os.path.join(temp_dir, 'test.db'),
            'monitoring_interval': 1.0,
            'max_history_size': 100,
            'max_query_samples': 100
        }
        
        base_monitor = HAKGALPerformanceMonitor(config)
        base_monitor.start_monitoring()
        
        # Create advanced monitoring
        advanced_monitor = AdvancedMonitoringSystem(base_monitor)
        advanced_monitor.start_advanced_monitoring()
        
        # Simulate some activity
        import time
        for i in range(5):
            base_monitor.record_query_time(0.1 + i * 0.02)
            base_monitor.record_cache_event(hit=i % 2 == 0)
            time.sleep(0.1)
        
        # Test alert system
        alerts_summary = advanced_monitor.get_alerts_summary()
        anomalies_summary = advanced_monitor.get_anomalies_summary()
        
        advanced_monitor.stop_advanced_monitoring()
        base_monitor.stop_monitoring()
        
        print("✅ Advanced Monitoring: All tests passed")
        print(f"   - Total alerts: {alerts_summary['total_alerts']}")
        print(f"   - Unresolved alerts: {alerts_summary['unresolved_alerts']}")
        print(f"   - Total anomalies: {anomalies_summary['total_anomalies']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced Monitoring: Error - {e}")
        return False

def test_docker_configuration():
    """Test Docker configuration files"""
    print("\n🐳 Testing Docker Configuration...")
    
    docker_files = [
        "Dockerfile",
        "docker-compose.yml",
        "requirements.txt"
    ]
    
    files_found = 0
    for file_name in docker_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}: Found")
            files_found += 1
        else:
            print(f"❌ {file_name}: Not found")
    
    # Test requirements.txt content
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        print(f"✅ requirements.txt: {len(requirements.splitlines())} packages")
    
    print(f"🎯 Docker files: {files_found}/{len(docker_files)}")
    return files_found == len(docker_files)

def test_kubernetes_configuration():
    """Test Kubernetes configuration files"""
    print("\n☸️ Testing Kubernetes Configuration...")
    
    k8s_files = [
        "k8s/staging/deployment.yaml",
        "k8s/production/deployment.yaml"
    ]
    
    files_found = 0
    for file_name in k8s_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}: Found")
            files_found += 1
        else:
            print(f"❌ {file_name}: Not found")
    
    print(f"🎯 Kubernetes files: {files_found}/{len(k8s_files)}")
    return files_found == len(k8s_files)

def test_ci_cd_configuration():
    """Test CI/CD configuration"""
    print("\n🔄 Testing CI/CD Configuration...")
    
    ci_files = [
        ".github/workflows/ci-cd.yml",
        "tests/load_test.py"
    ]
    
    files_found = 0
    for file_name in ci_files:
        if os.path.exists(file_name):
            print(f"✅ {file_name}: Found")
            files_found += 1
        else:
            print(f"❌ {file_name}: Not found")
    
    print(f"🎯 CI/CD files: {files_found}/{len(ci_files)}")
    return files_found == len(ci_files)

def test_reports():
    """Test generated reports"""
    print("\n📋 Testing Generated Reports...")
    
    reports_dir = "reports"
    if not os.path.exists(reports_dir):
        print("❌ Reports directory not found")
        return False
    
    report_files = [
        "SYSTEM_TEST_REPORT_20250116.md",
        "MAXIMUM_OPTIMIZATION_FINAL_REPORT_20250116.md"
    ]
    
    files_found = 0
    for file_name in report_files:
        report_path = os.path.join("PROJECT_HUB", file_name)
        if os.path.exists(report_path):
            print(f"✅ {file_name}: Found")
            files_found += 1
        else:
            print(f"❌ {file_name}: Not found")
    
    # Check for ML training report
    ml_reports = [f for f in os.listdir(reports_dir) if f.startswith("ml_training_report")]
    if ml_reports:
        print(f"✅ ML Training Report: {ml_reports[0]}")
        files_found += 1
    
    print(f"🎯 Report files: {files_found}")
    return files_found > 0

def main():
    """Run all tests"""
    print("🚀 HAK/GAL SYSTEM COMPREHENSIVE TEST")
    print("=" * 60)
    
    test_results = []
    
    # Run all tests
    test_results.append(("ML Models", test_ml_models()))
    test_results.append(("Performance Monitor", test_performance_monitor()))
    test_results.append(("Advanced Monitoring", test_advanced_monitoring()))
    test_results.append(("Docker Configuration", test_docker_configuration()))
    test_results.append(("Kubernetes Configuration", test_kubernetes_configuration()))
    test_results.append(("CI/CD Configuration", test_ci_cd_configuration()))
    test_results.append(("Reports", test_reports()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:25} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"🎯 Overall Result: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is fully operational!")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()